# ==========================================
# NELE – OGÓLNY POSTĘP UCZNIA
# STUDENT MEMORY 2.0
# ==========================================

from datetime import date


# ==========================================
# DOMYŚLNY STAN POSTĘPU
# ==========================================

def create_empty_student_progress():

    return {
        "current_level": "A1",
        "current_lesson": 1,

        "completed_lessons": [],

        "sessions": 0,
        "total_exercises": 0,

        "last_learning_date": None,
        "last_learning_topic": None
    }


# ==========================================
# POBRANIE POSTĘPU UCZNIA
# ==========================================

def get_student_progress(
    state
):

    if state is None:
        return {}

    if "student_progress" not in state:

        state[
            "student_progress"
        ] = create_empty_student_progress()


    progress = state[
        "student_progress"
    ]


    # ======================================
    # UZUPEŁNIENIE STARSZEJ PAMIĘCI
    # ======================================

    defaults = (
        create_empty_student_progress()
    )

    for key, value in defaults.items():

        if key not in progress:

            progress[
                key
            ] = value


    return progress


# ==========================================
# AKTUALNY POZIOM
# ==========================================

def get_current_level(
    state
):

    progress = get_student_progress(
        state
    )

    return progress.get(
        "current_level",
        "A1"
    )


def set_current_level(
    state,
    level
):

    if not level:
        return

    level = str(
        level
    ).strip().upper()

    if level not in {
        "A1",
        "A2",
        "B1",
        "B2",
        "C1",
        "C2"
    }:
        return

    progress = get_student_progress(
        state
    )

    progress[
        "current_level"
    ] = level


# ==========================================
# AKTUALNA LEKCJA
# ==========================================

def get_current_lesson(
    state
):

    progress = get_student_progress(
        state
    )

    return progress.get(
        "current_lesson",
        1
    )


def set_current_lesson(
    state,
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

        return


    if lesson < 1:
        return


    progress = get_student_progress(
        state
    )

    progress[
        "current_lesson"
    ] = lesson


# ==========================================
# ZAKOŃCZONA LEKCJA
# ==========================================

def remember_completed_lesson(
    state,
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

        return


    progress = get_student_progress(
        state
    )

    completed_lessons = progress[
        "completed_lessons"
    ]


    if lesson not in completed_lessons:

        completed_lessons.append(
            lesson
        )

        completed_lessons.sort()


# ==========================================
# CZY LEKCJA JEST UKOŃCZONA
# ==========================================

def is_lesson_completed(
    state,
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

        return False


    progress = get_student_progress(
        state
    )

    return lesson in progress.get(
        "completed_lessons",
        []
    )


# ==========================================
# NOWA SESJA NAUKI
# ==========================================

def remember_learning_session(
    state
):

    progress = get_student_progress(
        state
    )

    progress[
        "sessions"
    ] += 1

    progress[
        "last_learning_date"
    ] = date.today().isoformat()


# ==========================================
# WYKONANE ĆWICZENIE
# ==========================================

def remember_completed_exercise(
    state,
    count=1
):

    try:

        count = int(
            count
        )

    except (
        TypeError,
        ValueError
    ):

        count = 1


    if count < 1:
        return


    progress = get_student_progress(
        state
    )

    progress[
        "total_exercises"
    ] += count

    progress[
        "last_learning_date"
    ] = date.today().isoformat()


# ==========================================
# OSTATNI TEMAT NAUKI
# ==========================================

def remember_learning_topic(
    state,
    topic
):

    if not topic:
        return

    topic = str(
        topic
    ).strip()

    if not topic:
        return


    progress = get_student_progress(
        state
    )

    progress[
        "last_learning_topic"
    ] = topic

    progress[
        "last_learning_date"
    ] = date.today().isoformat()


# ==========================================
# PODSUMOWANIE POSTĘPU
# ==========================================

def get_progress_summary(
    state
):

    progress = get_student_progress(
        state
    )

    return {
        "current_level":
            progress.get(
                "current_level",
                "A1"
            ),

        "current_lesson":
            progress.get(
                "current_lesson",
                1
            ),

        "completed_lessons":
            list(
                progress.get(
                    "completed_lessons",
                    []
                )
            ),

        "sessions":
            progress.get(
                "sessions",
                0
            ),

        "total_exercises":
            progress.get(
                "total_exercises",
                0
            ),

        "last_learning_date":
            progress.get(
                "last_learning_date"
            ),

        "last_learning_topic":
            progress.get(
                "last_learning_topic"
            )
  }
