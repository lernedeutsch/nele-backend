# ==========================================
# NELE – WORTSCHATZMODUL: ÜBUNG
# ==========================================

from brain.logic.matcher import normalize

from brain.knowledge.A1.vocabulary import VOCABULARY

from brain.logic.vocabulary_modules.helpers import (
    clean_vocabulary_word,
    remember_vocabulary_word
)


# ==========================================
# ÜBUNG – WORT ERKENNEN
# ==========================================

def extract_practice_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [
        "übe mit mir das wort ",
        "übe mit mir ",
        "üben wir das wort ",
        "üben wir ",
        "ich möchte das wort ",
        "ich möchte ",
        "lass uns das wort ",
        "lass uns "
    ]

    patterns.sort(
        key=len,
        reverse=True
    )

    for pattern in patterns:

        if not message.startswith(
            pattern
        ):
            continue

        word = message[
            len(pattern):
        ]

        word = clean_vocabulary_word(
            word
        )

        endings = [
            " üben",
            " lernen"
        ]

        for ending in endings:

            if word.endswith(
                ending
            ):

                word = word[
                    :-len(ending)
                ].strip()

                break

        if word:
            return word

    return None


# ==========================================
# ÜBUNG – STARTEN
# ==========================================

def start_vocabulary_practice(
    user_message,
    state=None
):

    if state is None:
        return None

    word = extract_practice_word(
        user_message
    )

    if not word:
        return None

    if word not in VOCABULARY:
        return None

    remember_vocabulary_word(
        state,
        word
    )

    state[
        "vocabulary_practice_active"
    ] = True

    state[
        "vocabulary_practice_word"
    ] = word

    state[
        "vocabulary_practice_type"
    ] = "meaning"

    display_word = (
        word[:1].upper()
        + word[1:]
    )

    return (
        f"Was bedeutet „{display_word}“?"
    )
