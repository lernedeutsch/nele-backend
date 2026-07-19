import os

from flask import Flask, jsonify, request


app = Flask(__name__)


USE_OLLAMA = os.environ.get(
    "USE_OLLAMA",
    "false"
).lower() == "true"


avatar_state = {
    "speaking": False,
    "mouth": 0.0,
    "emotion": "neutral",
    "nod": False
}


@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/")
def home():
    return jsonify({
        "name": "Nele Backend",
        "status": "online",
        "ollama_enabled": USE_OLLAMA
    })


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
    value = request.args.get("value", "0")

    try:
        value = float(value)
    except ValueError:
        value = 0.0

    value = max(0.0, min(1.0, value))

    avatar_state["mouth"] = value
    avatar_state["speaking"] = value > 0.02

    return jsonify({
        "ok": True,
        "mouth": value
    })


@app.route("/emotion")
def emotion():
    value = request.args.get("value", "neutral").strip()

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


def generate_rule_reply(user_message: str) -> str:
    message_lower = user_message.lower()

    if "wie geht" in message_lower:
        return "Mir geht es gut, danke. Und wie geht es Ihnen?"

    if "hallo" in message_lower or "guten tag" in message_lower:
        return "Hallo! Schön, dass Sie da sind. Wie heißen Sie?"

    if "wie heißt du" in message_lower or "wie heisst du" in message_lower:
        return "Ich heiße Nele. Ich bin Ihre Deutschtrainerin."

    return f"Sie haben gesagt: {user_message}"


def create_nele_reply(user_message: str) -> str:
    if not USE_OLLAMA:
        return generate_rule_reply(user_message)

    try:
        from brain.model_service import generate_reply
        return generate_reply(user_message)

    except Exception as error:
        print(f"Ollama error: {error}")
        return generate_rule_reply(user_message)


@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({
            "ok": True
        })

    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()

    if not user_message:
        return jsonify({
            "reply": "Bitte sagen Sie etwas."
        }), 400

    answer = create_nele_reply(user_message)

    return jsonify({
        "reply": answer
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
