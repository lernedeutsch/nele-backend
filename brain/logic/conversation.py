# ==========================================
# NELE – LOGIKA ROZMOWY Z PAMIĘCIĄ SESJI
# ==========================================

from brain.responses.corrections import find_correction

from brain.logic.memory import get_conversation_state

from brain.logic.matcher import (
    normalize,
    clean_short_answer,
    capitalize_value
)

from brain.logic.user_info import (
    extract_user_information
)

from brain.logic.memory_answers import (
    answer_from_memory
)

from brain.logic.context import (
    handle_context_answer
)

from brain.logic.alphabet import (
    handle_alphabet_question
)

from brain.logic.lesson_loader import (
    load_lesson_module
)

from brain.logic.response_engine import (
    find_response
)

from brain.logic.intent_handler import (
    handle_intent
)

from brain.logic.intents import (
    detect_intent
)

from brain.logic.comparison import (
    compare_formality,
    compare_informality,
    explain_formality_difference
)

from brain.logic.comparison_context import (
    answer_comparison_usage,
    answer_current_expression_example,
    answer_next_expression_example,
    get_other_expression
)

from brain.logic.vocabulary import (
    answer_vocabulary_question,
    answer_vocabulary_example,
    answer_vocabulary_usage
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


# ==========================================
# GŁÓWNA LOGIKA ROZMOWY
# ==========================================

def generate_conversation_reply(
    user_message,
    level="A1",
    lesson=1,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    if "current_topic" not in state:
        state["current_topic"] = None

    if "current_comparison" not in state:
        state["current_comparison"] = None

    if "current_expression" not in state:
        state["current_expression"] = None

    if "last_example_expression" not in state:
        state["last_example_expression"] = None

    if "example_index" not in state:
        state["example_index"] = -1

    if "current_vocabulary_word" not in state:
        state["current_vocabulary_word"] = None


    # ======================================
    # 1. KOREKTA BŁĘDÓW
    # ======================================

    correction = find_correction(
        user_message
    )

    if correction:

        corrected = correction[
            "correct"
        ]

        explanation = correction[
            "explanation"
        ]

        corrected_clean = clean_short_answer(
            corrected
        )

        corrected_normalized = normalize(
            corrected_clean
        )

        if corrected_normalized.startswith(
            "ich heiße "
        ):

            value = corrected_clean[
                len("Ich heiße "):
            ].strip()

            value = capitalize_value(
                value
            )

            corrected = (
                f"Ich heiße {value}."
            )

        elif corrected_normalized.startswith(
            "mein name ist "
        ):

            value = corrected_clean[
                len("Mein Name ist "):
            ].strip()

            value = capitalize_value(
                value
            )

            corrected = (
                f"Mein Name ist {value}."
            )

        continuation = extract_user_information(
            corrected,
            session_id
        )

        if continuation:

            return (
                f"{explanation} "
                f"Richtig ist: "
                f"{corrected} "
                f"{continuation}"
            )

        return (
            f"{explanation} "
            f"Richtig ist: "
            f"{corrected}"
        )


    # ======================================
    # 2. ALFABET
    # ======================================

    alphabet_answer = handle_alphabet_question(
        user_message,
        load_lesson_module,
        level,
        lesson
    )

    if alphabet_answer:
        return alphabet_answer


    # ======================================
    # 3. PYTANIA O PAMIĘĆ UŻYTKOWNIKA
    # ======================================

    memory_answer = answer_from_memory(
        user_message,
        session_id
    )

    if memory_answer:
        return memory_answer


    # ======================================
    # 4. PYTANIE KONTYNUUJĄCE TEMAT
    # ======================================

    topic_answer = handle_topic_follow_up(
        user_message,
        session_id
    )

    if topic_answer:
        return topic_answer


    # ======================================
    # 5. PYTANIE KONTYNUUJĄCE PORÓWNANIE
    # ======================================

    comparison_answer = handle_comparison_follow_up(
        user_message,
        session_id
    )

    if comparison_answer:
        return comparison_answer


    # ======================================
    # 6. UŻYCIE ZWROTU Z PORÓWNANIA
    # ======================================

    comparison_usage_answer = answer_comparison_usage(
        user_message,
        state.get(
            "current_comparison"
        ),
        state
    )

    if comparison_usage_answer:
        return comparison_usage_answer


    # ======================================
    # 7. DRUGI ZWROT Z PORÓWNANIA
    # ======================================

    other_expression_answer = handle_other_expression(
        user_message,
        session_id
    )

    if other_expression_answer:
        return other_expression_answer


    # ======================================
    # 8. PRZYKŁAD DLA AKTUALNEGO ZWROTU
    # ======================================

    current_expression_example = (
        answer_current_expression_example(
            user_message,
            state
        )
    )

    if current_expression_example:
        return current_expression_example


    # ======================================
    # 9. KOLEJNY PRZYKŁAD
    # ======================================

    next_expression_example = (
        answer_next_expression_example(
            user_message,
            state
        )
    )

    if next_expression_example:
        return next_expression_example


    # ======================================
    # 10. PYTANIA O SŁOWNICTWO
    # ======================================

    vocabulary_answer = answer_vocabulary_question(
        user_message,
        state
    )

    if vocabulary_answer:
        return vocabulary_answer


    vocabulary_example = answer_vocabulary_example(
        user_message,
        state
    )

    if vocabulary_example:
        return vocabulary_example


    vocabulary_usage = answer_vocabulary_usage(
        user_message,
        state
    )

    if vocabulary_usage:
        return vocabulary_usage


    # ======================================
    # 11. ROZPOZNAWANIE INTENCJI
    # ======================================

    intent_answer = handle_intent(
        user_message,
        session_id
    )

    if intent_answer:

        remember_current_topic(
            user_message,
            session_id
        )

        remember_current_comparison(
            user_message,
            session_id
        )

        return intent_answer


    # ======================================
    # 12. INFORMACJE O UŻYTKOWNIKU
    # ======================================

    extracted_answer = extract_user_information(
        user_message,
        session_id
    )

    if extracted_answer:
        return extracted_answer


    # ======================================
    # 13. ZNANE PYTANIA I ZWROTY
    # ======================================

    known_answer = find_response(
        user_message,
        level,
        lesson,
        session_id
    )

    if known_answer:
        return known_answer


    # ======================================
    # 14. ODPOWIEDŹ KONTEKSTOWA
    # ======================================

    context_answer = handle_context_answer(
        user_message,
        session_id
    )

    if context_answer:
        return context_answer


    # ======================================
    # 15. BRAK WIEDZY
    # ======================================

    return (
        "Ich habe dich verstanden, "
        "aber diese Antwort habe ich "
        "noch nicht gelernt."
  )
