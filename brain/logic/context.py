# ==========================================
# NELE – ODPOWIEDZI KONTEKSTOWE
# ==========================================

from brain.logic.memory import get_conversation_state
from brain.logic.matcher import (
    normalize,
    clean_short_answer,
    capitalize_value
)


def handle_context_answer(
    user_message,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    last_question = state.get(
        "last_question"
    )

    if not last_question:
        return None

    answer = clean_short_answer(
        user_message
    )

    if not answer:
        return None

    normalized_answer = normalize(
        answer
    )

    # Nie traktujemy pytania użytkownika
    # jako odpowiedzi na wcześniejsze pytanie Nele.

    if (
        normalized_answer.startswith("wie ")
        or normalized_answer.startswith("was ")
        or normalized_answer.startswith("wo ")
        or normalized_answer.startswith("wer ")
        or normalized_answer.startswith("wann ")
        or normalized_answer.startswith("warum ")
    ):
        return None


    # ======================================
    # IMIĘ
    # ======================================

    if last_question == "name":

        if len(answer.split()) > 4:
            return None

        answer = capitalize_value(
            answer
        )

        state["name"] = answer
        state["last_question"] = "origin"

        return (
            f"Freut mich, {answer}. "
            f"Woher kommst du?"
        )


    # ======================================
    # POCHODZENIE
    # ======================================

    if last_question == "origin":

        origin = answer

        if normalized_answer.startswith(
            "aus "
        ):
            origin = answer[4:].strip()

        origin = capitalize_value(
            origin
        )

        state["origin"] = origin
        state["last_question"] = "residence"

        return (
            f"Schön. "
            f"Du kommst aus {origin}. "
            f"Wo wohnst du jetzt?"
        )


    # ======================================
    # MIEJSCE ZAMIESZKANIA
    # ======================================

    if last_question == "residence":

        residence = answer

        if normalized_answer.startswith(
            "in "
        ):
            residence = answer[3:].strip()

        residence = capitalize_value(
            residence
        )

        state["residence"] = residence
        state["last_question"] = None

        name = state.get(
            "name"
        )

        if name:
            return (
                f"Ah, {name}, "
                f"du wohnst in {residence}. "
                f"Schön!"
            )

        return (
            f"Ah, du wohnst in "
            f"{residence}. Schön!"
        )


    # ======================================
    # SAMOPOCZUCIE
    # ======================================

    if last_question == "wellbeing":

        state["last_question"] = None

        if normalized_answer in [
            "gut",
            "sehr gut",
            "mir geht es gut",
            "mir gehts gut"
        ]:
            return (
                "Das freut mich! "
                "Was möchtest du heute üben?"
            )

        if normalized_answer in [
            "nicht gut",
            "schlecht",
            "mir geht es nicht gut",
            "mir gehts nicht gut"
        ]:
            return (
                "Das tut mir leid. "
                "Möchtest du trotzdem "
                "ein bisschen Deutsch üben?"
            )

        return (
            "Danke, dass du mir das sagst."
        )

    return None
