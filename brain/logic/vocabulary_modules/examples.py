# ==========================================
# NELE – WORTSCHATZMODUL: BEISPIELE
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY


# ==========================================
# NACHRICHT BEREINIGEN
# ==========================================

def clean_example_message(
    user_message
):

    message = normalize(
        user_message
    )

    message = message.strip(
        " .?!„“\"'"
    )

    return message


# ==========================================
# BEISPIEL – ANTWORT
# ==========================================

def answer_vocabulary_example(
    user_message,
    state=None
):

    if state is None:
        return None

    current_word = state.get(
        "current_vocabulary_word"
    )

    if not current_word:
        return None

    message = clean_example_message(
        user_message
    )

    # ======================================
    # ERSTES BEISPIEL
    # ======================================

    first_example_questions = [

        # ----------------------------------
        # Kurz
        # ----------------------------------

        "ein beispiel",
        "und ein beispiel",

        "ein beispiel dafür",
        "und ein beispiel dafür",

        "ein beispiel dazu",
        "und ein beispiel dazu",

        # ----------------------------------
        # Gib mir ...
        # ----------------------------------

        "gib mir ein beispiel",
        "gib mir bitte ein beispiel",

        "gib mir ein beispiel dafür",
        "gib mir bitte ein beispiel dafür",

        "gib mir ein beispiel dazu",
        "gib mir bitte ein beispiel dazu",

        # ----------------------------------
        # Nenn mir ...
        # ----------------------------------

        "nenn mir ein beispiel",
        "nenn mir bitte ein beispiel",

        "nenn mir ein beispiel dafür",
        "nenn mir bitte ein beispiel dafür",

        "nenn mir ein beispiel dazu",
        "nenn mir bitte ein beispiel dazu",

        # ----------------------------------
        # Zeig mir ...
        # ----------------------------------

        "zeig mir ein beispiel",
        "zeig mir bitte ein beispiel",

        "zeig mir ein beispiel dafür",
        "zeig mir bitte ein beispiel dafür",

        "zeig mir ein beispiel dazu",
        "zeig mir bitte ein beispiel dazu",

        # ----------------------------------
        # Hast du ...
        # ----------------------------------

        "hast du ein beispiel",
        "hast du dafür ein beispiel",
        "hast du ein beispiel dafür",

        "hast du dazu ein beispiel",
        "hast du ein beispiel dazu",

        # ----------------------------------
        # Kannst du ... geben
        # ----------------------------------

        "kannst du mir ein beispiel geben",
        "kannst du mir bitte ein beispiel geben",
        "kannst du ein beispiel geben",

        "kannst du mir dafür ein beispiel geben",
        "kannst du mir dazu ein beispiel geben",

        # ----------------------------------
        # Kannst du ... nennen
        # ----------------------------------

        "kannst du mir ein beispiel nennen",
        "kannst du mir bitte ein beispiel nennen",
        "kannst du ein beispiel nennen",

        # ----------------------------------
        # Kannst du ... zeigen
        # ----------------------------------

        "kannst du mir ein beispiel zeigen",
        "kannst du mir bitte ein beispiel zeigen",
        "kannst du ein beispiel zeigen",

        # ----------------------------------
        # Kannst du ... machen
        # ----------------------------------

        "kannst du ein beispiel machen",
        "kannst du mir ein beispiel machen",
        "kannst du mir bitte ein beispiel machen"
    ]

    # ======================================
    # NÄCHSTES BEISPIEL
    # ======================================

    next_example_questions = [

        # ----------------------------------
        # Kurz
        # ----------------------------------

        "noch ein beispiel",
        "und noch ein beispiel",

        "noch eins",
        "und noch eins",

        "noch eines",
        "und noch eines",

        "ein weiteres beispiel",
        "und ein weiteres beispiel",

        "noch ein weiteres beispiel",
        "und noch ein weiteres beispiel",

        # ----------------------------------
        # Gib mir ...
        # ----------------------------------

        "gib mir noch ein beispiel",
        "gib mir bitte noch ein beispiel",

        "gib mir noch eins",
        "gib mir bitte noch eins",

        "gib mir noch eines",
        "gib mir bitte noch eines",

        # ----------------------------------
        # Nenn mir ...
        # ----------------------------------

        "nenn mir noch ein beispiel",
        "nenn mir bitte noch ein beispiel",

        "nenn mir noch eins",
        "nenn mir bitte noch eins",

        # ----------------------------------
        # Zeig mir ...
        # ----------------------------------

        "zeig mir noch ein beispiel",
        "zeig mir bitte noch ein beispiel",

        "zeig mir noch eins",
        "zeig mir bitte noch eins",

        # ----------------------------------
        # Hast du ...
        # ----------------------------------

        "hast du noch ein beispiel",
        "hast du noch eins",
        "hast du noch eines",

        "hast du ein weiteres beispiel",

        # ----------------------------------
        # Kannst du ... geben
        # ----------------------------------

        "kannst du mir noch ein beispiel geben",
        "kannst du mir bitte noch ein beispiel geben",

        "kannst du noch ein beispiel geben",

        "kannst du mir noch eins geben",
        "kannst du mir bitte noch eins geben",

        # ----------------------------------
        # Kannst du ... nennen
        # ----------------------------------

        "kannst du mir noch ein beispiel nennen",
        "kannst du mir bitte noch ein beispiel nennen",

        "kannst du noch ein beispiel nennen",

        # ----------------------------------
        # Kannst du ... zeigen
        # ----------------------------------

        "kannst du mir noch ein beispiel zeigen",
        "kannst du mir bitte noch ein beispiel zeigen",

        "kannst du noch ein beispiel zeigen"
    ]

    # ======================================
    # FRAGETYP ERKENNEN
    # ======================================

    is_first_example = (
        message in first_example_questions
    )

    is_next_example = (
        message in next_example_questions
    )

    if not is_first_example and not is_next_example:
        return None

    # ======================================
    # WORTSCHATZEINTRAG LADEN
    # ======================================

    vocabulary_entry = VOCABULARY.get(
        current_word
    )

    if not vocabulary_entry:
        return None

    # ======================================
    # BEISPIELE LADEN
    # ======================================

    examples = vocabulary_entry.get(
        "examples"
    )

    # --------------------------------------
    # Unterstützung für alte Struktur
    # --------------------------------------

    if not examples:

        old_example = vocabulary_entry.get(
            "example"
        )

        if not old_example:
            return None

        examples = [
            old_example
        ]

    # --------------------------------------
    # Einzelnes Beispiel in Liste umwandeln
    # --------------------------------------

    if not isinstance(
        examples,
        list
    ):

        examples = [
            examples
        ]

    if not examples:
        return None

    # ======================================
    # BEISPIELNUMMER BESTIMMEN
    # ======================================

    if is_first_example:

        example_index = 0

    else:

        old_index = state.get(
            "vocabulary_example_index",
            -1
        )

        example_index = (
            old_index + 1
        ) % len(
            examples
        )

    # ======================================
    # BEISPIELNUMMER SPEICHERN
    # ======================================

    state[
        "vocabulary_example_index"
    ] = example_index

    example = examples[
        example_index
    ]

    # ======================================
    # ANTWORT
    # ======================================

    if (
        isinstance(
            example,
            str
        )
        and example.lower().startswith(
            "beispiel:"
        )
    ):
        return example

    return (
        f"Beispiel: „{example}“"
    )
