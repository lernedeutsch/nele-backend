# ==========================================
# NELE – WORTSCHATZMODUL: PLURAL
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
# HILFSFUNKTION – WORT SCHÖN ANZEIGEN
# ==========================================

def display_vocabulary_word(
    word
):

    if not word:
        return ""

    return word[:1].upper() + word[1:]


# ==========================================
# HILFSFUNKTION – WORT MERKEN
# ==========================================

def remember_vocabulary_word(
    state,
    word
):

    if state is None:
        return

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


# ==========================================
# PLURAL – WORT ERKENNEN
# ==========================================

def extract_plural_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [
        "was ist der plural von dem wort ",
        "was ist der plural von ",

        "wie lautet der plural von dem wort ",
        "wie lautet der plural von ",

        "wie ist der plural von dem wort ",
        "wie ist der plural von ",

        "was ist die mehrzahl von dem wort ",
        "was ist die mehrzahl von ",

        "wie lautet die mehrzahl von dem wort ",
        "wie lautet die mehrzahl von ",

        "wie ist die mehrzahl von dem wort ",
        "wie ist die mehrzahl von ",

        "welche mehrzahl hat das wort ",
        "welche mehrzahl hat "
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
# PLURAL – KONTEXTFRAGE
# ==========================================

def is_plural_follow_up(
    user_message
):

    message = normalize(
        user_message
    )

    plural_questions = [
        "was ist der plural",
        "und was ist der plural",

        "wie lautet der plural",
        "und wie lautet der plural",

        "wie ist der plural",
        "und wie ist der plural",

        "was ist die mehrzahl",
        "und was ist die mehrzahl",

        "wie lautet die mehrzahl",
        "und wie lautet die mehrzahl",

        "wie ist die mehrzahl",
        "und wie ist die mehrzahl",

        "welche mehrzahl",
        "und welche mehrzahl"
    ]

    return message in plural_questions


# ==========================================
# PLURAL – ANTWORT
# ==========================================

def answer_vocabulary_plural(
    user_message,
    state=None
):

    word = extract_plural_word(
        user_message
    )

    if not word:

        if not is_plural_follow_up(
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

    plural = vocabulary_entry.get(
        "plural"
    )

    if not plural:
        return None

    remember_vocabulary_word(
        state,
        word
    )

    display_word = display_vocabulary_word(
        word
    )

    return (
        f"Der Plural von „{display_word}“ "
        f"ist „{plural}“."
    )
