# ==========================================
# NELE – LOGIKA ROZMOWY Z PAMIĘCIĄ SESJI
# ==========================================

from brain.responses.corrections import find_correction

from brain.logic.memory import get_conversation_state

from brain.logic.message_parser import (
    split_multiple_questions
)

from brain.logic.conversation_context import (
    remember_current_topic,
    remember_current_comparison,
    handle_topic_follow_up,
    handle_comparison_follow_up,
    handle_other_expression
)

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

from brain.logic.comparison_context import (
    answer_comparison_usage,
    answer_current_expression_example,
    answer_next_expression_example
)

from brain.logic.vocabulary import (
    answer_vocabulary_question,
    answer_vocabulary_example,
    answer_vocabulary_usage,
    answer_similar_vocabulary_word,
    answer_vocabulary_difference_follow_up,
    answer_explicit_vocabulary_difference
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

    # ======================================
    # KILKA PYTAŃ W JEDNEJ WIADOMOŚCI
    # ======================================

    multiple_questions = split_multiple_questions(
        user_message
    )

    if multiple_questions:

        answers = []

        for question in multiple_questions:

            answer = generate_conversation_reply(
                question,
                level,
                lesson,
                session_id
            )

            if answer:
                answers.append(
                    answer
                )

        if answers:
            return "\n\n".join(
                answers
            )


    # ======================================
    # PAMIĘĆ SESJI
    # ======================================

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

    if "current_vocabulary_related_word" not in state:
        state["current_vocabulary_related_word"] = None


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


    similar_vocabulary_answer = (
        answer_similar_vocabulary_word(
            user_message,
            state
        )
    )

    if similar_vocabulary_answer:
        return similar_vocabulary_answer


    vocabulary_difference_follow_up = (
        answer_vocabulary_difference_follow_up(
            user_message,
            state
        )
    )

    if vocabulary_difference_follow_up:
        return vocabulary_difference_follow_up


    explicit_vocabulary_difference = (
        answer_explicit_vocabulary_difference(
            user_message,
            state
        )
    )

    if explicit_vocabulary_difference:
        return explicit_vocabulary_difference


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
