from brain.logic.memory import get_conversation_state
from brain.logic.matcher import normalize

from brain.memory.user_facts import (
    get_user_fact
)


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
    # ULUBIONE SŁOWO
    # ======================================

    if message in [
        "was ist mein lieblingswort",
        "wie lautet mein lieblingswort",
        "welches ist mein lieblingswort"
    ]:

        favorite_word = get_user_fact(
            state,
            "favorite_word"
        )

        if not favorite_word:
            favorite_word = state.get(
                "favorite_word"
            )

        if favorite_word:

            return (
                f"Dein Lieblingswort ist "
                f"„{favorite_word}“."
            )

        return (
            "Das weiß ich noch nicht. "
            "Was ist dein Lieblingswort?"
        )


    # ======================================
    # ULUBIONY KOLOR
    # ======================================

    if message in [
        "was ist meine lieblingsfarbe",
        "welche ist meine lieblingsfarbe",
        "wie lautet meine lieblingsfarbe"
    ]:

        favorite_color = get_user_fact(
            state,
            "favorite_color"
        )

        if favorite_color:

            return (
                f"Deine Lieblingsfarbe ist "
                f"{favorite_color}."
            )

        return (
            "Das weiß ich noch nicht. "
            "Was ist deine Lieblingsfarbe?"
        )


    # ======================================
    # HOBBY
    # ======================================

    if message in [
        "was ist mein hobby",
        "welches hobby habe ich",
        "wie heißt mein hobby",
        "wie heisst mein hobby"
    ]:

        hobby = get_user_fact(
            state,
            "hobby"
        )

        if hobby:

            return (
                f"Dein Hobby ist "
                f"{hobby}."
            )

        return (
            "Das weiß ich noch nicht. "
            "Was ist dein Hobby?"
        )


    # ======================================
    # CEL NAUKI
    # ======================================

    if message in [
        "was ist mein lernziel",
        "was ist mein ziel",
        "welches lernziel habe ich"
    ]:

        learning_goal = get_user_fact(
            state,
            "learning_goal"
        )

        if learning_goal:

            return (
                f"Dein Lernziel ist "
                f"{learning_goal}."
            )

        return (
            "Das weiß ich noch nicht. "
            "Was ist dein Lernziel?"
        )


    # ======================================
    # IMIĘ
    # ======================================

    if message in [
        "wie heiße ich",
        "wie heisse ich",
        "was ist mein name"
    ]:

        name = get_user_fact(
            state,
            "name"
        )

        if not name:
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

        origin = get_user_fact(
            state,
            "origin"
        )

        if not origin:
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

        residence = get_user_fact(
            state,
            "residence"
        )

        if not residence:
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
