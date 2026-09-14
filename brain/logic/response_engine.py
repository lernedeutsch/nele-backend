# ==========================================
# NELE – SILNIK ODPOWIEDZI
# TEACHER MODE
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

from brain.logic.new_learning_resume import (
    set_new_learning_offer,
    handle_new_learning_resume
)

from brain.logic.wellbeing_feedback import (
    analyze_wellbeing_response
)

from brain.logic.vocabulary_modules.practice import (
    start_vocabulary_practice
)

from brain.memory.error_review import (
    refresh_error_reviews,
    get_due_error_reviews
)

from brain.memory.next_learning_step import (
    get_next_new_learning_step,
    get_teacher_learning_plan
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
# NAZWA AKTYWNOŚCI DO WYŚWIETLENIA
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
# POŁĄCZENIE POPRAWKI
# Z NORMALNĄ ODPOWIEDZIĄ NELE
# ==========================================

def combine_wellbeing_feedback(
    feedback,
    answer
):

    feedback = str(
        feedback or ""
    ).strip()

    answer = str(
        answer or ""
    ).strip()


    if (
        feedback
        and
        answer
    ):

        return (
            f"{feedback}\n\n"
            f"{answer}"
        )


    if feedback:

        return feedback


    return answer


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
#
# STARY TRYB
# ZOSTAJE DLA KOMPATYBILNOŚCI
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
                "Dann machen wir mit der "
                "Lektion weiter."
            )
        )


    # ======================================
    # INNE PYTANIE
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

    try:

        refresh_error_reviews(
            state
        )

    except Exception as error:

        print(
            f"Error review refresh error: {error}"
        )

        return None

    due_errors = get_due_error_reviews(
        state
    )

    if not due_errors:
        return None

    return due_errors[0]


# ==========================================
# PROPOZYCJA NALEŻNEJ POWTÓRKI
#
# STARY TRYB
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
# PLAN DALSZEJ LEKCJI
#
# STARY TRYB
# ==========================================

def create_lesson_continuation_offer(
    state,
    short_answer
):

    if state is None:
        return None

    try:

        plan = get_next_new_learning_step(
            state
        )

    except Exception as error:

        print(
            f"Next learning step error: {error}"
        )

        return None

    if not isinstance(
        plan,
        dict
    ):

        return None

    plan_type = str(
        plan.get(
            "type",
            ""
        )
        or
        ""
    ).strip().lower()

    section = plan.get(
        "section"
    )

    level = plan.get(
        "level"
    )

    lesson = plan.get(
        "lesson"
    )

    message = str(
        plan.get(
            "message",
            ""
        )
        or
        ""
    ).strip()


    # ======================================
    # OSTATNIA AKTYWNOŚĆ
    # ======================================

    last_activity = state.get(
        "last_activity"
    )

    last_detail = state.get(
        "last_activity_detail"
    )

    if last_detail:

        last_detail = str(
            last_detail
        ).strip()


    # ======================================
    # NASTĘPNA CZĘŚĆ LEKCJI
    # ======================================

    if section:

        section = str(
            section
        ).strip()

        offer_saved = (
            set_new_learning_offer(
                state,
                plan
            )
        )

        if offer_saved:

            if (
                last_activity == "lesson"
                and
                last_detail
                and
                normalize(
                    last_detail
                )
                ==
                normalize(
                    section
                )
            ):

                return (
                    f"{short_answer} "
                    f"Zuletzt waren wir bei "
                    f"„{section}“. "
                    f"Möchtest du dort "
                    f"weitermachen?"
                )


            if (
                last_activity == "lesson"
                and
                last_detail
            ):

                return (
                    f"{short_answer} "
                    f"Zuletzt haben wir "
                    f"„{last_detail}“ gemacht. "
                    f"Als Nächstes kommt "
                    f"„{section}“. "
                    f"Möchtest du weitermachen?"
                )


            return (
                f"{short_answer} "
                f"Als Nächstes kommt "
                f"„{section}“. "
                f"Möchtest du weitermachen?"
            )


    # ======================================
    # NOWA LEKCJA
    # ======================================

    if (
        plan_type == "new_lesson"
        and
        level
        and
        lesson
    ):

        offer_saved = (
            set_new_learning_offer(
                state,
                plan
            )
        )

        if offer_saved:

            if (
                last_activity == "lesson"
                and
                last_detail
            ):

                return (
                    f"{short_answer} "
                    f"Zuletzt haben wir "
                    f"„{last_detail}“ gemacht. "
                    f"Jetzt geht es mit "
                    f"{level}, Lektion {lesson} "
                    f"weiter. "
                    f"Möchtest du anfangen?"
                )

            return (
                f"{short_answer} "
                f"Als Nächstes kommt "
                f"{level}, Lektion {lesson}. "
                f"Möchtest du anfangen?"
            )


    # ======================================
    # PLAN MA TYLKO GOTOWY TEKST
    # ======================================

    if message:

        return (
            f"{short_answer} "
            f"{message}"
        )

    return None


# ==========================================
# TEACHER MODE
# BEZ PYTANIA UŻYTKOWNIKA O WYBÓR
# ==========================================
#
# Kolejność ustala Student Memory:
#
# 1. należny błąd
# 2. słownictwo do powtórki
# 3. kolejny materiał / lekcja
#
# Funkcja nie pyta:
#
# Möchtest du ...?
#
# tylko od razu rozpoczyna trening.
# ==========================================

def create_teacher_directed_follow_up(
    state,
    short_answer=""
):

    if state is None:
        return short_answer


    # ======================================
    # PLAN NAUCZYCIELA
    # ======================================

    try:

        plan = get_teacher_learning_plan(
            state
        )

    except Exception as error:

        print(
            f"Teacher learning plan error: {error}"
        )

        return short_answer


    if not isinstance(
        plan,
        dict
    ):

        return short_answer


    priority = str(
        plan.get(
            "priority",
            ""
        )
        or
        ""
    ).strip().lower()


    plan_type = str(
        plan.get(
            "type",
            ""
        )
        or
        ""
    ).strip().lower()


    message = str(
        plan.get(
            "message",
            ""
        )
        or
        ""
    ).strip()


    # ======================================
    # 1. POWTÓRKA BŁĘDU
    # ======================================

    if priority == "error_review":

        errors = plan.get(
            "errors",
            []
        )

        error_type = None


        if (
            isinstance(
                errors,
                list
            )
            and
            errors
        ):

            first_error = errors[0]


            if isinstance(
                first_error,
                dict
            ):

                error_type = first_error.get(
                    "error_type"
                )

            elif isinstance(
                first_error,
                str
            ):

                error_type = first_error


        if error_type:

            exercise = start_error_practice(
                state,
                error_type
            )


            parts = []


            if short_answer:

                parts.append(
                    short_answer
                )


            if message:

                parts.append(
                    message
                )


            if exercise:

                parts.append(
                    exercise
                )


            if parts:

                return "\n\n".join(
                    parts
                )


    # ======================================
    # 2. POWTÓRKA SŁOWNICTWA
    # ======================================

    if priority == "vocabulary_review":

        words = plan.get(
            "words",
            []
        )

        word = None


        if (
            isinstance(
                words,
                list
            )
            and
            words
        ):

            word = str(
                words[0]
            ).strip()


        if word:

            exercise = (
                start_vocabulary_practice(
                    (
                        "übe mit mir das wort "
                        + word
                    ),
                    state
                )
            )


            parts = []


            if short_answer:

                parts.append(
                    short_answer
                )


            if message:

                parts.append(
                    message
                )


            if exercise:

                parts.append(
                    exercise
                )


            if parts:

                return "\n\n".join(
                    parts
                )


    # ======================================
    # 3. NOWY MATERIAŁ / LEKCJA
    # ======================================
    #
    # Plan po braku powtórek jest już
    # planem następnej lekcji.
    #
    # Korzystamy z istniejącego
    # new_learning_resume, żeby nie
    # duplikować logiki lekcji.
    # ======================================

    new_learning_plan = plan


    # ======================================
    # teacher_plan może mieć następny
    # materiał w polu "next"
    # ======================================

    if plan_type == "teacher_plan":

        next_plan = plan.get(
            "next"
        )


        if isinstance(
            next_plan,
            dict
        ):

            new_learning_plan = next_plan


    if isinstance(
        new_learning_plan,
        dict
    ):

        offer_saved = (
            set_new_learning_offer(
                state,
                new_learning_plan
            )
        )


        if offer_saved:

            started_answer = (
                handle_new_learning_resume(
                    "ja",
                    state
                )
            )


            if started_answer:

                if short_answer:

                    return (
                        f"{short_answer}\n\n"
                        f"{started_answer}"
                    )

                return started_answer


    # ======================================
    # FALLBACK – GOTOWY TEKST PLANU
    # ======================================

    if message:

        if short_answer:

            return (
                f"{short_answer}\n\n"
                f"{message}"
            )

        return message


    return short_answer


# ==========================================
# ODPOWIEDŹ PO POWITANIU
# TEACHER MODE
# ==========================================

def create_returning_user_follow_up(
    state,
    normal_answer,
    wellbeing_type=""
):

    short_answer = get_short_answer(
        normal_answer
    )


    # ======================================
    # NOWY TRYB:
    #
    # Nele NIE pyta użytkownika,
    # co chce robić.
    #
    # Student Memory wybiera następny krok.
    # ======================================

    teacher_answer = (
        create_teacher_directed_follow_up(
            state,
            short_answer
        )
    )


    if teacher_answer:

        return teacher_answer


    # ======================================
    # BRAK PLANU
    # ======================================

    state[
        "last_question"
    ] = None


    if short_answer:

        return (
            f"{short_answer} "
            f"Wir machen jetzt weiter."
        )


    return (
        "Wir machen jetzt weiter."
    )


# ==========================================
# OBSŁUGA ODPOWIEDZI:
# "WIE GEHT ES DIR?"
# ==========================================

def handle_wellbeing_reply(
    user_message,
    state
):

    if state is None:
        return None

    if (
        state.get(
            "last_question"
        )
        !=
        "wellbeing"
    ):

        return None

    analysis = analyze_wellbeing_response(
        user_message
    )

    if not analysis.get(
        "recognized",
        False
    ):

        return None

    wellbeing_type = analysis.get(
        "type"
    )

    reaction = analysis.get(
        "reaction"
    )

    feedback = analysis.get(
        "feedback"
    )

    answer = create_returning_user_follow_up(
        state,
        reaction,
        wellbeing_type
    )

    return combine_wellbeing_feedback(
        feedback,
        answer
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
    # ODPOWIEDŹ NA STARĄ PROPOZYCJĘ
    # POWTÓRKI
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


    # ======================================
    # POPRZEDNIE PYTANIE NELE
    # ======================================

    previous_question = state.get(
        "last_question"
    )


    # ======================================
    # SPECJALNA OBSŁUGA:
    # WIE GEHT ES DIR?
    # ======================================

    if previous_question == "wellbeing":

        wellbeing_answer = (
            handle_wellbeing_reply(
                user_message,
                state
            )
        )


        if wellbeing_answer:

            return wellbeing_answer


    # ======================================
    # NORMALNE ODPOWIEDZI Z LEKCJI
    # ======================================

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
            match[
                "length"
            ],
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
    # STARY SYSTEM ODPOWIEDZI
    # NA SAMOPOCZUCIE
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

        return (
            create_returning_user_follow_up(
                state,
                answer,
                intent
            )
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
