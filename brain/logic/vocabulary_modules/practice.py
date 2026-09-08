# ==========================================
# NELE – WORTSCHATZMODUL: ÜBUNG
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY

from brain.logic.vocabulary_modules.helpers import (
    clean_vocabulary_word,
    display_vocabulary_word,
    remember_vocabulary_word
)

from brain.memory.vocabulary_memory import (
    remember_practiced_word,
    remember_correct_answer,
    remember_mistake
)


# ==========================================
# ÜBUNG – WORT ERKENNEN
# ==========================================

def extract_practice_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [
        "übe mit mir das wort ",
        "übe mit mir ",
        "üben wir das wort ",
        "üben wir ",
        "ich möchte das wort ",
        "ich möchte ",
        "lass uns das wort ",
        "lass uns "
    ]

    patterns.sort(
        key=len,
        reverse=True
    )

    for pattern in patterns:

        if not message.startswith(
            pattern
        ):
            continue

        word = message[
            len(pattern):
        ]

        word = clean_vocabulary_word(
            word
        )

        endings = [
            " üben",
            " lernen"
        ]

        for ending in endings:

            if word.endswith(
                ending
            ):

                word = word[
                    :-len(ending)
                ].strip()

                break

        if word:
            return word

    return None


# ==========================================
# ÜBUNG – STARTEN
# ==========================================

def start_vocabulary_practice(
    user_message,
    state=None
):

    if state is None:
        return None

    word = extract_practice_word(
        user_message
    )

    if not word:
        return None

    if word not in VOCABULARY:
        return None

    remember_vocabulary_word(
        state,
        word
    )

    remember_practiced_word(
        word,
        state
    )

    state[
        "vocabulary_practice_active"
    ] = True

    state[
        "vocabulary_practice_word"
    ] = word

    state[
        "vocabulary_practice_type"
    ] = "meaning"

    display_word = display_vocabulary_word(
        word
    )

    return (
        f"Was bedeutet „{display_word}“?"
    )


# ==========================================
# ÜBUNG – AKTIV?
# ==========================================

def is_vocabulary_practice_active(
    state
):

    if state is None:
        return False

    return bool(
        state.get(
            "vocabulary_practice_active"
        )
    )


# ==========================================
# TEXT FÜR VERGLEICH BEREINIGEN
# ==========================================

def clean_practice_answer(
    text
):

    text = normalize(
        text
    )

    text = text.strip(
        " .?!„“\"'"
    )

    return text


# ==========================================
# EINFACHE BEDEUTUNG HOLEN
# ==========================================

def get_simple_practice_meaning(
    word
):

    vocabulary_entry = VOCABULARY.get(
        word
    )

    if not vocabulary_entry:
        return None

    simple_meaning = vocabulary_entry.get(
        "simple_meaning"
    )

    if simple_meaning:
        return simple_meaning

    return vocabulary_entry.get(
        "meaning"
    )


# ==========================================
# RICHTIGE ANTWORT PRÜFEN
# ==========================================

def is_correct_practice_answer(
    user_message,
    word
):

    vocabulary_entry = VOCABULARY.get(
        word
    )

    if not vocabulary_entry:
        return False

    answer = clean_practice_answer(
        user_message
    )

    if not answer:
        return False

    possible_answers = []

    practice_answers = vocabulary_entry.get(
        "practice_answers"
    )

    if practice_answers:

        if isinstance(
            practice_answers,
            list
        ):
            possible_answers.extend(
                practice_answers
            )

        else:
            possible_answers.append(
                practice_answers
            )

    simple_meaning = vocabulary_entry.get(
        "simple_meaning"
    )

    if simple_meaning:
        possible_answers.append(
            simple_meaning
        )

    meaning = vocabulary_entry.get(
        "meaning"
    )

    if meaning:
        possible_answers.append(
            meaning
        )

    for possible_answer in possible_answers:

        cleaned_possible_answer = clean_practice_answer(
            possible_answer
        )

        if not cleaned_possible_answer:
            continue

        if answer == cleaned_possible_answer:
            return True

        if (
            len(answer) >= 4
            and answer in cleaned_possible_answer
        ):
            return True

        if (
            len(cleaned_possible_answer) >= 4
            and cleaned_possible_answer in answer
        ):
            return True

    return False


# ==========================================
# ÜBUNG BEENDEN
# ==========================================

def finish_vocabulary_practice(
    state
):

    if state is None:
        return

    state[
        "vocabulary_practice_active"
    ] = False

    state[
        "vocabulary_practice_word"
    ] = None

    state[
        "vocabulary_practice_type"
    ] = None


# ==========================================
# ANTWORT DES SCHÜLERS PRÜFEN
# ==========================================

def answer_vocabulary_practice(
    user_message,
    state=None
):

    if state is None:
        return None

    if not is_vocabulary_practice_active(
        state
    ):
        return None

    word = state.get(
        "vocabulary_practice_word"
    )

    if not word:
        return None

    if word not in VOCABULARY:
        return None

    display_word = display_vocabulary_word(
        word
    )

    simple_meaning = get_simple_practice_meaning(
        word
    )

    if is_correct_practice_answer(
        user_message,
        word
    ):

        remember_correct_answer(
            word,
            state
        )

        finish_vocabulary_practice(
            state
        )

        if simple_meaning:

            return (
                f"Richtig! {simple_meaning}"
            )

        return "Richtig!"

    remember_mistake(
        word,
        state
    )

    finish_vocabulary_practice(
        state
    )

    if simple_meaning:

        return (
            f"Noch nicht ganz. "
            f"{simple_meaning}"
        )

    return (
        f"Noch nicht ganz. "
        f"Schau dir „{display_word}“ noch einmal an."
    )
