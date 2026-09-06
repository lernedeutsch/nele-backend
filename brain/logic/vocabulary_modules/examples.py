# ==========================================
# NELE – WORTSCHATZMODUL: BEISPIELE
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY


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

    message = normalize(
        user_message
    )


    # ======================================
    # FRAGEN NACH EINEM BEISPIEL
    # ======================================

    example_questions = [
        "und ein beispiel",
        "und ein beispiel dafür",
        "ein beispiel",
        "ein beispiel dafür",

        "gib mir ein beispiel",
        "gib mir ein beispiel dafür",
        "gib mir bitte ein beispiel",

        "nenn mir ein beispiel",
        "nenn mir ein beispiel dafür",
        "nenn mir bitte ein beispiel",

        "zeig mir ein beispiel",
        "zeig mir ein beispiel dafür",
        "zeig mir bitte ein beispiel",

        "hast du ein beispiel",
        "hast du dafür ein beispiel",
        "hast du ein beispiel dafür",

        "kannst du mir ein beispiel geben",
        "kannst du mir bitte ein beispiel geben",
        "kannst du ein beispiel geben",

        "kannst du mir ein beispiel nennen",
        "kannst du mir bitte ein beispiel nennen",

        "kannst du mir ein beispiel zeigen",
        "kannst du mir bitte ein beispiel zeigen",

        "kannst du ein beispiel machen",
        "kannst du mir ein beispiel machen",

        "noch ein beispiel",
        "und noch ein beispiel",

        "gib mir noch ein beispiel",
        "gib mir bitte noch ein beispiel",

        "nenn mir noch ein beispiel",
        "nenn mir bitte noch ein beispiel",

        "zeig mir noch ein beispiel",
        "zeig mir bitte noch ein beispiel",

        "hast du noch ein beispiel",
        "hast du noch eins",
        "hast du noch eines",

        "kannst du mir noch ein beispiel geben",
        "kannst du mir bitte noch ein beispiel geben",

        "kannst du noch ein beispiel geben",
        "kannst du mir noch ein beispiel nennen",
        "kannst du mir noch ein beispiel zeigen",

        "noch eins",
        "und noch eins",

        "noch eines",
        "und noch eines",

        "ein weiteres beispiel",
        "und ein weiteres beispiel",
        "noch ein weiteres beispiel"
    ]


    # ======================================
    # IST ES EINE BEISPIELFRAGE?
    # ======================================

    if message not in example_questions:
        return None


    # ======================================
    # WORTSCHATZEINTRAG HOLEN
    # ======================================

    vocabulary_entry = VOCABULARY.get(
        current_word
    )

    if not vocabulary_entry:
        return None


    # ======================================
    # BEISPIELE HOLEN
    # ======================================

    examples = vocabulary_entry.get(
        "examples"
    )

    if not examples:

        old_example = vocabulary_entry.get(
            "example"
        )

        if not old_example:
            return None

        examples = [
            old_example
        ]


    # ======================================
    # EINZELNES BEISPIEL IN LISTE UMWANDELN
    # ======================================

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
    # NÄCHSTES BEISPIEL BESTIMMEN
    # ======================================

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
    # INDEX SPEICHERN
    # ======================================

    state[
        "vocabulary_example_index"
    ] = example_index


    # ======================================
    # BEISPIEL HOLEN
    # ======================================

    example = examples[
        example_index
    ]


    # ======================================
    # FERTIGE ANTWORT
    # ======================================

    if isinstance(
        example,
        str
    ) and example.lower().startswith(
        "beispiel:"
    ):

        return example

    return (
        f"Beispiel: „{example}“"
    )
