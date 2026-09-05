# ==========================================
# NELE – WORTSCHATZMODUL: VERWENDUNG
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY


# ==========================================
# HILFSFUNKTION – WORT BEREINIGEN
# ==========================================

def clean_vocabulary_word(
    word
):

    word = normalize(
        word
    )

    word = word.strip(
        " .?!„“\"'"
    )

    if word == "das wort":
        return ""

    if word.startswith(
        "das wort "
    ):
        word = word[
            len("das wort "):
        ].strip()

    return word


# ==========================================
# VERWENDUNG – WORT ERKENNEN
# ==========================================

def extract_usage_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [
        "wann benutzt man das wort ",
        "wann verwendet man das wort ",
        "wann sagt man das wort ",
        "wann benutze ich das wort ",
        "wann verwende ich das wort ",

        "wann benutzt man ",
        "wann verwendet man ",
        "wann sagt man ",
        "wann benutze ich ",
        "wann verwende ich "
    ]

    patterns.sort(
        key=len,
        reverse=True
    )

    for pattern in patterns:

        if message.startswith(
            pattern
        ):

            word = message[
                len(pattern):
            ]

            word = clean_vocabulary_word(
                word
            )

            if word:
                return word

    return None


# ==========================================
# VERWENDUNG – KONTEXTFRAGE
# ==========================================

def is_vocabulary_usage_follow_up(
    user_message
):

    message = normalize(
        user_message
    )

    usage_follow_ups = [
        "wann benutzt man das",
        "und wann benutzt man das",

        "wann verwendet man das",
        "und wann verwendet man das",

        "wann sagt man das",
        "und wann sagt man das",

        "wann benutzt man das wort",
        "und wann benutzt man das wort",

        "wann verwendet man das wort",
        "und wann verwendet man das wort",

        "wann sagt man das wort",
        "und wann sagt man das wort",

        "wann benutze ich das",
        "und wann benutze ich das",

        "wann verwende ich das",
        "und wann verwende ich das"
    ]

    return message in usage_follow_ups


# ==========================================
# VERWENDUNG – ANTWORT
# ==========================================

def answer_vocabulary_usage(
    user_message,
    state=None
):

    word = extract_usage_word(
        user_message
    )

    if not word:

        if not is_vocabulary_usage_follow_up(
            user_message
        ):
            return None

        if state is None:
            return None

        word = state.get(
            "current_vocabulary_word"
        )

    if not word:
        return None

    vocabulary_entry = VOCABULARY.get(
        word
    )

    if not vocabulary_entry:
        return None

    usage = vocabulary_entry.get(
        "usage"
    )

    if not usage:
        return None

    if state is not None:

        old_word = state.get(
            "current_vocabulary_word"
        )

        if old_word != word:

            state[
                "vocabulary_example_index"
            ] = -1

        state[
            "current_vocabulary_word"
        ] = word

    return usage
