from brain.logic.memory import get_conversation_state
from brain.logic.matcher import (
    normalize,
    clean_short_answer,
    capitalize_value
)


# ==========================================
# INFORMACJE O UŻYTKOWNIKU
# ==========================================

def extract_user_information(
    user_message,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    original = clean_short_answer(
        user_message
    )

    message = normalize(
        user_message
    )


    # ======================================
    # USER FACTS
    # ======================================

    if "user_facts" not in state:
        state["user_facts"] = {}

    user_facts = state[
        "user_facts"
    ]


    # ======================================
    # ULUBIONE SŁOWO
    # ======================================

    favorite_word_prefixes = [
        "mein lieblingswort ist "
    ]

    for prefix in favorite_word_prefixes:

        normalized_prefix = normalize(
            prefix
        )

        if message.startswith(
            normalized_prefix + " "
        ):

            value = original[
                len(prefix):
            ].strip()

            if value:

                value = capitalize_value(
                    value
                )

                # zgodność ze starszą pamięcią
                state[
                    "favorite_word"
                ] = value

                # nowa elastyczna pamięć
                user_facts[
                    "favorite_word"
                ] = value

                return (
                    f"Schön! Ich merke mir: "
                    f"Dein Lieblingswort ist "
                    f"„{value}“."
                )


    # ======================================
    # ULUBIONY KOLOR
    # ==========================================

    favorite_color_prefixes = [
        "meine lieblingsfarbe ist "
    ]

    for prefix in favorite_color_prefixes:

        normalized_prefix = normalize(
            prefix
        )

        if message.startswith(
            normalized_prefix + " "
        ):

            value = original[
                len(prefix):
            ].strip()

            if value:

                value = capitalize_value(
                    value
                )

                user_facts[
                    "favorite_color"
                ] = value

                return (
                    f"Schön! Ich merke mir: "
                    f"Deine Lieblingsfarbe ist "
                    f"{value}."
                )


    # ======================================
    # HOBBY
    # ==========================================

    hobby_prefixes = [
        "mein hobby ist ",
        "mein hobby heißt ",
        "mein hobby heisst "
    ]

    for prefix in hobby_prefixes:

        normalized_prefix = normalize(
            prefix
        )

        if message.startswith(
            normalized_prefix + " "
        ):

            value = original[
                len(prefix):
            ].strip()

            if value:

                value = capitalize_value(
                    value
                )

                user_facts[
                    "hobby"
                ] = value

                return (
                    f"Schön! Ich merke mir: "
                    f"Dein Hobby ist "
                    f"{value}."
                )


    # ======================================
    # CEL NAUKI
    # ==========================================

    learning_goal_prefixes = [
        "mein lernziel ist ",
        "mein ziel ist "
    ]

    for prefix in learning_goal_prefixes:

        normalized_prefix = normalize(
            prefix
        )

        if message.startswith(
            normalized_prefix + " "
        ):

            value = original[
                len(prefix):
            ].strip()

            if value:

                value = capitalize_value(
                    value
                )

                user_facts[
                    "learning_goal"
                ] = value

                return (
                    f"Gut! Ich merke mir: "
                    f"Dein Lernziel ist "
                    f"{value}."
                )


    # ======================================
    # IMIĘ
    # ======================================

    name_prefixes = [
        "ich heiße ",
        "ich heisse ",
        "mein name ist ",
        "ich bin "
    ]

    for prefix in name_prefixes:

        normalized_prefix = normalize(
            prefix
        )

        if message.startswith(
            normalized_prefix + " "
        ):

            value = original[
                len(prefix):
            ].strip()

            if value:

                value = capitalize_value(
                    value
                )

                state[
                    "name"
                ] = value

                user_facts[
                    "name"
                ] = value

                state[
                    "last_question"
                ] = "origin"

                return (
                    f"Freut mich, {value}. "
                    f"Woher kommst du?"
                )


    # ======================================
    # POCHODZENIE
    # ======================================

    origin_prefixes = [
        "ich komme aus ",
        "ich bin aus "
    ]

    for prefix in origin_prefixes:

        normalized_prefix = normalize(
            prefix
        )

        if message.startswith(
            normalized_prefix + " "
        ):

            value = original[
                len(prefix):
            ].strip()

            if value:

                value = capitalize_value(
                    value
                )

                state[
                    "origin"
                ] = value

                user_facts[
                    "origin"
                ] = value

                state[
                    "last_question"
                ] = "residence"

                return (
                    f"Schön. "
                    f"Du kommst aus {value}. "
                    f"Wo wohnst du jetzt?"
                )


    # ======================================
    # MIEJSCE ZAMIESZKANIA
    # ======================================

    residence_prefixes = [
        "ich wohne in ",
        "ich lebe in "
    ]

    for prefix in residence_prefixes:

        normalized_prefix = normalize(
            prefix
        )

        if message.startswith(
            normalized_prefix + " "
        ):

            value = original[
                len(prefix):
            ].strip()

            if value:

                value = capitalize_value(
                    value
                )

                state[
                    "residence"
                ] = value

                user_facts[
                    "residence"
                ] = value

                state[
                    "last_question"
                ] = None

                name = state.get(
                    "name"
                )

                if name:

                    return (
                        f"Ah, {name}, "
                        f"du wohnst in {value}. "
                        f"Schön!"
                    )

                return (
                    f"Ah, du wohnst in "
                    f"{value}. Schön!"
                )


    return None
