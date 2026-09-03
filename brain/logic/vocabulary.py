# ==========================================
# NELE – LOGIKA SŁOWNICTWA
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY


# ==========================================
# CZYSZCZENIE NAZWY SŁOWA
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

    # Obsługa:
    # "das wort reservierung"
    if word.startswith(
        "das wort "
    ):
        word = word[
            len("das wort "):
        ].strip()

    return word


# ==========================================
# ROZPOZNAWANIE PYTANIA O ZNACZENIE
# ==========================================

def extract_meaning_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [
        "was bedeutet ",
        "was heißt ",
        "was heisst ",
        "was bedeutet das wort ",
        "was heißt das wort ",
        "was heisst das wort "
    ]

    # Najpierw sprawdzamy dłuższe wzorce.
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

            return clean_vocabulary_word(
                word
            )

    return None


# ==========================================
# ODPOWIEDŹ NA PYTANIE O ZNACZENIE
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

    # Zapamiętujemy słowo,
    # o którym teraz rozmawiamy.
    if state is not None:

        state[
            "current_vocabulary_word"
        ] = word

    return meaning
