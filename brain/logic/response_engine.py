# ==========================================
# NELE – SILNIK ODPOWIEDZI
# ==========================================

import random

from brain.logic.memory import (
    get_conversation_state
)

from brain.logic.matcher import (
    normalize,
    pattern_matches
)

from brain.logic.lesson_loader import (
    load_lesson
)

from brain.logic.error_practice import (
    start_error_practice,
    get_error_practice_label
)

from brain.memory.error_review import (
    refresh_error_reviews,
    get_due_error_reviews
)


# ==========================================
# ODPOWIEDZI TAK / NIE
# ==========================================

YES_ANSWERS = {
    "ja",
    "ja gerne",
    "ja gern",
    "gerne",
    "gern",
    "okay",
    "ok",
    "klar",
    "natürlich",
    "machen wir",
    "ja machen wir"
}


NO_ANSWERS = {
    "nein",
    "nein danke",
    "nicht jetzt",
    "später",
    "lieber nicht",
    "jetzt nicht"
}


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
# WYCZYSZCZENIE OCZEKUJĄCEJ
# PROPOZYCJI POWTÓRKI
# ==========================================

def clear_pending_error_review(
    state
):

    if state is None:
        return

    state[
        "pending_error_review"
    ] = None

    if (
        state.get(
            "last_question"
        )
        ==
        "continue_error_review"
    ):

        state[
            "last_question"
        ] = None


# ==========================================
# ZAPISANIE PROPOZYCJI POWTÓRKI
# ==========================================

def set_pending_error_review(
    state,
    error_type
):

    if state is None:
        return False

    if not error_type:
        return False

    state[
        "pending_error_review"
    ] = error_type

    state[
        "last_question"
    ] = "continue_error_review"

    return True


# ==========================================
# CZY UŻYTKOWNIK ODPOWIADA
# NA PROPOZYCJĘ POWTÓRKI?
# ==========================================

def handle_pending_error_review_reply(
    user_message,
    state
):

    if state is None:

        return (
            False,
            None
        )


    if (
        state.get(
            "last_question"
        )
        !=
        "continue_error_review"
    ):

        return (
            False,
            None
        )


    error_type = state.get(
        "pending_error_review"
    )


    if not error_type:

        clear_pending_error_review(
            state
        )

        return (
            False,
            None
        )


    message = normalize(
        user_message
    ).strip(
        " .?!„“\"'"
    )


    # ======================================
    # TAK
    # ======================================

    if message in YES_ANSWERS:

        clear_pending_error_review(
            state
        )

        answer = start_error_practice(
            state,
            error_type
        )

        return (
            True,
            answer
        )


    # ======================================
    # NIE
    # ======================================

    if message in NO_ANSWERS:

        clear_pending_error_review(
            state
        )

        return (
            True,
            (
                "Okay. "
                "Womit möchtest du heute anfangen?"
            )
        )


    # ======================================
    # UŻYTKOWNIK ZADAŁ INNE PYTANIE
    #
    # Nie blokujemy rozmowy.
    # Powtórka nadal pozostaje w pamięci
    # jako needs_practice=True.
    # ======================================

    clear_pending_error_review(
        state
    )

    return (
        False,
        None
    )


# ==========================================
# NALEŻNA POWTÓRKA BŁĘDU
# ==========================================

def get_due_error_review(
    state
):

    if state is None:
        return None


    # ======================================
    # Adaptive Review sprawdza,
    # czy termin którejś powtórki nadszedł.
    #
    # Jeśli tak:
    #
    # needs_practice = True
    # ======================================

    refresh_error_reviews(
        state
    )


    due_errors = get_due_error_reviews(
        state
    )


    if not due_errors:
        return None


    return due_errors[0]


# ==========================================
# PROPOZYCJA NALEŻNEJ POWTÓRKI
# ==========================================

def create_due_error_review_offer(
    state,
    short_answer
):

    error_type = get_due_error_review(
        state
    )


    if not error_type:
        return None


    label = get_error_practice_label(
        error_type
    )


    set_pending_error_review(
        state,
        error_type
    )


    return (
        f"{short_answer} "
        f"Heute sollten wir kurz "
        f"{label} wiederholen. "
        f"Möchtest du das zuerst machen?"
    )


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
    #
    # W takim momencie nie wciskamy
    # użytkownikowi powtórki błędów.
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
    # NALEŻNA POWTÓRKA BŁĘDU
    #
    # Ma pierwszeństwo przed zwykłym
    # pytaniem "od czego zaczynamy?".
    # ======================================

    review_offer = (
        create_due_error_review_offer(
            state,
            short_answer
        )
    )


    if review_offer:

        return review_offer


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


    # ======================================
    # ODPOWIEDŹ NA PROPOZYCJĘ POWTÓRKI
    #
    # Sprawdzamy to przed zwykłymi
    # odpowiedziami lekcji.
    # ======================================

    (
        error_review_handled,
        error_review_answer
    ) = handle_pending_error_review_reply(
        user_message,
        state
    )


    if error_review_handled:

        return error_review_answer


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
                        "item":
                            item,

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
        and
        intent in wellbeing_intents
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
