# ==========================================
# NELE – POSTĘP W LEKCJI
# STUDENT MEMORY 2.0
# ==========================================

from datetime import (
    datetime,
    timezone
)


# ==========================================
# AKTUALNY CZAS
# ==========================================

def get_current_time_iso():

    return datetime.now(
        timezone.utc
    ).isoformat()


# ==========================================
# PUSTA PAMIĘĆ POSTĘPU LEKCJI
# ==========================================

def create_empty_lesson_progress():

    return {
        "lessons": {}
    }


# ==========================================
# PUSTA PAMIĘĆ POWTÓREK LEKCJI
# ==========================================

def create_empty_lesson_review():

    return {
        "review_count": 0,

        "last_reviewed_at": None,

        "next_review_at": None,

        "correct_answers": 0,

        "wrong_answers": 0,

        "last_score": None,

        "best_score": None,

        "needs_review": False
    }


# ==========================================
# GŁÓWNA PAMIĘĆ LEKCJI
# ==========================================

def get_lesson_progress_memory(
    state
):

    if state is None:
        return {}

    if "lesson_progress" not in state:

        state[
            "lesson_progress"
        ] = create_empty_lesson_progress()


    memory = state[
        "lesson_progress"
    ]


    if not isinstance(
        memory,
        dict
    ):

        memory = (
            create_empty_lesson_progress()
        )

        state[
            "lesson_progress"
        ] = memory


    if "lessons" not in memory:

        memory[
            "lessons"
        ] = {}


    if not isinstance(
        memory["lessons"],
        dict
    ):

        memory[
            "lessons"
        ] = {}


    return memory


# ==========================================
# KLUCZ LEKCJI
# ==========================================

def get_lesson_key(
    level,
    lesson
):

    level = str(
        level or "A1"
    ).strip().upper()


    try:

        lesson = int(
            lesson
        )

    except (
        TypeError,
        ValueError
    ):

        lesson = 1


    if lesson < 1:

        lesson = 1


    return (
        f"{level}:{lesson}"
    )


# ==========================================
# PAMIĘĆ JEDNEJ LEKCJI
# ==========================================

def get_lesson_progress(
    state,
    level="A1",
    lesson=1
):

    memory = get_lesson_progress_memory(
        state
    )

    if not memory:
        return {}


    lesson_key = get_lesson_key(
        level,
        lesson
    )


    lessons = memory[
        "lessons"
    ]


    if lesson_key not in lessons:

        lessons[
            lesson_key
        ] = {
            "level":
                str(
                    level or "A1"
                ).strip().upper(),

            "lesson":
                int(
                    lesson
                ),

            "sections": [],

            "completed_sections": [],

            "current_section": None,

            "completed": False,

            "review":
                create_empty_lesson_review()
        }


    lesson_progress = lessons[
        lesson_key
    ]


    # ======================================
    # UZUPEŁNIENIE STARSZEGO STANU
    # ======================================

    defaults = {
        "level":
            str(
                level or "A1"
            ).strip().upper(),

        "lesson":
            int(
                lesson
            ),

        "sections": [],

        "completed_sections": [],

        "current_section": None,

        "completed": False,

        "review":
            create_empty_lesson_review()
    }


    for key, value in defaults.items():

        if key not in lesson_progress:

            lesson_progress[
                key
            ] = value


    if not isinstance(
        lesson_progress.get(
            "sections"
        ),
        list
    ):

        lesson_progress[
            "sections"
        ] = []


    if not isinstance(
        lesson_progress.get(
            "completed_sections"
        ),
        list
    ):

        lesson_progress[
            "completed_sections"
        ] = []


    # ======================================
    # UZUPEŁNIENIE STARSZEJ PAMIĘCI
    # POWTÓREK
    # ======================================

    if not isinstance(
        lesson_progress.get(
            "review"
        ),
        dict
    ):

        lesson_progress[
            "review"
        ] = (
            create_empty_lesson_review()
        )


    review = lesson_progress[
        "review"
    ]


    review_defaults = (
        create_empty_lesson_review()
    )


    for key, value in review_defaults.items():

        if key not in review:

            review[
                key
            ] = value


    return lesson_progress


# ==========================================
# PAMIĘĆ POWTÓREK JEDNEJ LEKCJI
# ==========================================

def get_lesson_review(
    state,
    level="A1",
    lesson=1
):

    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )


    if not lesson_progress:
        return {}


    return lesson_progress[
        "review"
    ]


# ==========================================
# USTAWIENIE CZĘŚCI LEKCJI
# ==========================================

def set_lesson_sections(
    state,
    level,
    lesson,
    sections
):

    if not isinstance(
        sections,
        list
    ):

        return


    clean_sections = []


    for section in sections:

        if not section:
            continue


        section = str(
            section
        ).strip()


        if not section:
            continue


        if section not in clean_sections:

            clean_sections.append(
                section
            )


    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )


    lesson_progress[
        "sections"
    ] = clean_sections


    # ======================================
    # JEŻELI NIE MA JESZCZE AKTUALNEJ
    # CZĘŚCI, USTAWIAMY PIERWSZĄ
    # ======================================

    if (
        clean_sections
        and not lesson_progress.get(
            "current_section"
        )
    ):

        lesson_progress[
            "current_section"
        ] = clean_sections[0]


# ==========================================
# AKTUALNA CZĘŚĆ LEKCJI
# ==========================================

def get_current_section(
    state,
    level,
    lesson
):

    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )

    return lesson_progress.get(
        "current_section"
    )


# ==========================================
# USTAWIENIE AKTUALNEJ CZĘŚCI
# ==========================================

def set_current_section(
    state,
    level,
    lesson,
    section
):

    if not section:
        return


    section = str(
        section
    ).strip()


    if not section:
        return


    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )


    lesson_progress[
        "current_section"
    ] = section


# ==========================================
# COURSE MASTERY = JEDNO ŹRÓDŁO PRAWDY
# ==========================================

def _course_mode(state):
    return str((state or {}).get("conversation_mode") or "").strip().lower() == "course"


def _course_section_skill_candidates(state, level, lesson, section):
    """Return mastery records that can prove a course section is learned."""
    skills = ((((state or {}).get("learning_progress_v1") or {}).get("skills")) or {})
    prefix = f"course:{str(level or '').strip().lower()}:{lesson}:"
    section_slug = str(section or "").strip().lower().strip(" .?!„“\\\"'").replace(" ", "_")
    exact = prefix + section_slug
    # A section may only be proven by its own skill.  Reusing the sole
    # lesson skill for another section makes every later section look mastered
    # as soon as the first one is mastered.
    return [exact] if exact in skills else []


def is_course_section_mastered(state, level, lesson, section):
    """In course mode, completion is derived from learning_progress_v1 mastery."""
    if not _course_mode(state):
        return True
    skills = ((((state or {}).get("learning_progress_v1") or {}).get("skills")) or {})
    candidates = _course_section_skill_candidates(state, level, lesson, section)
    return bool(candidates) and all(
        (skills.get(key) or {}).get("status") == "mastered"
        for key in candidates
    )


# ==========================================
# OZNACZENIE CZĘŚCI JAKO UKOŃCZONEJ
# ==========================================

def mark_section_completed(
    state,
    level,
    lesson,
    section
):

    if not section:
        return False


    section = str(
        section
    ).strip()


    if not section:
        return False


    # In course mode a UI/dialogue event may request completion, but only
    # durable mastery may authorize it. This closes every legacy bypass at
    # the shared persistence boundary.
    if not is_course_section_mastered(state, level, lesson, section):
        return False


    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )


    completed_sections = lesson_progress[
        "completed_sections"
    ]


    if section not in completed_sections:

        completed_sections.append(
            section
        )


    # ======================================
    # SZUKAMY NASTĘPNEJ CZĘŚCI
    # ======================================

    next_section = get_next_incomplete_section(
        state,
        level,
        lesson
    )


    lesson_progress[
        "current_section"
    ] = next_section


    # ======================================
    # JEŻELI NIE MA JUŻ NIC DO ZROBIENIA
    # ======================================

    sections = lesson_progress.get(
        "sections",
        []
    )


    if (
        sections
        and
        next_section is None
    ):

        lesson_progress[
            "completed"
        ] = True


    return True


# ==========================================
# CZY CZĘŚĆ JEST UKOŃCZONA
# ==========================================

def is_section_completed(
    state,
    level,
    lesson,
    section
):

    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )


    if _course_mode(state):
        return is_course_section_mastered(state, level, lesson, section)


    return section in lesson_progress.get(
        "completed_sections",
        []
    )


# ==========================================
# UKOŃCZONE CZĘŚCI
# ==========================================

def get_completed_sections(
    state,
    level,
    lesson
):

    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )


    if _course_mode(state):
        return [
            section
            for section in lesson_progress.get("sections", [])
            if is_course_section_mastered(state, level, lesson, section)
        ]


    return list(
        lesson_progress.get(
            "completed_sections",
            []
        )
    )


# ==========================================
# NASTĘPNA NIEUKOŃCZONA CZĘŚĆ
# ==========================================

def get_next_incomplete_section(
    state,
    level,
    lesson
):

    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )


    sections = lesson_progress.get(
        "sections",
        []
    )


    completed_sections = set(
        get_completed_sections(state, level, lesson)
    )


    for section in sections:

        if section not in completed_sections:

            return section


    return None


# ==========================================
# PROCENT UKOŃCZENIA LEKCJI
# ==========================================

def get_lesson_completion_percent(
    state,
    level,
    lesson
):

    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )


    sections = lesson_progress.get(
        "sections",
        []
    )


    if not sections:

        return 0


    completed_sections = set(
        get_completed_sections(state, level, lesson)
    )


    completed_count = sum(
        1
        for section in sections
        if section in completed_sections
    )


    percent = (
        completed_count
        / len(sections)
        * 100
    )


    return round(
        percent
    )


# ==========================================
# CZY CAŁA LEKCJA JEST UKOŃCZONA
# ==========================================

def is_lesson_fully_completed(
    state,
    level,
    lesson
):

    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )


    if (
        not _course_mode(state)
        and lesson_progress.get("completed", False)
    ):

        return True


    sections = lesson_progress.get(
        "sections",
        []
    )


    if not sections:

        return False


    return (
        get_next_incomplete_section(
            state,
            level,
            lesson
        )
        is None
    )


# ==========================================
# OZNACZENIE LEKCJI DO POWTÓRKI
# ==========================================

def mark_lesson_for_review(
    state,
    level,
    lesson
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )


    if not review:
        return


    review[
        "needs_review"
    ] = True


# ==========================================
# USUNIĘCIE OZNACZENIA POWTÓRKI
# ==========================================

def clear_lesson_review_flag(
    state,
    level,
    lesson
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )


    if not review:
        return


    review[
        "needs_review"
    ] = False


# ==========================================
# ZAPIS WYNIKU POWTÓRKI
# ==========================================

def remember_lesson_review_result(
    state,
    level,
    lesson,
    correct_answers=0,
    wrong_answers=0,
    score=None
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )


    if not review:
        return


    try:

        correct_answers = int(
            correct_answers
        )

    except (
        TypeError,
        ValueError
    ):

        correct_answers = 0


    try:

        wrong_answers = int(
            wrong_answers
        )

    except (
        TypeError,
        ValueError
    ):

        wrong_answers = 0


    if correct_answers < 0:
        correct_answers = 0


    if wrong_answers < 0:
        wrong_answers = 0


    review[
        "review_count"
    ] += 1


    review[
        "correct_answers"
    ] += correct_answers


    review[
        "wrong_answers"
    ] += wrong_answers


    review[
        "last_reviewed_at"
    ] = get_current_time_iso()


    review[
        "needs_review"
    ] = False


    if score is not None:

        try:

            score = int(
                score
            )

        except (
            TypeError,
            ValueError
        ):

            score = None


    if score is not None:

        score = max(
            0,
            min(
                100,
                score
            )
        )


        review[
            "last_score"
        ] = score


        best_score = review.get(
            "best_score"
        )


        if (
            best_score is None
            or
            score > best_score
        ):

            review[
                "best_score"
            ] = score


# ==========================================
# USTAWIENIE TERMINU POWTÓRKI
# ==========================================

def set_next_lesson_review(
    state,
    level,
    lesson,
    next_review_at
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )


    if not review:
        return


    review[
        "next_review_at"
    ] = next_review_at


# ==========================================
# PODSUMOWANIE POWTÓREK LEKCJI
# ==========================================

def get_lesson_review_summary(
    state,
    level,
    lesson
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )


    if not review:
        return {}


    return {
        "review_count":
            review.get(
                "review_count",
                0
            ),

        "last_reviewed_at":
            review.get(
                "last_reviewed_at"
            ),

        "next_review_at":
            review.get(
                "next_review_at"
            ),

        "correct_answers":
            review.get(
                "correct_answers",
                0
            ),

        "wrong_answers":
            review.get(
                "wrong_answers",
                0
            ),

        "last_score":
            review.get(
                "last_score"
            ),

        "best_score":
            review.get(
                "best_score"
            ),

        "needs_review":
            review.get(
                "needs_review",
                False
            )
    }


# ==========================================
# PODSUMOWANIE LEKCJI
# ==========================================

def get_lesson_progress_summary(
    state,
    level,
    lesson
):

    lesson_progress = get_lesson_progress(
        state,
        level,
        lesson
    )


    return {
        "level":
            lesson_progress.get(
                "level"
            ),

        "lesson":
            lesson_progress.get(
                "lesson"
            ),

        "current_section":
            lesson_progress.get(
                "current_section"
            ),

        "completed_sections":
            list(
                lesson_progress.get(
                    "completed_sections",
                    []
                )
            ),

        "next_section":
            get_next_incomplete_section(
                state,
                level,
                lesson
            ),

        "completion_percent":
            get_lesson_completion_percent(
                state,
                level,
                lesson
            ),

        "completed":
            is_lesson_fully_completed(
                state,
                level,
                lesson
            ),

        "review":
            get_lesson_review_summary(
                state,
                level,
                lesson
            )
        }
