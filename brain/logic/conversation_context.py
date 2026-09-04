# ==========================================
# NELE – KONTEKST ROZMOWY
# ==========================================

from brain.logic.memory import get_conversation_state

from brain.logic.matcher import (
    normalize
)

from brain.logic.intents import (
    detect_intent
)

from brain.logic.intent_handler import (
    handle_intent
)

from brain.logic.comparison import (
    compare_formality,
    compare_informality,
    explain_formality_difference
)

from brain.logic.comparison_context import (
    get_other_expression
)


# ==========================================
# ZAPAMIĘTYWANIE TEMATU ROZMOWY
# ==========================================

def remember_current_topic(
    user_message,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    intent = detect_intent(
        user_message
    )

    if not intent:
        return None

    content = intent.get(
        "content",
        ""
    ).strip()

    if not content:
        return None

    if content == "das":
        return state.get(
            "current_topic"
        )

    if intent.get("intent") == "difference":
        return state.get(
            "current_topic"
        )

    state[
        "current_topic"
    ] = content

    return content


# ==========================================
# ZAPAMIĘTYWANIE PORÓWNANIA
# ==========================================

def remember_current_comparison(
    user_message,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    intent = detect_intent(
        user_message
    )

    if not intent:
        return None

    if intent.get("intent") != "difference":
        return None

    content = intent.get(
        "content",
        ""
    ).strip()

    if not content:
        return None

    if " und " not in content:
        return None

    parts = content.split(
        " und ",
        1
    )

    first = parts[0].strip()
    second = parts[1].strip()

    if not first or not second:
        return None

    comparison = [
        first,
        second
    ]

    state[
        "current_comparison"
    ] = comparison

    return comparison


# ==========================================
# PYTANIA O AKTUALNY TEMAT
# ==========================================

def handle_topic_follow_up(
    user_message,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    topic = state.get(
        "current_topic"
    )

    if not topic:
        return None

    message = normalize(
        user_message
    )

    meaning_follow_ups = [
        "was bedeutet das",
        "und was bedeutet das",
        "was heißt das",
        "was heisst das",
        "und was heißt das",
        "und was heisst das"
    ]

    if message in meaning_follow_ups:

        return handle_intent(
            f"Was bedeutet {topic}?",
            session_id
        )

    usage_follow_ups = [
        "wann benutzt man das",
        "und wann benutzt man das",
        "wann sagt man das",
        "und wann sagt man das",
        "wann verwendet man das",
        "und wann verwendet man das",
        "wie benutzt man das",
        "und wie benutzt man das"
    ]

    if message in usage_follow_ups:

        return handle_intent(
            f"Wann benutzt man {topic}?",
            session_id
        )

    explanation_follow_ups = [
        "warum",
        "warum denn",
        "und warum",
        "und warum denn",
        "warum ist das so",
        "und warum ist das so"
    ]

    if message in explanation_follow_ups:

        return handle_intent(
            f"Warum sagt man {topic}?",
            session_id
        )

    example_follow_ups = [
        "gib mir ein beispiel",
        "gib mir ein beispiel dafür",
        "und ein beispiel",
        "und ein beispiel dafür",
        "nenn mir ein beispiel",
        "nenn mir ein beispiel dafür",
        "zeig mir ein beispiel",
        "zeig mir ein beispiel dafür"
    ]

    if message in example_follow_ups:

        return handle_intent(
            f"Gib mir ein Beispiel für {topic}.",
            session_id
        )

    formality_follow_ups = [
        "ist das formell oder informell",
        "ist das informell oder formell",
        "ist das formell",
        "ist das informell",
        "und ist das formell oder informell",
        "und ist das informell oder formell",
        "und ist das formell",
        "und ist das informell"
    ]

    if message in formality_follow_ups:

        return handle_intent(
            f"Ist {topic} formell oder informell?",
            session_id
        )

    return None


# ==========================================
# PYTANIA O AKTUALNE PORÓWNANIE
# ==========================================

def handle_comparison_follow_up(
    user_message,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    comparison = state.get(
        "current_comparison"
    )

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

    first = comparison[0]
    second = comparison[1]

    formality_questions = [
        "welches ist formeller",
        "und welches ist formeller",
        "was ist formeller",
        "und was ist formeller",
        "welcher ausdruck ist formeller",
        "und welcher ausdruck ist formeller",
        "welcher ist formeller",
        "und welcher ist formeller"
    ]

    if message in formality_questions:

        return compare_formality(
            first,
            second
        )

    informality_questions = [
        "welches ist informeller",
        "und welches ist informeller",
        "was ist informeller",
        "und was ist informeller",
        "welcher ausdruck ist informeller",
        "und welcher ausdruck ist informeller",
        "welcher ist informeller",
        "und welcher ist informeller"
    ]

    if message in informality_questions:

        return compare_informality(
            first,
            second
        )

    explanation_questions = [
        "warum",
        "und warum",
        "warum denn",
        "und warum denn",
        "warum ist das so",
        "und warum ist das so"
    ]

    if message in explanation_questions:

        return explain_formality_difference(
            first,
            second
        )

    return None


# ==========================================
# DRUGI ZWROT Z AKTUALNEGO PORÓWNANIA
# ==========================================

def handle_other_expression(
    user_message,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    message = normalize(
        user_message
    )

    other_questions = [
        "und das andere",
        "das andere",
        "und der andere",
        "der andere",
        "und die andere",
        "die andere"
    ]

    if message not in other_questions:
        return None

    comparison = state.get(
        "current_comparison"
    )

    current_expression = state.get(
        "current_expression"
    )

    other_expression = get_other_expression(
        comparison,
        current_expression
    )

    if not other_expression:
        return None

    state[
        "current_expression"
    ] = other_expression

    return handle_intent(
        f"Wann benutzt man {other_expression}?",
        session_id
  )
