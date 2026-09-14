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

from brain.memory.student_progress import (
    remember_completed_exercise,
    remember_learning_topic
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


    # ======================================
    # WORT IM WORTSCHATZ SPEICHERN
    # ======================================

    remember_vocabulary_word(
        state,
        word
    )

    remember_practiced_word(
        word,
        state
    )


    # ======================================
    # AKTIVE ÜBUNG
    # ======================================

    state[
        "vocabulary_practice_active"
    ] = True

    state[
        "vocabulary_practice_word"
    ] = word

    state[
        "vocabulary_practice_type"
    ] = "meaning"


    # ======================================
    # OSTATNIA AKTYWNOŚĆ UŻYTKOWNIKA
    # ======================================

    state[
        "last_activity"
    ] = "vocabulary"

    state[
        "last_activity_detail"
    ] = word


    # ======================================
    # STUDENT MEMORY 2.0
    # OSTATNI TEMAT I DATA NAUKI
    # ======================================

    display_word = display_vocabulary_word(
        word
    )

    remember_learning_topic(
        state,
        f"Wortschatz: {display_word}"
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


    # ======================================
    # SPEZIELLE ÜBUNGSANTWORTEN
    # ======================================

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


    # ======================================
    # EINFACHE BEDEUTUNG
    # ======================================

    simple_meaning = vocabulary_entry.get(
        "simple_meaning"
    )

    if simple_meaning:

        possible_answers.append(
            simple_meaning
        )


    # ======================================
    # PEŁNE ZNACZENIE
    #
    # WAŻNE:
    # wcześniej tego brakowało.
    # Nele potrafiła wyświetlić "meaning",
    # ale nie uznawała go za poprawną
    # odpowiedź użytkownika.
    # ======================================

    meaning = vocabulary_entry.get(
        "meaning"
    )

    if meaning:

        possible_answers.append(
            meaning
        )


    # ======================================
    # USUWANIE DUPLIKATÓW
    # ======================================

    result = []
    seen = set()

    for answer in possible_answers:

        if not answer:
            continue

        cleaned = clean_practice_answer(
            answer
        )

        if not cleaned:
            continue

        if cleaned in seen:
            continue

        seen.add(
            cleaned
        )

        result.append(
            answer
        )


    return result


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
    # DOKŁADNIE TA SAMA ODPOWIEDŹ
    # ======================================

    if answer == possible_answer:
        return True


    # ======================================
    # NEGACJA MUSI SIĘ ZGADZAĆ
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
    # SŁOWA ODPOWIEDZI
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
    # ISTOTNE SŁOWA
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
    # UŻYTKOWNIK MOŻE POWIEDZIEĆ WIĘCEJ
    #
    # Poprawna odpowiedź może być częścią
    # dłuższego zdania użytkownika.
    #
    # Nie robimy już odwrotnego testu,
    # ponieważ zbyt krótka odpowiedź typu:
    #
    # "Zimmer ist ein Raum"
    #
    # nie powinna automatycznie zaliczać
    # pełnej definicji.
    # ======================================

    if meaningful_possible_words.issubset(
        meaningful_answer_words
    ):
        return True


    return False


# ==========================================
# RICHTIGE BEDEUTUNG PRÜFEN
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
# GEGENTEIL HOLEN
# ==========================================

def get_practice_opposite(
    word
):

    vocabulary_entry = VOCABULARY.get(
        word
    )

    if not vocabulary_entry:
        return None

    opposite = vocabulary_entry.get(
        "opposite"
    )

    if not opposite:
        return None

    if isinstance(
        opposite,
        list
    ):

        if not opposite:
            return None

        return opposite[0]

    return opposite


# ==========================================
# GEGENTEIL PRÜFEN
# ==========================================

def is_correct_opposite_answer(
    user_message,
    word
):

    opposite = get_practice_opposite(
        word
    )

    if not opposite:
        return False

    answer = clean_practice_answer(
        user_message
    )

    opposite = clean_practice_answer(
        opposite
    )

    if not answer:
        return False

    if answer == opposite:
        return True

    words = get_answer_words(
        answer
    )

    if opposite in words:
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
# NÄCHSTE FRAGE – GEGENTEIL
# ==========================================

def ask_opposite_question(
    word,
    state
):

    opposite = get_practice_opposite(
        word
    )

    if not opposite:

        finish_vocabulary_practice(
            state
        )

        return None

    state[
        "vocabulary_practice_type"
    ] = "opposite"

    display_word = display_vocabulary_word(
        word
    )

    return (
        f"Was ist das Gegenteil von „{display_word}“?"
    )


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

    practice_type = state.get(
        "vocabulary_practice_type"
    )


    # ======================================
    # 1. BEDEUTUNG
    # ======================================

    if practice_type == "meaning":

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

            next_question = ask_opposite_question(
                word,
                state
            )

            if next_question:

                if simple_meaning:

                    return (
                        f"Richtig! {simple_meaning}\n\n"
                        f"{next_question}"
                    )

                return (
                    f"Richtig!\n\n"
                    f"{next_question}"
                )


            # ==================================
            # STUDENT MEMORY 2.0
            # CAŁE ĆWICZENIE UKOŃCZONE
            # ==================================

            remember_completed_exercise(
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

        if simple_meaning:

            return (
                f"Noch nicht ganz. "
                f"{simple_meaning}\n\n"
                f"Versuch es noch einmal."
            )

        return (
            "Noch nicht ganz. "
            "Versuch es noch einmal."
        )


    # ======================================
    # 2. GEGENTEIL
    # ======================================

    if practice_type == "opposite":

        opposite = get_practice_opposite(
            word
        )

        if not opposite:

            finish_vocabulary_practice(
                state
            )

            return None

        opposite_display = display_vocabulary_word(
            opposite
        )

        if is_correct_opposite_answer(
            user_message,
            word
        ):

            remember_correct_answer(
                word,
                state
            )


            # ==================================
            # STUDENT MEMORY 2.0
            # CAŁE ĆWICZENIE UKOŃCZONE
            # ==================================

            remember_completed_exercise(
                state
            )

            finish_vocabulary_practice(
                state
            )

            return (
                f"Richtig! Das Gegenteil ist "
                f"„{opposite_display}“. "
                f"Sehr gut! Du hast "
                f"„{display_vocabulary_word(word)}“ "
                f"erfolgreich geübt."
            )


        remember_mistake(
            word,
            state
        )

        return (
            f"Noch nicht ganz. "
            f"Das Gegenteil von "
            f"„{display_vocabulary_word(word)}“ "
            f"ist „{opposite_display}“.\n\n"
            f"Versuch es noch einmal."
        )


    # ======================================
    # UNBEKANNTER ÜBUNGSTYP
    # ======================================

    finish_vocabulary_practice(
        state
    )

    return None
