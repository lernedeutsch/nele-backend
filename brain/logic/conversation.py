# ==========================================
# NELE – GŁÓWNY ROUTER ROZMOWY
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

from brain.logic.personalization_router import (
    handle_personalization
)

from brain.logic.onboarding import (
    is_onboarding_completed,
    is_new_user,
    get_onboarding_step,
    handle_onboarding_answer,
    complete_onboarding
)

from brain.logic.welcome import (
    generate_welcome_reply
)

from brain.logic.new_learning_resume import (
    handle_new_learning_resume
)

from brain.logic.lesson_teaching import (
    handle_lesson_teaching
)

from brain.logic.activity_resume import (
    handle_continue_last_activity
)

from brain.logic.lesson_progress_router import (
    handle_lesson_progress
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
# ZAPIS STANU I ZWROT ODPOWIEDZI
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
    # PAMIĘĆ UŻYTKOWNIKA
    # ======================================

    state = get_conversation_state(
        session_id
    )


    # ======================================
    # 0. PIERWSZE SPOTKANIE / ONBOARDING
    # ======================================

    if not is_onboarding_completed(
        state
    ):

        onboarding_step = get_onboarding_step(
            state
        )


        # ==================================
        # ONBOARDING JUŻ TRWA
        # ==================================

        if onboarding_step > 0:

            onboarding_answer = (
                handle_onboarding_answer(
                    user_message,
                    state,
                    session_id
                )
            )

            if onboarding_answer:

                return return_with_memory(
                    onboarding_answer,
                    session_id
                )


        # ==================================
        # NOWY UŻYTKOWNIK
        # ==================================

        elif is_new_user(
            state
        ):

            return generate_welcome_reply(
                session_id
            )


        # ==================================
        # STARY UŻYTKOWNIK
        # SPRZED WPROWADZENIA ONBOARDINGU
        # ==================================

        else:

            complete_onboarding(
                state
            )

            return_with_memory(
                None,
                session_id
            )


    # ======================================
    # 1. KONTYNUACJA NOWEJ NAUKI
    # STUDENT MEMORY 2.0
    #
    # Przykład:
    # Nele:
    # "Möchtest du damit anfangen?"
    #
    # Użytkownik:
    # "Ja"
    # ======================================

    new_learning_answer = (
        handle_new_learning_resume(
            user_message,
            state
        )
    )

    if new_learning_answer:

        return return_with_memory(
            new_learning_answer,
            session_id
        )


    # ======================================
    # 2. AKTYWNA LEKCJA
    #
    # Przykład:
    # Nele:
    # "Wie heißt du?"
    #
    # Użytkownik:
    # "Ich heiße Moni."
    # ======================================

    lesson_teaching_answer = (
        handle_lesson_teaching(
            user_message,
            state
        )
    )

    if lesson_teaching_answer:

        return return_with_memory(
            lesson_teaching_answer,
            session_id
        )


    # ======================================
    # 3. KONTYNUACJA OSTATNIEJ AKTYWNOŚCI
    # ======================================

    continue_answer = (
        handle_continue_last_activity(
            user_message,
            state
        )
    )

    if continue_answer:

        return return_with_memory(
            continue_answer,
            session_id
        )


    # ======================================
    # 4. KOREKTA
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
    # 5. ALFABET
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
    # 6. POSTĘP W LEKCJI
    # STUDENT MEMORY 2.0
    # ======================================

    lesson_progress_answer = (
        handle_lesson_progress(
            user_message,
            state
        )
    )

    if lesson_progress_answer:

        return return_with_memory(
            lesson_progress_answer,
            session_id
        )


    # ======================================
    # 7. PERSONALIZOWANE ĆWICZENIA
    # ======================================

    personalization_answer = (
        handle_personalization(
            user_message,
            state
        )
    )

    if personalization_answer:

        return return_with_memory(
            personalization_answer,
            session_id
        )


    # ======================================
    # 8. PAMIĘĆ INFORMACJI O UŻYTKOWNIKU
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
    # 9. PAMIĘĆ NAUKI / STUDENT MEMORY 2.0
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
    # 10. KONTYNUACJA AKTUALNEGO TEMATU
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
    # 11. PORÓWNANIA
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
    # 12. SŁOWNICTWO
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
    # 13. INTENCJE
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
    # 14. ZNANE PYTANIA I ZWROTY
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
    # 15. KONTEKST
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
    # 16. BRAK ZNANEJ ODPOWIEDZI
    # ======================================

    return return_with_memory(
        (
            "Ich habe dich verstanden, "
            "aber diese Antwort habe ich "
            "noch nicht gelernt."
        ),
        session_id
                )
