#!/usr/bin/env python3
"""Live conversation test for production Nele free conversation."""
import json
import os
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


def requested_questions():
    """Accept controlled questions from GitHub Actions, with CLI fallback."""
    raw = str(os.environ.get("NELE_LIVE_QUESTIONS_JSON", "") or "").strip()
    if raw:
        try:
            values = json.loads(raw)
        except json.JSONDecodeError as error:
            raise SystemExit(f"Invalid NELE_LIVE_QUESTIONS_JSON: {error}") from error

        if not isinstance(values, list):
            raise SystemExit("NELE_LIVE_QUESTIONS_JSON must be a JSON list.")

        questions = [str(value).strip() for value in values if str(value).strip()]
        if questions:
            return questions

    return sys.argv[1:] or QUESTIONS


def main():
    session_id = f"chatgpt-live-test-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    for question in requested_questions():
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
