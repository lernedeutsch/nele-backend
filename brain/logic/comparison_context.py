# ==========================================
# NELE – KONTEKST PORÓWNANIA
# ==========================================

from brain.logic.matcher import normalize

from brain.knowledge.A1.usage import USAGE
from brain.knowledge.A1.examples import EXAMPLES


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
# PRZYKŁAD DLA AKTUALNEGO ZWROTU
# ==========================================

def answer_current_expression_example(
    user_message,
    state
):

    if state is None:
        return None

    current_expression = state.get(
        "current_expression"
    )

    if not current_expression:
        return None

    message = normalize(
        user_message
    )

    example_questions = [
        "und ein beispiel",
        "und ein beispiel dafür",
        "ein beispiel",
        "ein beispiel dafür",
        "gib mir ein beispiel",
        "gib mir ein beispiel dafür",
        "nenn mir ein beispiel",
        "nenn mir ein beispiel dafür",
        "zeig mir ein beispiel",
        "zeig mir ein beispiel dafür",
        "noch ein beispiel"
    ]

    if message not in example_questions:
        return None

    answer = EXAMPLES.get(
        normalize(
            current_expression
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
