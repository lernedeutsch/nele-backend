# ==========================================
# NELE – WORTSCHATZMODUL: BEDEUTUNG
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY


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
# BEDEUTUNG – WORT ERKENNEN
# ==========================================

def extract_meaning_word(
    user_message
):

    message = normalize(
        user_message
    )

    # --------------------------------------
    # Direkte Fragen
    # --------------------------------------

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

    # --------------------------------------
    # Fragen mit "Kannst du ..."
    # --------------------------------------

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

    # --------------------------------------
    # Befehle mit "Erklär ..."
    # --------------------------------------

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

    if not word:
        return None

    vocabulary_entry = VOCABULARY.get(
        word
    )

    if not vocabulary_entry:
        return None

    meaning = vocabulary_entry.get(
        "meaning"
    )

    if not meaning:
        return None

    # --------------------------------------
    # Wort im Gesprächskontext speichern
    # --------------------------------------

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

    return meaning
