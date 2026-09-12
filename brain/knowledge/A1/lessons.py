# ==========================================
# NELE – STRUKTURA KURSU A1
# ==========================================


# ==========================================
# LEKCJE A1
# ==========================================
#
# Tutaj później będziemy podłączać
# prawdziwą strukturę kursu.
#
# Student Memory 2.0 korzysta z tego pliku,
# ale pamięć postępu pozostaje osobno
# w brain/memory/lesson_progress.py.
# ==========================================

A1_LESSONS = {}


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
