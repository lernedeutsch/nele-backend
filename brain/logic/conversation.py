# ==========================================
# NELE – LOGIKA ROZMOWY Z PAMIĘCIĄ SESJI
# ==========================================

from brain.logic.memory import (
    get_conversation_state,
    save_conversation_state
)

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

from brain.logic.alphabet_router import (
    handle_alphabet
)

from brain.logic.context_router import (
    handle_context
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

from brain.memory.review import (
    handle_memory
)


# ==========================================
# ZAPISANIE STANU I ZWROT ODPOWIEDZI
# ==========================================

def return_with_memory(
    answer,
    session_id
):

    try:

        save_conversation_state(
            session_id
        )

    except Exception as error:

        print(
            f"Conversation save error: {error}"
        )

    return answer


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

            return return_with_memory(
                "\n\n".join(
                    answers
                ),
                session_id
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

    if "vocabulary_memory" not in state:
        state["vocabulary_memory"] = {}


    # ======================================
    # 1. KOREKTA BŁĘDÓW
    # ======================================

    correction_answer = handle_correction(
        user_message,
        session_id
    )

    if correction_answer:

        return return_with_memory(
            correction_answer,
            session_id
        )


    # ======================================
    # 2. ALFABET
    # ======================================

    alphabet_answer = handle_alphabet(
        user_message,
        level,
        lesson
    )

    if alphabet_answer:

        return return_with_memory(
            alphabet_answer,
            session_id
        )


    # ======================================
    # 3. PAMIĘĆ I INFORMACJE O UŻYTKOWNIKU
    # ======================================

    user_memory_answer = handle_user_memory(
        user_message,
        session_id
    )

    if user_memory_answer:

        return return_with_memory(
            user_memory_answer,
            session_id
        )


    # ======================================
    # 4. PAMIĘĆ NAUKI SŁOWNICTWA
    # ======================================

    memory_answer = handle_memory(
        user_message,
        state
    )

    if memory_answer:

        return return_with_memory(
            memory_answer,
            session_id
        )


    # ======================================
    # 5. KONTYNUACJA AKTUALNEGO TEMATU
    # ======================================

    topic_answer = handle_topic_follow_up(
        user_message,
        session_id
    )

    if topic_answer:

        return return_with_memory(
            topic_answer,
            session_id
        )


    # ======================================
    # 6. PORÓWNANIA
    # ======================================

    comparison_answer = handle_comparison(
        user_message,
        state,
        session_id
    )

    if comparison_answer:

        return return_with_memory(
            comparison_answer,
            session_id
        )


    # ======================================
    # 7. SŁOWNICTWO
    # ======================================

    vocabulary_answer = handle_vocabulary(
        user_message,
        state
    )

    if vocabulary_answer:

        return return_with_memory(
            vocabulary_answer,
            session_id
        )


    # ======================================
    # 8. ROZPOZNAWANIE INTENCJI
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

        return return_with_memory(
            intent_answer,
            session_id
        )


    # ======================================
    # 9. ZNANE PYTANIA I ZWROTY
    # ======================================

    known_answer = find_response(
        user_message,
        level,
        lesson,
        session_id
    )

    if known_answer:

        return return_with_memory(
            known_answer,
            session_id
        )


    # ======================================
    # 10. ODPOWIEDŹ KONTEKSTOWA
    # ======================================

    context_answer = handle_context(
        user_message,
        session_id
    )

    if context_answer:

        return return_with_memory(
            context_answer,
            session_id
        )


    # ======================================
    # 11. BRAK WIEDZY
    # ======================================

    return return_with_memory(
        (
            "Ich habe dich verstanden, "
            "aber diese Antwort habe ich "
            "noch nicht gelernt."
        ),
        session_id
        )
