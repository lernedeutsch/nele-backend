# ==========================================
# NELE – KONTYNUACJA ROZMOWY I TRENINGU
# TEACHER MODE
# ==========================================

from brain.logic.activity_resume import (
    resume_current_training
)

from brain.logic.response_engine import (
    create_teacher_directed_follow_up
)


# ==========================================
# USUNIĘCIE STAREGO PYTANIA
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

    return answer[
        :min(
            positions
        )
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
# -> POWRÓT DO AKTUALNEGO TRENINGU
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
# ZAKOŃCZONE ĆWICZENIE
# -> KOLEJNY KROK NAUKI
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
