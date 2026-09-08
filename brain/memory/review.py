# ==========================================
# NELE – WIEDERHOLUNG UND LERNFORTSCHRITT
# ==========================================

from brain.logic.matcher import normalize

from brain.memory.vocabulary_memory import (
    get_vocabulary_memory,
    get_words_for_review
)


# ==========================================
# FRAGE NACH GEÜBTEN WÖRTERN ERKENNEN
# ==========================================

def is_practiced_words_request(
    user_message
):

    message = normalize(
        user_message
    )

    questions = [
        "welche wörter habe ich geübt",
        "welche wörter habe ich schon geübt",
        "welche wörter haben wir geübt",
        "welche wörter haben wir schon geübt",
        "was habe ich geübt",
        "was haben wir geübt",
        "was habe ich schon gelernt",
        "welche wörter habe ich gelernt"
    ]

    return message.strip(
        " .?!"
    ) in questions


# ==========================================
# FRAGE NACH ANZAHL DER ÜBUNGEN ERKENNEN
# ==========================================

def extract_practice_count_word(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!„“\"'"
    )

    patterns = [
        "wie oft habe ich ",
        "wie oft haben wir "
    ]

    for pattern in patterns:

        if not message.startswith(
            pattern
        ):
            continue

        content = message[
            len(pattern):
        ].strip()

        endings = [
            " geübt",
            " schon geübt"
        ]

        for ending in endings:

            if content.endswith(
                ending
            ):

                word = content[
                    :-len(ending)
                ].strip(
                    " .?!„“\"'"
                )

                if word:
                    return word

    return None


# ==========================================
# GEÜBTE WÖRTER FORMATIEREN
# ==========================================

def format_word_list(
    words
):

    if not words:
        return ""

    if len(words) == 1:
        return words[0]

    if len(words) == 2:
        return (
            words[0]
            + " und "
            + words[1]
        )

    return (
        ", ".join(
            words[:-1]
        )
        + " und "
        + words[-1]
    )


# ==========================================
# ANTWORT – GEÜBTE WÖRTER
# ==========================================

def answer_practiced_words(
    user_message,
    state
):

    if not is_practiced_words_request(
        user_message
    ):
        return None

    vocabulary_memory = get_vocabulary_memory(
        state
    )

    words = list(
        vocabulary_memory.keys()
    )

    if not words:
        return (
            "Du hast noch keine Wörter geübt."
        )

    word_list = format_word_list(
        words
    )

    return (
        "Du hast diese Wörter geübt: "
        + word_list
        + "."
    )


# ==========================================
# ANTWORT – WIE OFT WURDE EIN WORT GEÜBT
# ==========================================

def answer_practice_count(
    user_message,
    state
):

    word = extract_practice_count_word(
        user_message
    )

    if not word:
        return None

    vocabulary_memory = get_vocabulary_memory(
        state
    )

    word_memory = vocabulary_memory.get(
        word
    )

    if not word_memory:
        return (
            f"Du hast „{word}“ noch nicht geübt."
        )

    count = word_memory.get(
        "seen",
        0
    )

    if count == 1:
        return (
            f"Du hast „{word}“ 1-mal geübt."
        )

    return (
        f"Du hast „{word}“ {count}-mal geübt."
    )


# ==========================================
# FRAGE NACH WIEDERHOLUNG ERKENNEN
# ==========================================

def is_review_request(
    user_message
):

    message = normalize(
        user_message
    )

    questions = [
        "was soll ich wiederholen",
        "welche wörter soll ich wiederholen",
        "was muss ich wiederholen",
        "welche wörter muss ich wiederholen",
        "was soll ich üben",
        "welche wörter soll ich üben"
    ]

    return message.strip(
        " .?!"
    ) in questions


# ==========================================
# ANTWORT – WÖRTER ZUM WIEDERHOLEN
# ==========================================

def answer_review_words(
    user_message,
    state
):

    if not is_review_request(
        user_message
    ):
        return None

    words = get_words_for_review(
        state
    )

    if not words:
        return (
            "Im Moment musst du keine Wörter wiederholen."
        )

    word_list = format_word_list(
        words
    )

    return (
        "Diese Wörter solltest du wiederholen: "
        + word_list
        + "."
    )


# ==========================================
# MEMORY-ROUTER
# ==========================================

def handle_memory(
    user_message,
    state
):

    answer = answer_practiced_words(
        user_message,
        state
    )

    if answer:
        return answer

    answer = answer_practice_count(
        user_message,
        state
    )

    if answer:
        return answer

    answer = answer_review_words(
        user_message,
        state
    )

    if answer:
        return answer

    return None
