# ==========================================
# NELE – WORTSCHATZMODUL: BEDEUTUNG
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY

from brain.logic.vocabulary_modules.helpers import (
    clean_vocabulary_word,
    remember_vocabulary_word
)


# ==========================================
# BEDEUTUNG – KONTEXTFRAGE
# ==========================================

def is_meaning_follow_up(
    user_message
):

    message = normalize(
        user_message
    )

    meaning_questions = [
        "was bedeutet das",
        "und was bedeutet das",

        "was heißt das",
        "und was heißt das",

        "was heisst das",
        "und was heisst das",

        "was bedeutet es",
        "und was bedeutet es",

        "was bedeutet dieses wort",
        "und was bedeutet dieses wort",

        "was heißt dieses wort",
        "und was heißt dieses wort",

        "was heisst dieses wort",
        "und was heisst dieses wort"
    ]

    return message in meaning_questions


# ==========================================
# BEDEUTUNG – WORT ERKENNEN
# ==========================================

def extract_meaning_word(
    user_message
):

    message = normalize(
        user_message
    )


    # ======================================
    # KONTEXTFRAGEN NICHT ALS WORT LESEN
    # ======================================

    if is_meaning_follow_up(
        user_message
    ):
        return None


    # ======================================
    # DIREKTE FRAGEN
    # ======================================

    direct_patterns = [
        "was bedeutet eigentlich das wort ",
        "was heißt eigentlich das wort ",
        "was heisst eigentlich das wort ",

        "was genau bedeutet das wort ",
        "was genau heißt das wort ",
        "was genau heisst das wort ",

        "was bedeutet das wort ",
        "was heißt das wort ",
        "was heisst das wort ",

        "was bedeutet eigentlich ",
        "was heißt eigentlich ",
        "was heisst eigentlich ",

        "was genau bedeutet ",
        "was genau heißt ",
        "was genau heisst ",

        "was bedeutet ",
        "was heißt ",
        "was heisst "
    ]

    direct_patterns.sort(
        key=len,
        reverse=True
    )

    for pattern in direct_patterns:

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


    # ======================================
    # FRAGEN MIT "KANNST DU ..."
    # ======================================

    explanation_patterns = [
        "kannst du mir das wort ",
        "kannst du das wort ",
        "kannst du mir ",
        "kannst du "
    ]

    explanation_patterns.sort(
        key=len,
        reverse=True
    )

    explanation_endings = [
        " bitte erklären",
        " bitte erklaeren",
        " bitte erläutern",
        " bitte erlaeutern",

        " erklären",
        " erklaeren",

        " erläutern",
        " erlaeutern"
    ]

    for pattern in explanation_patterns:

        if not message.startswith(
            pattern
        ):
            continue

        content = message[
            len(pattern):
        ].strip()

        for ending in explanation_endings:

            if not content.endswith(
                ending
            ):
                continue

            content = content[
                :-len(ending)
            ].strip()

            word = clean_vocabulary_word(
                content
            )

            if word:
                return word


    # ======================================
    # BEFEHLE MIT "ERKLÄR ..."
    # ======================================

    command_patterns = [
        "erkläre mir bitte das wort ",
        "erklaere mir bitte das wort ",
        "erklär mir bitte das wort ",

        "erläutere mir bitte das wort ",
        "erlaeutere mir bitte das wort ",

        "erkläre mir das wort ",
        "erklaere mir das wort ",
        "erklär mir das wort ",

        "erläutere mir das wort ",
        "erlaeutere mir das wort ",

        "erkläre mir bitte ",
        "erklaere mir bitte ",
        "erklär mir bitte ",

        "erläutere mir bitte ",
        "erlaeutere mir bitte ",

        "erkläre mir ",
        "erklaere mir ",
        "erklär mir ",

        "erläutere mir ",
        "erlaeutere mir "
    ]

    command_patterns.sort(
        key=len,
        reverse=True
    )

    for pattern in command_patterns:

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
# BEDEUTUNG – ANTWORT
# ==========================================

def answer_vocabulary_question(
    user_message,
    state=None
):

    word = extract_meaning_word(
        user_message
    )

    is_follow_up = is_meaning_follow_up(
        user_message
    )


    # ======================================
    # KONTEXT:
    # "WAS BEDEUTET DAS?"
    # ======================================

    if not word:

        if not is_follow_up:
            return None

        if state is None:
            return None


        # ==================================
        # OSTATNIE POWIĄZANE SŁOWO
        #
        # Groß → Gegenteil → Klein
        # Was bedeutet das? → Klein
        #
        # Groß → ähnlich → Riesig
        # Was bedeutet das? → Riesig
        # ==================================

        related_word = state.get(
            "current_vocabulary_related_word"
        )

        if (
            related_word
            and related_word in VOCABULARY
        ):

            word = related_word

        else:

            word = state.get(
                "current_vocabulary_word"
            )


    if not word:
        return None


    # ======================================
    # WORTSCHATZEINTRAG
    # ======================================

    vocabulary_entry = VOCABULARY.get(
        word
    )

    if not vocabulary_entry:
        return None


    # ======================================
    # BEDEUTUNG
    # ======================================

    meaning = vocabulary_entry.get(
        "meaning"
    )

    if not meaning:
        return None


    # ======================================
    # AKTUELLES WORT MERKEN
    # ======================================

    if state is not None:

        remember_vocabulary_word(
            state,
            word
        )


        # ==================================
        # DIREKTE FRAGE:
        # NEUER WORTSCHATZ-KONTEXT
        #
        # Groß → Riesig
        # Was bedeutet Kaffee?
        #
        # Alte Beziehung "Riesig"
        # darf nicht aktiv bleiben.
        # ==================================

        if not is_follow_up:

            state[
                "current_vocabulary_related_word"
            ] = None


        # ==================================
        # KONTEXTFRAGE:
        # VERWANDTES WORT WIRD AKTUELL
        #
        # Groß → Klein
        # Was bedeutet das?
        # → Klein wird aktuelles Wort
        # ==================================

        elif state.get(
            "current_vocabulary_related_word"
        ) == word:

            state[
                "current_vocabulary_related_word"
            ] = None


    return meaning
