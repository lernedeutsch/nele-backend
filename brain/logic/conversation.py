# ==========================================
# NELE – LOGIKA ROZMOWY
# ==========================================

import importlib.util
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_lesson(level="A1", lesson=1):
    """
    Wczytuje wiedzę Nele z odpowiedniej lekcji,
    np. brain/responses/A1/1.py
    """

    lesson_path = (
        BASE_DIR
        / "responses"
        / level
        / f"{lesson}.py"
    )

    if not lesson_path.exists():
        return []

    module_name = f"nele_{level}_{lesson}"

    spec = importlib.util.spec_from_file_location(
        module_name,
        lesson_path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return getattr(
        module,
        "LESSON_RESPONSES",
        []
    )


def normalize(text):
    """
    Przygotowuje tekst do rozpoznawania.
    """

    return (
        text
        .lower()
        .strip()
        .replace("?", "")
        .replace("!", "")
        .replace(".", "")
        .replace(",", "")
    )


def find_response(user_message, level="A1", lesson=1):
    """
    Szuka odpowiedniej reakcji Nele.
    """

    message = normalize(user_message)

    responses = load_lesson(
        level,
        lesson
    )

    for item in responses:

        patterns = item.get(
            "patterns",
            []
        )

        for pattern in patterns:

            pattern_normalized = normalize(
                pattern
            )

            if pattern_normalized in message:

                answers = item.get(
                    "responses",
                    []
                )

                follow_up = item.get(
                    "follow_up",
                    []
                )

                if answers:
                    answer = random.choice(
                        answers
                    )
                else:
                    answer = ""

                if follow_up:
                    question = random.choice(
                        follow_up
                    )

                    if answer:
                        answer += " " + question
                    else:
                        answer = question

                return answer

    return None


def generate_conversation_reply(
    user_message,
    level="A1",
    lesson=1
):
    """
    Główna funkcja rozmowy Nele.
    """

    answer = find_response(
        user_message,
        level,
        lesson
    )

    if answer:
        return answer

    return (
        "Ich habe dich verstanden, "
        "aber diese Antwort habe ich noch nicht gelernt."
    )
