import os
from flask import Flask, jsonify, request

app = Flask(__name__)

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
    except:
        value = 0.0

    value = max(0.0, min(1.0, value))
    avatar_state["mouth"] = value
    avatar_state["speaking"] = value > 0.02

    return jsonify({"ok": True, "mouth": value})

@app.route("/emotion")
def emotion():
    value = request.args.get("value", "neutral")
    avatar_state["emotion"] = value
    return jsonify({"ok": True, "emotion": value})

@app.route("/nod")
def nod():
    avatar_state["nod"] = True
    return jsonify({"ok": True})
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_message = data.get("message", "")

    answer = f"Nele hat erhalten: {user_message}"

    return jsonify({
        "reply": answer
    })
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
