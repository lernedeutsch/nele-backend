# ==========================================
# NELE – WORTSCHATZMODUL: ÄHNLICHE WÖRTER
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY


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
# ÄHNLICHES WORT
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

    similar_word = similar_words[
        0
    ]

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
