# ==========================================
# NELE – WORTSCHATZMODUL: EINFACHE ERKLÄRUNG
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY

from brain.logic.vocabulary_modules.helpers import (
    remember_vocabulary_word
)


# ==========================================
# EINFACHE ERKLÄRUNG – FRAGE ERKENNEN
# ==========================================

def is_simple_explanation_request(
    user_message
):

    message = normalize(
        user_message
    )

    simple_questions = [
        "einfacher",
        "einfacher bitte",
        "bitte einfacher",

        "noch einfacher",
        "noch einfacher bitte",
        "bitte noch einfacher",

        "kannst du das einfacher erklären",
        "kannst du das bitte einfacher erklären",
        "kannst du es einfacher erklären",
        "kannst du es bitte einfacher erklären",

        "kannst du das einfacher erklaeren",
        "kannst du das bitte einfacher erklaeren",
        "kannst du es einfacher erklaeren",
        "kannst du es bitte einfacher erklaeren",

        "erklär das einfacher",
        "erklär es einfacher",
        "erkläre das einfacher",
        "erkläre es einfacher",
        "erklaere das einfacher",
        "erklaere es einfacher",

        "ich verstehe das nicht",
        "ich verstehe es nicht",
        "das verstehe ich nicht",
        "das ist zu schwer",
        "das ist schwierig"
    ]

    return message in simple_questions


# ==========================================
# EINFACHE ERKLÄRUNG – ANTWORT
# ==========================================

def answer_simple_explanation(
    user_message,
    state=None
):

    if not is_simple_explanation_request(
        user_message
    ):
        return None

    if state is None:
        return None


    # ======================================
    # ZUERST POWIĄZANE / NOWE WORT
    #
    # groß -> ähnlich -> riesig
    # Einfacher, bitte.
    # -> Erklärung von riesig
    #
    # groß -> Gegenteil -> klein
    # Einfacher, bitte.
    # -> Erklärung von klein
    # ======================================

    related_word = state.get(
        "current_vocabulary_related_word"
    )

    current_word = state.get(
        "current_vocabulary_word"
    )


    if (
        related_word
        and related_word in VOCABULARY
    ):

        word = related_word

    else:

        word = current_word


    if not word:
        return None


    vocabulary_entry = VOCABULARY.get(
        word
    )

    if not vocabulary_entry:
        return None


    # ======================================
    # GOTOWE PROSTE WYJAŚNIENIE
    # ======================================

    simple_meaning = vocabulary_entry.get(
        "simple_meaning"
    )

    if simple_meaning:

        remember_vocabulary_word(
            state,
            word
        )

        state[
            "current_vocabulary_related_word"
        ] = None

        return simple_meaning


    # ======================================
    # FALLBACK:
    # JEŚLI NIE MA SIMPLE_MEANING,
    # UŻYJ NORMALNEGO MEANING
    # ======================================

    meaning = vocabulary_entry.get(
        "meaning"
    )

    if not meaning:
        return None


    remember_vocabulary_word(
        state,
        word
    )

    state[
        "current_vocabulary_related_word"
    ] = None

    return meaning
