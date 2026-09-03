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
        "was bedeutet das wort ",
        "was heißt das wort ",
        "was heisst das wort ",
        "was bedeutet ",
        "was heißt ",
        "was heisst "
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

    if state is not None:

        state[
            "current_vocabulary_word"
        ] = word

    return meaning


# ==========================================
# PRZYKŁAD DLA AKTUALNEGO SŁOWA
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

    example_questions = [
        "und ein beispiel",
        "und ein beispiel dafür",
        "ein beispiel",
        "ein beispiel dafür",
        "gib mir ein beispiel",
        "gib mir ein beispiel dafür",
        "nenn mir ein beispiel",
        "nenn mir ein beispiel dafür",
        "zeig mir ein beispiel",
        "zeig mir ein beispiel dafür"
    ]

    if message not in example_questions:
        return None

    vocabulary_entry = VOCABULARY.get(
        current_word
    )

    if not vocabulary_entry:
        return None

    example = vocabulary_entry.get(
        "example"
    )

    if not example:
        return None

    return example


# ==========================================
# ROZPOZNAWANIE PYTANIA O UŻYCIE SŁOWA
# ==========================================

def extract_usage_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [
        "wann benutzt man das wort ",
        "wann verwendet man das wort ",
        "wann sagt man das wort ",
        "wann benutze ich das wort ",
        "wann verwende ich das wort ",
        "wann benutzt man ",
        "wann verwendet man ",
        "wann sagt man ",
        "wann benutze ich ",
        "wann verwende ich "
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
# PYTANIE KONTEKSTOWE O UŻYCIE
# ==========================================

def is_vocabulary_usage_follow_up(
    user_message
):

    message = normalize(
        user_message
    )

    usage_follow_ups = [
        "wann benutzt man das",
        "und wann benutzt man das",
        "wann verwendet man das",
        "und wann verwendet man das",
        "wann sagt man das",
        "und wann sagt man das",
        "wann benutzt man das wort",
        "und wann benutzt man das wort",
        "wann verwendet man das wort",
        "und wann verwendet man das wort",
        "wann sagt man das wort",
        "und wann sagt man das wort",
        "wann benutze ich das",
        "und wann benutze ich das",
        "wann verwende ich das",
        "und wann verwende ich das"
    ]

    return message in usage_follow_ups


# ==========================================
# ODPOWIEDŹ NA PYTANIE O UŻYCIE SŁOWA
# ==========================================

def answer_vocabulary_usage(
    user_message,
    state=None
):

    word = extract_usage_word(
        user_message
    )

    # Jeśli użytkownik nie podał słowa,
    # sprawdzamy kontekst rozmowy.
    if not word:

        if not is_vocabulary_usage_follow_up(
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

    usage = vocabulary_entry.get(
        "usage"
    )

    if not usage:
        return None

    if state is not None:

        state[
            "current_vocabulary_word"
        ] = word

    return usage
