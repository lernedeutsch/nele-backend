# ==========================================
# NELE – PAMIĘĆ W ROZMOWIE
# TEACHER MODE
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.error_memory_router import (
    handle_error_memory
)

from brain.logic.daily_learning_router import (
    handle_daily_learning
)

from brain.memory.review import (
    handle_memory
)

from brain.logic.conversation_continuation import (
    continue_after_side_answer
)


# ==========================================
# PAMIĘĆ DZISIEJSZEJ NAUKI
# ==========================================

def handle_daily_learning_request(
    user_message,
    state
):

    answer = handle_daily_learning(
        user_message,
        state
    )

    if not answer:

        return (
            False,
            None
        )


    answer = continue_after_side_answer(
        answer,
        state
    )


    return (
        True,
        answer
    )


# ==========================================
# PAMIĘĆ BŁĘDÓW
# ==========================================

def handle_error_memory_request(
    user_message,
    state
):

    error_practice_was_active = bool(
        state
        and
        state.get(
            "error_practice_active",
            False
        )
    )

    answer = handle_error_memory(
        user_message,
        state
    )

    if not answer:

        return (
            False,
            None
        )


    # Starting Error Practice is not a side answer. handle_error_memory()
    # has already returned the first exercise prompt and activated the
    # training. Resuming immediately would append the same newly-started
    # exercise a second time in the very same Nele response.
    error_practice_is_active = bool(
        state.get(
            "error_practice_active",
            False
        )
    )

    if (
        error_practice_is_active
        and
        not error_practice_was_active
    ):
        return (
            True,
            answer
        )


    answer = continue_after_side_answer(
        answer,
        state
    )


    return (
        True,
        answer
    )


# ==========================================
# OGÓLNA PAMIĘĆ NAUKI
# ==========================================

def handle_learning_memory_request(
    user_message,
    state
):

    answer = handle_memory(
        user_message,
        state
    )

    if not answer:

        return (
            False,
            None
        )


    answer = continue_after_side_answer(
        answer,
        state
    )


    return (
        True,
        answer
    )


# ==========================================
# GŁÓWNA OBSŁUGA PAMIĘCI
# ==========================================

def handle_conversation_memory(
    user_message,
    state
):

    # ======================================
    # 1. DAILY LEARNING MEMORY
    #
    # Tylko informacje dotyczące
    # DZISIEJSZEJ nauki.
    #
    # Przykłady:
    #
    # Was habe ich heute gemacht?
    #
    # Was habe ich heute geübt?
    #
    # Welche Wörter habe ich heute
    # wiederholt?
    #
    # Welche Fehler habe ich heute geübt?
    #
    # Habe ich heute schon gelernt?
    # ======================================

    (
        handled,
        answer
    ) = handle_daily_learning_request(
        user_message,
        state
    )

    if handled:

        return (
            True,
            answer
        )


    # ======================================
    # 2. PAMIĘĆ BŁĘDÓW
    #
    # Historia ogólna.
    #
    # Przykład:
    #
    # Wo mache ich noch Fehler?
    # ======================================

    (
        handled,
        answer
    ) = handle_error_memory_request(
        user_message,
        state
    )

    if handled:

        return (
            True,
            answer
        )


    # ======================================
    # 3. OGÓLNA PAMIĘĆ NAUKI
    #
    # Historia niezależna od dnia.
    #
    # Przykłady:
    #
    # Was habe ich zuletzt geübt?
    #
    # Welche Wörter habe ich geübt?
    #
    # Welche Wörter soll ich wiederholen?
    #
    # Welche Wörter sind schwierig für mich?
    # ======================================

    (
        handled,
        answer
    ) = handle_learning_memory_request(
        user_message,
        state
    )

    if handled:

        return (
            True,
            answer
        )


    # ======================================
    # BRAK PYTANIA O PAMIĘĆ
    # ======================================

    return (
        False,
        None
    )
