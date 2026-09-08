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

                state[
                    "favorite_word"
                ] = value

                return (
                    f"Schön! Ich merke mir: "
                    f"Dein Lieblingswort ist "
                    f"„{value}“."
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
