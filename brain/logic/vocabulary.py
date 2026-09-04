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

    # ======================================
    # SAMO "DAS WORT" = BRAK KONKRETNEGO SŁOWA
    # ======================================

    if word == "das wort":
        return ""

    # ======================================
    # "DAS WORT + KONKRETNE SŁOWO"
    # ======================================

    if word.startswith(
        "das wort "
    ):
        word = word[
            len("das wort "):
        ].strip()

    return word


# ==========================================
# ŁADNA NAZWA SŁOWA
# ==========================================

def display_vocabulary_word(
    word
):

    if not word:
        return ""

    return word[:1].upper() + word[1:]


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


# ==========================================
# PYTANIE O PODOBNE SŁOWO
# ==========================================

def answer_similar_vocabulary_word(
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

    similar_questions = [
        "gibt es ein ähnliches wort",
        "und gibt es ein ähnliches wort",
        "kennst du ein ähnliches wort",
        "und kennst du ein ähnliches wort",
        "was ist ein ähnliches wort",
        "und was ist ein ähnliches wort",
        "gibt es ein ähnliches wort dafür",
        "und gibt es ein ähnliches wort dafür"
    ]

    if message not in similar_questions:
        return None

    vocabulary_entry = VOCABULARY.get(
        current_word
    )

    if not vocabulary_entry:
        return None

    similar_words = vocabulary_entry.get(
        "similar"
    )

    if not similar_words:
        return None

    similar_word = similar_words[0]

    if similar_word not in VOCABULARY:
        return None

    state[
        "current_vocabulary_related_word"
    ] = similar_word

    current_display = display_vocabulary_word(
        current_word
    )

    similar_display = display_vocabulary_word(
        similar_word
    )

    return (
        f"Ein ähnliches Wort zu „{current_display}“ "
        f"ist „{similar_display}“."
    )


# ==========================================
# RÓŻNICA – PYTANIE KONTEKSTOWE
# ==========================================

def answer_vocabulary_difference_follow_up(
    user_message,
    state=None
):

    if state is None:
        return None

    message = normalize(
        user_message
    )

    difference_questions = [
        "was ist der unterschied",
        "und was ist der unterschied",
        "was ist der unterschied zwischen den beiden",
        "und was ist der unterschied zwischen den beiden",
        "was ist der unterschied zwischen diesen wörtern",
        "und was ist der unterschied zwischen diesen wörtern"
    ]

    if message not in difference_questions:
        return None

    current_word = state.get(
        "current_vocabulary_word"
    )

    related_word = state.get(
        "current_vocabulary_related_word"
    )

    if not current_word:
        return None

    if not related_word:
        return None

    vocabulary_entry = VOCABULARY.get(
        current_word
    )

    if not vocabulary_entry:
        return None

    differences = vocabulary_entry.get(
        "difference"
    )

    if not differences:
        return None

    answer = differences.get(
        related_word
    )

    if not answer:
        return None

    return answer


# ==========================================
# RÓŻNICA – PEŁNE PYTANIE
# ==========================================

def answer_explicit_vocabulary_difference(
    user_message,
    state=None
):

    message = normalize(
        user_message
    )

    prefix = (
        "was ist der unterschied zwischen "
    )

    if not message.startswith(
        prefix
    ):
        return None

    content = message[
        len(prefix):
    ].strip()

    if " und " not in content:
        return None

    first, second = content.split(
        " und ",
        1
    )

    first = clean_vocabulary_word(
        first
    )

    second = clean_vocabulary_word(
        second
    )

    if not first or not second:
        return None

    first_entry = VOCABULARY.get(
        first
    )

    if not first_entry:
        return None

    differences = first_entry.get(
        "difference"
    )

    if not differences:
        return None

    answer = differences.get(
        second
    )

    if not answer:
        return None

    if state is not None:

        state[
            "current_vocabulary_word"
        ] = first

        state[
            "current_vocabulary_related_word"
        ] = second

    return answer
