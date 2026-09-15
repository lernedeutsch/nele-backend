# ==========================================
# NELE – PAMIĘĆ W ROZMOWIE
# TEACHER MODE
# ==========================================

from brain.logic.error_memory_router import (
    handle_error_memory
)

from brain.memory.review import (
    handle_memory
)

from brain.logic.conversation_continuation import (
    continue_after_side_answer
)


# ==========================================
# PAMIĘĆ BŁĘDÓW
# ==========================================

def handle_error_memory_request(
    user_message,
    state
):

    answer = handle_error_memory(
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
# PAMIĘĆ NAUKI
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
    # 1. PAMIĘĆ BŁĘDÓW
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
    # 2. PAMIĘĆ NAUKI
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
