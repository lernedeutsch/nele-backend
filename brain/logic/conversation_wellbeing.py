# ==========================================
# NELE – SAMOPOCZUCIE W ROZMOWIE
# TEACHER MODE
# ==========================================

from brain.logic.wellbeing_feedback import (
    analyze_wellbeing_response
)

from brain.logic.response_engine import (
    create_returning_user_follow_up,
    get_short_answer
)


# ==========================================
# POŁĄCZENIE REAKCJI NA SAMOPOCZUCIE
# Z DALSZYM KROKIEM NAUKI
# ==========================================

def combine_full_wellbeing_reaction(
    reaction,
    continuation_answer
):

    reaction = str(
        reaction or ""
    ).strip()

    continuation_answer = str(
        continuation_answer or ""
    ).strip()


    if not reaction:

        return continuation_answer


    if not continuation_answer:

        return reaction


    # ======================================
    # response_engine może już rozpocząć
    # odpowiedź krótką reakcją:
    #
    # Das freut mich!
    #
    # Nie chcemy wtedy dostać:
    #
    # Das freut mich!
    # Das freut mich! ...
    # ======================================

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
# CZY NELE CZEKA NA ODPOWIEDŹ
# NA PYTANIE:
#
# Wie geht es dir?
# ==========================================

def is_waiting_for_wellbeing(
    state
):

    if state is None:
        return False

    return (
        state.get(
            "last_question"
        )
        ==
        "wellbeing"
    )


# ==========================================
# OBSŁUGA ODPOWIEDZI NA:
#
# Wie geht es dir?
#
# Zwraca:
#
# (
#     handled,
#     answer,
#     feedback
# )
# ==========================================

def handle_wellbeing_reply(
    user_message,
    state
):

    # ======================================
    # NELE NIE CZEKA TERAZ
    # NA ODPOWIEDŹ O SAMOPOCZUCIU
    # ======================================

    if not is_waiting_for_wellbeing(
        state
    ):

        return (
            False,
            None,
            None
        )


    # ======================================
    # ANALIZA ODPOWIEDZI UŻYTKOWNIKA
    #
    # np.
    #
    # Gut
    # Nicht schlecht
    # Ich bin müde
    # Ich bin krank
    # Mir geht gut
    # Gutt
    # ======================================

    analysis = analyze_wellbeing_response(
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


    reaction = analysis.get(
        "reaction"
    )

    feedback = analysis.get(
        "feedback"
    )


    if not reaction:

        return (
            False,
            None,
            feedback
        )


    # ======================================
    # PO REAKCJI NA SAMOPOCZUCIE
    # NELE MA DALEJ PROWADZIĆ NAUKĘ
    #
    # np.
    #
    # Das freut mich!
    # +
    # Wir machen mit ...
    #
    # albo:
    #
    # Verstehe. Dann machen wir heute
    # etwas Kurzes und Leichtes.
    # +
    # Zuletzt waren wir bei ...
    # ======================================

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


    return (
        True,
        final_answer,
        feedback
    )
