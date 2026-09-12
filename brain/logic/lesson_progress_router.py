# ==========================================
# NELE – ROUTER POSTĘPU W LEKCJI
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import normalize

from brain.memory.lesson_progress import (
    set_lesson_sections,
    mark_section_completed,
    is_section_completed,
    get_next_incomplete_section,
    get_lesson_completion_percent,
    is_lesson_fully_completed
)

from brain.memory.student_progress import (
    remember_completed_lesson,
    remember_learning_topic
)

from brain.knowledge.A1.lessons import (
    lesson_exists as a1_lesson_exists,
    get_lesson_sections as get_a1_lesson_sections
)


# ==========================================
# STRUKTURA LEKCJI
# ==========================================

def get_course_lesson_sections(
    level,
    lesson
):

    level = str(
        level or ""
    ).strip().upper()


    # ======================================
    # A1
    # ======================================

    if level == "A1":

        if not a1_lesson_exists(
            lesson
        ):

            return []

        return get_a1_lesson_sections(
            lesson
        )


    # ======================================
    # A2 / B1 / ...
    # PODŁĄCZYMY PÓŹNIEJ
    # ======================================

    return []


# ==========================================
# SYNCHRONIZACJA STRUKTURY
# ==========================================

def sync_lesson_progress(
    state,
    level,
    lesson
):

    if state is None:
        return []


    sections = get_course_lesson_sections(
        level,
        lesson
    )


    if not sections:
        return []


    set_lesson_sections(
        state,
        level,
        lesson,
        sections
    )


    return sections


# ==========================================
# ZNALEZIENIE PRAWDZIWEJ NAZWY CZĘŚCI
# ==========================================

def find_lesson_section(
    state,
    level,
    lesson,
    section
):

    if not section:
        return None


    sections = sync_lesson_progress(
        state,
        level,
        lesson
    )


    if not sections:
        return None


    requested_section = normalize(
        str(
            section
        )
    ).strip(
        " .?!„“\"'"
    )


    if not requested_section:
        return None


    for real_section in sections:

        normalized_section = normalize(
            real_section
        ).strip(
            " .?!„“\"'"
        )


        if (
            requested_section
            == normalized_section
        ):

            return real_section


    return None


# ==========================================
# UKOŃCZENIE CZĘŚCI LEKCJI
# ==========================================

def complete_lesson_section(
    state,
    level,
    lesson,
    section
):
    """
    Oznacza jedną część lekcji
    jako ukończoną.

    Zwraca dane potrzebne później
    Nele oraz frontendowi.
    """

    if state is None:

        return {
            "ok": False,
            "reason": "no_state"
        }


    # ======================================
    # PRAWDZIWA NAZWA CZĘŚCI
    # ======================================

    real_section = find_lesson_section(
        state,
        level,
        lesson,
        section
    )


    if not real_section:

        return {
            "ok": False,
            "reason": "section_not_found"
        }


    # ======================================
    # CZY JUŻ BYŁA UKOŃCZONA
    # ======================================

    already_completed = (
        is_section_completed(
            state,
            level,
            lesson,
            real_section
        )
    )


    # ======================================
    # ZAPIS UKOŃCZENIA
    # ======================================

    if not already_completed:

        mark_section_completed(
            state,
            level,
            lesson,
            real_section
        )


    # ======================================
    # ZAPIS OSTATNIEJ AKTYWNOŚCI
    # ======================================

    remember_learning_topic(
        state,
        (
            f"{level} Lektion "
            f"{lesson}: "
            f"{real_section}"
        )
    )


    # ======================================
    # NASTĘPNA CZĘŚĆ
    # ======================================

    next_section = (
        get_next_incomplete_section(
            state,
            level,
            lesson
        )
    )


    # ======================================
    # PROCENT LEKCJI
    # ======================================

    completion_percent = (
        get_lesson_completion_percent(
            state,
            level,
            lesson
        )
    )


    # ======================================
    # CZY CAŁA LEKCJA GOTOWA
    # ======================================

    lesson_completed = (
        is_lesson_fully_completed(
            state,
            level,
            lesson
        )
    )


    # ======================================
    # JEŻELI CAŁA LEKCJA UKOŃCZONA
    # ======================================

    if lesson_completed:

        remember_completed_lesson(
            state,
            lesson
        )


    return {
        "ok": True,

        "level":
            str(
                level
            ).upper(),

        "lesson":
            lesson,

        "completed_section":
            real_section,

        "already_completed":
            already_completed,

        "next_section":
            next_section,

        "completion_percent":
            completion_percent,

        "lesson_completed":
            lesson_completed
    }


# ==========================================
# STATUS POSTĘPU W LEKCJI
# ==========================================

def get_lesson_progress_status(
    state,
    level,
    lesson
):

    if state is None:

        return {
            "ok": False,
            "reason": "no_state"
        }


    sections = sync_lesson_progress(
        state,
        level,
        lesson
    )


    if not sections:

        return {
            "ok": False,
            "reason": "lesson_not_found"
        }


    next_section = (
        get_next_incomplete_section(
            state,
            level,
            lesson
        )
    )


    completion_percent = (
        get_lesson_completion_percent(
            state,
            level,
            lesson
        )
    )


    lesson_completed = (
        is_lesson_fully_completed(
            state,
            level,
            lesson
        )
    )


    completed_sections = [
        section
        for section in sections
        if is_section_completed(
            state,
            level,
            lesson,
            section
        )
    ]


    return {
        "ok": True,

        "level":
            str(
                level
            ).upper(),

        "lesson":
            lesson,

        "sections":
            list(
                sections
            ),

        "completed_sections":
            completed_sections,

        "next_section":
            next_section,

        "completion_percent":
            completion_percent,

        "lesson_completed":
            lesson_completed
    }


# ==========================================
# ODPOWIEDŹ NELE PO UKOŃCZENIU CZĘŚCI
# ==========================================

def create_section_completed_message(
    result
):

    if not result:
        return None


    if not result.get(
        "ok"
    ):

        return None


    completed_section = result.get(
        "completed_section"
    )

    next_section = result.get(
        "next_section"
    )

    lesson_completed = result.get(
        "lesson_completed",
        False
    )


    # ======================================
    # CAŁA LEKCJA UKOŃCZONA
    # ======================================

    if lesson_completed:

        return (
            f"Sehr gut! "
            f"„{completed_section}“ "
            "hast du abgeschlossen. "
            "Damit hast du die ganze "
            "Lektion geschafft."
        )


    # ======================================
    # JEST NASTĘPNA CZĘŚĆ
    # ======================================

    if next_section:

        return (
            f"Sehr gut! "
            f"„{completed_section}“ "
            "hast du abgeschlossen. "
            "Als Nächstes ist "
            f"„{next_section}“ dran."
        )


    return (
        f"Sehr gut! "
        f"„{completed_section}“ "
        "hast du abgeschlossen."
  )
