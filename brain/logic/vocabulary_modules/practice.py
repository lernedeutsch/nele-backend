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
# TEXT IN WÖRTER AUFTEILEN
# ==========================================

def get_answer_words(
    text
):

    text = clean_practice_answer(
        text
    )

    if not text:
        return []

    return [
        word.strip(
            " .,!?:;„“\"'"
        )
        for word in text.split()
        if word.strip(
            " .,!?:;„“\"'"
        )
    ]


# ==========================================
# NEGATION ERKENNEN
# ==========================================

def has_negation(
    text
):

    words = get_answer_words(
        text
    )

    negations = {
        "nicht",
        "kein",
        "keine",
        "keinen",
        "keinem",
        "keiner"
    }

    return any(
        word in negations
        for word in words
    )


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
# MÖGLICHE ANTWORTEN HOLEN
# ==========================================

def get_possible_practice_answers(
    word
):

    vocabulary_entry = VOCABULARY.get(
        word
    )

    if not vocabulary_entry:
        return []

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

    return possible_answers


# ==========================================
# EINZELNE ANTWORT VERGLEICHEN
# ==========================================

def answers_match(
    answer,
    possible_answer
):

    answer = clean_practice_answer(
        answer
    )

    possible_answer = clean_practice_answer(
        possible_answer
    )

    if not answer or not possible_answer:
        return False


    # ======================================
    # GENAU GLEICH
    # ======================================

    if answer == possible_answer:
        return True


    # ======================================
    # NEGATION MUSS ÜBEREINSTIMMEN
    #
    # "nicht schnell" ≠ "sehr schnell"
    # ======================================

    answer_has_negation = has_negation(
        answer
    )

    possible_has_negation = has_negation(
        possible_answer
    )

    if (
        answer_has_negation
        != possible_has_negation
    ):
        return False


    # ======================================
    # WÖRTER VERGLEICHEN
    # ======================================

    answer_words = set(
        get_answer_words(
            answer
        )
    )

    possible_words = set(
        get_answer_words(
            possible_answer
        )
    )

    if not answer_words:
        return False

    if not possible_words:
        return False


    # ======================================
    # KURZE RICHTIGE ANTWORT
    #
    # Beispiel:
    # mögliche Antwort: "sehr groß"
    # Schüler: "sehr groß"
    #
    # oder:
    # mögliche Antwort: "sehr groß"
    # Schüler: "groß"
    # ======================================

    meaningful_answer_words = {
        word
        for word in answer_words
        if len(word) >= 3
    }

    meaningful_possible_words = {
        word
        for word in possible_words
        if len(word) >= 3
    }

    if not meaningful_answer_words:
        return False

    if not meaningful_possible_words:
        return False


    # ======================================
    # ALLE WICHTIGEN WÖRTER DER
    # SCHÜLERANTWORT MÜSSEN PASSEN
    # ======================================

    if meaningful_answer_words.issubset(
        meaningful_possible_words
    ):
        return True


    # ======================================
    # ODER ALLE WICHTIGEN WÖRTER DER
    # MUSTERANTWORT SIND VORHANDEN
    # ======================================

    if meaningful_possible_words.issubset(
        meaningful_answer_words
    ):
        return True

    return False


# ==========================================
# RICHTIGE ANTWORT PRÜFEN
# ==========================================

def is_correct_practice_answer(
    user_message,
    word
):

    answer = clean_practice_answer(
        user_message
    )

    if not answer:
        return False

    possible_answers = get_possible_practice_answers(
        word
    )

    if not possible_answers:
        return False

    for possible_answer in possible_answers:

        if answers_match(
            answer,
            possible_answer
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
