# ==========================================
# NELE – KONTEKST PORÓWNANIA
# ==========================================

from brain.logic.matcher import normalize

from brain.knowledge.A1.usage import USAGE


# ==========================================
# SZUKANIE ZWROTU Z AKTUALNEGO PORÓWNANIA
# ==========================================

def find_expression_in_comparison(
    user_message,
    comparison
):

    if not comparison:
        return None

    if not isinstance(
        comparison,
        list
    ):
        return None

    if len(comparison) != 2:
        return None

    message = normalize(
        user_message
    )

    for expression in comparison:

        expression_normalized = normalize(
            expression
        )

        if expression_normalized in message:
            return expression

    return None


# ==========================================
# PYTANIE O UŻYCIE JEDNEGO ZE ZWROTÓW
# ==========================================

def answer_comparison_usage(
    user_message,
    comparison,
    state=None
):

    message = normalize(
        user_message
    )

    usage_phrases = [
        "wann benutze ich",
        "wann benutzt man",
        "wann sagt man",
        "wann verwende ich",
        "wann verwendet man",
        "wo benutze ich",
        "wo benutzt man",
        "in welcher situation"
    ]

    is_usage_question = False

    for phrase in usage_phrases:

        if phrase in message:

            is_usage_question = True
            break

    if not is_usage_question:
        return None


    expression = find_expression_in_comparison(
        user_message,
        comparison
    )

    if not expression:
        return None


    # ======================================
    # ZAPAMIĘTANIE AKTUALNEGO ZWROTU
    # ======================================

    if state is not None:

        state[
            "current_expression"
        ] = expression


    answer = USAGE.get(
        normalize(
            expression
        )
    )

    if answer:
        return answer

    return None


# ==========================================
# DRUGI ZWROT Z PORÓWNANIA
# ==========================================

def get_other_expression(
    comparison,
    current_expression
):

    if not comparison:
        return None

    if not isinstance(
        comparison,
        list
    ):
        return None

    if len(comparison) != 2:
        return None

    if not current_expression:
        return None

    first = comparison[0]
    second = comparison[1]

    if current_expression == first:
        return second

    if current_expression == second:
        return first

    return None
