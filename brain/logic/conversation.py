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

from brain.logic.error_practice import (
    handle_error_practice,
    is_error_practice_active,
    is_first_answer,
    is_second_answer,
    wants_to_stop_error_practice,
    clean_error_practice_message
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

from brain.logic.conversation_commands import (
    handle_repeat_request,
    handle_return_to_training_request
)

from brain.memory.review import (
    handle_memory
)

from brain.memory.error_review import (
    refresh_error_reviews
)

from brain.memory.error_memory import (
    remember_error,
    get_error_summary
)


# ==========================================
# FEEDBACK
# ==========================================

def merge_feedback_texts(*feedbacks):

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

def extract_last_question(answer):

    if not answer:
        return None

    questions = re.findall(
        r'[^.!?\n]*\?',
        str(answer).strip()
    )

    if not questions:
        return None

    question = questions[-1].strip()

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
# ZAPAMIĘTANIE BŁĘDU JĘZYKOWEGO
# DLA PYTAŃ O SŁOWA
# ==========================================

def remember_special_language_error(
    state,
    wrong_text,
    correct_text,
    error_type="grammar"
):

    if state is None:
        return

    wrong_text = str(
        wrong_text or ""
    ).strip()

    correct_text = str(
        correct_text or ""
    ).strip()

    if (
        not wrong_text
        or
        not correct_text
    ):

        return

    try:

        remember_error(
            state,
            error_type,
            wrong_text,
            correct_text
        )

    except Exception as error:

        print(
            f"Special language error memory: {error}"
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

    positions = [
        answer.find(prompt)
        for prompt in old_prompts
        if answer.find(prompt) >= 0
    ]

    if not positions:
        return answer

    return answer[
        :min(positions)
    ].rstrip()


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
# KONIEC ĆWICZENIA
# -> NASTĘPNY KROK
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

    return answer or continuation


# ==========================================
# PRIORYTET AKTYWNEGO FEHLERTRAINING
# ==========================================

def should_prioritize_error_practice(
    user_message,
    state
):

    if (
        state is None
        or
        not is_error_practice_active(
            state
        )
    ):

        return False

    if wants_to_stop_error_practice(
        user_message
    ):

        return True

    if (
        is_first_answer(
            user_message
        )
        or
        is_second_answer(
            user_message
        )
    ):

        return True

    error_type = state.get(
        "error_practice_type"
    )

    if not error_type:
        return False

    try:

        summary = get_error_summary(
            state,
            error_type
        )

    except Exception as error:

        print(
            f"Error practice priority: {error}"
        )

        return False

    if not isinstance(
        summary,
        dict
    ):

        return False

    user_clean = clean_error_practice_message(
        user_message
    )

    wrong_clean = clean_error_practice_message(
        summary.get(
            "last_wrong"
        )
    )

    correct_clean = clean_error_practice_message(
        summary.get(
            "last_correct"
        )
    )

    return bool(
        user_clean
        and
        user_clean in {
            wrong_clean,
            correct_clean
        }
    )


def handle_priority_error_practice(
    user_message,
    state
):

    if not should_prioritize_error_practice(
        user_message,
        state
    ):

        return (
            False,
            None
        )

    was_active = is_error_practice_active(
        state
    )

    answer = handle_error_practice(
        user_message,
        state
    )

    if not answer:

        return (
            False,
            None
        )

    is_still_active = (
        is_error_practice_active(
            state
        )
    )

    if (
        was_active
        and
        not is_still_active
    ):

        answer = (
            continue_after_finished_training(
                answer,
                state
            )
        )

    return (
        True,
        answer
    )


# ==========================================
# PYTANIA O ZNACZENIE SŁOWA
# ==========================================

def clean_vocabulary_target(
    target
):

    target = str(
        target or ""
    ).strip()

    target = target.strip(
        " .?!„“\"'"
    )

    target = re.sub(
        r"\s+",
        " ",
        target
    )

    if target.lower().startswith(
        "das wort "
    ):

        target = target[
            len("das wort "):
        ].strip()

    return target


def display_target_word(
    target
):

    target = clean_vocabulary_target(
        target
    )

    if not target:
        return ""

    return (
        target[:1].upper()
        + target[1:]
    )


def build_vocabulary_analysis(
    target,
    feedback=None,
    corrected=None,
    error_type=None
):

    target = clean_vocabulary_target(
        target
    )

    if not target:

        return {
            "recognized":
                False
        }

    return {
        "recognized":
            True,

        "target":
            target,

        "canonical":
            (
                "Was bedeutet das Wort "
                f"{target}?"
            ),

        "feedback":
            feedback,

        "corrected":
            corrected,

        "error_type":
            error_type
    }


def analyze_vocabulary_explanation_request(
    user_message
):

    text = str(
        user_message or ""
    ).strip()

    if not text:

        return {
            "recognized":
                False
        }


    # Was bedeutet Zimmer?

    match = re.match(
        (
            r"^\s*was\s+bedeutet\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        return build_vocabulary_analysis(
            match.group(1)
        )


    # Was heißt Zimmer?

    match = re.match(
        (
            r"^\s*was\s+heißt\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        return build_vocabulary_analysis(
            match.group(1)
        )


    # Was heisst Zimmer?

    match = re.match(
        (
            r"^\s*was\s+heisst\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        corrected = (
            "Was heißt "
            f"{display_target_word(target)}?"
        )

        return build_vocabulary_analysis(
            target,
            (
                "Fast! Richtig schreibt man: "
                f"„{corrected}“"
            ),
            corrected,
            "spelling"
        )


    # Was bedeuten Zimmer?

    match = re.match(
        (
            r"^\s*was\s+bedeuten\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        corrected = (
            "Was bedeutet "
            f"{display_target_word(target)}?"
        )

        return build_vocabulary_analysis(
            target,
            (
                "Fast! Richtig sagt man: "
                f"„{corrected}“"
            ),
            corrected,
            "grammar"
        )


    # Was ist bedeutet Zimmer?

    match = re.match(
        (
            r"^\s*was\s+ist\s+bedeutet\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        corrected = (
            "Was bedeutet "
            f"{display_target_word(target)}?"
        )

        return build_vocabulary_analysis(
            target,
            (
                "Fast! Richtig sagt man: "
                f"„{corrected}“"
            ),
            corrected,
            "grammar"
        )


    # Kannst du mir Zimmer erklären?

    match = re.match(
        (
            r"^\s*kannst\s+du\s+mir\s+"
            r"(?:bitte\s+)?"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s+erklären\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        return build_vocabulary_analysis(
            match.group(1)
        )


    # Kannst du bitte Zimmer erklären?

    match = re.match(
        (
            r"^\s*kannst\s+du\s+bitte\s+"
            r"(?:mir\s+)?"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s+erklären\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        return build_vocabulary_analysis(
            match.group(1)
        )


    # Kannst du mir Zimmer bitte erklären?

    match = re.match(
        (
            r"^\s*kannst\s+du\s+mir\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s+bitte\s+erklären"
            r"\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        return build_vocabulary_analysis(
            match.group(1)
        )


    # Kannst du mir Zimmer erkläre?

    match = re.match(
        (
            r"^\s*kannst\s+du\s+"
            r"(?:mir\s+|bitte\s+mir\s+|bitte\s+)?"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s+erkläre\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        corrected = (
            "Kannst du mir "
            f"{display_target_word(target)} "
            "erklären?"
        )

        return build_vocabulary_analysis(
            target,
            (
                "Fast! Nach „kannst“ "
                "steht der Infinitiv: "
                f"„{corrected}“"
            ),
            corrected,
            "grammar"
        )


    # Kannst du mir erklären Zimmer?

    match = re.match(
        (
            r"^\s*kannst\s+du\s+mir\s+"
            r"erklären\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        corrected = (
            "Kannst du mir "
            f"{display_target_word(target)} "
            "erklären?"
        )

        return build_vocabulary_analysis(
            target,
            (
                "Fast! Natürlicher sagt man: "
                f"„{corrected}“"
            ),
            corrected,
            "word_order"
        )


    return {
        "recognized":
            False
    }


def handle_vocabulary_explanation_request(
    user_message,
    state
):

    analysis = (
        analyze_vocabulary_explanation_request(
            user_message
        )
    )

    if not analysis.get(
        "recognized",
        False
    ):

        return (
            False,
            None,
            None
        )

    canonical = analysis.get(
        "canonical"
    )

    feedback = analysis.get(
        "feedback"
    )

    corrected = analysis.get(
        "corrected"
    )

    error_type = analysis.get(
        "error_type"
    )

    if (
        corrected
        and
        error_type
    ):

        remember_special_language_error(
            state,
            user_message,
            corrected,
            error_type
        )

    vocabulary_active = (
        is_vocabulary_practice_active(
            state
        )
    )

    saved_vocabulary_state = None

    if vocabulary_active:

        saved_vocabulary_state = {
            "vocabulary_practice_active":
                state.get(
                    "vocabulary_practice_active"
                ),

            "vocabulary_practice_word":
                state.get(
                    "vocabulary_practice_word"
                ),

            "vocabulary_practice_type":
                state.get(
                    "vocabulary_practice_type"
                ),

            "last_activity":
                state.get(
                    "last_activity"
                ),

            "last_activity_detail":
                state.get(
                    "last_activity_detail"
                )
        }

        state[
            "vocabulary_practice_active"
        ] = False

    answer = handle_vocabulary(
        canonical,
        state
    )

    if saved_vocabulary_state is not None:

        for key, value in (
            saved_vocabulary_state.items()
        ):

            state[
                key
            ] = value

    if not answer:

        return (
            False,
            None,
            feedback
        )

    return (
        True,
        answer,
        feedback
    )


# ==========================================
# SAMOPOCZUCIE
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

        return (
            f"{reaction}"
            f"{continuation_answer[len(short_reaction):]}"
        )

    return (
        f"{reaction} "
        f"{continuation_answer}"
    )


def handle_wellbeing_reply(
    user_message,
    state,
    session_id
):

    if (
        state is None
        or
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
    # ======================================

    answer = handle_wellbeing_reply(
        user_message,
        state,
        session_id
    )

    if answer:
        return answer


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
    # 4A. POWTÓRZ
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
    # 4B. WRÓĆ DO TRENINGU
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
    # 4C. ODPOWIEDŹ NA FEHLERTRAINING
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
    # 4D. PYTANIE O SŁOWO
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
    # ======================================

    was_active = is_error_practice_active(
        state
    )

    answer = handle_error_practice(
        processed_message,
        state
    )

    if answer:

        if (
            was_active
            and
            not is_error_practice_active(
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
