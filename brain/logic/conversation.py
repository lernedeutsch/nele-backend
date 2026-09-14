# ==========================================
# NELE – GŁÓWNY ROUTER ROZMOWY
# TEACHER MODE
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

from brain.logic.error_progress import (
    handle_error_progress
)

from brain.logic.learner_feedback import (
    prepare_message_with_feedback
)

from brain.logic.wellbeing_feedback import (
    analyze_wellbeing_response
)

from brain.logic.activity_resume import (
    handle_continue_last_activity,
    resume_current_training
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
    find_response,
    create_returning_user_follow_up,
    create_teacher_directed_follow_up,
    get_short_answer
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

from brain.logic.vocabulary_modules.practice import (
    is_vocabulary_practice_active
)

from brain.memory.review import (
    handle_memory
)

from brain.memory.error_review import (
    refresh_error_reviews
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
# USUNIĘCIE STARYCH PYTAŃ
# O WYBÓR UŻYTKOWNIKA
# ==========================================

def remove_old_teacher_choice_prompt(
    answer
):

    if not answer:
        return answer


    answer = str(
        answer
    ).strip()


    old_prompts = [
        "Möchtest du ",
        "Was möchtest du heute üben?",
        "Womit möchtest du heute anfangen?"
    ]


    positions = []


    for prompt in old_prompts:

        position = answer.find(
            prompt
        )


        if position >= 0:

            positions.append(
                position
            )


    if not positions:
        return answer


    first_position = min(
        positions
    )


    return answer[
        :first_position
    ].rstrip()


# ==========================================
# WYCZYSZCZENIE STAREGO STANU
# PYTANIA O KONTYNUACJĘ
# ==========================================

def clear_old_teacher_choice_state(
    state
):

    if state is None:
        return


    last_question = state.get(
        "last_question"
    )


    if last_question in {
        "continue_last_activity",
        "continue_error_review"
    }:

        state[
            "last_question"
        ] = None


# ==========================================
# ODPOWIEDŹ NA PYTANIE POBOCZNE
# + AUTOMATYCZNY POWRÓT DO TRENINGU
# ==========================================

def continue_after_side_answer(
    answer,
    state
):

    answer = remove_old_teacher_choice_prompt(
        answer
    )


    clear_old_teacher_choice_state(
        state
    )


    # ======================================
    # 1. DOKŁADNIE PRZERWANY TRENING
    # ======================================

    continuation = resume_current_training(
        state
    )


    # ======================================
    # 2. NIC NIE JEST AKTYWNE
    # -> TEACHER BRAIN WYBIERA CO DALEJ
    # ======================================

    if not continuation:

        continuation = (
            create_teacher_directed_follow_up(
                state,
                ""
            )
        )


    if (
        answer
        and
        continuation
    ):

        return (
            f"{answer}\n\n"
            f"{continuation}"
        )


    if answer:
        return answer


    return continuation


# ==========================================
# ZAKOŃCZONE ĆWICZENIE
# -> AUTOMATYCZNY KOLEJNY KROK
# ==========================================
#
# Używamy tego wtedy, gdy ćwiczenie
# właśnie zostało ukończone.
#
# Przykład:
#
# Was bedeutet „Zimmer“?
#
# poprawna odpowiedź
#
# Richtig! ...
#
# ↓
#
# Teacher Brain sam wybiera:
#
# kolejna powtórka
# albo
# dalsza lekcja.
#
# Nie pytamy:
#
# Möchtest du ...?
# ==========================================

def continue_after_finished_training(
    answer,
    state
):

    answer = remove_old_teacher_choice_prompt(
        answer
    )


    clear_old_teacher_choice_state(
        state
    )


    continuation = (
        create_teacher_directed_follow_up(
            state,
            ""
        )
    )


    if (
        answer
        and
        continuation
    ):

        return (
            f"{answer}\n\n"
            f"{continuation}"
        )


    if answer:
        return answer


    return continuation


# ==========================================
# PEŁNA REAKCJA + DALSZA NAUKA
# ==========================================

def combine_full_wellbeing_reaction(
    reaction,
    continuation_answer
):

    if not reaction:
        return continuation_answer

    if not continuation_answer:
        return reaction


    short_reaction = get_short_answer(
        reaction
    )


    if (
        short_reaction
        and
        continuation_answer.startswith(
            short_reaction
        )
    ):

        rest = continuation_answer[
            len(
                short_reaction
            ):
        ]


        return (
            f"{reaction}"
            f"{rest}"
        )


    return (
        f"{reaction} "
        f"{continuation_answer}"
    )


# ==========================================
# ODPOWIEDŹ NA SAMOPOCZUCIE
# ==========================================

def handle_wellbeing_reply(
    user_message,
    state,
    session_id
):

    if state is None:
        return None


    if (
        state.get(
            "last_question"
        )
        !=
        "wellbeing"
    ):

        return None


    analysis = analyze_wellbeing_response(
        user_message
    )


    if not analysis.get(
        "recognized"
    ):

        return None


    reaction = analysis.get(
        "reaction"
    )

    feedback = analysis.get(
        "feedback"
    )


    if not reaction:
        return None


    continuation_answer = (
        create_returning_user_follow_up(
            state,
            reaction,
            ""
        )
    )


    final_answer = (
        combine_full_wellbeing_reaction(
            reaction,
            continuation_answer
        )
    )


    return return_with_feedback(
        final_answer,
        feedback,
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


        elif is_new_user(
            state
        ):

            return generate_welcome_reply(
                session_id
            )


        else:

            complete_onboarding(
                state
            )

            return_with_memory(
                None,
                session_id
            )


    # ======================================
    # 1. SPRAWDZENIE POWTÓREK BŁĘDÓW
    # ======================================

    try:

        refresh_error_reviews(
            state
        )

    except Exception as error:

        print(
            f"Error review refresh error: {error}"
        )


    # ======================================
    # 2. ODPOWIEDŹ NA:
    # WIE GEHT ES DIR?
    # ======================================

    wellbeing_answer = handle_wellbeing_reply(
        user_message,
        state,
        session_id
    )

    if wellbeing_answer:

        return wellbeing_answer


    # ======================================
    # 3. LEARNER FEEDBACK
    # ======================================

    processed_message, feedback_text = (
        prepare_message_with_feedback(
            user_message,
            state
        )
    )


    # ======================================
    # 4. PYTANIA POBOCZNE PODCZAS TRENINGU
    # ======================================


    # ======================================
    # 4A. PYTANIA O BŁĘDY
    # ======================================

    side_error_memory_answer = (
        handle_error_memory(
            processed_message,
            state
        )
    )

    if side_error_memory_answer:

        teacher_answer = (
            continue_after_side_answer(
                side_error_memory_answer,
                state
            )
        )

        return return_with_feedback(
            teacher_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 4B. PYTANIA O PAMIĘĆ NAUKI
    # ======================================

    side_memory_answer = (
        handle_memory(
            processed_message,
            state
        )
    )

    if side_memory_answer:

        teacher_answer = (
            continue_after_side_answer(
                side_memory_answer,
                state
            )
        )

        return return_with_feedback(
            teacher_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 5. AKTYWNE ĆWICZENIE BŁĘDÓW
    # ======================================

    error_practice_answer = (
        handle_error_practice(
            processed_message,
            state
        )
    )

    if error_practice_answer:

        return return_with_feedback(
            error_practice_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 6. POSTĘP W BŁĘDACH
    # ======================================

    error_progress_answer = (
        handle_error_progress(
            processed_message,
            state
        )
    )

    if error_progress_answer:

        return return_with_feedback(
            error_progress_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 7. KONTYNUACJA NOWEJ NAUKI
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
    # 8. AKTYWNA LEKCJA
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
    # 9. STARA KONTYNUACJA AKTYWNOŚCI
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
    # 10. KOREKTA
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
    # 11. ALFABET
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
    # 12. POSTĘP W LEKCJI
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
    # 13. PERSONALIZOWANE ĆWICZENIA
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
    # 14. PAMIĘĆ INFORMACJI O UŻYTKOWNIKU
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
    # 15. PAMIĘĆ BŁĘDÓW
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
    # 16. PAMIĘĆ NAUKI
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
    # 17. KONTYNUACJA AKTUALNEGO TEMATU
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
    # 18. PORÓWNANIA
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
    # 19. SŁOWNICTWO
    #
    # WAŻNE:
    #
    # Zapamiętujemy, czy ćwiczenie było
    # aktywne PRZED odpowiedzią.
    #
    # Następnie sprawdzamy, czy po
    # odpowiedzi nadal jest aktywne.
    #
    # Jeśli:
    #
    # wcześniej = aktywne
    # teraz = zakończone
    #
    # Teacher Mode natychmiast wybiera
    # następny krok.
    #
    # Jeżeli słowo ma np. pytanie
    # o przeciwieństwo, ćwiczenie nadal
    # będzie aktywne i tutaj NIE przejdziemy
    # jeszcze do lekcji.
    # ======================================

    vocabulary_was_active = (
        is_vocabulary_practice_active(
            state
        )
    )


    vocabulary_answer = handle_vocabulary(
        processed_message,
        state
    )


    if vocabulary_answer:

        vocabulary_is_still_active = (
            is_vocabulary_practice_active(
                state
            )
        )


        # ==================================
        # ĆWICZENIE WŁAŚNIE SIĘ ZAKOŃCZYŁO
        # ==================================

        if (
            vocabulary_was_active
            and
            not vocabulary_is_still_active
        ):

            teacher_answer = (
                continue_after_finished_training(
                    vocabulary_answer,
                    state
                )
            )


            return return_with_feedback(
                teacher_answer,
                feedback_text,
                session_id
            )


        # ==================================
        # ĆWICZENIE NADAL TRWA
        # ==================================

        return return_with_feedback(
            vocabulary_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 20. INTENCJE
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
    # 21. ZNANE PYTANIA I ZWROTY
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
    # 22. KONTEKST
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
    # 23. BRAK ZNANEJ ODPOWIEDZI
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
