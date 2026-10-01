from brain.logic.memory import get_conversation_state

from brain.logic.matcher import (
    normalize,
    clean_short_answer,
    capitalize_value
)

from brain.memory.user_facts import (
    remember_user_fact
)


# ==========================================
# INFORMACJE O UŻYTKOWNIKU
# ==========================================

# German origin phrases may begin with an inflected article after "aus"
# (for example "der Schweiz" or "den USA").  Capitalising the first
# character of the whole value changes correct German into "Der/Den".
_GERMAN_ORIGIN_ARTICLES = {"der", "den", "dem", "die", "das"}


def format_origin_value(value):
    value = clean_short_answer(value)
    if not value:
        return value
    first_word = value.split(maxsplit=1)[0].lower()
    if first_word in _GERMAN_ORIGIN_ARTICLES:
        return first_word + value[len(value.split(maxsplit=1)[0]):]
    return capitalize_value(value)


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

                remember_user_fact(
                    state,
                    "favorite_word",
                    value
                )

                return (
                    f"Schön! Ich merke mir: "
                    f"Dein Lieblingswort ist "
                    f"„{value}“."
                )


    # ======================================
    # ULUBIONY KOLOR
    # ======================================

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

                remember_user_fact(
                    state,
                    "favorite_color",
                    value
                )

                return (
                    f"Schön! Ich merke mir: "
                    f"Deine Lieblingsfarbe ist "
                    f"{value}."
                )


    # ======================================
    # HOBBY
    # ======================================

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

                remember_user_fact(
                    state,
                    "hobby",
                    value
                )

                return (
                    f"Schön! Ich merke mir: "
                    f"Dein Hobby ist "
                    f"{value}."
                )


    # ======================================
    # CEL NAUKI
    # ======================================

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

                remember_user_fact(
                    state,
                    "learning_goal",
                    value
                )

                return (
                    f"Gut! Ich merke mir: "
                    f"Dein Lernziel ist "
                    f"{value}."
                )


    # ======================================
    # POCHODZENIE
    # ======================================
    # Ważne:
    # sprawdzamy pochodzenie PRZED "ich bin",
    # żeby "Ich bin aus Polen" nie zostało
    # zapisane jako imię "Aus Polen".
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

                value = format_origin_value(
                    value
                )

                state[
                    "origin"
                ] = value

                remember_user_fact(
                    state,
                    "origin",
                    value
                )

                state[
                    "last_question"
                ] = "residence"

                return (
                    f"Schön. "
                    f"Du kommst aus {value}. "
                    f"Wo wohnst du jetzt?"
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

                remember_user_fact(
                    state,
                    "name",
                    value
                )

                state[
                    "last_question"
                ] = "origin"

                return (
                    f"Freut mich, {value}. "
                    f"Woher kommst du?"
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

                remember_user_fact(
                    state,
                    "residence",
                    value
                )

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


    # ======================================
    # BRAK DOPASOWANIA
    # ======================================

    return None
