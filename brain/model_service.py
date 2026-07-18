import os
import requests


OLLAMA_URL = os.environ.get(
    "OLLAMA_URL",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.environ.get(
    "OLLAMA_MODEL",
    "qwen3:4b"
)


SYSTEM_PROMPT = """
Du bist Nele, eine freundliche Deutschtrainerin.

Regeln:
- Sprich ausschließlich Deutsch.
- Übersetze nicht ins Polnische oder in andere Sprachen.
- Verwende einfache, natürliche Sätze.
- Passe deine Sprache an das Niveau A1 an.
- Verbessere Fehler freundlich und kurz.
- Stelle höchstens eine Frage pro Antwort.
- Sage niemals, dass du Qwen oder ein Sprachmodell bist.
- Dein Name ist Nele.
- Zeige niemals deinen Denkprozess.
- Gib nur die fertige Antwort aus.
"""


def generate_reply(user_message: str) -> str:
    if not user_message or not user_message.strip():
        return "Bitte sagen Sie etwas."

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_message.strip()
            }
        ],
        "stream": False,
        "think": False
    }

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        data = response.json()

        answer = data.get("message", {}).get("content", "").strip()

        if not answer:
            return "Entschuldigung, ich konnte keine Antwort erstellen."

        return answer

    except requests.RequestException:
        return "Entschuldigung, die Verbindung zum Sprachmodell ist momentan nicht verfügbar."
