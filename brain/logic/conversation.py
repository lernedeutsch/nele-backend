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
# ŁĄCZENIE FEEDBACKU
# ==========================================

def merge_feedback_texts(
    *feedbacks
):

    result = []

    for feedback in feedbacks:

        feedback = str(
            feedback or ""
        ).strip()

        if not feedback:
            continue

        if feedback in result:
            continue

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

    text = str(
        answer
    ).strip()

    if not text:
        return None

    questions = re.findall(
        r'[^.!?\n]*\?',
        text
    )

    if not questions:
        return None

    question = questions[-1].strip()

    if not question:
        return None

    return question


# ==========================================
# ZAPAMIĘTANIE OSTATNIEJ WYPOWIEDZI NELE
# ==========================================

def remember_nele_output(
    answer,
    state
):

    if state is None:
        return

    if not answer:
        return

    answer = str(
        answer
    ).strip()

    if not answer:
        return


    state[
        "last_nele_message"
    ] = answer


    question = extract_last_question(
        answer
    )


    if question:

        state[
            "last_nele_question"
        ] = question

    else:

        state[
            "last_nele_question"
        ] = None


# ==========================================
# ZAPIS STANU I ZWROT ODPOWIEDZI
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
# POŁĄCZENIE FEEDBACKU Z ODPOWIEDZIĄ
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
# ZAPAMIĘTANIE SPECJALNEGO BŁĘDU
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

    if not wrong_text:
        return

    if not correct_text:
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
# CZYSZCZENIE TEKSTU POLECENIA
# ==========================================

def clean_control_message(
    text
):

    text = str(
        text or ""
    ).strip().lower()

    text = text.strip(
        " .?!„“\"'"
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


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
# PYTANIE POBOCZNE
# + POWRÓT DO TRENINGU
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

    if answer:
        return answer

    return continuation


# ==========================================
# ZAKOŃCZONE ĆWICZENIE
# -> AUTOMATYCZNY KOLEJNY KROK
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
# CZY WIADOMOŚĆ JEST ODPOWIEDZIĄ
# NA AKTYWNE FEHLERTRAINING
# ==========================================
#
# To jest kluczowa poprawka.
#
# Jeżeli Nele właśnie ćwiczy błąd:
#
# 1. Was bedeuten Zimmer?
# 2. Was bedeutet Zimmer?
#
# i użytkownik wpisze:
#
# Was bedeutet Zimmer?
#
# zdanie MUSI trafić najpierw
# do Fehlertraining.
#
# Nie może zostać potraktowane jako nowe:
#
# "Was bedeutet Zimmer?"
# ==========================================

def should_prioritize_error_practice(
    user_message,
    state
):

    if state is None:
        return False


    if not is_error_practice_active(
        state
    ):

        return False


    # ======================================
    # STOP
    # ======================================

    if wants_to_stop_error_practice(
        user_message
    ):

        return True


    # ======================================
    # ODPOWIEDZI 1 / 2
    # ======================================

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


    wrong_sentence = summary.get(
        "last_wrong"
    )

    correct_sentence = summary.get(
        "last_correct"
    )


    user_clean = clean_error_practice_message(
        user_message
    )

    wrong_clean = clean_error_practice_message(
        wrong_sentence
    )

    correct_clean = clean_error_practice_message(
        correct_sentence
    )


    # ======================================
    # JEŻELI TO JEDNO Z DWÓCH ZDAŃ
    # Z AKTUALNEGO ĆWICZENIA,
    # Fehlertraining ma pierwszeństwo.
    # ======================================

    if (
        user_clean
        and
        (
            user_clean == correct_clean
            or
            user_clean == wrong_clean
        )
    ):

        return True


    return False


# ==========================================
# OBSŁUGA ODPOWIEDZI,
# KTÓRA NALEŻY DO FEHLERTRAINING
# ==========================================

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


    # ======================================
    # ĆWICZENIE WŁAŚNIE SIĘ ZAKOŃCZYŁO
    # ======================================

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

    lower_target = target.lower()

    if lower_target.startswith(
        "das wort "
    ):

        target = target[
            len("das wort "):
        ].strip()

    return target


# ==========================================
# ŁADNA FORMA SŁOWA
# ==========================================

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


# ==========================================
# ROZPOZNANIE PYTANIA O SŁOWO
# ==========================================

def analyze_vocabulary_explanation_request(
    user_message
):

    text = str(
        user_message or ""
    ).strip()

    if not text:

        return {
            "recognized": False
        }


    # ======================================
    # WAS BEDEUTET...
    # ======================================

    match = re.match(
        r"^\s*was\s+bedeutet\s+(?:das\s+wort\s+)?(.+?)\s*[?.!]*\s*$",
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        if target:

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
                    None,

                "corrected":
                    None,

                "error_type":
                    None
            }


    # ======================================
    # WAS HEIẞT...
    # ======================================

    match = re.match(
        r"^\s*was\s+heißt\s+(?:das\s+wort\s+)?(.+?)\s*[?.!]*\s*$",
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        if target:

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
                    None,

                "corrected":
                    None,

                "error_type":
                    None
            }


    # ======================================
    # HEISST ZAMIAST HEIẞT
    # ======================================

    match = re.match(
        r"^\s*was\s+heisst\s+(?:das\s+wort\s+)?(.+?)\s*[?.!]*\s*$",
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        display_target = display_target_word(
            target
        )

        corrected = (
            f"Was heißt {display_target}?"
        )

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
                (
                    "Fast! Richtig schreibt man: "
                    f"„{corrected}“"
                ),

            "corrected":
                corrected,

            "error_type":
                "spelling"
        }


    # ======================================
    # BEDEUTEN ZAMIAST BEDEUTET
    # ======================================

    match = re.match(
        r"^\s*was\s+bedeuten\s+(?:das\s+wort\s+)?(.+?)\s*[?.!]*\s*$",
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        display_target = display_target_word(
            target
        )

        corrected = (
            f"Was bedeutet {display_target}?"
        )

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
                (
                    "Fast! Richtig sagt man: "
                    f"„{corrected}“"
                ),

            "corrected":
                corrected,

            "error_type":
                "grammar"
        }


    # ======================================
    # WAS IST BEDEUTET...
    # ======================================

    match = re.match(
        r"^\s*was\s+ist\s+bedeutet\s+(?:das\s+wort\s+)?(.+?)\s*[?.!]*\s*$",
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        display_target = display_target_word(
            target
        )

        corrected = (
            f"Was bedeutet {display_target}?"
        )

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
                (
                    "Fast! Richtig sagt man: "
                    f"„{corrected}“"
                ),

            "corrected":
                corrected,

            "error_type":
                "grammar"
        }


    # ======================================
    # KANNST DU MIR ... ERKLÄREN?
    # ======================================

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

        target = clean_vocabulary_target(
            match.group(1)
        )

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
                None,

            "corrected":
                None,

            "error_type":
                None
        }


    # ======================================
    # KANNST DU BITTE ... ERKLÄREN?
    # ======================================

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

        target = clean_vocabulary_target(
            match.group(1)
        )

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
                None,

            "corrected":
                None,

            "error_type":
                None
        }


    # ======================================
    # KANNST DU MIR ...
    # BITTE ERKLÄREN?
    # ======================================

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

        target = clean_vocabulary_target(
            match.group(1)
        )

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
                None,

            "corrected":
                None,

            "error_type":
                None
        }


    # ======================================
    # ERKLÄRE ZAMIAST ERKLÄREN
    # ======================================

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

        display_target = display_target_word(
            target
        )

        corrected = (
            "Kannst du mir "
            f"{display_target} erklären?"
        )

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
                (
                    "Fast! Nach „kannst“ "
                    "steht der Infinitiv: "
                    f"„{corrected}“"
                ),

            "corrected":
                corrected,

            "error_type":
                "grammar"
        }


    # ======================================
    # FALSCHE WORTSTELLUNG
    # ======================================

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

        display_target = display_target_word(
            target
        )

        corrected = (
            "Kannst du mir "
            f"{display_target} erklären?"
        )

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
                (
                    "Fast! Natürlicher sagt man: "
                    f"„{corrected}“"
                ),

            "corrected":
                corrected,

            "error_type":
                "word_order"
        }


    return {
        "recognized":
            False
    }


# ==========================================
# ODPOWIEDŹ NA PYTANIE O SŁOWO
# ==========================================

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

        for (
            key,
            value
        ) in saved_vocabulary_state.items():

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
# PROŚBA O POWTÓRZENIE
# ==========================================

def analyze_repeat_request(
    user_message
):

    message = clean_control_message(
        user_message
    )


    correct_requests = {

        "kannst du bitte wiederholen",
        "kannst du das bitte wiederholen",
        "kannst du es bitte wiederholen",
        "kannst du bitte noch einmal wiederholen",
        "kannst du die frage bitte wiederholen",
        "kannst du die frage wiederholen",
        "bitte wiederholen",
        "bitte noch einmal",
        "noch einmal bitte",
        "noch mal bitte",
        "nochmal bitte",
        "wiederhole bitte",
        "kannst du das noch einmal sagen",
        "kannst du das noch mal sagen"
    }


    if message in correct_requests:

        return {

            "recognized":
                True,

            "question_only":
                (
                    "frage"
                    in message
                ),

            "feedback":
                None,

            "corrected":
                None,

            "error_type":
                None
        }


    wrong_repeat_patterns = {

        "kannst du bitte wiederhole":
            "Kannst du bitte wiederholen?",

        "kannst du das bitte wiederhole":
            "Kannst du das bitte wiederholen?",

        "kannst du die frage bitte wiederhole":
            "Kannst du die Frage bitte wiederholen?",

        "kanst du bitte wiederholen":
            "Kannst du bitte wiederholen?",

        "kanst du das bitte wiederholen":
            "Kannst du das bitte wiederholen?"
    }


    if message in wrong_repeat_patterns:

        corrected = (
            wrong_repeat_patterns[
                message
            ]
        )


        return {

            "recognized":
                True,

            "question_only":
                (
                    "frage"
                    in message
                ),

            "feedback":
                (
                    "Fast! Richtig sagt man: "
                    f"„{corrected}“"
                ),

            "corrected":
                corrected,

            "error_type":
                "grammar"
        }


    return {
        "recognized":
            False
    }


# ==========================================
# POWTÓRZENIE OSTATNIEJ WYPOWIEDZI
# ==========================================

def handle_repeat_request(
    user_message,
    state
):

    analysis = analyze_repeat_request(
        user_message
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


    if analysis.get(
        "question_only",
        False
    ):

        repeated = state.get(
            "last_nele_question"
        )

        if not repeated:

            repeated = state.get(
                "last_nele_message"
            )

    else:

        repeated = state.get(
            "last_nele_message"
        )


    if not repeated:

        repeated = resume_current_training(
            state
        )


    if not repeated:

        repeated = (
            "Ich habe gerade noch nichts "
            "zum Wiederholen."
        )


    return (
        True,
        repeated,
        feedback
    )


# ==========================================
# WRÓĆMY DO TRENINGU
# ==========================================

def analyze_return_to_training_request(
    user_message
):

    message = clean_control_message(
        user_message
    )


    correct_requests = {

        "zurück zum training",
        "zuruck zum training",

        "zurück zur übung",
        "zuruck zur ubung",

        "zurück zur lektion",
        "zuruck zur lektion",

        "gehen wir zurück zum training",
        "gehen wir zuruck zum training",

        "lass uns zum training zurückgehen",
        "lass uns zum training zuruckgehen",

        "lass uns zurück zum training gehen",
        "lass uns zuruck zum training gehen",

        "machen wir mit dem training weiter",
        "wir machen mit dem training weiter",

        "weiter mit dem training",
        "machen wir weiter",
        "wir machen weiter",

        "weiter bitte",
        "bitte weiter",
        "weiter"
    }


    if message in correct_requests:

        return {

            "recognized":
                True,

            "feedback":
                None,

            "corrected":
                None,

            "error_type":
                None
        }


    wrong_requests = {

        "zurück zu training":
            "Zurück zum Training.",

        "zuruck zu training":
            "Zurück zum Training.",

        "gehen wir zurück zu training":
            "Gehen wir zurück zum Training.",

        "gehen wir zuruck zu training":
            "Gehen wir zurück zum Training.",

        "lass uns zurück zu training gehen":
            "Lass uns zum Training zurückgehen.",

        "lass uns zuruck zu training gehen":
            "Lass uns zum Training zurückgehen.",

        "machen wir weiter mit training":
            "Machen wir mit dem Training weiter.",

        "wir machen weiter mit training":
            "Wir machen mit dem Training weiter.",

        "zurück in training":
            "Zurück zum Training."
    }


    if message in wrong_requests:

        corrected = wrong_requests[
            message
        ]


        return {

            "recognized":
                True,

            "feedback":
                (
                    "Fast! Richtig sagt man: "
                    f"„{corrected}“"
                ),

            "corrected":
                corrected,

            "error_type":
                "preposition"
        }


    return {
        "recognized":
            False
    }


# ==========================================
# OBSŁUGA:
# WRÓĆMY DO TRENINGU
# ==========================================

def handle_return_to_training_request(
    user_message,
    state
):

    analysis = (
        analyze_return_to_training_request(
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


    if continuation:

        answer = (
            "Gerne. Wir machen weiter.\n\n"
            f"{continuation}"
        )

    else:

        answer = (
            "Gerne. Wir machen weiter."
        )


    return (
        True,
        answer,
        feedback
    )


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

            welcome_answer = (
                generate_welcome_reply(
                    session_id
                )
            )


            return return_with_memory(
                welcome_answer,
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
    # 4A. POWTÓRZ
    # ======================================

    (
        repeat_handled,
        repeat_answer,
        repeat_feedback
    ) = handle_repeat_request(
        processed_message,
        state
    )


    if repeat_handled:

        final_feedback = merge_feedback_texts(
            feedback_text,
            repeat_feedback
        )


        return return_with_feedback(
            repeat_answer,
            final_feedback,
            session_id
        )


    # ======================================
    # 4B. WRÓĆ DO TRENINGU
    # ======================================

    (
        return_handled,
        return_answer,
        return_feedback
    ) = handle_return_to_training_request(
        processed_message,
        state
    )


    if return_handled:

        final_feedback = merge_feedback_texts(
            feedback_text,
            return_feedback
        )


        return return_with_feedback(
            return_answer,
            final_feedback,
            session_id
        )


    # ======================================
    # 4C. ODPOWIEDŹ NA AKTYWNE
    # FEHLERTRAINING
    #
    # MUSI BYĆ PRZED:
    #
    # Was bedeutet...?
    #
    # ======================================

    (
        priority_error_handled,
        priority_error_answer
    ) = handle_priority_error_practice(
        processed_message,
        state
    )


    if priority_error_handled:

        return return_with_feedback(
            priority_error_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 4D. PYTANIE O ZNACZENIE SŁOWA
    # ======================================

    (
        vocabulary_question_handled,
        vocabulary_question_answer,
        vocabulary_question_feedback
    ) = handle_vocabulary_explanation_request(
        processed_message,
        state
    )


    if vocabulary_question_handled:

        teacher_answer = (
            continue_after_side_answer(
                vocabulary_question_answer,
                state
            )
        )


        final_feedback = merge_feedback_texts(
            feedback_text,
            vocabulary_question_feedback
        )


        return return_with_feedback(
            teacher_answer,
            final_feedback,
            session_id
        )


    # ======================================
    # 5A. PYTANIA O BŁĘDY
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
    # 5B. PYTANIA O PAMIĘĆ NAUKI
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
    # 6. AKTYWNE FEHLERTRAINING
    #
    # Tutaj trafiają inne odpowiedzi,
    # które nie były pytaniem pobocznym.
    # ======================================

    error_practice_was_active = (
        is_error_practice_active(
            state
        )
    )


    error_practice_answer = (
        handle_error_practice(
            processed_message,
            state
        )
    )


    if error_practice_answer:

        error_practice_is_still_active = (
            is_error_practice_active(
                state
            )
        )


        # ==================================
        # WŁAŚNIE ZAKOŃCZONO BŁĄD
        # ==================================

        if (
            error_practice_was_active
            and
            not error_practice_is_still_active
        ):

            teacher_answer = (
                continue_after_finished_training(
                    error_practice_answer,
                    state
                )
            )


            return return_with_feedback(
                teacher_answer,
                feedback_text,
                session_id
            )


        return return_with_feedback(
            error_practice_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 7. POSTĘP W BŁĘDACH
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
    # 8. KONTYNUACJA NOWEJ NAUKI
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
    # 9. AKTYWNA LEKCJA
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
    # 10. STARA KONTYNUACJA
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
    # 11. KOREKTA
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
    # 12. ALFABET
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
    # 13. POSTĘP LEKCJI
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
    # 14. PERSONALIZACJA
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
    # 15. PAMIĘĆ UŻYTKOWNIKA
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
    # 16. PAMIĘĆ BŁĘDÓW
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
    # 17. PAMIĘĆ NAUKI
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
    # 18. TEMAT
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
    # 19. PORÓWNANIA
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
    # 20. SŁOWNICTWO
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


        return return_with_feedback(
            vocabulary_answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 21. INTENCJE
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
    # 22. ZNANE PYTANIA
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
    # 23. KONTEKST
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
    # 24. FALLBACK
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
