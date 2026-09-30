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
        # A returning-course wellbeing question is optional small talk, not a
        # gate that may trap the learner forever. If the learner answers with a
        # clear course utterance or simply wants to continue ("ja"), release
        # the gate and let the normal course router own this same turn.
        text = str(user_message or "").strip()
        normalized = text.lower().strip(" .?!„“\\\"'")
        course_mode = str((state or {}).get("conversation_mode") or "").strip().lower() == "course"
        course_continuation = normalized in {
            "ja", "ja gern", "ja gerne", "gerne", "gern", "okay", "ok", "weiter"
        }
        looks_like_course_utterance = bool(
            len(normalized.split()) >= 3
            or "?" in text
        )

        if course_mode and (course_continuation or looks_like_course_utterance):
            state["last_question"] = None
            return (False, None, None)

        return (
            True,
            (
                "Ich habe dich noch nicht ganz verstanden. "
                "Wie geht es dir? Zum Beispiel: „Gut.“"
            ),
            None
        )


    reaction = analysis.get(
        "reaction"
    )

    feedback = analysis.get(
        "feedback"
    )


    # Odpowiedź na "Wie geht es dir?" została
    # rozpoznana. Od tej chwili kolejne słowo
    # użytkownika należy już do ćwiczenia,
    # a nie do starego pytania o samopoczucie.
    state[
        "last_question"
    ] = None


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
