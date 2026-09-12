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

from brain.logic.error_practice import (
    handle_error_practice
)

from brain.logic.learner_feedback import (
    prepare_message_with_feedback
)

from brain.logic.activity_resume import (
    handle_continue_last_activity
)

from brain.logic.lesson_progress_router import (
    handle_lesson_progress
)

from brain.logic.error_memory_router import (
    handle_error_memory
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
# POŁĄCZENIE FEEDBACKU Z ODPOWIEDZIĄ
# ==========================================

def combine_learner_feedback(
    feedback_text,
    answer
):

    if not feedback_text:
        return answer

    if not answer:
        return feedback_text

    return (
        f"{feedback_text}\n\n"
        f"{answer}"
    )


# ==========================================
# ZAPIS + FEEDBACK + ODPOWIEDŹ
# ==========================================

def return_with_feedback(
    answer,
    feedback_text,
    session_id
):

    final_answer = combine_learner_feedback(
        feedback_text,
        answer
    )

    return return_with_memory(
        final_answer,
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
    # 1. AKTYWNE ĆWICZENIE BŁĘDÓW
    # STUDENT MEMORY 2.0
    #
    # Musi być przed learner feedback,
    # żeby odpowiedź użytkownika została
    # najpierw oceniona przez ćwiczenie.
    # ======================================

    error_practice_answer = (
        handle_error_practice(
            user_message,
            state
        )
    )

    if error_practice_answer:

        return return_with_memory(
            error_practice_answer,
            session_id
        )


    # ======================================
    # 2. LEARNER FEEDBACK
    #
    # Nele może poprawić błędne zdanie,
    # dalej rozumie jego intencję
    # i zapisuje błąd w Student Memory 2.0.
    #
    # Przykład:
    #
    # Was soll ich lernen heute?
    #
    # ->
    #
    # Was soll ich heute lernen?
    # ======================================

    processed_message, feedback_text = (
        prepare_message_with_feedback(
            user_message,
            state
        )
    )


    # ======================================
    # 3. KONTYNUACJA NOWEJ NAUKI
    # ======================================

    new_learning_answer = (
        handle_new_learning_resume(
            processed_message,
            state
        )
    )

    if new_learning_answer:

        return return_with_feedback(
            new_learning_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 4. AKTYWNA LEKCJA
    # ======================================

    lesson_teaching_answer = (
        handle_lesson_teaching(
            processed_message,
            state
        )
    )

    if lesson_teaching_answer:

        return return_with_feedback(
            lesson_teaching_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 5. KONTYNUACJA OSTATNIEJ AKTYWNOŚCI
    # ======================================

    continue_answer = (
        handle_continue_last_activity(
            processed_message,
            state
        )
    )

    if continue_answer:

        return return_with_feedback(
            continue_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 6. KOREKTA
    # ======================================

    correction_answer = handle_correction(
        processed_message,
        session_id
    )

    if correction_answer:

        return return_with_feedback(
            correction_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 7. ALFABET
    # ======================================

    alphabet_answer = handle_alphabet(
        processed_message,
        level,
        lesson
    )

    if alphabet_answer:

        return return_with_feedback(
            alphabet_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 8. POSTĘP W LEKCJI
    # STUDENT MEMORY 2.0
    # ======================================

    lesson_progress_answer = (
        handle_lesson_progress(
            processed_message,
            state
        )
    )

    if lesson_progress_answer:

        return return_with_feedback(
            lesson_progress_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 9. PERSONALIZOWANE ĆWICZENIA
    # ======================================

    personalization_answer = (
        handle_personalization(
            processed_message,
            state
        )
    )

    if personalization_answer:

        return return_with_feedback(
            personalization_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 10. PAMIĘĆ INFORMACJI O UŻYTKOWNIKU
    # ======================================

    user_memory_answer = handle_user_memory(
        processed_message,
        session_id
    )

    if user_memory_answer:

        return return_with_feedback(
            user_memory_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 11. PAMIĘĆ BŁĘDÓW
    # STUDENT MEMORY 2.0
    # ======================================

    error_memory_answer = handle_error_memory(
        processed_message,
        state
    )

    if error_memory_answer:

        return return_with_feedback(
            error_memory_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 12. PAMIĘĆ NAUKI
    # STUDENT MEMORY 2.0
    # ======================================

    memory_answer = handle_memory(
        processed_message,
        state
    )

    if memory_answer:

        return return_with_feedback(
            memory_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 13. KONTYNUACJA AKTUALNEGO TEMATU
    # ======================================

    topic_answer = handle_topic_follow_up(
        processed_message,
        session_id
    )

    if topic_answer:

        return return_with_feedback(
            topic_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 14. PORÓWNANIA
    # ======================================

    comparison_answer = handle_comparison(
        processed_message,
        state,
        session_id
    )

    if comparison_answer:

        return return_with_feedback(
            comparison_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 15. SŁOWNICTWO
    # ======================================

    vocabulary_answer = handle_vocabulary(
        processed_message,
        state
    )

    if vocabulary_answer:

        return return_with_feedback(
            vocabulary_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 16. INTENCJE
    # ======================================

    intent_answer = handle_intent(
        processed_message,
        session_id
    )

    if intent_answer:

        remember_current_topic(
            processed_message,
            session_id
        )

        remember_current_comparison(
            processed_message,
            session_id
        )

        return return_with_feedback(
            intent_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 17. ZNANE PYTANIA I ZWROTY
    # ======================================

    known_answer = find_response(
        processed_message,
        level,
        lesson,
        session_id
    )

    if known_answer:

        return return_with_feedback(
            known_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 18. KONTEKST
    # ======================================

    context_answer = handle_context(
        processed_message,
        session_id
    )

    if context_answer:

        return return_with_feedback(
            context_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 19. BRAK ZNANEJ ODPOWIEDZI
    # ======================================

    fallback_answer = (
        "Ich habe dich verstanden, "
        "aber diese Antwort habe ich "
        "noch nicht gelernt."
    )

    return return_with_feedback(
        fallback_answer,
        feedback_text,
        session_id
                )
