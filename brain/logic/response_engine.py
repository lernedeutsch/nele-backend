# ==========================================
# NELE – SILNIK ODPOWIEDZI
# ==========================================

import random

from brain.logic.memory import get_conversation_state

from brain.logic.matcher import (
    normalize,
    pattern_matches
)

from brain.logic.lesson_loader import (
    load_lesson
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
# NAZWA SŁOWA DO WYŚWIETLENIA
# ==========================================

def display_activity_word(
    word
):

    if not word:
        return ""

    word = str(
        word
    ).strip()

    if not word:
        return ""

    return (
        word[:1].upper()
        + word[1:]
    )


# ==========================================
# KRÓTKA CZĘŚĆ ODPOWIEDZI
# ==========================================
#
# Przykład:
#
# "Sehr schön! Möchtest du heute ..."
#
# zostanie skrócone do:
#
# "Sehr schön!"
#
# Dzięki temu Nele nie zada dwóch
# różnych pytań w jednej odpowiedzi.
# ==========================================

def get_short_answer(
    answer
):

    if not answer:
        return ""

    answer = str(
        answer
    ).strip()

    if not answer:
        return ""

    endings = [
        "!",
        ".",
        "?"
    ]

    positions = []

    for ending in endings:

        position = answer.find(
            ending
        )

        if position >= 0:

            positions.append(
                position
            )


    if not positions:

        return answer


    first_position = min(
        positions
    )


    return answer[
        :first_position + 1
    ].strip()


# ==========================================
# ODPOWIEDŹ PO POWITANIU
# ==========================================

def create_returning_user_follow_up(
    state,
    normal_answer,
    intent=""
):

    short_answer = get_short_answer(
        normal_answer
    )


    # ======================================
    # GORSZE SAMOPOCZUCIE
    # ======================================

    if intent == "user_wellbeing_bad":

        state[
            "last_question"
        ] = None

        return (
            f"{short_answer} "
            f"Möchtest du heute lieber "
            f"etwas Leichtes auf Deutsch üben?"
        )


    # ======================================
    # OSTATNIA AKTYWNOŚĆ
    # ======================================

    last_activity = state.get(
        "last_activity"
    )

    last_activity_detail = state.get(
        "last_activity_detail"
    )


    # ======================================
    # OSTATNIO ĆWICZONE SŁOWO
    # ======================================

    if (
        last_activity == "vocabulary"
        and last_activity_detail
    ):

        word = display_activity_word(
            last_activity_detail
        )

        state[
            "last_question"
        ] = "continue_last_activity"

        return (
            f"{short_answer} "
            f"Möchtest du mit dem Wort "
            f"„{word}“ weitermachen?"
        )


    # ======================================
    # BRAK ZAPISANEJ AKTYWNOŚCI
    # ======================================

    state[
        "last_question"
    ] = None

    return (
        f"{short_answer} "
        f"Womit möchtest du heute anfangen?"
    )


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
    # POPRZEDNIE PYTANIE NELE
    # ======================================

    previous_question = state.get(
        "last_question"
    )


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

    best_match = matches[
        0
    ]

    item = best_match[
        "item"
    ]

    intent = item.get(
        "intent",
        ""
    )


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


    # ======================================
    # ODPOWIEDŹ NA:
    # "WIE GEHT ES DIR?"
    # ======================================

    wellbeing_intents = {
        "user_wellbeing_good",
        "user_wellbeing_bad"
    }


    if (
        previous_question == "wellbeing"
        and intent in wellbeing_intents
    ):

        return create_returning_user_follow_up(
            state,
            answer,
            intent
        )


    # ======================================
    # STANDARDOWY FOLLOW-UP
    # ======================================

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
                " "
                + question
            )

        else:

            answer = question

    else:

        state[
            "last_question"
        ] = None


    return answer
