# ==========================================
# NELE – ROUTER FÜR FEHLERSPEICHER
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import normalize

from brain.logic.error_practice import (
    start_error_practice
)

from brain.memory.error_memory import (
    get_error_summary,
    get_most_common_errors,
    get_errors_for_practice
)


# ==========================================
# NAZWY BŁĘDÓW DLA UŻYTKOWNIKA
# ==========================================

ERROR_LABELS = {

    "word_order":
        "der Wortstellung",

    "article":
        "den Artikeln",

    "grammar":
        "der Grammatik",

    "vocabulary":
        "dem Wortschatz",

    "spelling":
        "der Rechtschreibung",

    "verb":
        "den Verben",

    "preposition":
        "den Präpositionen"
}


# ==========================================
# WIADOMOŚĆ DO PORÓWNANIA
# ==========================================

def clean_error_memory_message(
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
# CZY UŻYTKOWNIK PYTA O SWOJE BŁĘDY
# ==========================================

def is_error_memory_question(
    user_message
):

    message = clean_error_memory_message(
        user_message
    )

    questions = {

        "wo mache ich oft fehler",
        "wo mache ich fehler",
        "welche fehler mache ich oft",
        "welche fehler mache ich",
        "was sind meine häufigsten fehler",
        "was sind meine fehler",
        "welche fehler habe ich",
        "wobei mache ich oft fehler",
        "wobei mache ich fehler"
    }

    return message in questions


# ==========================================
# CZY UŻYTKOWNIK PYTA,
# CO POWINIEN ĆWICZYĆ
# ==========================================

def is_error_practice_question(
    user_message
):

    message = clean_error_memory_message(
        user_message
    )

    questions = {

        "welche fehler soll ich üben",
        "welche fehler muss ich üben",
        "was soll ich bei meinen fehlern üben",
        "welche fehler soll ich wiederholen",
        "was soll ich wegen meiner fehler üben"
    }

    return message in questions


# ==========================================
# CZY UŻYTKOWNIK CHCE ROZPOCZĄĆ
# ĆWICZENIE SWOICH BŁĘDÓW
# ==========================================

def is_error_practice_start_request(
    user_message
):

    message = clean_error_memory_message(
        user_message
    )

    requests = {

        "ich möchte meine fehler üben",
        "ich will meine fehler üben",
        "lass uns meine fehler üben",
        "wir können meine fehler üben",
        "ich möchte fehler üben",
        "ich will fehler üben",
        "lass uns fehler üben",
        "fehler üben",
        "meine fehler üben",
        "ich möchte meine fehler trainieren",
        "ich will meine fehler trainieren",
        "lass uns meine fehler trainieren"
    }

    return message in requests


# ==========================================
# ŁADNA NAZWA TYPU BŁĘDU
# ==========================================

def get_error_label(
    error_type
):

    return ERROR_LABELS.get(
        error_type,
        "diesem Bereich"
    )


# ==========================================
# ODPOWIEDŹ O NAJCZĘSTSZYCH BŁĘDACH
# ==========================================

def answer_error_memory_question(
    state
):

    common_errors = get_most_common_errors(
        state,
        limit=3
    )


    if not common_errors:

        return (
            "Ich habe bisher noch keine "
            "wiederkehrenden Fehler von dir gespeichert."
        )


    main_error = common_errors[0]

    summary = get_error_summary(
        state,
        main_error
    )


    if not summary:

        return (
            "Ich habe bisher noch keine "
            "wiederkehrenden Fehler von dir gespeichert."
        )


    label = get_error_label(
        main_error
    )

    count = summary.get(
        "count",
        0
    )

    last_wrong = summary.get(
        "last_wrong"
    )

    last_correct = summary.get(
        "last_correct"
    )


    # ======================================
    # PODSTAWOWA ODPOWIEDŹ
    # ======================================

    if count == 1:

        answer = (
            f"Du hattest bisher einen Fehler bei "
            f"{label}."
        )

    else:

        answer = (
            f"Du machst noch öfter Fehler bei "
            f"{label}."
        )


    # ======================================
    # OSTATNI PRZYKŁAD
    # ======================================

    if last_wrong and last_correct:

        answer += (
            f' Zuletzt hast du gesagt: '
            f'„{last_wrong}“ '
            f'Richtig ist: '
            f'„{last_correct}“'
        )


    return answer


# ==========================================
# ODPOWIEDŹ:
# CO POWINIENEM ĆWICZYĆ?
# ==========================================

def answer_error_practice_question(
    state
):

    errors = get_errors_for_practice(
        state
    )


    if not errors:

        return (
            "Im Moment habe ich keinen "
            "bestimmten Fehler gespeichert, "
            "den du besonders üben musst."
        )


    error_type = errors[0]

    summary = get_error_summary(
        state,
        error_type
    )

    label = get_error_label(
        error_type
    )


    if not summary:

        return (
            f"Du solltest noch etwas bei "
            f"{label} üben."
        )


    last_wrong = summary.get(
        "last_wrong"
    )

    last_correct = summary.get(
        "last_correct"
    )


    if last_wrong and last_correct:

        return (
            f"Du solltest noch etwas bei "
            f"{label} üben. "
            f'Zum Beispiel: „{last_wrong}“ '
            f'→ „{last_correct}“'
        )


    return (
        f"Du solltest noch etwas bei "
        f"{label} üben."
    )


# ==========================================
# GŁÓWNY ROUTER
# ==========================================

def handle_error_memory(
    user_message,
    state
):

    if state is None:
        return None


    # ======================================
    # ROZPOCZĘCIE ĆWICZENIA BŁĘDÓW
    # ======================================

    if is_error_practice_start_request(
        user_message
    ):

        return start_error_practice(
            state
        )


    # ======================================
    # PYTANIE O SWOJE BŁĘDY
    # ======================================

    if is_error_memory_question(
        user_message
    ):

        return answer_error_memory_question(
            state
        )


    # ======================================
    # PYTANIE O BŁĘDY DO ĆWICZENIA
    # ======================================

    if is_error_practice_question(
        user_message
    ):

        return answer_error_practice_question(
            state
        )


    return None
