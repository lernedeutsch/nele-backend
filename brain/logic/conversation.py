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

from brain.logic.user_info import (
    extract_user_information
)

from brain.logic.memory_answers import (
    answer_from_memory
)

from brain.logic.context import (
    handle_context_answer
)

from brain.logic.alphabet import (
    handle_alphabet_question
)


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


    # ======================================
    # SZUKAMY WSZYSTKICH DOPASOWAŃ
    # ======================================

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


    # ======================================
    # NAJDŁUŻSZY WZORZEC WYGRYWA
    # ======================================

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


        # ==================================
        # POPRAWIONE IMIĘ
        # ==================================

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


        # ==================================
        # POPRAWIONE ZDANIE DO PAMIĘCI
        # ==================================

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
            load_lesson_module,
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
