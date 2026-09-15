# ==========================================
# NELE – WYJŚCIE ROZMOWY
# TEACHER MODE
# ==========================================

import re

from brain.logic.memory import (
    get_conversation_state,
    save_conversation_state
)


# ==========================================
# ŁĄCZENIE FEEDBACKÓW
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


# ==========================================
# ZWRÓCENIE ODPOWIEDZI Z FEEDBACKIEM
# ==========================================

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
