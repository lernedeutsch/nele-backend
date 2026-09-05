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


# ==========================================
# PLURAL – WORT ERKENNEN
# ==========================================

def extract_plural_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [
        "was ist der plural von dem wort ",
        "was ist der plural von ",

        "wie lautet der plural von dem wort ",
        "wie lautet der plural von ",

        "wie ist der plural von dem wort ",
        "wie ist der plural von ",

        "was ist die mehrzahl von dem wort ",
        "was ist die mehrzahl von ",

        "wie lautet die mehrzahl von dem wort ",
        "wie lautet die mehrzahl von ",

        "wie ist die mehrzahl von dem wort ",
        "wie ist die mehrzahl von ",

        "welche mehrzahl hat das wort ",
        "welche mehrzahl hat "
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
# PLURAL – KONTEXTFRAGE
# ==========================================

def is_plural_follow_up(
    user_message
):

    message = normalize(
        user_message
    )

    plural_questions = [
        "was ist der plural",
        "und was ist der plural",

        "wie lautet der plural",
        "und wie lautet der plural",

        "wie ist der plural",
        "und wie ist der plural",

        "was ist die mehrzahl",
        "und was ist die mehrzahl",

        "wie lautet die mehrzahl",
        "und wie lautet die mehrzahl",

        "wie ist die mehrzahl",
        "und wie ist die mehrzahl",

        "welche mehrzahl",
        "und welche mehrzahl"
    ]

    return message in plural_questions


# ==========================================
# PLURAL – ANTWORT
# ==========================================

def answer_vocabulary_plural(
    user_message,
    state=None
):

    word = extract_plural_word(
        user_message
    )

    if not word:

        if not is_plural_follow_up(
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

    plural = vocabulary_entry.get(
        "plural"
    )

    if not plural:
        return None

    remember_vocabulary_word(
        state,
        word
    )

    display_word = display_vocabulary_word(
        word
    )

    return (
        f"Der Plural von „{display_word}“ "
        f"ist „{plural}“."
    )
