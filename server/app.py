import os
import tempfile

from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, request, send_file

from speech.speaker import Speaker
from brain.logic.conversation import generate_conversation_reply


app = Flask(__name__)
speaker = Speaker()


# ==========================================
# STAN AVATARA
# Na razie nie jest potrzebny do działania Nele,
# ale zostawiamy go bez zmian.
# ==========================================

avatar_state = {
    "speaking": False,
    "mouth": 0.0,
    "emotion": "neutral",
    "nod": False
}


# ==========================================
# CORS
# Pozwala stronie GitHub Pages łączyć się
# z backendem na Render.
# ==========================================

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
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

    avatar_state["nod"] = False

    return jsonify(state)


@app.route("/start")
def start():

    avatar_state["speaking"] = True
    avatar_state["mouth"] = 0.5

    return jsonify({
        "ok": True
    })


@app.route("/stop")
def stop():

    avatar_state["speaking"] = False
    avatar_state["mouth"] = 0.0
    avatar_state["emotion"] = "neutral"
    avatar_state["nod"] = False

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
        value = float(value)

    except ValueError:
        value = 0.0


    value = max(
        0.0,
        min(1.0, value)
    )


    avatar_state["mouth"] = value

    avatar_state["speaking"] = (
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


    avatar_state["emotion"] = value


    return jsonify({
        "ok": True,
        "emotion": value
    })


@app.route("/nod")
def nod():

    avatar_state["nod"] = True

    return jsonify({
        "ok": True
    })


# ==========================================
# MÓZG NELE
# ==========================================

def create_nele_reply(
    user_message: str
) -> str:

    try:

        return generate_conversation_reply(
            user_message,
            level="A1",
            lesson=1
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


    if not user_message:

        return jsonify({
            "reply":
                "Bitte sag etwas."
        }), 400


    answer = create_nele_reply(
        user_message
    )


    return jsonify({
        "reply": answer
    })


# ==========================================
# TTS – PIPER
#
# Na razie frontend Nele używa
# SpeechSynthesis przeglądarki.
# Endpoint zostawiamy na przyszłość.
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
            BytesIO(audio_data),
            mimetype="audio/wav",
            as_attachment=False,
            download_name="nele.wav"
        )


    except FileNotFoundError:

        return jsonify({
            "error":
                "Piper oder das deutsche Sprachmodell wurde nicht gefunden."
        }), 503


    except Exception as error:

        print(
            f"TTS error: {error}"
        )


        return jsonify({
            "error":
                "Die Sprachausgabe konnte nicht erstellt werden."
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
