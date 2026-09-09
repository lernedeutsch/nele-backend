import os
import tempfile

from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, request, send_file

from speech.speaker import Speaker

from brain.logic.conversation import (
    generate_conversation_reply
)

from brain.logic.memory import (
    get_conversation_state,
    save_conversation_state
)

from brain.logic.onboarding import (
    is_onboarding_completed,
    is_new_user,
    get_onboarding_step,
    start_onboarding,
    get_onboarding_question
)

from brain.memory.user_facts import (
    get_user_fact
)


app = Flask(__name__)
speaker = Speaker()


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


        # ==================================
        # NOWY UŻYTKOWNIK
        # ==================================

        if (
            not is_onboarding_completed(
                state
            )
            and is_new_user(
                state
            )
        ):

            onboarding_step = (
                get_onboarding_step(
                    state
                )
            )

            if onboarding_step == 0:

                answer = start_onboarding(
                    state
                )

                save_conversation_state(
                    session_id
                )

                return answer


        # ==================================
        # ONBOARDING JUŻ ROZPOCZĘTY
        # ==================================

        if not is_onboarding_completed(
            state
        ):

            onboarding_step = (
                get_onboarding_step(
                    state
                )
            )

            if onboarding_step > 0:

                question = (
                    get_onboarding_question(
                        state
                    )
                )

                if question:

                    return question


        # ==================================
        # ZNANY UŻYTKOWNIK
        # ==================================

        name = get_user_fact(
            state,
            "name"
        )

        if name:

            return (
                f"Hallo {name}! "
                f"Schön, dich wiederzusehen. "
                f"Wie geht es dir?"
            )


        # ==================================
        # ZNANY UŻYTKOWNIK BEZ IMIENIA
        # ==================================

        return (
            "Hallo! "
            "Schön, dich wiederzusehen. "
            "Wie geht es dir?"
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
        "reply": answer,
        "session_id": session_id
    })


# ==========================================
# CHAT
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


    if not user_message:

        return jsonify({
            "reply":
                "Bitte sag etwas."
        }), 400


    answer = create_nele_reply(
        user_message,
        session_id
    )


    return jsonify({
        "reply": answer,
        "session_id": session_id
    })


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
                "Piper oder das deutsche "
                "Sprachmodell wurde nicht gefunden."
        }), 503


    except Exception as error:

        print(
            f"TTS error: {error}"
        )


        return jsonify({
            "error":
                "Die Sprachausgabe konnte "
                "nicht erstellt werden."
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
