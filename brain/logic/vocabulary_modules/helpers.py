# ==========================================
# NELE – WORTSCHATZMODUL: HILFSFUNKTIONEN
# ==========================================

from brain.logic.matcher import normalize

from brain.memory.vocabulary_memory import (
    remember_practiced_word
)


# ==========================================
# WORT BEREINIGEN
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
# WORT SCHÖN ANZEIGEN
# ==========================================

def display_vocabulary_word(
    word
):

    if not word:
        return ""

    return word[:1].upper() + word[1:]


# ==========================================
# WORT IM KONTEXT MERKEN
# ==========================================

def remember_vocabulary_word(
    state,
    word
):

    if state is None:
        return

    if not word:
        return

    old_word = state.get(
        "current_vocabulary_word"
    )

    if old_word != word:

        state[
            "vocabulary_example_index"
        ] = -1

        state[
            "current_vocabulary_related_word"
        ] = None

    state[
        "current_vocabulary_word"
    ] = word


    # ======================================
    # WORT ALS GEÜBT SPEICHERN
    # ======================================

    remember_practiced_word(
        word,
        state
    )
