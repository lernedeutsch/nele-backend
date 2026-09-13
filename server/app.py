import os
import tempfile

from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, request, send_file

from speech.speaker import Speaker

from brain.logic.conversation import (
    generate_conversation_reply
)

from brain.logic.welcome import (
    generate_welcome_reply
)

from brain.logic.memory import (
    get_conversation_state,
    save_conversation_state,
    reset_conversation_state
)

from brain.logic.vocabulary_modules.practice import (
    finish_vocabulary_practice
)

from brain.logic.pronunciation_audio import (
    transcribe_audio
)


app = Flask(__name__)
speaker = Speaker()


# ==========================================
# MAKSYMALNY ROZMIAR AUDIO
# ==========================================

MAX_AUDIO_SIZE = (
    15
    * 1024
    * 1024
)


# ==========================================
# STAN AVATARA
# ==========================================

avatar_state = {
    "speaking": False,
    "mouth": 0.0,
    "emotion": "neutral",
    "nod": False
}


# ==========================================
# CORS
# ==========================================

@app.after_request
def after_request(response):

    response.headers[
        "Access-Control-Allow-Origin"
    ] = "*"

    response.headers[
        "Access-Control-Allow-Headers"
    ] = "Content-Type"

    response.headers[
        "Access-Control-Allow-Methods"
    ] = "GET, POST, OPTIONS"

    return response


# ==========================================
# STRONA GŁÓWNA BACKENDU
# ==========================================

@app.route("/")
def home():

    return jsonify({
        "name": "Nele Backend",
        "status": "online",
        "brain": "conversation"
    })


# ==========================================
# STATUS AVATARA
# ==========================================

@app.route("/status")
def status():

    state = avatar_state.copy()

    avatar_state[
        "nod"
    ] = False

    return jsonify(
        state
    )


@app.route("/start")
def start():

    avatar_state[
        "speaking"
    ] = True

    avatar_state[
        "mouth"
    ] = 0.5

    return jsonify({
        "ok": True
    })


@app.route("/stop")
def stop():

    avatar_state[
        "speaking"
    ] = False

    avatar_state[
        "mouth"
    ] = 0.0

    avatar_state[
        "emotion"
    ] = "neutral"

    avatar_state[
        "nod"
    ] = False

    return jsonify({
        "ok": True
    })


@app.route("/mouth")
def mouth():

    value = request.args.get(
        "value",
        "0"
    )

    try:

        value = float(
            value
        )

    except ValueError:

        value = 0.0


    value = max(
        0.0,
        min(
            1.0,
            value
        )
    )


    avatar_state[
        "mouth"
    ] = value

    avatar_state[
        "speaking"
    ] = (
        value > 0.02
    )


    return jsonify({
        "ok": True,
        "mouth": value
    })


@app.route("/emotion")
def emotion():

    value = request.args.get(
        "value",
        "neutral"
    ).strip()


    allowed_emotions = {
        "neutral",
        "happy",
        "sad",
        "surprised",
        "thinking"
    }


    if value not in allowed_emotions:

        value = "neutral"


    avatar_state[
        "emotion"
    ] = value


    return jsonify({
        "ok": True,
        "emotion": value
    })


@app.route("/nod")
def nod():

    avatar_state[
        "nod"
    ] = True

    return jsonify({
        "ok": True
    })


# ==========================================
# NORMALIZACJA SESSION ID
# ==========================================

def normalize_session_id(
    session_id
):

    session_id = str(
        session_id or "default"
    ).strip()


    if not session_id:

        session_id = "default"


    return session_id[:100]


# ==========================================
# MÓZG NELE
# ==========================================

def create_nele_reply(
    user_message: str,
    session_id: str
) -> str:

    try:

        return generate_conversation_reply(
            user_message,
            level="A1",
            lesson=1,
            session_id=session_id
        )

    except Exception as error:

        print(
            f"Nele conversation error: {error}"
        )

        return (
            "Entschuldigung. "
            "Ich kann gerade keine Antwort erstellen."
        )


# ==========================================
# POWITANIE NELE
# ==========================================

def create_welcome_reply(
    session_id
):

    try:

        state = get_conversation_state(
            session_id
        )


        finish_vocabulary_practice(
            state
        )


        save_conversation_state(
            session_id
        )


        return generate_welcome_reply(
            session_id
        )


    except Exception as error:

        print(
            f"Nele welcome error: {error}"
        )

        return (
            "Hallo! "
            "Ich bin Nele, "
            "deine persönliche Deutschtrainerin."
        )


# ==========================================
# ODCZYT DANYCH DLA /CHAT
# ==========================================

def get_chat_request_data():

    content_type = str(
        request.content_type
        or ""
    ).lower()


    # ======================================
    # MULTIPART:
    # TEKST + AUDIO
    # LUB SAMO AUDIO
    # ======================================

    if (
        "multipart/form-data"
        in content_type
    ):

        user_message = str(
            request.form.get(
                "message",
                ""
            )
        ).strip()


        session_id = normalize_session_id(
            request.form.get(
                "session_id",
                "default"
            )
        )


        audio_file = request.files.get(
            "audio"
        )


        return (
            user_message,
            session_id,
            audio_file
        )


    # ======================================
    # NORMALNY JSON
    # ======================================

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    user_message = str(
        data.get(
            "message",
            ""
        )
    ).strip()


    session_id = normalize_session_id(
        data.get(
            "session_id",
            "default"
        )
    )


    return (
        user_message,
        session_id,
        None
    )


# ==========================================
# SPRAWDZENIE AUDIO
# ==========================================

def get_audio_info(
    audio_file
):

    if not audio_file:

        return None


    filename = str(
        audio_file.filename
        or ""
    ).strip()


    mimetype = str(
        audio_file.mimetype
        or ""
    ).strip()


    if not filename:

        return None


    stream = audio_file.stream


    try:

        current_position = (
            stream.tell()
        )

    except Exception:

        current_position = 0


    try:

        stream.seek(
            0,
            os.SEEK_END
        )

        size = stream.tell()

        stream.seek(
            current_position
        )

    except Exception:

        size = None


    if (
        size is not None
        and
        size > MAX_AUDIO_SIZE
    ):

        return {
            "error":
                "audio_too_large",

            "size":
                size,

            "filename":
                filename,

            "mimetype":
                mimetype
        }


    return {
        "received":
            True,

        "filename":
            filename,

        "mimetype":
            mimetype,

        "size":
            size
    }


# ==========================================
# ROZSZERZENIE TYMCZASOWEGO AUDIO
# ==========================================

def get_audio_suffix(
    audio_file
):

    filename = str(
        getattr(
            audio_file,
            "filename",
            ""
        )
        or
        ""
    ).lower()


    mimetype = str(
        getattr(
            audio_file,
            "mimetype",
            ""
        )
        or
        ""
    ).lower()


    if filename.endswith(
        ".webm"
    ):

        return ".webm"


    if filename.endswith(
        ".ogg"
    ):

        return ".ogg"


    if filename.endswith(
        ".wav"
    ):

        return ".wav"


    if (
        filename.endswith(
            ".m4a"
        )
        or
        filename.endswith(
            ".mp4"
        )
    ):

        return ".m4a"


    if (
        "webm"
        in mimetype
    ):

        return ".webm"


    if (
        "ogg"
        in mimetype
    ):

        return ".ogg"


    if (
        "wav"
        in mimetype
    ):

        return ".wav"


    if (
        "mp4"
        in mimetype
        or
        "m4a"
        in mimetype
    ):

        return ".m4a"


    return ".webm"


# ==========================================
# ZAPIS AUDIO DO PLIKU TYMCZASOWEGO
# ==========================================

def save_chat_audio_to_temp(
    audio_file
):

    if not audio_file:

        return None


    suffix = get_audio_suffix(
        audio_file
    )


    temporary_file = (
        tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        )
    )


    audio_path = (
        temporary_file.name
    )


    temporary_file.close()


    try:

        try:

            audio_file.stream.seek(
                0
            )

        except Exception:

            pass


        audio_file.save(
            audio_path
        )


        if (
            not os.path.exists(
                audio_path
            )
        ):

            return None


        if (
            os.path.getsize(
                audio_path
            )
            <= 0
        ):

            return None


        return audio_path


    except Exception as error:

        print(
            "Nele audio save error:",
            error
        )


        if os.path.exists(
            audio_path
        ):

            try:

                os.remove(
                    audio_path
                )

            except OSError:

                pass


        return None


# ==========================================
# WHISPER:
# AUDIO -> TEKST
# ==========================================

def transcribe_chat_audio(
    audio_file
):

    audio_path = (
        save_chat_audio_to_temp(
            audio_file
        )
    )


    if not audio_path:

        return {
            "ok":
                False,

            "error":
                "audio_save_failed",

            "text":
                ""
        }


    try:

        result = transcribe_audio(
            audio_path,
            language="de"
        )


        return result


    except Exception as error:

        print(
            "Nele audio transcription error:",
            error
        )


        return {
            "ok":
                False,

            "error":
                "transcription_failed",

            "message":
                str(
                    error
                ),

            "text":
                ""
        }


    finally:

        if os.path.exists(
            audio_path
        ):

            try:

                os.remove(
                    audio_path
                )

            except OSError as error:

                print(
                    "Nele temporary audio "
                    "delete error:",
                    error
                )


# ==========================================
# WELCOME
# ==========================================

@app.route(
    "/welcome",
    methods=["POST", "OPTIONS"]
)
def welcome():

    if request.method == "OPTIONS":

        return jsonify({
            "ok": True
        })


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    session_id = normalize_session_id(
        data.get(
            "session_id",
            "default"
        )
    )


    answer = create_welcome_reply(
        session_id
    )


    return jsonify({
        "reply":
            answer,

        "session_id":
            session_id
    })


# ==========================================
# RESET CAŁEJ PAMIĘCI UŻYTKOWNIKA
# ==========================================

@app.route(
    "/reset",
    methods=["POST", "OPTIONS"]
)
def reset():

    if request.method == "OPTIONS":

        return jsonify({
            "ok": True
        })


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    session_id = normalize_session_id(
        data.get(
            "session_id",
            "default"
        )
    )


    try:

        reset_success = (
            reset_conversation_state(
                session_id
            )
        )

    except Exception as error:

        print(
            f"Nele reset error: {error}"
        )

        reset_success = False


    if not reset_success:

        return jsonify({
            "ok":
                False,

            "error":
                (
                    "Die Lerndaten konnten "
                    "nicht gelöscht werden."
                ),

            "session_id":
                session_id
        }), 500


    answer = create_welcome_reply(
        session_id
    )


    return jsonify({
        "ok":
            True,

        "reply":
            answer,

        "session_id":
            session_id
    })


# ==========================================
# CHAT
# ==========================================
#
# OBSŁUGIWANE:
#
# 1. JSON
#
# message
# session_id
#
#
# 2. multipart/form-data
#
# message – opcjonalnie
# session_id
# audio
#
#
# Jeśli otrzymamy samo audio:
#
# audio
#   ↓
# faster-whisper
#   ↓
# tekst
#   ↓
# mózg Nele
#   ↓
# odpowiedź
#
# ==========================================

@app.route(
    "/chat",
    methods=["POST", "OPTIONS"]
)
def chat():

    if request.method == "OPTIONS":

        return jsonify({
            "ok": True
        })


    (
        user_message,
        session_id,
        audio_file
    ) = get_chat_request_data()


    # ======================================
    # INFORMACJA O AUDIO
    # ======================================

    audio_info = get_audio_info(
        audio_file
    )


    # ======================================
    # AUDIO ZA DUŻE
    # ======================================

    if (
        audio_info
        and
        audio_info.get(
            "error"
        )
        ==
        "audio_too_large"
    ):

        return jsonify({
            "reply":
                "Die Audioaufnahme ist zu lang.",

            "session_id":
                session_id,

            "audio_received":
                False
        }), 413


    # ======================================
    # WHISPER
    #
    # Jeżeli mamy audio,
    # a nie mamy tekstu,
    # Whisper tworzy wiadomość.
    # ======================================

    transcription = None


    if (
        audio_info
        and
        not user_message
    ):

        print(
            "Nele: audio received, "
            "starting Whisper."
        )


        transcription = (
            transcribe_chat_audio(
                audio_file
            )
        )


        if not transcription.get(
            "ok"
        ):

            print(
                "Nele Whisper failed:",
                transcription
            )


            return jsonify({
                "reply":
                    (
                        "Ich konnte deine "
                        "Aufnahme leider noch "
                        "nicht verstehen. "
                        "Versuch es bitte "
                        "noch einmal."
                    ),

                "session_id":
                    session_id,

                "audio_received":
                    True,

                "transcription_ok":
                    False,

                "transcription_error":
                    transcription.get(
                        "error"
                    )
            }), 503


        user_message = str(
            transcription.get(
                "text",
                ""
            )
        ).strip()


        print(
            "Nele Whisper text:",
            user_message
        )


    # ======================================
    # BRAK ROZPOZNANEJ MOWY
    # ======================================

    if not user_message:

        if audio_info:

            return jsonify({
                "reply":
                    (
                        "Ich habe leider keine "
                        "Sprache erkannt. "
                        "Sag es bitte noch einmal."
                    ),

                "session_id":
                    session_id,

                "audio_received":
                    True,

                "transcription_ok":
                    True,

                "transcript":
                    ""
            }), 400


        return jsonify({
            "reply":
                "Bitte sag etwas.",

            "session_id":
                session_id,

            "audio_received":
                False
        }), 400


    # ======================================
    # NORMALNA ODPOWIEDŹ NELE
    # ======================================

    answer = create_nele_reply(
        user_message,
        session_id
    )


    response_data = {
        "reply":
            answer,

        "session_id":
            session_id,

        "audio_received":
            bool(
                audio_info
            )
    }


    # ======================================
    # JEŚLI UŻYTO WHISPERA,
    # ZWRACAMY TEŻ TRANSKRYPCJĘ
    # ======================================

    if transcription:

        response_data[
            "transcription_ok"
        ] = True

        response_data[
            "transcript"
        ] = user_message

        response_data[
            "detected_language"
        ] = transcription.get(
            "language"
        )

        response_data[
            "audio_duration"
        ] = transcription.get(
            "duration"
        )


    return jsonify(
        response_data
    )


# ==========================================
# TTS – PIPER
# ==========================================

@app.route(
    "/tts",
    methods=["POST", "OPTIONS"]
)
def tts():

    if request.method == "OPTIONS":

        return jsonify({
            "ok": True
        })


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    text = str(
        data.get(
            "text",
            ""
        )
    ).strip()


    if not text:

        return jsonify({
            "error":
                "Bitte geben Sie einen Text ein."
        }), 400


    if len(text) > 1000:

        return jsonify({
            "error":
                "Der Text ist zu lang."
        }), 400


    temporary_file = (
        tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        )
    )


    wav_path = (
        temporary_file.name
    )


    temporary_file.close()


    try:

        speaker.create_wav(
            text,
            wav_path
        )


        audio_data = (
            Path(
                wav_path
            ).read_bytes()
        )


        return send_file(
            BytesIO(
                audio_data
            ),
            mimetype="audio/wav",
            as_attachment=False,
            download_name="nele.wav"
        )


    except FileNotFoundError:

        return jsonify({
            "error":
                (
                    "Piper oder das deutsche "
                    "Sprachmodell wurde nicht "
                    "gefunden."
                )
        }), 503


    except Exception as error:

        print(
            f"TTS error: {error}"
        )


        return jsonify({
            "error":
                (
                    "Die Sprachausgabe konnte "
                    "nicht erstellt werden."
                )
        }), 500


    finally:

        if os.path.exists(
            wav_path
        ):

            os.remove(
                wav_path
            )


# ==========================================
# START SERWERA
# ==========================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port
    )
