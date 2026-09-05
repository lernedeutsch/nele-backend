# ==========================================
# NELE – WORTSCHATZLOGIK
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
# BEDEUTUNG – WORT ERKENNEN
# ==========================================

def extract_meaning_word(
    user_message
):

    message = normalize(
        user_message
    )

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

    for pattern in explanation_patterns:

        if message.startswith(
            pattern
        ):

            content = message[
                len(pattern):
            ].strip()

            endings = [
                " bitte erklären",
                " bitte erklaeren",
                " bitte erläutern",
                " bitte erlaeutern",
                " erklären",
                " erklaeren",
                " erläutern",
                " erlaeutern"
            ]

            for ending in endings:

                if content.endswith(
                    ending
                ):

                    content = content[
                        :-len(ending)
                    ].strip()

                    word = clean_vocabulary_word(
                        content
                    )

                    if word:
                        return word

    command_patterns = [
        "erkläre mir bitte das wort ",
        "erklaere mir bitte das wort ",
        "erklär mir bitte das wort ",
        "erkläre mir das wort ",
        "erklaere mir das wort ",
        "erklär mir das wort ",
        "erläutere mir das wort ",
        "erlaeutere mir das wort ",
        "erkläre mir bitte ",
        "erklaere mir bitte ",
        "erklär mir bitte ",
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

    remember_vocabulary_word(
        state,
        word
    )

    return meaning


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

    first_example_questions = [
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
        "kannst du mir ein beispiel machen"
    ]

    next_example_questions = [
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

    is_first_example = (
        message in first_example_questions
    )

    is_next_example = (
        message in next_example_questions
    )

    if not is_first_example and not is_next_example:
        return None

    vocabulary_entry = VOCABULARY.get(
        current_word
    )

    if not vocabulary_entry:
        return None

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

    if not isinstance(
        examples,
        list
    ):
        examples = [
            examples
        ]

    if not examples:
        return None

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

    state[
        "vocabulary_example_index"
    ] = example_index

    example = examples[
        example_index
    ]

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


# ==========================================
# VERWENDUNG – WORT ERKENNEN
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
# VERWENDUNG – KONTEXTFRAGE
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
# VERWENDUNG – ANTWORT
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

    remember_vocabulary_word(
        state,
        word
    )

    return usage


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
# ARTIKEL – WORT ERKENNEN
# ==========================================

def extract_article_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [
        "welchen artikel hat das wort ",
        "welchen artikel hat eigentlich das wort ",
        "welchen artikel hat eigentlich ",
        "welchen artikel hat ",

        "was für einen artikel hat das wort ",
        "was für einen artikel hat ",
        "was fuer einen artikel hat das wort ",
        "was fuer einen artikel hat ",

        "welcher artikel gehört zu dem wort ",
        "welcher artikel gehört zu ",
        "welcher artikel gehoert zu dem wort ",
        "welcher artikel gehoert zu ",

        "wie lautet der artikel von dem wort ",
        "wie lautet der artikel von ",

        "wie ist der artikel von dem wort ",
        "wie ist der artikel von ",

        "was ist der artikel von dem wort ",
        "was ist der artikel von "
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
# ARTIKEL – KONTEXTFRAGE
# ==========================================

def is_article_follow_up(
    user_message
):

    message = normalize(
        user_message
    )

    article_questions = [
        "welchen artikel hat das wort",
        "und welchen artikel hat das wort",
        "welchen artikel hat es",
        "und welchen artikel hat es",

        "welcher artikel",
        "und welcher artikel",

        "was ist der artikel",
        "und was ist der artikel",

        "wie ist der artikel",
        "und wie ist der artikel",

        "wie lautet der artikel",
        "und wie lautet der artikel",

        "was für einen artikel hat es",
        "und was für einen artikel hat es",

        "was fuer einen artikel hat es",
        "und was fuer einen artikel hat es"
    ]

    return message in article_questions


# ==========================================
# ARTIKEL – ANTWORT
# ==========================================

def answer_vocabulary_article(
    user_message,
    state=None
):

    word = extract_article_word(
        user_message
    )

    if not word:

        if not is_article_follow_up(
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

    article = vocabulary_entry.get(
        "article"
    )

    if not article:
        return None

    remember_vocabulary_word(
        state,
        word
    )

    display_word = display_vocabulary_word(
        word
    )

    return (
        f"Es heißt „{article} {display_word}“."
    )


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
