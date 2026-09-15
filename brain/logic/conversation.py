# ==========================================
# NELE – GŁÓWNY ROUTER ROZMOWY
# TEACHER MODE
# ==========================================

import re

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

from brain.logic.error_progress import (
    handle_error_progress
)

from brain.logic.learner_feedback import (
    prepare_message_with_feedback
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
    create_teacher_directed_follow_up
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

from brain.logic.conversation_commands import (
    handle_repeat_request,
    handle_return_to_training_request
)

from brain.logic.conversation_vocabulary import (
    handle_vocabulary_explanation_request
)

from brain.logic.conversation_error_training import (
    handle_priority_error_practice,
    handle_active_error_practice,
    continue_after_finished_training
)

from brain.logic.conversation_wellbeing import (
    handle_wellbeing_reply
)

from brain.memory.review import (
    handle_memory
)

from brain.memory.error_review import (
    refresh_error_reviews
)


# ==========================================
# FEEDBACK
# ==========================================

def merge_feedback_texts(
    *feedbacks
):

    result = []

    for feedback in feedbacks:

        feedback = str(
            feedback or ""
        ).strip()

        if (
            feedback
            and
            feedback not in result
        ):

            result.append(
                feedback
            )

    return "\n\n".join(
        result
    )


# ==========================================
# OSTATNIE PYTANIE NELE
# ==========================================

def extract_last_question(
    answer
):

    if not answer:
        return None

    questions = re.findall(
        r'[^.!?\n]*\?',
        str(
            answer
        ).strip()
    )

    if not questions:
        return None

    question = questions[
        -1
    ].strip()

    return question or None


# ==========================================
# ZAPAMIĘTANIE WYPOWIEDZI NELE
# ==========================================

def remember_nele_output(
    answer,
    state
):

    if (
        state is None
        or
        not answer
    ):

        return

    answer = str(
        answer
    ).strip()

    if not answer:
        return

    state[
        "last_nele_message"
    ] = answer

    state[
        "last_nele_question"
    ] = extract_last_question(
        answer
    )


# ==========================================
# ZAPIS STANU
# ==========================================

def return_with_memory(
    answer,
    session_id
):

    try:

        state = get_conversation_state(
            session_id
        )

        remember_nele_output(
            answer,
            state
        )

        save_conversation_state(
            session_id
        )

    except Exception as error:

        print(
            f"Conversation save error: {error}"
        )

    return answer


# ==========================================
# FEEDBACK + ODPOWIEDŹ
# ==========================================

def combine_learner_feedback(
    feedback_text,
    answer
):

    feedback_text = str(
        feedback_text or ""
    ).strip()

    answer = str(
        answer or ""
    ).strip()

    if not feedback_text:
        return answer

    if not answer:
        return feedback_text

    return (
        f"{feedback_text}\n\n"
        f"{answer}"
    )


def return_with_feedback(
    answer,
    feedback_text,
    session_id
):

    return return_with_memory(
        combine_learner_feedback(
            feedback_text,
            answer
        ),
        session_id
    )


# ==========================================
# USUWANIE STAREGO PYTANIA O WYBÓR
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

    return answer[
        :min(
            positions
        )
    ].rstrip()


# ==========================================
# CZYSZCZENIE STAREGO PYTANIA
# O KONTYNUACJĘ
# ==========================================

def clear_old_teacher_choice_state(
    state
):

    if state is None:
        return

    if state.get(
        "last_question"
    ) in {
        "continue_last_activity",
        "continue_error_review"
    }:

        state[
            "last_question"
        ] = None


# ==========================================
# PYTANIE POBOCZNE
# -> POWRÓT DO TRENINGU
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

    continuation = resume_current_training(
        state
    )

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

    return answer or continuation


# ==========================================
# GŁÓWNY ROUTER
# ==========================================

def generate_conversation_reply(
    user_message,
    level="A1",
    lesson=1,
    session_id="default"
):

    # ======================================
    # KILKA PYTAŃ
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
    # STAN
    # ======================================

    state = get_conversation_state(
        session_id
    )


    # ======================================
    # 0. ONBOARDING
    # ======================================

    if not is_onboarding_completed(
        state
    ):

        onboarding_step = get_onboarding_step(
            state
        )

        if onboarding_step > 0:

            answer = handle_onboarding_answer(
                user_message,
                state,
                session_id
            )

            if answer:

                return return_with_memory(
                    answer,
                    session_id
                )

        elif is_new_user(
            state
        ):

            return return_with_memory(
                generate_welcome_reply(
                    session_id
                ),
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
    # 1. POWTÓRKI BŁĘDÓW
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
    # 2. SAMOPOCZUCIE
    #
    # Logika znajduje się teraz w:
    #
    # conversation_wellbeing.py
    #
    # Musi być przed pamięcią użytkownika,
    # żeby np.:
    #
    # Ich bin müde.
    #
    # nie zostało potraktowane jako imię.
    # ======================================

    (
        wellbeing_handled,
        wellbeing_answer,
        wellbeing_feedback
    ) = handle_wellbeing_reply(
        user_message,
        state
    )

    if wellbeing_handled:

        return return_with_feedback(
            wellbeing_answer,
            wellbeing_feedback,
            session_id
        )


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
    # 4A. AKTYWNE FEHLERTRAINING
    #
    # Logika:
    #
    # conversation_error_training.py
    #
    # Fehlertraining ma pierwszeństwo
    # przed komendami rozmowy.
    # ======================================

    (
        handled,
        answer
    ) = handle_priority_error_practice(
        processed_message,
        state
    )

    if handled:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 4B. POWTÓRZ
    # ======================================

    (
        handled,
        answer,
        command_feedback
    ) = handle_repeat_request(
        processed_message,
        state
    )

    if handled:

        return return_with_feedback(
            answer,
            merge_feedback_texts(
                feedback_text,
                command_feedback
            ),
            session_id
        )


    # ======================================
    # 4C. WRÓĆ DO TRENINGU
    # ======================================

    (
        handled,
        answer,
        command_feedback
    ) = handle_return_to_training_request(
        processed_message,
        state
    )

    if handled:

        return return_with_feedback(
            answer,
            merge_feedback_texts(
                feedback_text,
                command_feedback
            ),
            session_id
        )


    # ======================================
    # 4D. PYTANIE O ZNACZENIE SŁOWA
    #
    # Logika:
    #
    # conversation_vocabulary.py
    # ======================================

    (
        handled,
        answer,
        vocabulary_feedback
    ) = handle_vocabulary_explanation_request(
        processed_message,
        state
    )

    if handled:

        return return_with_feedback(
            continue_after_side_answer(
                answer,
                state
            ),
            merge_feedback_texts(
                feedback_text,
                vocabulary_feedback
            ),
            session_id
        )


    # ======================================
    # 5A. PAMIĘĆ BŁĘDÓW
    # ======================================

    answer = handle_error_memory(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            continue_after_side_answer(
                answer,
                state
            ),
            feedback_text,
            session_id
        )


    # ======================================
    # 5B. PAMIĘĆ NAUKI
    # ======================================

    answer = handle_memory(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            continue_after_side_answer(
                answer,
                state
            ),
            feedback_text,
            session_id
        )


    # ======================================
    # 6. AKTYWNE FEHLERTRAINING
    #
    # Cała logika znajduje się już w:
    #
    # conversation_error_training.py
    # ======================================

    answer = handle_active_error_practice(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 7. POSTĘP BŁĘDÓW
    # ======================================

    answer = handle_error_progress(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 8. NOWA NAUKA
    # ======================================

    answer = handle_new_learning_resume(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 9. AKTYWNA LEKCJA
    # ======================================

    answer = handle_lesson_teaching(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 10. KONTYNUACJA AKTYWNOŚCI
    # ======================================

    answer = handle_continue_last_activity(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 11. KOREKTA
    # ======================================

    answer = handle_correction(
        processed_message,
        session_id
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 12. ALFABET
    # ======================================

    answer = handle_alphabet(
        processed_message,
        level,
        lesson
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 13. POSTĘP LEKCJI
    # ======================================

    answer = handle_lesson_progress(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 14. PERSONALIZACJA
    # ======================================

    answer = handle_personalization(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 15. PAMIĘĆ UŻYTKOWNIKA
    # ======================================

    answer = handle_user_memory(
        processed_message,
        session_id
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 16. PAMIĘĆ BŁĘDÓW – FALLBACK
    # ======================================

    answer = handle_error_memory(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 17. PAMIĘĆ NAUKI – FALLBACK
    # ======================================

    answer = handle_memory(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 18. TEMAT
    # ======================================

    answer = handle_topic_follow_up(
        processed_message,
        session_id
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 19. PORÓWNANIA
    # ======================================

    answer = handle_comparison(
        processed_message,
        state,
        session_id
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 20. SŁOWNICTWO
    # ======================================

    was_active = (
        is_vocabulary_practice_active(
            state
        )
    )

    answer = handle_vocabulary(
        processed_message,
        state
    )

    if answer:

        if (
            was_active
            and
            not is_vocabulary_practice_active(
                state
            )
        ):

            answer = (
                continue_after_finished_training(
                    answer,
                    state
                )
            )

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 21. INTENCJE
    # ======================================

    answer = handle_intent(
        processed_message,
        session_id
    )

    if answer:

        remember_current_topic(
            processed_message,
            session_id
        )

        remember_current_comparison(
            processed_message,
            session_id
        )

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 22. ZNANE PYTANIA
    # ======================================

    answer = find_response(
        processed_message,
        level,
        lesson,
        session_id
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 23. KONTEKST
    # ======================================

    answer = handle_context(
        processed_message,
        session_id
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 24. FALLBACK
    # ======================================

    return return_with_feedback(
        (
            "Ich habe dich verstanden, "
            "aber diese Antwort habe ich "
            "noch nicht gelernt."
        ),
        feedback_text,
        session_id
    )
