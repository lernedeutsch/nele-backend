# ==========================================
# NELE – LOGIKA ROZMOWY Z PAMIĘCIĄ SESJI
# ==========================================

import importlib.util
import random
from pathlib import Path

from brain.responses.corrections import find_correction
from brain.logic.memory import get_conversation_state
from brain.logic.matcher import (
    normalize,
    clean_short_answer,
    capitalize_value,
    pattern_matches
)
from brain.logic.user_info import extract_user_information
from brain.logic.memory_answers import answer_from_memory
from brain.logic.context import handle_context_answer

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# ŁADOWANIE LEKCJI
# ==========================================

def load_lesson_module(
    level="A1",
    lesson=1
):

    lesson_path = (
        BASE_DIR
        / "responses"
        / level
        / f"{lesson}.py"
    )

    if not lesson_path.exists():
        return None

    module_name = (
        f"nele_{level}_{lesson}"
    )

    spec = importlib.util.spec_from_file_location(
        module_name,
        lesson_path
    )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    return module


def load_lesson(
    level="A1",
    lesson=1
):

    module = load_lesson_module(
        level,
        lesson
    )

    if module is None:
        return []

    return getattr(
        module,
        "LESSON_RESPONSES",
        []
    )


# ==========================================
# ZAPAMIĘTYWANIE PYTANIA NELE
# ==========================================

def remember_follow_up(
    question,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    question_normalized = normalize(
        question
    )

    if (
        "wie heißt du"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "name"

    elif (
        "wie heißen sie"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "name"

    elif (
        "woher kommst du"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "origin"

    elif (
        "wo wohnst du"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "residence"

    elif (
        "wo wohnen sie"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "residence"

    elif (
        "wie geht es dir"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "wellbeing"

    else:

        state[
            "last_question"
        ] = None


# ==========================================
# ALFABET
# ==========================================

def handle_alphabet_question(
    user_message,
    level="A1",
    lesson=1
):

    message = normalize(
        user_message
    )

    module = load_lesson_module(
        level,
        lesson
    )

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

                pronunciation = alphabet[
                    clean_word
                ]

                display_letter = (
                    clean_word.upper()
                )

                if clean_word == "ß":
                    display_letter = "ß"

                return (
                    f"{display_letter} "
                    f"spricht man "
                    f"„{pronunciation}“ aus."
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

                pronunciation = alphabet[
                    clean_word
                ]

                display_letter = (
                    clean_word.upper()
                )

                if clean_word == "ß":
                    display_letter = "ß"

                return (
                    f"{display_letter} "
                    f"heißt "
                    f"„{pronunciation}“."
                )


    if message in [
        "was ist ß",
        "wie heißt ß",
        "wie heisst ß"
    ]:

        return (
            "Das Zeichen ß heißt Eszett."
        )


    return None


# ==========================================
# ZNANE ZWROTY Z LEKCJI
# ==========================================

def find_response(
    user_message,
    level="A1",
    lesson=1,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    responses = load_lesson(
        level,
        lesson
    )

    matches = []


    for item in responses:

        patterns = item.get(
            "patterns",
            []
        )

        for pattern in patterns:

            if pattern_matches(
                user_message,
                pattern
            ):

                pattern_normalized = normalize(
                    pattern
                )

                matches.append(
                    {
                        "item": item,
                        "pattern":
                            pattern_normalized,
                        "length":
                            len(
                                pattern_normalized
                            )
                    }
                )


    if not matches:
        return None


    matches.sort(
        key=lambda match:
            match["length"],
        reverse=True
    )

    best_match = matches[0]

    item = best_match[
        "item"
    ]


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

        remember_follow_up(
            question,
            session_id
        )

        if answer:

            answer += (
                " " + question
            )

        else:

            answer = question

    else:

        state[
            "last_question"
        ] = None


    return answer


    # ======================================
    # IMIĘ
    # ======================================

    if last_question == "name":

        if len(answer.split()) > 4:
            return None

        answer = capitalize_value(
            answer
        )

        state[
            "name"
        ] = answer

        state[
            "last_question"
        ] = "origin"

        return (
            f"Freut mich, {answer}. "
            f"Woher kommst du?"
        )


    # ======================================
    # POCHODZENIE
    # ======================================

    if last_question == "origin":

        origin = answer

        if normalized_answer.startswith(
            "aus "
        ):

            origin = answer[
                4:
            ].strip()

        origin = capitalize_value(
            origin
        )

        state[
            "origin"
        ] = origin

        state[
            "last_question"
        ] = "residence"

        return (
            f"Schön. "
            f"Du kommst aus {origin}. "
            f"Wo wohnst du jetzt?"
        )


    # ======================================
    # MIEJSCE ZAMIESZKANIA
    # ======================================

    if last_question == "residence":

        residence = answer

        if normalized_answer.startswith(
            "in "
        ):

            residence = answer[
                3:
            ].strip()

        residence = capitalize_value(
            residence
        )

        state[
            "residence"
        ] = residence

        state[
            "last_question"
        ] = None

        name = state.get(
            "name"
        )

        if name:

            return (
                f"Ah, {name}, "
                f"du wohnst in {residence}. "
                f"Schön!"
            )

        return (
            f"Ah, du wohnst in "
            f"{residence}. Schön!"
        )


    # ======================================
    # SAMOPOCZUCIE
    # ======================================

    if last_question == "wellbeing":

        state[
            "last_question"
        ] = None

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

        return (
            "Danke, dass du mir das sagst."
        )


    return None


# ==========================================
# GŁÓWNA LOGIKA ROZMOWY
# ==========================================

def generate_conversation_reply(
    user_message,
    level="A1",
    lesson=1,
    session_id="default"
):

    get_conversation_state(
        session_id
    )


    # ======================================
    # 1. KOREKTA BŁĘDÓW
    # ======================================

    correction = find_correction(
        user_message
    )

    if correction:

        corrected = correction[
            "correct"
        ]

        explanation = correction[
            "explanation"
        ]

        corrected_clean = (
            clean_short_answer(
                corrected
            )
        )

        corrected_normalized = (
            normalize(
                corrected_clean
            )
        )


        if corrected_normalized.startswith(
            "ich heiße "
        ):

            value = corrected_clean[
                len("Ich heiße "):
            ].strip()

            value = capitalize_value(
                value
            )

            corrected = (
                f"Ich heiße {value}."
            )


        elif corrected_normalized.startswith(
            "mein name ist "
        ):

            value = corrected_clean[
                len("Mein Name ist "):
            ].strip()

            value = capitalize_value(
                value
            )

            corrected = (
                f"Mein Name ist {value}."
            )


        continuation = (
            extract_user_information(
                corrected,
                session_id
            )
        )

        if continuation:

            return (
                f"{explanation} "
                f"Richtig ist: "
                f"{corrected} "
                f"{continuation}"
            )


        return (
            f"{explanation} "
            f"Richtig ist: "
            f"{corrected}"
        )


    # ======================================
    # 2. ALFABET
    # ======================================

    alphabet_answer = (
        handle_alphabet_question(
            user_message,
            level,
            lesson
        )
    )

    if alphabet_answer:
        return alphabet_answer


    # ======================================
    # 3. PYTANIA O PAMIĘĆ
    # ======================================

    memory_answer = (
        answer_from_memory(
            user_message,
            session_id
        )
    )

    if memory_answer:
        return memory_answer


    # ======================================
    # 4. INFORMACJE O UŻYTKOWNIKU
    # ======================================

    extracted_answer = (
        extract_user_information(
            user_message,
            session_id
        )
    )

    if extracted_answer:
        return extracted_answer


    # ======================================
    # 5. ZNANE PYTANIA I ZWROTY
    # ======================================

    known_answer = find_response(
        user_message,
        level,
        lesson,
        session_id
    )

    if known_answer:
        return known_answer


    # ======================================
    # 6. ODPOWIEDŹ KONTEKSTOWA
    # ======================================

    context_answer = (
        handle_context_answer(
            user_message,
            session_id
        )
    )

    if context_answer:
        return context_answer


    # ======================================
    # 7. BRAK WIEDZY
    # ======================================

    return (
        "Ich habe dich verstanden, "
        "aber diese Antwort habe ich "
        "noch nicht gelernt."
              )
