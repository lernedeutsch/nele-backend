from brain.logic.memory import get_conversation_state
from brain.logic.matcher import normalize


# ==========================================
# PYTANIA O ZAPAMIĘTANE INFORMACJE
# ==========================================

def answer_from_memory(
    user_message,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    message = normalize(
        user_message
    )


    # ======================================
    # IMIĘ
    # ======================================

    if message in [
        "wie heiße ich",
        "wie heisse ich",
        "was ist mein name"
    ]:

        name = state.get(
            "name"
        )

        if name:

            return (
                f"Du heißt {name}."
            )

        state[
            "last_question"
        ] = "name"

        return (
            "Das weiß ich noch nicht. "
            "Wie heißt du?"
        )


    # ======================================
    # POCHODZENIE
    # ======================================

    if message in [
        "woher komme ich",
        "aus welchem land komme ich"
    ]:

        origin = state.get(
            "origin"
        )

        if origin:

            return (
                f"Du kommst aus {origin}."
            )

        state[
            "last_question"
        ] = "origin"

        return (
            "Das weiß ich noch nicht. "
            "Woher kommst du?"
        )


    # ======================================
    # MIEJSCE ZAMIESZKANIA
    # ======================================

    if message in [
        "wo wohne ich",
        "wo lebe ich",
        "in welcher stadt wohne ich"
    ]:

        residence = state.get(
            "residence"
        )

        if residence:

            return (
                f"Du wohnst in {residence}."
            )

        state[
            "last_question"
        ] = "residence"

        return (
            "Das weiß ich noch nicht. "
            "Wo wohnst du?"
        )


    return None
