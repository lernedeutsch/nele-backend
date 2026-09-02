# ==========================================
# NELE – LOGIKA ROZMOWY Z PAMIĘCIĄ
# ==========================================

import importlib.util
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# PAMIĘĆ ROZMOWY
# ==========================================

conversation_state = {
    "last_question": None,
    "name": None,
    "origin": None,
    "residence": None
}


# ==========================================
# ŁADOWANIE LEKCJI
# ==========================================

def load_lesson_module(level="A1", lesson=1):
    lesson_path = (
        BASE_DIR
        / "responses"
        / level
        / f"{lesson}.py"
    )

    if not lesson_path.exists():
        return None

    module_name = f"nele_{level}_{lesson}"

    spec = importlib.util.spec_from_file_location(
        module_name,
        lesson_path
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def load_lesson(level="A1", lesson=1):
    module = load_lesson_module(level, lesson)

    if module is None:
        return []

    return getattr(
        module,
        "LESSON_RESPONSES",
        []
    )


# ==========================================
# NORMALIZACJA
# ==========================================

def normalize(text):
    return (
        text
        .lower()
        .strip()
        .replace("?", "")
        .replace("!", "")
        .replace(".", "")
        .replace(",", "")
        .replace(":", "")
        .replace(";", "")
    )


def clean_short_answer(text):
    return (
        text
        .strip()
        .strip(".!?")
        .strip()
    )


# ==========================================
# ZAPAMIĘTYWANIE PYTANIA NELE
# ==========================================

def remember_follow_up(question):
    question_normalized = normalize(question)

    if "wie heißt du" in question_normalized:
        conversation_state["last_question"] = "name"

    elif "wie heißen sie" in question_normalized:
        conversation_state["last_question"] = "name"

    elif "woher kommst du" in question_normalized:
        conversation_state["last_question"] = "origin"

    elif "wo wohnst du" in question_normalized:
        conversation_state["last_question"] = "residence"

    elif "wo wohnen sie" in question_normalized:
        conversation_state["last_question"] = "residence"

    elif "wie geht es dir" in question_normalized:
        conversation_state["last_question"] = "wellbeing"

    else:
        conversation_state["last_question"] = None


# ==========================================
# WYCIĄGANIE INFORMACJI Z PEŁNYCH ZDAŃ
# ==========================================

def extract_user_information(user_message):
    original = clean_short_answer(user_message)
    message = normalize(user_message)

    # --------------------------------------
    # IMIĘ
    # --------------------------------------

    name_prefixes = [
        "ich heiße ",
        "ich heisse ",
        "mein name ist ",
        "ich bin "
    ]

    for prefix in name_prefixes:
        if message.startswith(prefix):

            value = original[len(prefix):].strip()

            if value:
                conversation_state["name"] = value
                conversation_state["last_question"] = "origin"

                return (
                    f"Freut mich, {value}. "
                    f"Woher kommst du?"
                )

    # --------------------------------------
    # POCHODZENIE
    # --------------------------------------

    origin_prefixes = [
        "ich komme aus ",
        "ich bin aus "
    ]

    for prefix in origin_prefixes:
        if message.startswith(prefix):

            value = original[len(prefix):].strip()

            if value:
                conversation_state["origin"] = value
                conversation_state["last_question"] = "residence"

                return (
                    f"Schön. Du kommst aus {value}. "
                    f"Wo wohnst du jetzt?"
                )

    # --------------------------------------
    # MIEJSCE ZAMIESZKANIA
    # --------------------------------------

    residence_prefixes = [
        "ich wohne in ",
        "ich lebe in "
    ]

    for prefix in residence_prefixes:
        if message.startswith(prefix):

            value = original[len(prefix):].strip()

            if value:
                conversation_state["residence"] = value
                conversation_state["last_question"] = None

                name = conversation_state.get("name")

                if name:
                    return (
                        f"Ah, {name}, "
                        f"du wohnst in {value}. Schön!"
                    )

                return (
                    f"Ah, du wohnst in {value}. Schön!"
                )

    return None


# ==========================================
# ALFABET
# ==========================================

def handle_alphabet_question(
    user_message,
    level="A1",
    lesson=1
):
    message = normalize(user_message)

    module = load_lesson_module(level, lesson)

    if module is None:
        return None

    alphabet = getattr(
        module,
        "ALPHABET",
        {}
    )

    if not alphabet:
        return None

    if (
        "wie spricht man" in message
        and "aus" in message
    ):

        words = message.split()

        for word in words:

            clean_word = (
                word
                .strip()
                .strip("?!.:,")
                .lower()
            )

            if clean_word in alphabet:

                pronunciation = alphabet[clean_word]

                display_letter = clean_word.upper()

                if clean_word == "ß":
                    display_letter = "ß"

                return (
                    f"{display_letter} "
                    f"spricht man „{pronunciation}“ aus."
                )

    if (
        "wie heißt" in message
        or "wie heisst" in message
    ):

        words = message.split()

        for word in words:

            clean_word = (
                word
                .strip()
                .strip("?!.:,")
                .lower()
            )

            if clean_word in alphabet:

                pronunciation = alphabet[clean_word]

                display_letter = clean_word.upper()

                if clean_word == "ß":
                    display_letter = "ß"

                return (
                    f"{display_letter} heißt "
                    f"„{pronunciation}“."
                )

    if message in [
        "was ist ß",
        "wie heißt ß",
        "wie heisst ß"
    ]:
        return "Das Zeichen ß heißt Eszett."

    return None


# ==========================================
# ZNANE ZWROTY Z LEKCJI
# ==========================================

def find_response(
    user_message,
    level="A1",
    lesson=1
):
    message = normalize(user_message)
    responses = load_lesson(level, lesson)

    for item in responses:

        patterns = item.get("patterns", [])

        for pattern in patterns:

            pattern_normalized = normalize(pattern)

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
                    answer = random.choice(answers)
                else:
                    answer = ""

                if follow_up:

                    question = random.choice(follow_up)

                    remember_follow_up(question)

                    if answer:
                        answer += " " + question
                    else:
                        answer = question

                else:
                    conversation_state["last_question"] = None

                return answer

    return None


# ==========================================
# ODPOWIEDŹ KONTEKSTOWA
# ==========================================

def handle_context_answer(user_message):
    last_question = conversation_state.get(
        "last_question"
    )

    if not last_question:
        return None

    answer = clean_short_answer(user_message)

    if not answer:
        return None

    normalized_answer = normalize(answer)

    if (
        normalized_answer.startswith("wie ")
        or normalized_answer.startswith("was ")
        or normalized_answer.startswith("wo ")
        or normalized_answer.startswith("wer ")
        or normalized_answer.startswith("wann ")
        or normalized_answer.startswith("warum ")
    ):
        return None

    # ======================================
    # IMIĘ
    # ======================================

    if last_question == "name":

        if len(answer.split()) > 4:
            return None

        conversation_state["name"] = answer
        conversation_state["last_question"] = "origin"

        return (
            f"Freut mich, {answer}. "
            f"Woher kommst du?"
        )

    # ======================================
    # POCHODZENIE
    # ======================================

    if last_question == "origin":

        origin = answer

        if normalized_answer.startswith("aus "):
            origin = answer[4:].strip()

        conversation_state["origin"] = origin
        conversation_state["last_question"] = "residence"

        return (
            f"Schön. Du kommst aus {origin}. "
            f"Wo wohnst du jetzt?"
        )

    # ======================================
    # MIEJSCE ZAMIESZKANIA
    # ======================================

    if last_question == "residence":

        residence = answer

        if normalized_answer.startswith("in "):
            residence = answer[3:].strip()

        conversation_state["residence"] = residence
        conversation_state["last_question"] = None

        name = conversation_state.get("name")

        if name:
            return (
                f"Ah, {name}, "
                f"du wohnst in {residence}. Schön!"
            )

        return (
            f"Ah, du wohnst in {residence}. Schön!"
        )

    # ======================================
    # SAMOPOCZUCIE
    # ======================================

    if last_question == "wellbeing":

        conversation_state["last_question"] = None

        if normalized_answer in [
            "gut",
            "sehr gut",
            "mir geht es gut",
            "mir gehts gut"
        ]:
            return (
                "Das freut mich! "
                "Was möchtest du heute üben?"
            )

        if normalized_answer in [
            "nicht gut",
            "schlecht",
            "mir geht es nicht gut",
            "mir gehts nicht gut"
        ]:
            return (
                "Das tut mir leid. "
                "Möchtest du trotzdem "
                "ein bisschen Deutsch üben?"
            )

        return "Danke, dass du mir das sagst."

    return None


# ==========================================
# GŁÓWNA LOGIKA
# ==========================================

def generate_conversation_reply(
    user_message,
    level="A1",
    lesson=1
):

    # 1. Alfabet
    alphabet_answer = handle_alphabet_question(
        user_message,
        level,
        lesson
    )

    if alphabet_answer:
        return alphabet_answer

    # 2. Pełne zdania z informacją o użytkowniku
    extracted_answer = extract_user_information(
        user_message
    )

    if extracted_answer:
        return extracted_answer

    # 3. Znane pytania i zwroty z lekcji
    known_answer = find_response(
        user_message,
        level,
        lesson
    )

    if known_answer:
        return known_answer

    # 4. Odpowiedź na wcześniejsze pytanie Nele
    context_answer = handle_context_answer(
        user_message
    )

    if context_answer:
        return context_answer

    # 5. Brak wiedzy
    return (
        "Ich habe dich verstanden, "
        "aber diese Antwort habe ich noch nicht gelernt."
              )
