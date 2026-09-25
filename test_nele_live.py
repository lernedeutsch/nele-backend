#!/usr/bin/env python3
"""Live smoke test for production Nele free conversation."""
import sys
import time
import uuid
import requests

CHAT_URL = "https://nele-backend.onrender.com/api/chat"
QUESTIONS = [
    "Wann hast du frei?",
    "Arbeitest du heute?",
    "Welches Wetter magst du am liebsten?",
]


def main():
    session_id = f"chatgpt-live-test-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    for question in (sys.argv[1:] or QUESTIONS):
        response = requests.post(
            CHAT_URL,
            json={
                "message": question,
                "session_id": session_id,
                "input_mode": "keyboard",
                "conversation_mode": "free",
            },
            timeout=90,
        )
        response.raise_for_status()
        print(f"DU: {question}")
        print(f"NELE: {response.json().get('reply', '')}")


if __name__ == "__main__":
    main()
