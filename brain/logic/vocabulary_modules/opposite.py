# ==========================================
# NELE – WORTSCHATZMODUL: GEGENTEILE
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
# GEGENTEIL – WORT ERKENNEN
# ==========================================

def extract_opposite_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [
        "was ist das gegenteil von dem wort ",
        "was ist das gegenteil von ",

        "welches ist das gegenteil von dem wort ",
        "welches ist das gegenteil von ",

        "wie lautet das gegenteil von dem wort ",
        "wie lautet das gegenteil von ",

        "kennst du das gegenteil von dem wort ",
        "kennst du das gegenteil von "
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
# GEGENTEIL – KONTEXTFRAGE
# ==========================================

def is_opposite_follow_up(
    user_message
):

    message = normalize(
        user_message
    )

    opposite_questions = [
        "gegenteil",
        "das gegenteil",
        "und das gegenteil",

        "was ist das gegenteil",
        "und was ist das gegenteil",

        "welches ist das gegenteil",
        "und welches ist das gegenteil",

        "wie lautet das gegenteil",
        "und wie lautet das gegenteil",

        "kennst du das gegenteil",
        "und kennst du das gegenteil"
    ]

    return message in opposite_questions


# ==========================================
# GEGENTEIL – ANTWORT
# ==========================================

def answer_vocabulary_opposite(
    user_message,
    state=None
):

    word = extract_opposite_word(
        user_message
    )

    if not word:

        if not is_opposite_follow_up(
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

    opposite = vocabulary_entry.get(
        "opposite"
    )

    if not opposite:
        return None

    if isinstance(
        opposite,
        list
    ):

        if not opposite:
            return None

        opposite_word = opposite[
            0
        ]

    else:

        opposite_word = opposite

    remember_vocabulary_word(
        state,
        word
    )

    state[
        "current_vocabulary_related_word"
    ] = opposite_word

    display_word = display_vocabulary_word(
        word
    )

    opposite_display = display_vocabulary_word(
        opposite_word
    )

    return (
        f"Das Gegenteil von „{display_word}“ "
        f"ist „{opposite_display}“."
    )
