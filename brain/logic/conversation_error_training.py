# ==========================================
# NELE – FEHLERTRAINING W ROZMOWIE
# TEACHER MODE
# ==========================================

from brain.logic.error_practice import (
    handle_error_practice,
    is_error_practice_active,
    is_first_answer,
    is_second_answer,
    wants_to_stop_error_practice,
    clean_error_practice_message
)

from brain.logic.response_engine import (
    create_teacher_directed_follow_up
)

from brain.memory.error_memory import (
    get_error_summary
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
# ZAKOŃCZONE FEHLERTRAINING
# -> KOLEJNY KROK NAUKI
# ==========================================

def continue_after_finished_error_training(
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
# CZY FEHLERTRAINING MA PIERWSZEŃSTWO
# ==========================================
#
# Jest to ważne, ponieważ odpowiedź
# w ćwiczeniu może wyglądać jak zwykła
# komenda albo normalne pytanie.
#
# Przykłady:
#
# Kannst du die Frage bitte wiederholen?
#
# Was bedeutet Zimmer?
#
# Jeżeli takie zdanie jest aktualnie
# odpowiedzią w Fehlertraining,
# musi najpierw trafić właśnie tam.
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
    # ODPOWIEDŹ 1 LUB 2
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


    # ======================================
    # TYP AKTUALNEGO BŁĘDU
    # ======================================

    error_type = state.get(
        "error_practice_type"
    )

    if not error_type:
        return False


    # ======================================
    # POBIERAMY OSTATNI BŁĄD
    # ======================================

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


    # ======================================
    # CZYSZCZENIE ZDAŃ
    # ======================================

    user_clean = (
        clean_error_practice_message(
            user_message
        )
    )

    wrong_clean = (
        clean_error_practice_message(
            summary.get(
                "last_wrong"
            )
        )
    )

    correct_clean = (
        clean_error_practice_message(
            summary.get(
                "last_correct"
            )
        )
    )


    # ======================================
    # DOKŁADNE ZDANIE Z ĆWICZENIA
    # ======================================

    return bool(
        user_clean
        and
        user_clean in {
            wrong_clean,
            correct_clean
        }
    )


# ==========================================
# PRIORYTETOWA ODPOWIEDŹ
# NA FEHLERTRAINING
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


    was_active = (
        is_error_practice_active(
            state
        )
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
            continue_after_finished_error_training(
                answer,
                state
            )
        )


    return (
        True,
        answer
    )


# ==========================================
# NORMALNA OBSŁUGA AKTYWNEGO
# FEHLERTRAINING
# ==========================================
#
# Ta funkcja obsługuje pozostałe odpowiedzi,
# które wcześniej nie zostały przechwycone
# przez handle_priority_error_practice().
# ==========================================

def handle_active_error_practice(
    user_message,
    state
):

    was_active = (
        is_error_practice_active(
            state
        )
    )


    answer = handle_error_practice(
        user_message,
        state
    )


    if not answer:
        return None


    is_still_active = (
        is_error_practice_active(
            state
        )
    )


    # ======================================
    # FEHLERTRAINING ZOSTAŁO ZAKOŃCZONE
    # ======================================

    if (
        was_active
        and
        not is_still_active
    ):

        answer = (
            continue_after_finished_error_training(
                answer,
                state
            )
        )


    return answer
