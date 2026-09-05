# ==========================================
# NELE – WORTSCHATZMODUL: ARTIKEL
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
# ARTIKEL – WORT ERKENNEN
# ==========================================

def extract_article_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [
        "welchen artikel hat das wort ",
        "welchen artikel hat eigentlich das wort ",
        "welchen artikel hat eigentlich ",
        "welchen artikel hat ",

        "was für einen artikel hat das wort ",
        "was für einen artikel hat ",
        "was fuer einen artikel hat das wort ",
        "was fuer einen artikel hat ",

        "welcher artikel gehört zu dem wort ",
        "welcher artikel gehört zu ",
        "welcher artikel gehoert zu dem wort ",
        "welcher artikel gehoert zu ",

        "wie lautet der artikel von dem wort ",
        "wie lautet der artikel von ",

        "wie ist der artikel von dem wort ",
        "wie ist der artikel von ",

        "was ist der artikel von dem wort ",
        "was ist der artikel von "
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
# ARTIKEL – KONTEXTFRAGE
# ==========================================

def is_article_follow_up(
    user_message
):

    message = normalize(
        user_message
    )

    article_questions = [
        "welchen artikel hat das wort",
        "und welchen artikel hat das wort",
        "welchen artikel hat es",
        "und welchen artikel hat es",

        "welcher artikel",
        "und welcher artikel",

        "was ist der artikel",
        "und was ist der artikel",

        "wie ist der artikel",
        "und wie ist der artikel",

        "wie lautet der artikel",
        "und wie lautet der artikel",

        "was für einen artikel hat es",
        "und was für einen artikel hat es",

        "was fuer einen artikel hat es",
        "und was fuer einen artikel hat es"
    ]

    return message in article_questions


# ==========================================
# ARTIKEL – ANTWORT
# ==========================================

def answer_vocabulary_article(
    user_message,
    state=None
):

    # --------------------------------------
    # Zuerst Kontextfrage prüfen
    # --------------------------------------

    if is_article_follow_up(
        user_message
    ):

        if state is None:
            return None

        word = state.get(
            "current_vocabulary_word"
        )

    else:

        word = extract_article_word(
            user_message
        )

    if not word:
        return None

    vocabulary_entry = VOCABULARY.get(
        word
    )

    if not vocabulary_entry:
        return None

    article = vocabulary_entry.get(
        "article"
    )

    if not article:
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

    display_word = display_vocabulary_word(
        word
    )

    return (
        f"Es heißt „{article} {display_word}“."
      )
