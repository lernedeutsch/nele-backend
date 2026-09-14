# ==========================================
# NELE – KOMENDY ROZMOWY
# TEACHER MODE
# ==========================================

import re

from brain.logic.activity_resume import (
    resume_current_training
)

from brain.logic.response_engine import (
    create_teacher_directed_follow_up
)

from brain.memory.error_memory import (
    remember_error
)


# ==========================================
# CZYSZCZENIE KOMENDY
# ==========================================

def clean_control_message(
    text
):

    text = str(
        text or ""
    ).strip().lower()

    text = text.strip(
        " .?!„“\"'"
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ==========================================
# ZAPAMIĘTANIE BŁĘDU JĘZYKOWEGO
# ==========================================

def remember_command_language_error(
    state,
    wrong_text,
    correct_text,
    error_type="grammar"
):

    if state is None:
        return

    wrong_text = str(
        wrong_text or ""
    ).strip()

    correct_text = str(
        correct_text or ""
    ).strip()

    if not wrong_text:
        return

    if not correct_text:
        return

    try:

        remember_error(
            state,
            error_type,
            wrong_text,
            correct_text
        )

    except Exception as error:

        print(
            f"Conversation command error memory: {error}"
        )


# ==========================================
# USUNIĘCIE STAREGO PYTANIA
# O KONTYNUACJĘ
# ==========================================

def clear_old_teacher_choice_state(
    state
):

    if state is None:
        return

    last_question = state.get(
        "last_question"
    )

    if last_question in {
        "continue_last_activity",
        "continue_error_review"
    }:

        state[
            "last_question"
        ] = None


# ==========================================
# ROZPOZNANIE:
# POWTÓRZ
# ==========================================

def analyze_repeat_request(
    user_message
):

    message = clean_control_message(
        user_message
    )


    # ======================================
    # POPRAWNE FORMЫ
    # ======================================

    correct_requests = {

        "kannst du bitte wiederholen",

        "kannst du das bitte wiederholen",

        "kannst du es bitte wiederholen",

        "kannst du bitte noch einmal wiederholen",

        "kannst du die frage bitte wiederholen",

        "kannst du die frage wiederholen",

        "bitte wiederholen",

        "bitte noch einmal",

        "noch einmal bitte",

        "noch mal bitte",

        "nochmal bitte",

        "wiederhole bitte",

        "kannst du das noch einmal sagen",

        "kannst du das noch mal sagen"
    }


    if message in correct_requests:

        return {

            "recognized":
                True,

            "question_only":
                (
                    "frage"
                    in message
                ),

            "feedback":
                None,

            "corrected":
                None,

            "error_type":
                None
        }


    # ======================================
    # TYPOWE BŁĘDY
    # ======================================

    wrong_repeat_patterns = {

        "kannst du bitte wiederhole":
            "Kannst du bitte wiederholen?",

        "kannst du das bitte wiederhole":
            "Kannst du das bitte wiederholen?",

        "kannst du die frage bitte wiederhole":
            "Kannst du die Frage bitte wiederholen?",

        "kanst du bitte wiederholen":
            "Kannst du bitte wiederholen?",

        "kanst du das bitte wiederholen":
            "Kannst du das bitte wiederholen?",

        "kanst du die frage bitte wiederholen":
            "Kannst du die Frage bitte wiederholen?",

        "kannst du bitte wiederholen die frage":
            "Kannst du die Frage bitte wiederholen?",

        "kannst du bitte die frage wiederhole":
            "Kannst du die Frage bitte wiederholen?"
    }


    if message in wrong_repeat_patterns:

        corrected = (
            wrong_repeat_patterns[
                message
            ]
        )


        return {

            "recognized":
                True,

            "question_only":
                (
                    "frage"
                    in message
                ),

            "feedback":
                (
                    "Fast! Richtig sagt man: "
                    f"„{corrected}“"
                ),

            "corrected":
                corrected,

            "error_type":
                "grammar"
        }


    return {
        "recognized":
            False
    }


# ==========================================
# OBSŁUGA:
# POWTÓRZ
# ==========================================

def handle_repeat_request(
    user_message,
    state
):

    analysis = analyze_repeat_request(
        user_message
    )


    if not analysis.get(
        "recognized",
        False
    ):

        return (
            False,
            None,
            None
        )


    feedback = analysis.get(
        "feedback"
    )

    corrected = analysis.get(
        "corrected"
    )

    error_type = analysis.get(
        "error_type"
    )


    # ======================================
    # JEŻELI UŻYTKOWNIK POPEŁNIŁ BŁĄD,
    # ZAPAMIĘTUJEMY GO
    # ======================================

    if (
        corrected
        and
        error_type
    ):

        remember_command_language_error(
            state,
            user_message,
            corrected,
            error_type
        )


    # ======================================
    # POWTÓRZENIE TYLKO PYTANIA
    # ======================================

    if analysis.get(
        "question_only",
        False
    ):

        repeated = state.get(
            "last_nele_question"
        )


        # ==================================
        # JEŻELI OSTATNIA WYPOWIEDŹ
        # NIE MIAŁA PYTANIA,
        # POWTARZAMY CAŁĄ WYPOWIEDŹ
        # ==================================

        if not repeated:

            repeated = state.get(
                "last_nele_message"
            )


    # ======================================
    # POWTÓRZENIE CAŁEJ WYPOWIEDZI
    # ======================================

    else:

        repeated = state.get(
            "last_nele_message"
        )


    # ======================================
    # FALLBACK:
    # AKTYWNY TRENING
    # ======================================

    if not repeated:

        repeated = resume_current_training(
            state
        )


    # ======================================
    # NIC JESZCZE NIE MA
    # ======================================

    if not repeated:

        repeated = (
            "Ich habe gerade noch nichts "
            "zum Wiederholen."
        )


    return (
        True,
        repeated,
        feedback
    )


# ==========================================
# ROZPOZNANIE:
# WRÓĆ DO TRENINGU
# ==========================================

def analyze_return_to_training_request(
    user_message
):

    message = clean_control_message(
        user_message
    )


    # ======================================
    # POPRAWNE FORMЫ
    # ======================================

    correct_requests = {

        "zurück zum training",
        "zuruck zum training",

        "zurück zur übung",
        "zuruck zur ubung",

        "zurück zur lektion",
        "zuruck zur lektion",

        "gehen wir zurück zum training",
        "gehen wir zuruck zum training",

        "lass uns zum training zurückgehen",
        "lass uns zum training zuruckgehen",

        "lass uns zurück zum training gehen",
        "lass uns zuruck zum training gehen",

        "machen wir mit dem training weiter",
        "wir machen mit dem training weiter",

        "weiter mit dem training",

        "machen wir weiter",

        "wir machen weiter",

        "weiter bitte",

        "bitte weiter",

        "weiter"
    }


    if message in correct_requests:

        return {

            "recognized":
                True,

            "feedback":
                None,

            "corrected":
                None,

            "error_type":
                None
        }


    # ======================================
    # TYPOWE BŁĘDY
    # ======================================

    wrong_requests = {

        "zurück zu training":
            "Zurück zum Training.",

        "zuruck zu training":
            "Zurück zum Training.",

        "gehen wir zurück zu training":
            "Gehen wir zurück zum Training.",

        "gehen wir zuruck zu training":
            "Gehen wir zurück zum Training.",

        "lass uns zurück zu training gehen":
            "Lass uns zum Training zurückgehen.",

        "lass uns zuruck zu training gehen":
            "Lass uns zum Training zurückgehen.",

        "machen wir weiter mit training":
            "Machen wir mit dem Training weiter.",

        "wir machen weiter mit training":
            "Wir machen mit dem Training weiter.",

        "zurück in training":
            "Zurück zum Training.",

        "zuruck in training":
            "Zurück zum Training."
    }


    if message in wrong_requests:

        corrected = (
            wrong_requests[
                message
            ]
        )


        return {

            "recognized":
                True,

            "feedback":
                (
                    "Fast! Richtig sagt man: "
                    f"„{corrected}“"
                ),

            "corrected":
                corrected,

            "error_type":
                "preposition"
        }


    return {
        "recognized":
            False
    }


# ==========================================
# OBSŁUGA:
# WRÓĆ DO TRENINGU
# ==========================================

def handle_return_to_training_request(
    user_message,
    state
):

    analysis = (
        analyze_return_to_training_request(
            user_message
        )
    )


    if not analysis.get(
        "recognized",
        False
    ):

        return (
            False,
            None,
            None
        )


    feedback = analysis.get(
        "feedback"
    )

    corrected = analysis.get(
        "corrected"
    )

    error_type = analysis.get(
        "error_type"
    )


    # ======================================
    # ZAPAMIĘTANIE BŁĘDU
    # ======================================

    if (
        corrected
        and
        error_type
    ):

        remember_command_language_error(
            state,
            user_message,
            corrected,
            error_type
        )


    # ======================================
    # USUWAMY STARY STAN PYTANIA
    # O KONTYNUACJĘ
    # ======================================

    clear_old_teacher_choice_state(
        state
    )


    # ======================================
    # NAJPIERW DOKŁADNIE PRZERWANY TRENING
    # ======================================

    continuation = resume_current_training(
        state
    )


    # ======================================
    # JEŻELI NIC NIE JEST AKTYWNE,
    # TEACHER BRAIN WYBIERA DALEJ
    # ======================================

    if not continuation:

        continuation = (
            create_teacher_directed_follow_up(
                state,
                ""
            )
        )


    # ======================================
    # ODPOWIEDŹ
    # ======================================

    if continuation:

        answer = (
            "Gerne. Wir machen weiter.\n\n"
            f"{continuation}"
        )

    else:

        answer = (
            "Gerne. Wir machen weiter."
        )


    return (
        True,
        answer,
        feedback
        )
