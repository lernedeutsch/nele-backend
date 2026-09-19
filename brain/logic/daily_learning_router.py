# ==========================================
# NELE – DAILY LEARNING ROUTER
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import (
    normalize
)

from brain.memory.daily_learning import (
    get_daily_learning_summary
)


# ==========================================
# CZYSZCZENIE PYTANIA
# ==========================================

def clean_message(
    text
):

    return normalize(
        str(
            text or ""
        )
    ).strip(
        " .?!„“\"'"
    )


# ==========================================
# ŁADNE WYŚWIETLANIE SŁOWA
# ==========================================

def display_word(
    word
):

    word = str(
        word or ""
    ).strip()


    if not word:

        return ""


    return (
        word[:1].upper()
        + word[1:]
    )


# ==========================================
# NAZWA BŁĘDU PO NIEMIECKU
# ==========================================

def display_error(
    error_type
):

    error_type = str(
        error_type or ""
    ).strip().lower()


    names = {

        "word_order":
            "Wortstellung",

        "wortstellung":
            "Wortstellung",

        "article":
            "Artikel",

        "articles":
            "Artikel",

        "artikel":
            "Artikel",

        "grammar":
            "Grammatik",

        "grammatik":
            "Grammatik",

        "preposition":
            "Präpositionen",

        "prepositions":
            "Präpositionen",

        "verb":
            "Verben",

        "verb_form":
            "Verbformen",

        "verb_forms":
            "Verbformen",

        "spelling":
            "Rechtschreibung",

        "vocabulary":
            "Wortschatz",

        "case":
            "Kasus",

        "kasus":
            "Kasus",

        "pronoun":
            "Pronomen",

        "sentence_structure":
            "Satzbau",

        "sentence_order":
            "Wortstellung"
    }


    if error_type in names:

        return names[
            error_type
        ]


    if not error_type:

        return "Grammatik"


    return display_word(
        error_type.replace(
            "_",
            " "
        )
    )


# ==========================================
# LISTA PO NIEMIECKU
# ==========================================

def format_list(
    items
):

    clean_items = []


    for item in items:

        item = str(
            item or ""
        ).strip()


        if not item:

            continue


        if item not in clean_items:

            clean_items.append(
                item
            )


    if not clean_items:

        return ""


    if len(
        clean_items
    ) == 1:

        return clean_items[0]


    if len(
        clean_items
    ) == 2:

        return (
            clean_items[0]
            + " und "
            + clean_items[1]
        )


    return (
        ", ".join(
            clean_items[:-1]
        )
        + " und "
        + clean_items[-1]
    )


# ==========================================
# CZY TO PYTANIE O DZISIEJSZĄ NAUKĘ
# ==========================================

def is_today_learning_question(
    message
):

    questions = {

        "was habe ich heute gemacht",

        "was habe ich heute geübt",

        "was habe ich heute gelernt",

        "was habe ich heute schon gemacht",

        "was habe ich heute schon geübt",

        "was habe ich heute schon gelernt",

        "was haben wir heute gemacht",

        "was haben wir heute geübt",

        "was haben wir heute gelernt",

        "habe ich heute schon gelernt",

        "habe ich heute schon geübt"
    }


    return message in questions


# ==========================================
# CZY TO PYTANIE O DZISIEJSZE SŁOWA
# ==========================================

def is_today_words_question(
    message
):

    questions = {

        "welche wörter habe ich heute wiederholt",

        "welche wörter habe ich heute geübt",

        "welche wörter habe ich heute gelernt",

        "welche wörter haben wir heute wiederholt",

        "welche wörter haben wir heute geübt",

        "was habe ich heute für wörter geübt"
    }


    return message in questions


# ==========================================
# CZY TO PYTANIE O DZISIEJSZE BŁĘDY
# ==========================================

def is_today_errors_question(
    message
):

    questions = {

        "welche fehler habe ich heute geübt",

        "welche fehler habe ich heute wiederholt",

        "welche fehler haben wir heute geübt",

        "welche fehler haben wir heute wiederholt",

        "was habe ich heute bei meinen fehlern geübt"
    }


    return message in questions


# ==========================================
# CZY TO PYTANIE O LICZBĘ ĆWICZEŃ
# ==========================================

def is_today_exercises_question(
    message
):

    questions = {

        "wie viele übungen habe ich heute gemacht",

        "wie viele übungen habe ich heute geschafft",

        "wie viele übungen haben wir heute gemacht"
    }


    return message in questions


# ==========================================
# CZY TO PYTANIE O PLAN DNIA
# ==========================================

def is_today_plan_question(
    message
):

    questions = {

        "habe ich meinen plan heute geschafft",

        "ist mein plan für heute fertig",

        "habe ich heute alles gemacht",

        "bin ich für heute fertig"
    }


    return message in questions


# ==========================================
# PODSUMOWANIE DZISIEJSZEJ NAUKI
# ==========================================

def create_today_summary(
    state
):

    summary = get_daily_learning_summary(
        state
    )


    words = summary.get(
        "reviewed_words",
        []
    )

    errors = summary.get(
        "reviewed_errors",
        []
    )

    lesson_reviews = summary.get(
        "lesson_reviews",
        []
    )

    lesson_sections = summary.get(
        "lesson_sections",
        []
    )


    try:

        exercises = int(
            summary.get(
                "completed_exercises",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        exercises = 0


    parts = []


    # ======================================
    # SŁOWA
    # ======================================

    if words:

        word_names = [
            f"„{display_word(word)}“"
            for word in words
            if word
        ]


        formatted_words = format_list(
            word_names
        )


        if formatted_words:

            parts.append(
                "Du hast heute "
                f"{formatted_words} wiederholt."
            )


    # ======================================
    # BŁĘDY
    # ======================================

    if errors:

        error_names = [
            display_error(
                error_type
            )
            for error_type in errors
            if error_type
        ]


        formatted_errors = format_list(
            error_names
        )


        if formatted_errors:

            parts.append(
                "Du hast heute "
                f"{formatted_errors} geübt."
            )


    # ======================================
    # POWTÓRKI LEKCJI
    # ======================================

    if lesson_reviews:

        if len(
            lesson_reviews
        ) == 1:

            parts.append(
                "Du hast heute eine "
                "Lektionswiederholung gemacht."
            )

        else:

            parts.append(
                "Du hast heute "
                f"{len(lesson_reviews)} "
                "Lektionswiederholungen gemacht."
            )


    # ======================================
    # CZĘŚCI LEKCJI
    # ======================================

    if lesson_sections:

        if len(
            lesson_sections
        ) == 1:

            parts.append(
                "Du hast heute auch an "
                "einer Lektion gearbeitet."
            )

        else:

            parts.append(
                "Du hast heute auch an "
                "mehreren Teilen deiner Lektionen "
                "gearbeitet."
            )


    # ======================================
    # BRAK SZCZEGÓŁÓW, ALE BYŁY ĆWICZENIA
    # ======================================

    if (
        not parts
        and
        exercises > 0
    ):

        if exercises == 1:

            return (
                "Du hast heute schon "
                "eine Übung gemacht."
            )


        return (
            "Du hast heute schon "
            f"{exercises} Übungen gemacht."
        )


    # ======================================
    # NIC JESZCZE NIE ZROBIONO
    # ======================================

    if not parts:

        return (
            "Heute haben wir noch keine "
            "Lernaktivität abgeschlossen."
        )


    return " ".join(
        parts
    )


# ==========================================
# ODPOWIEDŹ – SŁOWA DZISIAJ
# ==========================================

def create_today_words_answer(
    state
):

    summary = get_daily_learning_summary(
        state
    )


    words = summary.get(
        "reviewed_words",
        []
    )


    if not words:

        return (
            "Heute hast du noch keine "
            "Wörter wiederholt."
        )


    display_words = [
        f"„{display_word(word)}“"
        for word in words
        if word
    ]


    return (
        "Heute hast du diese Wörter "
        "wiederholt: "
        f"{format_list(display_words)}."
    )


# ==========================================
# ODPOWIEDŹ – BŁĘDY DZISIAJ
# ==========================================

def create_today_errors_answer(
    state
):

    summary = get_daily_learning_summary(
        state
    )


    errors = summary.get(
        "reviewed_errors",
        []
    )


    if not errors:

        return (
            "Heute hast du noch keine "
            "Fehlerwiederholung gemacht."
        )


    display_errors = [
        display_error(
            error_type
        )
        for error_type in errors
        if error_type
    ]


    return (
        "Heute hast du diese Bereiche "
        "geübt: "
        f"{format_list(display_errors)}."
    )


# ==========================================
# ODPOWIEDŹ – LICZBA ĆWICZEŃ
# ==========================================

def create_today_exercises_answer(
    state
):

    summary = get_daily_learning_summary(
        state
    )


    try:

        exercises = int(
            summary.get(
                "completed_exercises",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        exercises = 0


    if exercises <= 0:

        return (
            "Heute hast du noch keine "
            "Übung abgeschlossen."
        )


    if exercises == 1:

        return (
            "Heute hast du eine "
            "Übung abgeschlossen."
        )


    return (
        "Heute hast du "
        f"{exercises} Übungen abgeschlossen."
    )


# ==========================================
# ODPOWIEDŹ – PLAN DNIA
# ==========================================

def create_today_plan_answer(
    state
):

    summary = get_daily_learning_summary(
        state
    )


    completed = bool(
        summary.get(
            "daily_plan_completed",
            False
        )
    )


    if completed:

        return (
            "Ja. Deinen Lernplan für heute "
            "hast du geschafft."
        )


    return (
        "Noch nicht ganz. "
        "Für heute ist noch etwas offen."
    )


# ==========================================
# GŁÓWNY ROUTER DAILY LEARNING
# ==========================================

def handle_daily_learning(
    user_message,
    state
):

    if state is None:
        return None


    message = clean_message(
        user_message
    )


    if not message:
        return None


    # ======================================
    # DZISIEJSZE SŁOWA
    # ======================================

    if is_today_words_question(
        message
    ):

        return create_today_words_answer(
            state
        )


    # ======================================
    # DZISIEJSZE BŁĘDY
    # ======================================

    if is_today_errors_question(
        message
    ):

        return create_today_errors_answer(
            state
        )


    # ======================================
    # LICZBA ĆWICZEŃ
    # ======================================

    if is_today_exercises_question(
        message
    ):

        return create_today_exercises_answer(
            state
        )


    # ======================================
    # PLAN DNIA
    # ======================================

    if is_today_plan_question(
        message
    ):

        return create_today_plan_answer(
            state
        )


    # ======================================
    # OGÓLNE PODSUMOWANIE DNIA
    # ======================================

    if is_today_learning_question(
        message
    ):

        return create_today_summary(
            state
        )


    return None
