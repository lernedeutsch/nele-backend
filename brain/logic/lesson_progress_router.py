# ==========================================
# NELE – ROUTER POSTĘPU W LEKCJI
# STUDENT MEMORY 2.0
# ==========================================

import re

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
    remember_learning_topic,
    get_current_level,
    get_current_lesson
)

from brain.knowledge.A1.lessons import (
    lesson_exists as a1_lesson_exists,
    get_lesson_sections as get_a1_lesson_sections
)


from brain.logic.lesson_loader import (
    lesson_module_exists,
    get_lesson_sections_from_module
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

        if a1_lesson_exists(
            lesson
        ):

            sections = get_a1_lesson_sections(
                lesson
            )


            if sections:
                return sections


        if lesson_module_exists(
            level,
            lesson
        ):

            return get_lesson_sections_from_module(
                level,
                lesson
            )


        return []


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
# CZY WIADOMOŚĆ OZNACZA UKOŃCZENIE
# ==========================================

def has_completion_intent(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!„“\"'"
    )


    completion_words = [
        "fertig",
        "abgeschlossen",
        "geschafft",
        "beendet"
    ]


    return any(
        word in message
        for word in completion_words
    )


# ==========================================
# NUMER CZĘŚCI Z WIADOMOŚCI
# ==========================================

def extract_part_number(
    user_message
):

    message = normalize(
        user_message
    )


    # ======================================
    # TEIL 1 / TEIL 2 / TEIL 3
    # ======================================

    match = re.search(
        r"\bteil\s+([0-9]+)\b",
        message
    )


    if match:

        try:

            return int(
                match.group(1)
            )

        except (
            TypeError,
            ValueError
        ):

            return None


    # ======================================
    # TEIL EINS / ZWEI / DREI ...
    # ======================================

    german_numbers = {
        "eins": 1,
        "ein": 1,
        "erste": 1,
        "ersten": 1,
        "erster": 1,

        "zwei": 2,
        "zweite": 2,
        "zweiten": 2,
        "zweiter": 2,

        "drei": 3,
        "dritte": 3,
        "dritten": 3,
        "dritter": 3,

        "vier": 4,
        "vierte": 4,
        "vierten": 4,
        "vierter": 4,

        "fünf": 5,
        "fünfte": 5,
        "fünften": 5,
        "fünfter": 5
    }


    for word, number in german_numbers.items():

        patterns = [
            f"teil {word}",
            f"{word} teil"
        ]


        if any(
            pattern in message
            for pattern in patterns
        ):

            return number


    return None


# ==========================================
# CZĘŚĆ LEKCJI Z NATURALNEJ WIADOMOŚCI
# ==========================================

def extract_completed_section(
    user_message,
    state,
    level,
    lesson
):

    if not has_completion_intent(
        user_message
    ):

        return None


    sections = sync_lesson_progress(
        state,
        level,
        lesson
    )


    if not sections:
        return None


    message = normalize(
        user_message
    ).strip(
        " .?!„“\"'"
    )


    # ======================================
    # 1. UŻYTKOWNIK PODAŁ NAZWĘ CZĘŚCI
    # ======================================

    for real_section in sections:

        normalized_section = normalize(
            real_section
        ).strip(
            " .?!„“\"'"
        )


        if normalized_section in message:

            return real_section


    # ======================================
    # 2. UŻYTKOWNIK POWIEDZIAŁ:
    # "TEIL 1 IST FERTIG"
    # ======================================

    part_number = extract_part_number(
        user_message
    )


    if part_number is not None:

        section_index = (
            part_number - 1
        )


        if (
            section_index >= 0
            and
            section_index < len(
                sections
            )
        ):

            return sections[
                section_index
            ]


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

    already_completed = result.get(
        "already_completed",
        False
    )


    # ======================================
    # CZĘŚĆ BYŁA JUŻ WCZEŚNIEJ UKOŃCZONA
    # ======================================

    if already_completed:

        if next_section:

            return (
                f"„{completed_section}“ "
                "hast du schon abgeschlossen. "
                "Als Nächstes ist "
                f"„{next_section}“ dran."
            )

        return (
            f"„{completed_section}“ "
            "hast du schon abgeschlossen."
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


# ==========================================
# GŁÓWNY ROUTER POSTĘPU LEKCJI
# ==========================================

def handle_lesson_progress(
    user_message,
    state
):
    """
    Rozpoznaje naturalną informację
    użytkownika o ukończeniu części lekcji.

    Przykłady:

    "Ich bin mit Wir begrüßen uns fertig."
    "Ich habe Wir begrüßen uns abgeschlossen."
    "Teil 1 ist fertig."
    """

    if state is None:
        return None


    # ======================================
    # AKTUALNY POZIOM I LEKCJA
    # ======================================

    level = get_current_level(
        state
    )

    lesson = get_current_lesson(
        state
    )


    # ======================================
    # ROZPOZNANIE UKOŃCZONEJ CZĘŚCI
    # ======================================

    section = extract_completed_section(
        user_message,
        state,
        level,
        lesson
    )


    if not section:
        return None


    # ======================================
    # ZAPIS DO STUDENT MEMORY 2.0
    # ======================================

    result = complete_lesson_section(
        state,
        level,
        lesson,
        section
    )


    if not result.get(
        "ok"
    ):

        return None


    # ======================================
    # ODPOWIEDŹ NELE
    # ======================================

    return create_section_completed_message(
        result
        )
