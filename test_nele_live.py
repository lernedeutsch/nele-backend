#!/usr/bin/env python3
"""Live conversation test for production Nele in free or course mode."""
import json
import os
import sys
import time
import uuid

import requests

CHAT_URL = "https://nele-backend.onrender.com/api/chat"
WELCOME_URL = "https://nele-backend.onrender.com/welcome"
STUDENT_URL = "https://nele-backend.onrender.com/api/students"
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
    """Accept controlled questions from GitHub Actions, a durable request file, or CLI."""
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

    request_file = os.path.join(os.path.dirname(__file__), ".nele-live-request.json")
    if os.path.exists(request_file):
        try:
            with open(request_file, "r", encoding="utf-8") as handle:
                values = json.load(handle)
            questions = [str(value).strip() for value in values if str(value).strip()]
            if questions:
                return questions
        except (OSError, ValueError, TypeError):
            pass

    return sys.argv[1:] or QUESTIONS


def requested_mode():
    mode = str(os.environ.get("NELE_LIVE_MODE", "free") or "free").strip().lower()
    return mode if mode in {"free", "course"} else "free"


def requested_course():
    level = str(os.environ.get("NELE_LIVE_LEVEL", "A1") or "A1").strip().upper()
    raw_lesson = str(os.environ.get("NELE_LIVE_LESSON", "") or "").strip()
    if not raw_lesson:
        return level, None
    try:
        lesson = int(raw_lesson)
    except ValueError as error:
        raise SystemExit("NELE_LIVE_LESSON must be an integer.") from error
    if lesson < 1:
        raise SystemExit("NELE_LIVE_LESSON must be >= 1.")
    return level, lesson


def main():
    session_id = str(os.environ.get("NELE_LIVE_SESSION_ID", "") or "").strip() or f"chatgpt-live-test-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    conversation_mode = requested_mode()
    print(f"MODE: {conversation_mode}", flush=True)
    if conversation_mode == "course":
        level, lesson = requested_course()
        if lesson is not None:
            student = requests.post(
                STUDENT_URL,
                json={
                    "session_id": session_id,
                    "name": os.environ.get("NELE_LIVE_STUDENT_NAME", "Moni"),
                    "level": level,
                    "lesson": lesson,
                },
                timeout=90,
            )
            student.raise_for_status()
            student_payload = student.json()
            print(f"COURSE SELECT: {level}.{lesson} -> {json.dumps(student_payload, ensure_ascii=False)}")
            if int(student_payload.get("lesson") or 0) != lesson:
                raise RuntimeError(
                    f"Production did not select requested lesson {level}.{lesson}: {student_payload}"
                )

        welcome = requests.post(
            WELCOME_URL,
            json={"session_id": session_id, "conversation_mode": "course", "new_conversation": True},
            timeout=90,
        )
        welcome.raise_for_status()
        welcome_payload = welcome.json()
        print(f"NELE WELCOME: {welcome_payload.get('reply', '')}")
        print(f"COURSE META: {json.dumps(welcome_payload.get('meta') or {}, ensure_ascii=False)}")

        # A fresh Live session has no durable learner facts yet. Complete the
        # normal first-use onboarding through the public chat API, then reopen
        # the same learner. This makes targeted course tests exercise the
        # selected lesson as a returning learner without adding a test-only
        # production endpoint or bypassing onboarding state.
        if "Wie heißt du?" in str(welcome_payload.get("reply") or ""):
            bootstrap_answers = [
                f"ich heiße {os.environ.get('NELE_LIVE_STUDENT_NAME', 'Moni')}",
                os.environ.get("NELE_LIVE_BOOTSTRAP_ORIGIN", "ich komme aus Polen"),
            ]
            origin_confirm = str(os.environ.get("NELE_LIVE_BOOTSTRAP_ORIGIN_CONFIRM", "") or "").strip()
            if origin_confirm:
                bootstrap_answers.append(origin_confirm)
            bootstrap_answers.append(
                os.environ.get("NELE_LIVE_BOOTSTRAP_RESIDENCE", "ich wohne in Heidelberg")
            )
            for answer in bootstrap_answers:
                bootstrap = requests.post(
                    CHAT_URL,
                    json={
                        "message": answer,
                        "session_id": session_id,
                        "input_mode": "keyboard",
                        "conversation_mode": "course",
                    },
                    timeout=90,
                )
                bootstrap.raise_for_status()
                print(
                    f"ONBOARDING: {answer} -> "
                    f"{bootstrap.json().get('reply', '')}"
                )

            welcome = requests.post(
                WELCOME_URL,
                json={
                    "session_id": session_id,
                    "conversation_mode": "course",
                    "new_conversation": True,
                },
                timeout=90,
            )
            welcome.raise_for_status()
            welcome_payload = welcome.json()
            print(f"NELE RETURNING WELCOME: {welcome_payload.get('reply', '')}")
            if "Wie heißt du?" in str(welcome_payload.get("reply") or ""):
                raise RuntimeError("Course Live onboarding did not complete.")

    for question in requested_questions():
        print(f"REQUEST {question}", flush=True)
        try:
            response = requests.post(
                CHAT_URL,
                json={
                    "message": question,
                    "session_id": session_id,
                    "input_mode": "keyboard",
                    "conversation_mode": conversation_mode,
                },
                timeout=90,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as error:
            print(f"ERROR calling production Nele: {type(error).__name__}: {error}", flush=True)
            raise
        print(f"DU: {question}")
        print(f"NELE: {payload.get('reply', '')}")
        meta = payload.get("meta") or {}
        diagnostic = {
            key: meta.get(key)
            for key in (
                "dialogue_knowledge", "dialogue_id", "dialogue_active",
                "contextual_short_answer", "a1_everyday_router",
                "topic", "global_conversation_guard", "topic_manager",
            )
            if key in meta
        }
        print(f"ROUTER: {json.dumps(diagnostic, ensure_ascii=False, default=str)}")


if __name__ == "__main__":
    main()
