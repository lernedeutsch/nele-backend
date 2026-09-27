import os
import secrets
import tempfile

from io import BytesIO
from pathlib import Path

from flask import Flask, g, jsonify, request, send_file

from speech.speaker import Speaker

from brain.logic.conversation import generate_conversation_reply
from brain.logic.free_conversation import generate_free_conversation_reply, generate_free_welcome
from brain.logic.welcome import generate_welcome_reply
from brain.logic.memory import (
    get_conversation_state,
    refresh_conversation_state,
    save_conversation_state,
    reset_conversation_state,
)
from brain.logic.learner_identity import normalize_learner_id
from brain.logic.session_service import start_conversation_session
from brain.logic.pronunciation_audio import transcribe_audio
from brain.logic.conversation_output import remember_nele_output
from brain.logic.personal_sentences import handle_personal_sentence
from brain.nele3_upgrade import UPGRADE_VERSION
from brain.nele3_upgrade.api import nele3_api
from brain.nele3_upgrade.router import handle_upgrade_message
from brain.nele3_upgrade.state import (
    ensure_upgrade_state,
    record_event,
)
from brain.memory.persistent_memory import (
    acquire_session_lock,
    release_session_lock,
)


app = Flask(__name__)
app.register_blueprint(nele3_api)
speaker = Speaker()

MAX_AUDIO_SIZE = 15 * 1024 * 1024

avatar_state = {
    "speaking": False,
    "mouth": 0.0,
    "emotion": "neutral",
    "nod": False,
}


# =========================================================
# CORS
# =========================================================

DEFAULT_CORS_ORIGINS = (
    "https://lernedeutsch.github.io",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
)


def get_allowed_origins():
    configured = str(
        os.environ.get("CORS_ORIGINS", "")
        or ""
    ).strip()

    if not configured:
        return set(DEFAULT_CORS_ORIGINS)

    return {
        item.strip().rstrip("/")
        for item in configured.split(",")
        if item.strip()
    }


@app.after_request
def after_request(response):
    origin = str(
        request.headers.get("Origin", "")
        or ""
    ).strip().rstrip("/")

    if origin and origin in get_allowed_origins():
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"

    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type, X-Nele-Reset-Token"
    )
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# =========================================================
# DESTRUCTIVE RESET PROTECTION
# =========================================================

def destructive_reset_is_authorized():
    enabled = str(
        os.environ.get(
            "NELE_ENABLE_DESTRUCTIVE_RESET",
            "false",
        )
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    secret = str(
        os.environ.get(
            "NELE_RESET_SECRET",
            "",
        )
        or ""
    ).strip()

    provided = str(
        request.headers.get(
            "X-Nele-Reset-Token",
            "",
        )
        or ""
    ).strip()

    if not enabled or not secret or not provided:
        return False

    return secrets.compare_digest(
        provided,
        secret,
    )


def destructive_reset_blocked_response():
    return jsonify({
        "ok": False,
        "error": "destructive_reset_disabled",
        "message": (
            "Der vollständige Lernreset ist nicht öffentlich verfügbar."
        ),
    }), 403


# =========================================================
# BASIC STATUS
# =========================================================

@app.route("/")
def home():
    return jsonify({
        "name": "Nele Backend",
        "status": "online",
        "brain": "conversation",
        "nele3_upgrade": UPGRADE_VERSION,
    })


@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "Nele Backend",
        "nele3_upgrade": UPGRADE_VERSION,
    })


# =========================================================
# AVATAR
# =========================================================

@app.route("/status")
def status():
    state = avatar_state.copy()
    avatar_state["nod"] = False
    return jsonify(state)


@app.route("/start")
def start():
    avatar_state["speaking"] = True
    avatar_state["mouth"] = 0.5
    return jsonify({"ok": True})


@app.route("/stop")
def stop():
    avatar_state["speaking"] = False
    avatar_state["mouth"] = 0.0
    avatar_state["emotion"] = "neutral"
    avatar_state["nod"] = False
    return jsonify({"ok": True})


@app.route("/mouth")
def mouth():
    value = request.args.get("value", "0")
    try:
        value = float(value)
    except ValueError:
        value = 0.0

    value = max(0.0, min(1.0, value))
    avatar_state["mouth"] = value
    avatar_state["speaking"] = value > 0.02
    return jsonify({"ok": True, "mouth": value})


@app.route("/emotion")
def emotion():
    value = request.args.get("value", "neutral").strip()
    allowed = {"neutral", "happy", "sad", "surprised", "thinking"}
    if value not in allowed:
        value = "neutral"
    avatar_state["emotion"] = value
    return jsonify({"ok": True, "emotion": value})


@app.route("/nod")
def nod():
    avatar_state["nod"] = True
    return jsonify({"ok": True})


# =========================================================
# SESSION HELPERS
# =========================================================

def normalize_session_id(session_id):
    """Compatibility wrapper around the one production learner-id rule."""

    return normalize_learner_id(session_id)


STATEFUL_BODY_PATHS = {
    "/welcome",
    "/reset",
    "/chat",
    "/api/chat",
    "/api/students",
    "/api/session/start",
    "/api/activity/start",
    "/api/activity/answer",
    "/api/pronunciation/evaluate",
}

STATEFUL_PATH_PREFIXES = (
    "/api/reset/",
    "/api/dashboard/",
    "/api/daily/",
    "/api/weekly/",
    "/api/next/",
)


def _is_stateful_session_request():
    path = str(request.path or "")
    return (
        path in STATEFUL_BODY_PATHS
        or any(
            path.startswith(prefix)
            for prefix in STATEFUL_PATH_PREFIXES
        )
    )


def _request_learner_id():
    view_args = request.view_args or {}

    explicit = (
        view_args.get("session_id")
        or view_args.get("student_id")
    )
    if explicit:
        return normalize_learner_id(explicit)

    content_type = str(
        request.content_type
        or ""
    ).lower()

    if "multipart/form-data" in content_type:
        value = (
            request.form.get("session_id")
            or request.form.get("student_id")
        )
        return normalize_learner_id(value)

    data = request.get_json(
        silent=True
    ) or {}

    value = (
        data.get("session_id")
        or data.get("student_id")
    )

    return normalize_learner_id(value)


def session_id_required_response():
    return jsonify({
        "ok": False,
        "error": "session_id_required",
        "message": "Eine gültige session_id ist erforderlich.",
    }), 400


@app.before_request
def prepare_learner_request():
    """Serialize and refresh stateful learner requests."""

    if request.method == "OPTIONS":
        return None

    if not _is_stateful_session_request():
        return None

    session_id = _request_learner_id()

    if not session_id:
        return session_id_required_response()

    g.nele_session_id = session_id
    g.nele_session_lock = acquire_session_lock(
        session_id
    )

    refresh_conversation_state(
        session_id
    )

    return None


@app.teardown_request
def release_learner_request_lock(_error=None):
    connection = getattr(
        g,
        "nele_session_lock",
        None,
    )
    session_id = getattr(
        g,
        "nele_session_id",
        None,
    )

    if connection is not None and session_id:
        release_session_lock(
            connection,
            session_id,
        )


def create_nele_reply(
    user_message: str,
    session_id: str,
    transcript: str | None = None,
    input_mode: str | None = None,
    conversation_mode: str | None = None,
):
    """Run Nele 3 feature commands first, otherwise use Nele 1's original router."""
    try:
        state = get_conversation_state(session_id)
        ensure_upgrade_state(state)

        conversation_mode = str(conversation_mode or "course").strip().lower()
        if conversation_mode not in {"course", "free"}:
            conversation_mode = "course"
        state["conversation_mode"] = conversation_mode

        mode = str(input_mode or "").strip().lower()
        if mode not in {"voice", "keyboard"}:
            mode = "voice" if transcript else "keyboard"

        state["last_input_mode"] = mode
        state["input_mode"] = mode

        if conversation_mode == "free":
            answer, meta = generate_free_conversation_reply(
                user_message,
                state,
                session_id=session_id,
            )
            remember_nele_output(answer, state)
            save_conversation_state(session_id)
            return answer, meta or {}

        # Meine Sätze are also understood in course mode. This is a global
        # learner layer, not content hard-coded into one lesson.
        personal = handle_personal_sentence(
            user_message,
            state,
            mode="course",
        )
        if personal:
            answer = personal["reply"]
            remember_nele_output(answer, state)
            save_conversation_state(session_id)
            return answer, personal.get("meta", {})

        handled, answer, meta = handle_upgrade_message(
            user_message,
            state,
            session_id=session_id,
            transcript=transcript,
            input_mode=mode,
        )

        if handled:
            remember_nele_output(
                answer,
                state,
            )
            save_conversation_state(session_id)
            return answer, meta or {}

        answer = generate_conversation_reply(
            user_message,
            level="A1",
            lesson=1,
            session_id=session_id,
        )

        # Add a lightweight event without changing the original learning logic.
        record_event(state, "chat_turn", detail={"message_length": len(user_message or "")})
        save_conversation_state(session_id)
        progress = state.get("student_progress") or {}
        return answer, {
            "level": progress.get("current_level", "A1"),
            "lesson": progress.get("current_lesson", 1),
        }

    except Exception as error:
        print(f"Nele conversation error: {error}")
        return (
            "Entschuldigung. Ich kann gerade keine Antwort erstellen.",
            {"error": "conversation_error"},
        )


def create_welcome_reply(session_id, preserve_active_task=True, conversation_mode="course"):
    try:
        if str(conversation_mode).strip().lower() == "free":
            state = get_conversation_state(session_id)
            ensure_upgrade_state(state)
            state["conversation_mode"] = "free"
            answer = generate_free_welcome(state, session_id=session_id)
            remember_nele_output(answer, state)
            save_conversation_state(session_id)
            return answer
        return start_conversation_session(
            session_id,
            new_conversation=not preserve_active_task,
        )
    except Exception as error:
        print(f"Nele welcome error: {error}")
        return "Hallo! Ich bin Nele, deine persönliche Deutschtrainerin."


# =========================================================
# CHAT REQUEST PARSING
# =========================================================

def get_chat_request_data():
    content_type = str(request.content_type or "").lower()

    if "multipart/form-data" in content_type:
        user_message = str(request.form.get("message", "")).strip()
        session_id = getattr(g, "nele_session_id", None)
        audio_file = request.files.get("audio")
        input_mode = str(
            request.form.get("input_mode")
            or ("voice" if audio_file else "keyboard")
        ).strip().lower()
        conversation_mode = str(request.form.get("conversation_mode") or "course").strip().lower()
        return user_message, session_id, audio_file, input_mode, conversation_mode

    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()
    session_id = getattr(g, "nele_session_id", None)
    input_mode = str(data.get("input_mode") or "keyboard").strip().lower()
    conversation_mode = str(data.get("conversation_mode") or "course").strip().lower()
    return user_message, session_id, None, input_mode, conversation_mode


def get_audio_info(audio_file):
    if not audio_file:
        return None

    filename = str(audio_file.filename or "").strip()
    mimetype = str(audio_file.mimetype or "").strip()
    if not filename:
        return None

    stream = audio_file.stream
    try:
        current_position = stream.tell()
    except Exception:
        current_position = 0

    try:
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(current_position)
    except Exception:
        size = None

    if size is not None and size > MAX_AUDIO_SIZE:
        return {
            "error": "audio_too_large",
            "size": size,
            "filename": filename,
            "mimetype": mimetype,
        }

    return {
        "received": True,
        "filename": filename,
        "mimetype": mimetype,
        "size": size,
    }


def get_audio_suffix(audio_file):
    filename = str(getattr(audio_file, "filename", "") or "").lower()
    mimetype = str(getattr(audio_file, "mimetype", "") or "").lower()

    if filename.endswith(".webm") or "webm" in mimetype:
        return ".webm"
    if filename.endswith(".ogg") or "ogg" in mimetype:
        return ".ogg"
    if filename.endswith(".wav") or "wav" in mimetype:
        return ".wav"
    if filename.endswith((".m4a", ".mp4")) or "mp4" in mimetype or "m4a" in mimetype:
        return ".m4a"
    return ".webm"


def save_chat_audio_to_temp(audio_file):
    if not audio_file:
        return None

    temporary_file = tempfile.NamedTemporaryFile(delete=False, suffix=get_audio_suffix(audio_file))
    audio_path = temporary_file.name
    temporary_file.close()

    try:
        try:
            audio_file.stream.seek(0)
        except Exception:
            pass

        audio_file.save(audio_path)
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) <= 0:
            return None
        return audio_path

    except Exception as error:
        print("Nele audio save error:", error)
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                pass
        return None


def transcribe_chat_audio(audio_file):
    audio_path = save_chat_audio_to_temp(audio_file)
    if not audio_path:
        return {"ok": False, "error": "audio_save_failed", "text": ""}

    try:
        return transcribe_audio(audio_path, language="de")
    except Exception as error:
        print("Nele audio transcription error:", error)
        return {
            "ok": False,
            "error": "transcription_failed",
            "message": str(error),
            "text": "",
        }
    finally:
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError as error:
                print("Nele temporary audio delete error:", error)


# =========================================================
# WELCOME
# =========================================================

@app.route("/welcome", methods=["POST", "OPTIONS"])
def welcome():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    data = request.get_json(silent=True) or {}
    session_id = getattr(g, "nele_session_id", None)

    new_conversation = bool(
        data.get("new_conversation", False)
    )

    conversation_mode = str(data.get("conversation_mode") or "course").strip().lower()
    answer = create_welcome_reply(
        session_id,
        preserve_active_task=not new_conversation,
        conversation_mode=conversation_mode,
    )
    state = get_conversation_state(session_id)
    progress = state.get("student_progress") or {}
    return jsonify({
        "reply": answer,
        "session_id": session_id,
        "meta": {
            "level": progress.get("current_level", "A1"),
            "lesson": progress.get("current_lesson", 1),
        },
    })


# =========================================================
# RESET
# =========================================================

@app.route("/reset", methods=["POST", "OPTIONS"])
def reset():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    if not destructive_reset_is_authorized():
        return destructive_reset_blocked_response()

    data = request.get_json(silent=True) or {}
    session_id = getattr(g, "nele_session_id", None)

    try:
        reset_success = reset_conversation_state(session_id)
    except Exception as error:
        print(f"Nele reset error: {error}")
        reset_success = False

    if not reset_success:
        return jsonify({
            "ok": False,
            "error": "Die Lerndaten konnten nicht gelöscht werden.",
            "session_id": session_id,
        }), 500

    answer = create_welcome_reply(
        session_id,
        preserve_active_task=False
    )
    return jsonify({
        "ok": True,
        "reply": answer,
        "session_id": session_id,
    })


# =========================================================
# CHAT: JSON OR AUDIO
# =========================================================

@app.route("/chat", methods=["POST", "OPTIONS"])
@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    user_message, session_id, audio_file, input_mode, conversation_mode = get_chat_request_data()
    audio_info = get_audio_info(audio_file)

    if audio_info and audio_info.get("error") == "audio_too_large":
        return jsonify({
            "reply": "Die Audioaufnahme ist zu lang.",
            "session_id": session_id,
            "audio_received": False,
        }), 413

    transcription = None

    if audio_info and not user_message:
        print("Nele: audio received, starting Whisper.")
        transcription = transcribe_chat_audio(audio_file)

        if not transcription.get("ok"):
            print("Nele Whisper failed:", transcription)
            return jsonify({
                "reply": "Ich konnte deine Aufnahme leider noch nicht verstehen. Versuch es bitte noch einmal.",
                "session_id": session_id,
                "audio_received": True,
                "transcription_ok": False,
                "transcription_error": transcription.get("error"),
            }), 503

        user_message = str(transcription.get("text", "")).strip()
        print("Nele Whisper text:", user_message)

    if not user_message:
        if audio_info:
            return jsonify({
                "reply": "Ich habe leider keine Sprache erkannt. Sag es bitte noch einmal.",
                "session_id": session_id,
                "audio_received": True,
                "transcription_ok": True,
                "transcript": "",
            }), 400

        return jsonify({
            "reply": "Bitte sag etwas.",
            "session_id": session_id,
            "audio_received": False,
        }), 400

    answer, meta = create_nele_reply(
        user_message,
        session_id,
        transcript=(transcription or {}).get("text") if transcription else None,
        input_mode=input_mode,
        conversation_mode=conversation_mode,
    )

    response_data = {
        "reply": answer,
        "session_id": session_id,
        "student_id": session_id,
        "audio_received": bool(audio_info),
        "meta": meta or {},
    }

    if meta and meta.get("speak_text"):
        response_data["speak_text"] = meta["speak_text"]

    if transcription:
        response_data["transcription_ok"] = True
        response_data["transcript"] = user_message
        response_data["detected_language"] = transcription.get("language")
        response_data["audio_duration"] = transcription.get("duration")

    return jsonify(response_data)


# =========================================================
# NELE 3 COMPATIBILITY ENDPOINTS
# =========================================================

@app.route("/api/students", methods=["POST", "OPTIONS"])
def api_students():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    data = request.get_json(silent=True) or {}
    session_id = getattr(g, "nele_session_id", None)
    state = get_conversation_state(session_id)
    ensure_upgrade_state(state)

    name = str(data.get("name") or "").strip()
    if name and not state.get("name"):
        state["name"] = name

    # Optional course selection for clients and production live tests.
    # Existing callers remain unchanged when level/lesson are omitted.
    progress = state.setdefault("student_progress", {})
    level = str(data.get("level") or "").strip().upper()
    lesson = data.get("lesson")
    if level in {"A1", "A2", "B1", "B2", "C1", "C2"}:
        progress["current_level"] = level
    if lesson is not None:
        try:
            lesson = int(lesson)
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "invalid_lesson"}), 400
        if lesson < 1:
            return jsonify({"ok": False, "error": "invalid_lesson"}), 400
        progress["current_lesson"] = lesson

    save_conversation_state(session_id)
    return jsonify({
        "ok": True,
        "student_id": session_id,
        "session_id": session_id,
        "name": state.get("name"),
        "level": (state.get("student_progress") or {}).get("current_level", "A1"),
        "lesson": (state.get("student_progress") or {}).get("current_lesson", 1),
    })


@app.route("/api/reset/<student_id>", methods=["POST", "OPTIONS"])
def api_reset_student(student_id):
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    if not destructive_reset_is_authorized():
        return destructive_reset_blocked_response()

    session_id = getattr(g, "nele_session_id", None)
    try:
        ok = reset_conversation_state(session_id)
    except Exception as error:
        print(f"Nele API reset error: {error}")
        ok = False
    return jsonify({"ok": bool(ok), "reset": bool(ok), "student_id": session_id}), (200 if ok else 500)


@app.route("/api/asr", methods=["POST", "OPTIONS"])
def api_asr():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"ok": False, "error": "audio_required"}), 400

    info = get_audio_info(audio_file)
    if info and info.get("error") == "audio_too_large":
        return jsonify({"ok": False, "error": "audio_too_large"}), 413

    result = transcribe_chat_audio(audio_file)
    return jsonify(result), (200 if result.get("ok") else 503)


# =========================================================
# TTS – PIPER
# =========================================================

@app.route("/tts", methods=["POST", "OPTIONS"])
@app.route("/api/tts", methods=["POST", "OPTIONS"])
def tts():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()

    if not text:
        return jsonify({"error": "Bitte geben Sie einen Text ein."}), 400
    if len(text) > 1000:
        return jsonify({"error": "Der Text ist zu lang."}), 400

    temporary_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav_path = temporary_file.name
    temporary_file.close()

    try:
        speaker.create_wav(text, wav_path)
        audio_data = Path(wav_path).read_bytes()
        return send_file(
            BytesIO(audio_data),
            mimetype="audio/wav",
            as_attachment=False,
            download_name="nele.wav",
        )
    except FileNotFoundError:
        return jsonify({
            "error": "Piper oder das deutsche Sprachmodell wurde nicht gefunden."
        }), 503
    except Exception as error:
        print(f"TTS error: {error}")
        return jsonify({
            "error": "Die Sprachausgabe konnte nicht erstellt werden."
        }), 500
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
