# ==========================================
# NELE – STRUKTURA KURSU A1
# ==========================================


# ==========================================
# LEKCJE A1
# ==========================================

A1_LESSONS = {

    1: {
        "level": "A1",
        "lesson": 1,

        "title":
            "Guten Tag! – Begrüßung und Vorstellung",

        "description":
            (
                "Begrüßung, Vorstellung "
                "und das deutsche Alphabet."
            ),

        # ==================================
        # PRAWDZIWA KOLEJNOŚĆ Z
        # lessons/a1/lektion-1.html
        # ==================================

        "sections": [
            "Wir begrüßen uns",
            "Ich stelle mich vor",
            "Das deutsche Alphabet"
        ],

        # ==================================
        # INFORMACJA POMOCNICZA
        # ==================================

        "source":
            "lessons/a1/lektion-1.html"
    },

    2: {
        "level": "A1",
        "lesson": 2,
        "title": "Woher kommen Sie?",
        "description": (
            "Herkunft, Länder, Nationalitäten, "
            "das Verb kommen und die Zahlen 1 bis 20."
        ),
        "sections": [
            "Woher kommen Sie?",
            "Länder und Nationalitäten",
            "Das Verb kommen",
            "Zahlen 1–20"
        ],
        "source": "lessons/a1/lektion-2.html"
    },

    3: {
        "level": "A1",
        "lesson": 3,
        "title": "Wie alt sind Sie?",
        "description": (
            "Alter, Zahlen 11 bis 100, das Verb sein "
            "und persönliche Daten."
        ),
        "sections": [
            "Wie alt sind Sie?",
            "Zahlen 11–100",
            "Das Verb sein",
            "Persönliche Daten"
        ],
        "source": "lessons/a1/lektion-3.html"
    }
}


# ==========================================
# POBRANIE DANYCH LEKCJI
# ==========================================

def get_lesson(
    lesson
):

    try:

        lesson = int(
            lesson
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    return A1_LESSONS.get(
        lesson
    )


# ==========================================
# CZY LEKCJA ISTNIEJE
# ==========================================

def lesson_exists(
    lesson
):

    return (
        get_lesson(
            lesson
        )
        is not None
    )


# ==========================================
# TYTUŁ LEKCJI
# ==========================================

def get_lesson_title(
    lesson
):

    lesson_data = get_lesson(
        lesson
    )

    if not lesson_data:
        return None


    return lesson_data.get(
        "title"
    )


# ==========================================
# OPIS LEKCJI
# ==========================================

def get_lesson_description(
    lesson
):

    lesson_data = get_lesson(
        lesson
    )

    if not lesson_data:
        return None


    return lesson_data.get(
        "description"
    )


# ==========================================
# CZĘŚCI LEKCJI
# ==========================================

def get_lesson_sections(
    lesson
):

    lesson_data = get_lesson(
        lesson
    )

    if not lesson_data:
        return []


    sections = lesson_data.get(
        "sections",
        []
    )


    if not isinstance(
        sections,
        list
    ):

        return []


    return list(
        sections
    )


# ==========================================
# LICZBA CZĘŚCI LEKCJI
# ==========================================

def get_lesson_section_count(
    lesson
):

    return len(
        get_lesson_sections(
            lesson
        )
    )


# ==========================================
# POBRANIE KONKRETNEJ CZĘŚCI
# ==========================================

def get_lesson_section(
    lesson,
    index
):

    sections = get_lesson_sections(
        lesson
    )


    try:

        index = int(
            index
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    if index < 0:
        return None


    if index >= len(
        sections
    ):

        return None


    return sections[
        index
    ]


# ==========================================
# PIERWSZA CZĘŚĆ LEKCJI
# ==========================================

def get_first_lesson_section(
    lesson
):

    return get_lesson_section(
        lesson,
        0
    )


# ==========================================
# WSZYSTKIE NUMERY LEKCJI
# ==========================================

def get_available_lessons():

    return sorted(
        A1_LESSONS.keys()
    )


# ==========================================
# NASTĘPNA LEKCJA
# ==========================================

def get_next_lesson_number(
    lesson
):

    try:

        lesson = int(
            lesson
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    available_lessons = (
        get_available_lessons()
    )


    for lesson_number in available_lessons:

        if lesson_number > lesson:

            return lesson_number


    return None
