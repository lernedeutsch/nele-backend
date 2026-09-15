# ==========================================
# NELE – POWTÓRKI LEKCJI
# STUDENT MEMORY 2.0
# ==========================================

from datetime import (
    datetime,
    timedelta,
    timezone
)

from brain.memory.lesson_progress import (
    get_lesson_progress,
    get_lesson_progress_memory
)


# ==========================================
# INTERWAŁY POWTÓREK
#
# 1. powtórka  -> 1 dzień
# 2. powtórka  -> 3 dni
# 3. powtórka  -> 7 dni
# 4. powtórka  -> 14 dni
# kolejne      -> 30 dni
# ==========================================

REVIEW_INTERVALS = [
    1,
    3,
    7,
    14,
    30
]


# ==========================================
# AKTUALNY CZAS
# ==========================================

def get_current_time():

    return datetime.now(
        timezone.utc
    )


def get_current_time_iso():

    return get_current_time().isoformat()


# ==========================================
# ZAMIANA DATY ISO NA DATETIME
# ==========================================

def parse_datetime(
    value
):

    if not value:
        return None

    try:

        parsed = datetime.fromisoformat(
            str(
                value
            )
        )

        if parsed.tzinfo is None:

            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed

    except (
        TypeError,
        ValueError
    ):

        return None


# ==========================================
# PUSTA PAMIĘĆ POWTÓRKI LEKCJI
# ==========================================

def create_empty_lesson_review():

    return {
        "review_count": 0,
        "last_review_at": None,
        "next_review_at": None,
        "needs_review": False,
        "last_result": None,
        "history": []
    }


# ==========================================
# PAMIĘĆ POWTÓRKI JEDNEJ LEKCJI
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


    review = lesson_progress.get(
        "review"
    )


    if not isinstance(
        review,
        dict
    ):

        review = (
            create_empty_lesson_review()
        )

        lesson_progress[
            "review"
        ] = review


    defaults = (
        create_empty_lesson_review()
    )


    for key, value in defaults.items():

        if key not in review:

            if isinstance(
                value,
                list
            ):

                value = list(
                    value
                )

            review[
                key
            ] = value


    if not isinstance(
        review.get(
            "history"
        ),
        list
    ):

        review[
            "history"
        ] = []


    try:

        review[
            "review_count"
        ] = int(
            review.get(
                "review_count",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        review[
            "review_count"
        ] = 0


    return review


# ==========================================
# INTERWAŁ NASTĘPNEJ POWTÓRKI
# ==========================================

def get_review_interval_days(
    review_count
):

    try:

        review_count = int(
            review_count
        )

    except (
        TypeError,
        ValueError
    ):

        review_count = 0


    if review_count < 0:

        review_count = 0


    index = min(
        review_count,
        len(
            REVIEW_INTERVALS
        ) - 1
    )


    return REVIEW_INTERVALS[
        index
    ]


# ==========================================
# ZAPLANOWANIE POWTÓRKI
# ==========================================

def schedule_lesson_review(
    state,
    level="A1",
    lesson=1,
    days=None,
    force=False
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )

    if not review:
        return None


    # ======================================
    # JEŻELI POWTÓRKA JEST JUŻ ZAPLANOWANA
    # NIE NADPISUJEMY JEJ BEZ FORCE
    # ======================================

    if (
        review.get(
            "next_review_at"
        )
        and
        not force
    ):

        return review.get(
            "next_review_at"
        )


    if days is None:

        days = get_review_interval_days(
            review.get(
                "review_count",
                0
            )
        )


    try:

        days = int(
            days
        )

    except (
        TypeError,
        ValueError
    ):

        days = 1


    if days < 0:

        days = 0


    next_review = (
        get_current_time()
        +
        timedelta(
            days=days
        )
    )


    review[
        "next_review_at"
    ] = next_review.isoformat()

    review[
        "needs_review"
    ] = (
        days == 0
    )


    return review[
        "next_review_at"
    ]


# ==========================================
# POWTÓRKA OD RAZU
# ==========================================

def schedule_lesson_review_now(
    state,
    level="A1",
    lesson=1
):

    return schedule_lesson_review(
        state,
        level,
        lesson,
        days=0,
        force=True
    )


# ==========================================
# CZY POWTÓRKA JEST JUŻ POTRZEBNA
# ==========================================

def is_lesson_review_due(
    state,
    level="A1",
    lesson=1
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )

    if not review:
        return False


    if review.get(
        "needs_review",
        False
    ):

        return True


    next_review_at = parse_datetime(
        review.get(
            "next_review_at"
        )
    )


    if next_review_at is None:

        return False


    if (
        get_current_time()
        >=
        next_review_at
    ):

        review[
            "needs_review"
        ] = True

        return True


    return False


# ==========================================
# OZNACZENIE POWTÓRKI JAKO POTRZEBNEJ
# ==========================================

def mark_lesson_review_due(
    state,
    level="A1",
    lesson=1
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
# ZAKOŃCZENIE POWTÓRKI
# ==========================================

def mark_lesson_review_completed(
    state,
    level="A1",
    lesson=1,
    result="good"
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )

    if not review:
        return


    now = get_current_time()


    try:

        review_count = int(
            review.get(
                "review_count",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        review_count = 0


    review_count += 1


    review[
        "review_count"
    ] = review_count

    review[
        "last_review_at"
    ] = now.isoformat()

    review[
        "last_result"
    ] = str(
        result or "good"
    )

    review[
        "needs_review"
    ] = False


    history = review.get(
        "history"
    )

    if not isinstance(
        history,
        list
    ):

        history = []

        review[
            "history"
        ] = history


    history.append(
        {
            "reviewed_at":
                now.isoformat(),

            "result":
                str(
                    result or "good"
                )
        }
    )


    # ======================================
    # OGRANICZENIE HISTORII
    # ======================================

    if len(
        history
    ) > 30:

        review[
            "history"
        ] = history[
            -30:
        ]


    # ======================================
    # PLAN KOLEJNEJ POWTÓRKI
    # ======================================

    next_days = get_review_interval_days(
        review_count
    )


    review[
        "next_review_at"
    ] = (
        now
        +
        timedelta(
            days=next_days
        )
    ).isoformat()


# ==========================================
# POWTÓRKA NIE POSZŁA DOBRZE
#
# Nele może wtedy zaplanować ją szybciej.
# ==========================================

def mark_lesson_review_difficult(
    state,
    level="A1",
    lesson=1
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )

    if not review:
        return


    now = get_current_time()


    review[
        "last_review_at"
    ] = now.isoformat()

    review[
        "last_result"
    ] = "difficult"

    review[
        "needs_review"
    ] = False


    # ======================================
    # TRUDNA LEKCJA -> POWTÓRKA JUTRO
    # ======================================

    review[
        "next_review_at"
    ] = (
        now
        +
        timedelta(
            days=1
        )
    ).isoformat()


    history = review.get(
        "history"
    )

    if not isinstance(
        history,
        list
    ):

        history = []

        review[
            "history"
        ] = history


    history.append(
        {
            "reviewed_at":
                now.isoformat(),

            "result":
                "difficult"
        }
    )


    if len(
        history
    ) > 30:

        review[
            "history"
        ] = history[
            -30:
        ]


# ==========================================
# AKTUALIZACJA TERMINU POWTÓRKI
# ==========================================

def refresh_lesson_review(
    state,
    level="A1",
    lesson=1
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )

    if not review:
        return False


    return is_lesson_review_due(
        state,
        level,
        lesson
    )


# ==========================================
# WSZYSTKIE LEKCJE DO POWTÓRKI
# ==========================================

def get_due_lesson_reviews(
    state
):

    memory = get_lesson_progress_memory(
        state
    )

    if not memory:
        return []


    lessons = memory.get(
        "lessons",
        {}
    )


    if not isinstance(
        lessons,
        dict
    ):

        return []


    due_reviews = []


    for lesson_key, lesson_progress in lessons.items():

        if not isinstance(
            lesson_progress,
            dict
        ):

            continue


        level = lesson_progress.get(
            "level",
            "A1"
        )

        lesson = lesson_progress.get(
            "lesson",
            1
        )


        if is_lesson_review_due(
            state,
            level,
            lesson
        ):

            due_reviews.append(
                {
                    "key":
                        lesson_key,

                    "level":
                        level,

                    "lesson":
                        lesson,

                    "review":
                        get_lesson_review(
                            state,
                            level,
                            lesson
                        )
                }
            )


    return due_reviews


# ==========================================
# CZY JEST JAKAŚ LEKCJA DO POWTÓRKI
# ==========================================

def has_due_lesson_review(
    state
):

    return bool(
        get_due_lesson_reviews(
            state
        )
    )


# ==========================================
# PODSUMOWANIE POWTÓRKI LEKCJI
# ==========================================

def get_lesson_review_summary(
    state,
    level="A1",
    lesson=1
):

    review = get_lesson_review(
        state,
        level,
        lesson
    )


    return {
        "level":
            str(
                level or "A1"
            ).strip().upper(),

        "lesson":
            lesson,

        "review_count":
            review.get(
                "review_count",
                0
            ),

        "last_review_at":
            review.get(
                "last_review_at"
            ),

        "next_review_at":
            review.get(
                "next_review_at"
            ),

        "needs_review":
            is_lesson_review_due(
                state,
                level,
                lesson
            ),

        "last_result":
            review.get(
                "last_result"
            )
      }
