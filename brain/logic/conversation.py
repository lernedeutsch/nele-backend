# ==========================================
# NELE – LOGIKA ROZMOWY Z PAMIĘCIĄ SESJI
# ==========================================

from brain.logic.memory import get_conversation_state

from brain.logic.message_parser import (
    split_multiple_questions
)

from brain.logic.conversation_context import (
    remember_current_topic,
    remember_current_comparison,
    handle_topic_follow_up
)

from brain.logic.correction_router import (
    handle_correction
)

from brain.logic.user_memory_router import (
    handle_user_memory
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

from brain.logic.comparison_router import (
    handle_comparison
)

from brain.logic.vocabulary_router import (
    handle_vocabulary
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

    correction_answer = handle_correction(
        user_message,
        session_id
    )

    if correction_answer:
        return correction_answer


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
    # 3. PAMIĘĆ I INFORMACJE O UŻYTKOWNIKU
    # ======================================

    user_memory_answer = handle_user_memory(
        user_message,
        session_id
    )

    if user_memory_answer:
        return user_memory_answer


    # ======================================
    # 4. KONTYNUACJA AKTUALNEGO TEMATU
    # ======================================

    topic_answer = handle_topic_follow_up(
        user_message,
        session_id
    )

    if topic_answer:
        return topic_answer


    # ======================================
    # 5. PORÓWNANIA
    # ======================================

    comparison_answer = handle_comparison(
        user_message,
        state,
        session_id
    )

    if comparison_answer:
        return comparison_answer


    # ======================================
    # 6. SŁOWNICTWO
    # ======================================

    vocabulary_answer = handle_vocabulary(
        user_message,
        state
    )

    if vocabulary_answer:
        return vocabulary_answer


    # ======================================
    # 7. ROZPOZNAWANIE INTENCJI
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
    # 8. ZNANE PYTANIA I ZWROTY
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
    # 9. ODPOWIEDŹ KONTEKSTOWA
    # ======================================

    context_answer = handle_context_answer(
        user_message,
        session_id
    )

    if context_answer:
        return context_answer


    # ======================================
    # 10. BRAK WIEDZY
    # ======================================

    return (
        "Ich habe dich verstanden, "
        "aber diese Antwort habe ich "
        "noch nicht gelernt."
    )
