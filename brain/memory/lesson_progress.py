# ==========================================
# NELE – POSTĘP W LEKCJI
# STUDENT MEMORY 2.0
# ==========================================


# ==========================================
# PUSTA PAMIĘĆ POSTĘPU LEKCJI
# ==========================================

def create_empty_lesson_progress():

    return {
        "lessons": {}
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

            "completed": False
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

        "completed": False
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


    return lesson_progress


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
# OZNACZENIE CZĘŚCI JAKO UKOŃCZONEJ
# ==========================================

def mark_section_completed(
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
        lesson_progress.get(
            "completed_sections",
            []
        )
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
        lesson_progress.get(
            "completed_sections",
            []
        )
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


    if lesson_progress.get(
        "completed",
        False
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
            )
  }
