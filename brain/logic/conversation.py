# ==========================================
# NELE – LOGIKA ROZMOWY Z PAMIĘCIĄ
# ==========================================

import importlib.util
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# PROSTA PAMIĘĆ ROZMOWY
# ==========================================

conversation_state = {
    "last_question": None,
    "name": None,
    "origin": None,
    "residence": None
}


# ==========================================
# WCZYTYWANIE LEKCJI
# ==========================================

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


# ==========================================
# NORMALIZACJA TEKSTU
# ==========================================

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


# ==========================================
# POMOCNICZE FUNKCJE
# ==========================================

def clean_short_answer(text):
    """
    Czyści krótką odpowiedź użytkownika,
    np. imię, kraj, miasto.
    """

    return (
        text
        .strip()
        .strip(".!?")
        .strip()
    )


def remember_follow_up(question):
    """
    Zapamiętuje, o co Nele właśnie zapytała.
    """

    question_normalized = normalize(question)

    if "wie heißt du" in question_normalized:
        conversation_state["last_question"] = "name"

    elif "woher kommst du" in question_normalized:
        conversation_state["last_question"] = "origin"

    elif "wo wohnst du" in question_normalized:
        conversation_state["last_question"] = "residence"

    elif "wie geht es dir" in question_normalized:
        conversation_state["last_question"] = "wellbeing"

    else:
        conversation_state["last_question"] = None


# ==========================================
# ODPOWIEDŹ NA PODSTAWIE PAMIĘCI
# ==========================================

def handle_context_answer(user_message):
    """
    Reaguje na krótkie odpowiedzi zależnie od tego,
    o co Nele pytała wcześniej.
    """

    last_question = conversation_state.get("last_question")

    if not last_question:
        return None

    answer = clean_short_answer(user_message)

    if not answer:
        return None


    # --------------------------------------
    # IMIĘ
    # --------------------------------------

    if last_question == "name":

        name = answer.split()[0].capitalize()

        conversation_state["name"] = name
        conversation_state["last_question"] = "origin"

        return f"Freut mich, {name}. Woher kommst du?"


    # --------------------------------------
    # POCHODZENIE
    # --------------------------------------

    if last_question == "origin":

        origin = answer

        origin_lower = normalize(origin)

        if origin_lower.startswith("aus "):
            origin = origin[4:].strip()

        conversation_state["origin"] = origin
        conversation_state["last_question"] = "residence"

        return f"Schön. Du kommst aus {origin}. Wo wohnst du jetzt?"


    # --------------------------------------
    # MIEJSCE ZAMIESZKANIA
    # --------------------------------------

    if last_question == "residence":

        residence = answer

        residence_lower = normalize(residence)

        if residence_lower.startswith("in "):
            residence = residence[3:].strip()

        conversation_state["residence"] = residence
        conversation_state["last_question"] = None

        name = conversation_state.get("name")

        if name:
            return f"Ah, {name}, du wohnst in {residence}. Schön!"

        return f"Ah, du wohnst in {residence}. Schön!"


    # --------------------------------------
    # SAMOPOCZUCIE
    # --------------------------------------

    if last_question == "wellbeing":

        message = normalize(answer)

        conversation_state["last_question"] = None

        if message in [
            "gut",
            "sehr gut",
            "mir geht es gut",
            "mir gehts gut"
        ]:
            return "Das freut mich! Was möchtest du heute üben?"

        if message in [
            "nicht gut",
            "schlecht",
            "mir geht es nicht gut",
            "mir gehts nicht gut"
        ]:
            return "Das tut mir leid. Möchtest du trotzdem ein bisschen Deutsch üben?"

        return "Danke, dass du mir das sagst."


    return None


# ==========================================
# SZUKANIE ODPOWIEDZI W LEKCJI
# ==========================================

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

                question = ""

                if follow_up:
                    question = random.choice(
                        follow_up
                    )

                    remember_follow_up(
                        question
                    )

                    if answer:
                        answer += " " + question
                    else:
                        answer = question

                else:
                    conversation_state["last_question"] = None

                return answer

    return None


# ==========================================
# GŁÓWNA FUNKCJA ROZMOWY
# ==========================================

def generate_conversation_reply(
    user_message,
    level="A1",
    lesson=1
):
    """
    Główna funkcja rozmowy Nele.
    Najpierw sprawdza pamięć rozmowy,
    potem wiedzę z lekcji.
    """

    # --------------------------------------
    # 1. Najpierw sprawdź kontekst
    # --------------------------------------

    context_answer = handle_context_answer(
        user_message
    )

    if context_answer:
        return context_answer


    # --------------------------------------
    # 2. Potem sprawdź bazę lekcji
    # --------------------------------------

    answer = find_response(
        user_message,
        level,
        lesson
    )

    if answer:
        return answer


    # --------------------------------------
    # 3. Odpowiedź domyślna
    # --------------------------------------

    return (
        "Ich habe dich verstanden, "
        "aber diese Antwort habe ich noch nicht gelernt."
          )
