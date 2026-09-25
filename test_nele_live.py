#!/usr/bin/env python3
"""Live conversation test for production Nele free conversation."""
import sys
import time
import uuid
import requests

CHAT_URL = "https://nele-backend.onrender.com/api/chat"
QUESTIONS = [
    "Hallo Nele, wie geht es dir heute?",
    "Wann hast du frei?",
    "Arbeitest du heute?",
    "Arbeitest du am Sonntag?",
    "Welcher Tag ist heute?",
    "Ist heute Montag?",
    "Welches Wetter magst du am liebsten?",
    "Welche Wetter magst du am liebsten?",
    "Ich mag es, wenn es warm ist.",
    "Ich bin heute müde.",
    "Was machst du gern am Wochenende?",
]


def main():
    session_id = f"chatgpt-live-test-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    for question in (sys.argv[1:] or QUESTIONS):
        response = requests.post(
            CHAT_URL,
            json={"message": question, "session_id": session_id, "input_mode": "keyboard", "conversation_mode": "free"},
            timeout=90,
        )
        response.raise_for_status()
        print(f"DU: {question}")
        print(f"NELE: {response.json().get('reply', '')}")


if __name__ == "__main__":
    main()
