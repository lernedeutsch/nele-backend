# ==========================================
# NELE – POSTĘP W BŁĘDACH UCZNIA
# STUDENT MEMORY 2.0
# ==========================================

from datetime import datetime, timezone

from brain.logic.matcher import normalize

from brain.memory.error_memory import (
    get_error_memory,
    get_error_summary,
    get_most_common_errors
)

from brain.memory.error_review import (
    get_next_error_review
)


# ==========================================
# NAZWY OBSZARÓW
# ==========================================

ERROR_PROGRESS_LABELS = {

    "word_order":
        "Wortstellung",

    "article":
        "Artikel",

    "grammar":
        "Grammatik",

    "vocabulary":
        "Wortschatz",

    "spelling":
        "Rechtschreibung",

    "verb":
        "Verben",

    "preposition":
        "Präpositionen"
}


# ==========================================
# SŁOWA DO ROZPOZNAWANIA OBSZARU
# ==========================================

ERROR_PROGRESS_KEYWORDS = {

    "word_order": {
        "wortstellung",
        "satzstellung"
    },

    "article": {
        "artikel",
        "artikeln"
    },

    "grammar": {
        "grammatik"
    },

    "vocabulary": {
        "wortschatz",
        "vokabeln"
    },

    "spelling": {
        "rechtschreibung"
    },

    "verb": {
        "verb",
        "verben"
    },

    "preposition": {
        "präposition",
        "präpositionen"
    }
}


# ==========================================
# WIADOMOŚĆ DO PORÓWNANIA
# ==========================================

def clean_error_progress_message(
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
# ŁADNA NAZWA OBSZARU
# ==========================================

def get_error_progress_label(
    error_type
):

    return ERROR_PROGRESS_LABELS.get(
        error_type,
        "diesem Bereich"
    )


# ==========================================
# ROZPOZNANIE OBSZARU W PYTANIU
# ==========================================

def extract_error_progress_type(
    user_message
):

    message = clean_error_progress_message(
        user_message
    )


    for error_type, keywords in (
        ERROR_PROGRESS_KEYWORDS.items()
    ):

        for keyword in keywords:

            if keyword in message:

                return error_type


    return None


# ==========================================
# PYTANIE:
# CZY SIĘ POPRAWIŁEM?
# ==========================================

def is_general_improvement_question(
    user_message
):

    message = clean_error_progress_message(
        user_message
    )

    questions = {

        "habe ich mich verbessert",
        "habe ich mich schon verbessert",
        "werde ich besser",
        "bin ich besser geworden",
        "mache ich fortschritte",
        "habe ich fortschritte gemacht",
        "wie ist mein fortschritt",
        "wie sind meine fortschritte",
        "wie läuft mein lernen"
    }

    return message in questions


# ==========================================
# PYTANIE:
# ILE BŁĘDÓW ĆWICZYŁEM?
# ==========================================

def is_error_practice_count_question(
    user_message
):

    message = clean_error_progress_message(
        user_message
    )

    questions = {

        "wie viele fehler habe ich geübt",
        "wie oft habe ich meine fehler geübt",
        "wie viele fehlerübungen habe ich gemacht",
        "wie oft habe ich fehler geübt",
        "wie viele fehler habe ich schon geübt"
    }

    return message in questions


# ==========================================
# PYTANIE:
# KIEDY NASTĘPNA POWTÓRKA?
# ==========================================

def is_next_error_review_question(
    user_message
):

    message = clean_error_progress_message(
        user_message
    )

    questions = {

        "wann soll ich meine fehler wiederholen",
        "wann soll ich meine fehler wieder üben",
        "wann muss ich meine fehler wiederholen",
        "wann muss ich meine fehler wieder üben",
        "wann üben wir meine fehler wieder",
        "wann wiederholen wir meine fehler",
        "wann machen wir mit meinen fehlern weiter",
        "wann übe ich meine fehler wieder",
        "wann ist die nächste fehlerübung",
        "wann ist meine nächste fehlerübung"
    }

    return message in questions


# ==========================================
# PYTANIE:
# JAK DOBRZE UMIEM KONKRETNY OBSZAR?
# ==========================================

def is_specific_error_progress_question(
    user_message
):

    message = clean_error_progress_message(
        user_message
    )

    error_type = extract_error_progress_type(
        user_message
    )


    if not error_type:
        return False


    patterns = (
        "wie gut",
        "wie sicher",
        "wie ist mein fortschritt",
        "wie sind meine fortschritte",
        "wie läuft es mit",
        "kann ich schon"
    )


    return any(
        pattern in message
        for pattern in patterns
    )


# ==========================================
# SUMA WSZYSTKICH ĆWICZEŃ BŁĘDÓW
# ==========================================

def get_total_error_practice_count(
    state
):

    error_memory = get_error_memory(
        state
    )

    total = 0


    for error_item in error_memory.values():

        if not isinstance(
            error_item,
            dict
        ):

            continue


        total += error_item.get(
            "practice_count",
            0
        )


    return total


# ==========================================
# LICZBA OPANOWANYCH OBSZARÓW
# ==========================================

def get_mastered_error_count(
    state
):

    error_memory = get_error_memory(
        state
    )

    count = 0


    for error_item in error_memory.values():

        if not isinstance(
            error_item,
            dict
        ):

            continue


        if error_item.get(
            "mastered",
            False
        ):

            count += 1


    return count


# ==========================================
# ODCZYT DATY ISO
# ==========================================

def parse_progress_timestamp(
    timestamp
):

    if not timestamp:
        return None


    try:

        parsed = datetime.fromisoformat(
            str(
                timestamp
            ).replace(
                "Z",
                "+00:00"
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    if parsed.tzinfo is None:

        parsed = parsed.replace(
            tzinfo=timezone.utc
        )


    return parsed.astimezone(
        timezone.utc
    )


# ==========================================
# ODPOWIEDŹ:
# KIEDY NASTĘPNA POWTÓRKA?
# ==========================================

def answer_next_error_review(
    state
):

    next_review = get_next_error_review(
        state
    )


    if not next_review:

        return (
            "Im Moment ist keine weitere "
            "Fehlerübung geplant."
        )


    review_at = parse_progress_timestamp(
        next_review.get(
            "review_at"
        )
    )


    if review_at is None:

        return (
            "Wir machen später mit deinen "
            "Fehlern weiter."
        )


    now = datetime.now(
        timezone.utc
    )


    seconds = (
        review_at
        -
        now
    ).total_seconds()


    # ======================================
    # POWTÓRKA JEST JUŻ GOTOWA
    # ======================================

    if seconds <= 0:

        return (
            "Jetzt ist eine gute Zeit für die "
            "Wiederholung. Wir können gleich "
            "deine Fehler üben."
        )


    hours = seconds / 3600


    # ======================================
    # JESZCZE DZISIAJ
    # ======================================

    if hours < 8:

        return (
            "Heute musst du sie noch nicht "
            "wiederholen. Wir machen später weiter."
        )


    # ======================================
    # OKOŁO JEDNEGO DNIA
    # ======================================

    if hours < 36:

        return (
            "Heute musst du deine Fehler nicht "
            "mehr üben. Wir machen morgen weiter."
        )


    # ======================================
    # OKOŁO DWÓCH DNI
    # ======================================

    if hours < 60:

        return (
            "Wir wiederholen deine Fehler "
            "übermorgen."
        )


    # ======================================
    # WIĘCEJ NIŻ DWA DNI
    # ======================================

    days = max(
        1,
        round(
            hours / 24
        )
    )


    return (
        f"Wir wiederholen deine Fehler "
        f"in {days} Tagen."
    )


# ==========================================
# ODPOWIEDŹ:
# CZY SIĘ POPRAWIŁEM?
# ==========================================

def answer_general_improvement(
    state
):

    error_memory = get_error_memory(
        state
    )


    saved_errors = [
        error_type
        for error_type, error_item
        in error_memory.items()
        if isinstance(
            error_item,
            dict
        )
        and error_item.get(
            "count",
            0
        ) > 0
    ]


    if not saved_errors:

        return (
            "Dazu habe ich noch nicht genug "
            "von dir gespeichert."
        )


    practice_count = (
        get_total_error_practice_count(
            state
        )
    )

    mastered_count = (
        get_mastered_error_count(
            state
        )
    )


    if practice_count == 0:

        return (
            "Wir haben schon Fehler gefunden, "
            "aber noch nicht genug geübt, "
            "um deinen Fortschritt gut zu beurteilen."
        )


    if mastered_count > 0:

        if mastered_count == 1:

            return (
                "Ja, du hast Fortschritte gemacht. "
                "Einen Bereich hast du schon gut gefestigt."
            )


        return (
            "Ja, du hast Fortschritte gemacht. "
            f"{mastered_count} Bereiche hast du "
            "schon gut gefestigt."
        )


    common_errors = get_most_common_errors(
        state,
        limit=1
    )


    if common_errors:

        error_type = common_errors[0]

        summary = get_error_summary(
            state,
            error_type
        )

        label = get_error_progress_label(
            error_type
        )


        if summary:

            streak = summary.get(
                "correct_streak",
                0
            )


            if streak >= 2:

                return (
                    "Ja, du machst Fortschritte. "
                    f"Bei der {label} bist du "
                    "schon deutlich sicherer. "
                    "Wir wiederholen das später noch einmal."
                )


            if streak == 1:

                return (
                    "Ja, du machst Fortschritte. "
                    f"Die {label} hast du schon "
                    "einmal richtig geübt. "
                    "Später wiederholen wir sie noch einmal."
                )


    return (
        "Ja, du machst Fortschritte. "
        "Wir üben deine Fehler Schritt für Schritt weiter."
    )


# ==========================================
# ODPOWIEDŹ:
# ILE RAZY ĆWICZYŁEM BŁĘDY?
# ==========================================

def answer_error_practice_count(
    state
):

    practice_count = (
        get_total_error_practice_count(
            state
        )
    )


    if practice_count == 0:

        return (
            "Bisher haben wir noch keine "
            "Fehlerübung abgeschlossen."
        )


    if practice_count == 1:

        return (
            "Du hast bisher eine "
            "Fehlerübung abgeschlossen."
        )


    return (
        f"Du hast bisher {practice_count} "
        "Fehlerübungen abgeschlossen."
    )


# ==========================================
# ODPOWIEDŹ:
# JAK DOBRZE UMIEM KONKRETNY OBSZAR?
# ==========================================

def answer_specific_error_progress(
    state,
    error_type
):

    summary = get_error_summary(
        state,
        error_type
    )

    label = get_error_progress_label(
        error_type
    )


    if not summary:

        return (
            f"Zur {label} habe ich noch "
            "nicht genug gespeichert."
        )


    error_count = summary.get(
        "count",
        0
    )


    if error_count <= 0:

        return (
            f"Zur {label} habe ich noch "
            "keinen Fehler gespeichert."
        )


    practice_count = summary.get(
        "practice_count",
        0
    )

    correct_streak = summary.get(
        "correct_streak",
        0
    )

    mastered = summary.get(
        "mastered",
        False
    )

    needs_practice = summary.get(
        "needs_practice",
        False
    )


    if mastered:

        return (
            f"Die {label} kannst du schon gut. "
            "Du hast sie mehrmals richtig geübt."
        )


    if correct_streak >= 2:

        return (
            f"Bei der {label} bist du schon "
            "ziemlich sicher. "
            "Eine spätere Wiederholung fehlt "
            "noch, dann ist sie gut gefestigt."
        )


    if correct_streak == 1:

        return (
            f"Bei der {label} bist du auf "
            "einem guten Weg. "
            "Du hast sie schon einmal richtig geübt. "
            "Später wiederholen wir sie noch einmal."
        )


    if practice_count > 0:

        return (
            f"Die {label} hast du schon geübt, "
            "aber wir sollten sie noch weiter festigen."
        )


    if needs_practice:

        return (
            f"Bei der {label} machen wir noch Fehler. "
            "Das sollten wir noch üben."
        )


    return (
        f"Zur {label} habe ich schon etwas gespeichert. "
        "Wir schauen uns das später noch einmal an."
    )


# ==========================================
# GŁÓWNY ROUTER POSTĘPU
# ==========================================

def handle_error_progress(
    user_message,
    state
):

    if state is None:
        return None


    # ======================================
    # KIEDY NASTĘPNA POWTÓRKA?
    # ======================================

    if is_next_error_review_question(
        user_message
    ):

        return answer_next_error_review(
            state
        )


    # ======================================
    # KONKRETNY OBSZAR
    # ======================================

    if is_specific_error_progress_question(
        user_message
    ):

        error_type = extract_error_progress_type(
            user_message
        )

        if error_type:

            return answer_specific_error_progress(
                state,
                error_type
            )


    # ======================================
    # LICZBA ĆWICZEŃ
    # ======================================

    if is_error_practice_count_question(
        user_message
    ):

        return answer_error_practice_count(
            state
        )


    # ======================================
    # OGÓLNY POSTĘP
    # ======================================

    if is_general_improvement_question(
        user_message
    ):

        return answer_general_improvement(
            state
        )


    return None
