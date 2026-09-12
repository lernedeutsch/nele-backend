# ==========================================
# NELE – ĆWICZENIE Z BŁĘDÓW UCZNIA
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import normalize

from brain.memory.error_memory import (
    get_error_summary,
    get_errors_for_practice,
    mark_error_practiced
)


# ==========================================
# NAZWY RODZAJÓW BŁĘDÓW
# ==========================================

ERROR_PRACTICE_LABELS = {

    "word_order":
        "die Wortstellung",

    "article":
        "die Artikel",

    "grammar":
        "die Grammatik",

    "vocabulary":
        "den Wortschatz",

    "spelling":
        "die Rechtschreibung",

    "verb":
        "die Verben",

    "preposition":
        "die Präpositionen"
}


# ==========================================
# TEKST DO PORÓWNANIA
# ==========================================

def clean_error_practice_message(
    text
):

    if not text:
        return ""

    text = normalize(
        text
    )

    return text.strip(
        " .?!„“\"'"
    )


# ==========================================
# ŁADNA NAZWA BŁĘDU
# ==========================================

def get_error_practice_label(
    error_type
):

    return ERROR_PRACTICE_LABELS.get(
        error_type,
        "diesen Bereich"
    )


# ==========================================
# CZY ĆWICZENIE JEST AKTYWNE
# ==========================================

def is_error_practice_active(
    state
):

    if not state:
        return False

    return bool(
        state.get(
            "error_practice_active",
            False
        )
    )


# ==========================================
# ZAKOŃCZENIE ĆWICZENIA
# ==========================================

def finish_error_practice(
    state
):

    if state is None:
        return

    state[
        "error_practice_active"
    ] = False

    state[
        "error_practice_type"
    ] = None

    state[
        "error_practice_step"
    ] = 0

    state[
        "error_practice_attempts"
    ] = 0


# ==========================================
# ROZPOCZĘCIE ĆWICZENIA
# ==========================================

def start_error_practice(
    state,
    error_type=None
):

    if state is None:

        return (
            "Im Moment kann ich kein "
            "Fehlertraining starten."
        )


    # ======================================
    # JEŚLI NIE PODANO TYPU BŁĘDU,
    # BIORĘ PIERWSZY DO POWTÓRKI
    # ======================================

    if not error_type:

        errors = get_errors_for_practice(
            state
        )

        if not errors:

            return (
                "Im Moment habe ich keinen "
                "bestimmten Fehler gespeichert, "
                "den du üben musst."
            )

        error_type = errors[0]


    # ======================================
    # POBRANIE PRZYKŁADU
    # ======================================

    summary = get_error_summary(
        state,
        error_type
    )


    if not summary:

        return (
            "Dazu habe ich noch kein "
            "passendes Beispiel gespeichert."
        )


    wrong_sentence = summary.get(
        "last_wrong"
    )

    correct_sentence = summary.get(
        "last_correct"
    )


    if not wrong_sentence or not correct_sentence:

        return (
            "Dazu habe ich noch kein "
            "vollständiges Beispiel gespeichert."
        )


    # ======================================
    # USTAWIENIE AKTYWNEGO ĆWICZENIA
    # ======================================

    state[
        "error_practice_active"
    ] = True

    state[
        "error_practice_type"
    ] = error_type

    state[
        "error_practice_step"
    ] = 1

    state[
        "error_practice_attempts"
    ] = 0


    label = get_error_practice_label(
        error_type
    )


    return (
        f"Dann üben wir kurz {label}. "
        f"Welcher Satz ist richtig?\n\n"
        f"1. {wrong_sentence}\n"
        f"2. {correct_sentence}"
    )


# ==========================================
# CZY ODPOWIEDŹ OZNACZA:
# DRUGI WARIANT
# ==========================================

def is_second_answer(
    user_message
):

    message = clean_error_practice_message(
        user_message
    )

    answers = {
        "2",
        "satz 2",
        "nummer 2",
        "die 2",
        "der zweite",
        "der zweite satz",
        "zweite",
        "zwei"
    }

    return message in answers


# ==========================================
# CZY ODPOWIEDŹ OZNACZA:
# PIERWSZY WARIANT
# ==========================================

def is_first_answer(
    user_message
):

    message = clean_error_practice_message(
        user_message
    )

    answers = {
        "1",
        "satz 1",
        "nummer 1",
        "die 1",
        "der erste",
        "der erste satz",
        "erste",
        "eins"
    }

    return message in answers


# ==========================================
# CZY UŻYTKOWNIK CHCE ZAKOŃCZYĆ
# ==========================================

def wants_to_stop_error_practice(
    user_message
):

    message = clean_error_practice_message(
        user_message
    )

    stop_answers = {
        "stop",
        "stopp",
        "aufhören",
        "ich möchte aufhören",
        "nicht mehr",
        "ende"
    }

    return message in stop_answers


# ==========================================
# KROK 1
# WYBÓR POPRAWNEGO ZDANIA
# ==========================================

def handle_error_practice_step_one(
    user_message,
    state,
    summary
):

    wrong_sentence = summary.get(
        "last_wrong"
    )

    correct_sentence = summary.get(
        "last_correct"
    )


    user_clean = clean_error_practice_message(
        user_message
    )

    correct_clean = clean_error_practice_message(
        correct_sentence
    )

    wrong_clean = clean_error_practice_message(
        wrong_sentence
    )


    # ======================================
    # DOBRA ODPOWIEDŹ
    # ======================================

    if (
        is_second_answer(
            user_message
        )
        or
        user_clean == correct_clean
    ):

        state[
            "error_practice_step"
        ] = 2

        state[
            "error_practice_attempts"
        ] = 0

        return (
            "Richtig! Sehr gut. "
            f"„{correct_sentence}“ ist korrekt. "
            "Sag den richtigen Satz "
            "jetzt bitte selbst."
        )


    # ======================================
    # ZŁA ODPOWIEDŹ
    # ======================================

    if (
        is_first_answer(
            user_message
        )
        or
        user_clean == wrong_clean
    ):

        state[
            "error_practice_attempts"
        ] = (
            state.get(
                "error_practice_attempts",
                0
            )
            + 1
        )

        return (
            "Noch nicht. "
            "Achte auf die Wortstellung. "
            "Welcher Satz ist richtig?\n\n"
            f"1. {wrong_sentence}\n"
            f"2. {correct_sentence}"
        )


    # ======================================
    # NIEJASNA ODPOWIEDŹ
    # ======================================

    return (
        "Antworte bitte mit 1 oder 2. "
        "Welcher Satz ist richtig?\n\n"
        f"1. {wrong_sentence}\n"
        f"2. {correct_sentence}"
    )


# ==========================================
# KROK 2
# SAMODZIELNE POWIEDZENIE ZDANIA
# ==========================================

def handle_error_practice_step_two(
    user_message,
    state,
    summary
):

    correct_sentence = summary.get(
        "last_correct"
    )


    user_clean = clean_error_practice_message(
        user_message
    )

    correct_clean = clean_error_practice_message(
        correct_sentence
    )


    # ======================================
    # DOBRA ODPOWIEDŹ
    # ======================================

    if user_clean == correct_clean:

        error_type = state.get(
            "error_practice_type"
        )


        if error_type:

            mark_error_practiced(
                state,
                error_type
            )


        finish_error_practice(
            state
        )


        return (
            "Sehr gut! Genau richtig. "
            f"„{correct_sentence}“ "
            "Diesen Fehler hast du jetzt geübt."
        )


    # ======================================
    # ZŁA ODPOWIEDŹ
    # ======================================

    state[
        "error_practice_attempts"
    ] = (
        state.get(
            "error_practice_attempts",
            0
        )
        + 1
    )


    return (
        "Fast. "
        f"Richtig ist: „{correct_sentence}“ "
        "Sag den Satz bitte noch einmal."
    )


# ==========================================
# GŁÓWNA OBSŁUGA AKTYWNEGO ĆWICZENIA
# ==========================================

def handle_error_practice(
    user_message,
    state
):

    if state is None:
        return None


    if not is_error_practice_active(
        state
    ):

        return None


    # ======================================
    # STOP
    # ======================================

    if wants_to_stop_error_practice(
        user_message
    ):

        finish_error_practice(
            state
        )

        return (
            "Okay, wir beenden das "
            "Fehlertraining."
        )


    # ======================================
    # AKTUALNY TYP BŁĘDU
    # ======================================

    error_type = state.get(
        "error_practice_type"
    )


    if not error_type:

        finish_error_practice(
            state
        )

        return None


    summary = get_error_summary(
        state,
        error_type
    )


    if not summary:

        finish_error_practice(
            state
        )

        return None


    step = state.get(
        "error_practice_step",
        1
    )


    # ======================================
    # KROK 1
    # ======================================

    if step == 1:

        return handle_error_practice_step_one(
            user_message,
            state,
            summary
        )


    # ======================================
    # KROK 2
    # ======================================

    if step == 2:

        return handle_error_practice_step_two(
            user_message,
            state,
            summary
        )


    # ======================================
    # NIEZNANY KROK
    # ======================================

    finish_error_practice(
        state
    )

    return None
