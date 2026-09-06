# ==========================================
# NELE – WORTSCHATZLOGIK
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY

from brain.logic.vocabulary_modules.meaning import (
    extract_meaning_word,
    answer_vocabulary_question
)

from brain.logic.vocabulary_modules.examples import (
    answer_vocabulary_example
)

from brain.logic.vocabulary_modules.usage import (
    extract_usage_word,
    is_vocabulary_usage_follow_up,
    answer_vocabulary_usage
)

from brain.logic.vocabulary_modules.article import (
    extract_article_word,
    is_article_follow_up,
    answer_vocabulary_article
)

from brain.logic.vocabulary_modules.plural import (
    extract_plural_word,
    is_plural_follow_up,
    answer_vocabulary_plural
)

from brain.logic.vocabulary_modules.similar import (
    answer_similar_vocabulary_word
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


# ==========================================
# UNTERSCHIED – KONTEXTFRAGE
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
# UNTERSCHIED – DIREKTE FRAGE
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

        remember_vocabulary_word(
            state,
            first
        )

        state[
            "current_vocabulary_related_word"
        ] = second

    return answer
