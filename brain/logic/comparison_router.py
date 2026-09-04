# ==========================================
# NELE – ROUTER PORÓWNAŃ
# ==========================================

from brain.logic.conversation_context import (
    handle_comparison_follow_up,
    handle_other_expression
)

from brain.logic.comparison_context import (
    answer_comparison_usage,
    answer_current_expression_example,
    answer_next_expression_example
)


# ==========================================
# GŁÓWNA OBSŁUGA PORÓWNAŃ
# ==========================================

def handle_comparison(
    user_message,
    state,
    session_id="default"
):

    # ======================================
    # KONTYNUACJA PORÓWNANIA
    # ======================================

    answer = handle_comparison_follow_up(
        user_message,
        session_id
    )

    if answer:
        return answer


    # ======================================
    # UŻYCIE ZWROTU Z PORÓWNANIA
    # ======================================

    answer = answer_comparison_usage(
        user_message,
        state.get(
            "current_comparison"
        ),
        state
    )

    if answer:
        return answer


    # ======================================
    # DRUGI ZWROT Z PORÓWNANIA
    # ======================================

    answer = handle_other_expression(
        user_message,
        session_id
    )

    if answer:
        return answer


    # ======================================
    # PRZYKŁAD DLA AKTUALNEGO ZWROTU
    # ======================================

    answer = answer_current_expression_example(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # KOLEJNY PRZYKŁAD
    # ======================================

    answer = answer_next_expression_example(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # BRAK ODPOWIEDZI PORÓWNAWCZEJ
    # ======================================

    return None
