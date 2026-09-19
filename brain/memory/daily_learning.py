# ==========================================
# NELE – DAILY LEARNING MEMORY
# STUDENT MEMORY 2.0
# ==========================================

from datetime import (
    datetime,
    timezone
)

from zoneinfo import (
    ZoneInfo
)


# ==========================================
# DOMYŚLNA STREFA CZASOWA
#
# Jeżeli później użytkownik będzie miał
# własną strefę czasową w pamięci,
# użyjemy jej automatycznie.
# ==========================================

DEFAULT_TIMEZONE = "Europe/Berlin"


# ==========================================
# MAKSYMALNA HISTORIA AKTYWNOŚCI
# JEDNEGO DNIA
# ==========================================

MAX_DAILY_ACTIVITIES = 100

MAX_SESSION_STARTS = 30

MAX_DAILY_MISTAKES = 50


# ==========================================
# STREFA CZASOWA UŻYTKOWNIKA
# ==========================================

def get_user_timezone(
    state=None
):

    timezone_name = (
        DEFAULT_TIMEZONE
    )


    if isinstance(
        state,
        dict
    ):

        timezone_name = (
            state.get(
                "user_timezone"
            )
            or
            state.get(
                "timezone"
            )
            or
            DEFAULT_TIMEZONE
        )


    try:

        return ZoneInfo(
            str(
                timezone_name
            )
        )

    except Exception:

        return timezone.utc


# ==========================================
# AKTUALNY CZAS UŻYTKOWNIKA
# ==========================================

def get_current_time(
    state=None
):

    return datetime.now(
        get_user_timezone(
            state
        )
    )


# ==========================================
# AKTUALNY CZAS ISO
# ==========================================

def get_current_time_iso(
    state=None
):

    return get_current_time(
        state
    ).isoformat()


# ==========================================
# DZISIEJSZA DATA
# ==========================================

def get_today_key(
    state=None
):

    return get_current_time(
        state
    ).date().isoformat()


# ==========================================
# PUSTA PAMIĘĆ DNIA
# ==========================================

def create_empty_daily_learning(
    date_key=None
):

    if not date_key:

        date_key = get_today_key()


    return {

        "date":
            date_key,

        # ----------------------------------
        # SESJE
        # ----------------------------------

        "session_count":
            0,

        "session_starts":
            [],

        "last_session_started_at":
            None,

        # ----------------------------------
        # ĆWICZENIA
        # ----------------------------------

        "completed_exercises":
            0,

        # ----------------------------------
        # SŁOWNICTWO
        # ----------------------------------

        "reviewed_words":
            [],

        # ----------------------------------
        # BŁĘDY PRZEĆWICZONE
        # ----------------------------------

        "reviewed_errors":
            [],

        # ----------------------------------
        # BŁĘDY ZROBIONE DZISIAJ
        # ----------------------------------

        "mistakes":
            [],

        "mistake_counts":
            {},

        # ----------------------------------
        # LEKCJE
        # ----------------------------------

        "lesson_recaps":
            [],

        "lesson_reviews":
            [],

        "lesson_sections":
            [],

        # ----------------------------------
        # PLAN DNIA / SESJI
        # ----------------------------------

        "daily_plan_completed":
            False,

        # ----------------------------------
        # KRÓTKIE PODSUMOWANIE DNIA
        #
        # Pokazujemy je najwyżej raz dziennie,
        # żeby przy każdym ponownym otwarciu
        # Nele nie powtarzała:
        # "Heute hast du schon ..."
        # ----------------------------------

        "progress_message_shown":
            False,

        # ----------------------------------
        # HISTORIA AKTYWNOŚCI
        # ----------------------------------

        "activities":
            []
    }


# ==========================================
# UZUPEŁNIENIE BRAKUJĄCYCH PÓL
# ==========================================

def ensure_daily_learning_defaults(
    memory,
    date_key
):

    defaults = (
        create_empty_daily_learning(
            date_key
        )
    )


    for key, value in defaults.items():

        if key in memory:
            continue


        if isinstance(
            value,
            list
        ):

            memory[
                key
            ] = list(
                value
            )

        elif isinstance(
            value,
            dict
        ):

            memory[
                key
            ] = dict(
                value
            )

        else:

            memory[
                key
            ] = value


    return memory


# ==========================================
# GŁÓWNA PAMIĘĆ DNIA
#
# Jeżeli zmienił się dzień,
# automatycznie zaczynamy nową pamięć.
#
# Dzięki temu ponowne otwarcie strony
# tego samego dnia NIE zeruje historii.
# ==========================================

def get_daily_learning_memory(
    state
):

    if state is None:
        return {}


    today = get_today_key(
        state
    )


    memory = state.get(
        "daily_learning"
    )


    if not isinstance(
        memory,
        dict
    ):

        memory = (
            create_empty_daily_learning(
                today
            )
        )

        state[
            "daily_learning"
        ] = memory


        return memory


    stored_date = str(
        memory.get(
            "date",
            ""
        )
        or
        ""
    ).strip()


    # ======================================
    # NOWY DZIEŃ
    # ======================================

    if stored_date != today:

        memory = (
            create_empty_daily_learning(
                today
            )
        )

        state[
            "daily_learning"
        ] = memory


        return memory


    ensure_daily_learning_defaults(
        memory,
        today
    )


    return memory


# ==========================================
# NOWA SESJA W TYM SAMYM DNIU
# ==========================================

def start_daily_session(
    state
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return {}


    try:

        session_count = int(
            memory.get(
                "session_count",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        session_count = 0


    session_count += 1


    now = get_current_time_iso(
        state
    )


    memory[
        "session_count"
    ] = session_count

    memory[
        "last_session_started_at"
    ] = now


    starts = memory.get(
        "session_starts"
    )


    if not isinstance(
        starts,
        list
    ):

        starts = []

        memory[
            "session_starts"
        ] = starts


    starts.append(
        now
    )


    if len(
        starts
    ) > MAX_SESSION_STARTS:

        memory[
            "session_starts"
        ] = starts[
            -MAX_SESSION_STARTS:
        ]


    return memory


# ==========================================
# CZY PODSUMOWANIE DNIA BYŁO JUŻ POKAZANE
# ==========================================

def was_daily_progress_message_shown(
    state
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return False


    return bool(
        memory.get(
            "progress_message_shown",
            False
        )
    )


# ==========================================
# OZNACZ PODSUMOWANIE DNIA JAKO POKAZANE
# ==========================================

def mark_daily_progress_message_shown(
    state
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return False


    memory[
        "progress_message_shown"
    ] = True


    return True


# ==========================================
# ZAPIS AKTYWNOŚCI DNIA
# ==========================================

def record_daily_activity(
    state,
    activity_type,
    detail=None,
    result=None
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return


    activity_type = str(
        activity_type or ""
    ).strip()


    if not activity_type:
        return


    activities = memory.get(
        "activities"
    )


    if not isinstance(
        activities,
        list
    ):

        activities = []

        memory[
            "activities"
        ] = activities


    item = {

        "type":
            activity_type,

        "at":
            get_current_time_iso(
                state
            )
    }


    if detail is not None:

        item[
            "detail"
        ] = detail


    if result is not None:

        item[
            "result"
        ] = result


    activities.append(
        item
    )


    if len(
        activities
    ) > MAX_DAILY_ACTIVITIES:

        memory[
            "activities"
        ] = activities[
            -MAX_DAILY_ACTIVITIES:
        ]


# ==========================================
# ZAKOŃCZONE ĆWICZENIE
# ==========================================

def mark_exercise_completed_today(
    state,
    activity_type=None,
    detail=None
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return


    try:

        count = int(
            memory.get(
                "completed_exercises",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        count = 0


    memory[
        "completed_exercises"
    ] = count + 1


    if activity_type:

        record_daily_activity(
            state,
            activity_type,
            detail=detail,
            result="completed"
        )


# ==========================================
# DODANIE UNIKALNEJ WARTOŚCI
# ==========================================

def add_unique_value(
    items,
    value
):

    if not isinstance(
        items,
        list
    ):

        return False


    value = str(
        value or ""
    ).strip()


    if not value:
        return False


    value_key = value.lower()


    for existing in items:

        if (
            str(
                existing or ""
            )
            .strip()
            .lower()
            ==
            value_key
        ):

            return False


    items.append(
        value
    )


    return True


# ==========================================
# SŁOWO POWTÓRZONE DZISIAJ
# ==========================================

def mark_word_reviewed_today(
    state,
    word
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return False


    words = memory.get(
        "reviewed_words"
    )


    if not isinstance(
        words,
        list
    ):

        words = []

        memory[
            "reviewed_words"
        ] = words


    added = add_unique_value(
        words,
        word
    )


    if added:

        record_daily_activity(
            state,
            "vocabulary_review",
            detail=str(
                word
            ).strip(),
            result="completed"
        )


    return added


# ==========================================
# CZY SŁOWO BYŁO JUŻ DZISIAJ
# ==========================================

def was_word_reviewed_today(
    state,
    word
):

    memory = get_daily_learning_memory(
        state
    )


    word = str(
        word or ""
    ).strip().lower()


    if not word:
        return False


    return any(
        str(
            item or ""
        ).strip().lower()
        ==
        word
        for item in memory.get(
            "reviewed_words",
            []
        )
    )


# ==========================================
# BŁĄD PRZEĆWICZONY DZISIAJ
# ==========================================

def mark_error_reviewed_today(
    state,
    error_type
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return False


    errors = memory.get(
        "reviewed_errors"
    )


    if not isinstance(
        errors,
        list
    ):

        errors = []

        memory[
            "reviewed_errors"
        ] = errors


    added = add_unique_value(
        errors,
        error_type
    )


    if added:

        record_daily_activity(
            state,
            "error_review",
            detail=str(
                error_type
            ).strip(),
            result="completed"
        )


    return added


# ==========================================
# CZY BŁĄD BYŁ JUŻ DZISIAJ ĆWICZONY
# ==========================================

def was_error_reviewed_today(
    state,
    error_type
):

    memory = get_daily_learning_memory(
        state
    )


    error_type = str(
        error_type or ""
    ).strip().lower()


    if not error_type:
        return False


    return any(
        str(
            item or ""
        ).strip().lower()
        ==
        error_type
        for item in memory.get(
            "reviewed_errors",
            []
        )
    )


# ==========================================
# BŁĄD ZROBIONY DZISIAJ
# ==========================================

def record_mistake_today(
    state,
    error_type,
    wrong=None,
    correct=None
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return


    error_type = str(
        error_type or "unknown"
    ).strip().lower()


    counts = memory.get(
        "mistake_counts"
    )


    if not isinstance(
        counts,
        dict
    ):

        counts = {}

        memory[
            "mistake_counts"
        ] = counts


    try:

        count = int(
            counts.get(
                error_type,
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        count = 0


    counts[
        error_type
    ] = count + 1


    mistakes = memory.get(
        "mistakes"
    )


    if not isinstance(
        mistakes,
        list
    ):

        mistakes = []

        memory[
            "mistakes"
        ] = mistakes


    item = {

        "type":
            error_type,

        "at":
            get_current_time_iso(
                state
            )
    }


    if wrong:

        item[
            "wrong"
        ] = str(
            wrong
        ).strip()


    if correct:

        item[
            "correct"
        ] = str(
            correct
        ).strip()


    mistakes.append(
        item
    )


    if len(
        mistakes
    ) > MAX_DAILY_MISTAKES:

        memory[
            "mistakes"
        ] = mistakes[
            -MAX_DAILY_MISTAKES:
        ]


    record_daily_activity(
        state,
        "mistake",
        detail=error_type
    )


# ==========================================
# KRÓTKIE PRZYPOMNIENIE LEKCJI
# ==========================================

def mark_lesson_recap_today(
    state,
    level,
    lesson,
    section=None
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return False


    key = (
        f"{str(level or 'A1').strip().upper()}"
        f":{lesson}"
    )


    if section:

        key += (
            ":"
            + str(
                section
            ).strip()
        )


    recaps = memory.get(
        "lesson_recaps"
    )


    if not isinstance(
        recaps,
        list
    ):

        recaps = []

        memory[
            "lesson_recaps"
        ] = recaps


    added = add_unique_value(
        recaps,
        key
    )


    if added:

        record_daily_activity(
            state,
            "lesson_recap",
            detail=key,
            result="completed"
        )


    return added


# ==========================================
# PEŁNA POWTÓRKA LEKCJI
# ==========================================

def mark_lesson_reviewed_today(
    state,
    level,
    lesson,
    result=None
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return False


    key = (
        f"{str(level or 'A1').strip().upper()}"
        f":{lesson}"
    )


    reviews = memory.get(
        "lesson_reviews"
    )


    if not isinstance(
        reviews,
        list
    ):

        reviews = []

        memory[
            "lesson_reviews"
        ] = reviews


    added = add_unique_value(
        reviews,
        key
    )


    if added:

        record_daily_activity(
            state,
            "lesson_review",
            detail=key,
            result=result or "completed"
        )


    return added


# ==========================================
# CZĘŚĆ LEKCJI ĆWICZONA DZISIAJ
# ==========================================

def mark_lesson_section_today(
    state,
    level,
    lesson,
    section
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return False


    section = str(
        section or ""
    ).strip()


    if not section:
        return False


    key = (
        f"{str(level or 'A1').strip().upper()}"
        f":{lesson}:{section}"
    )


    sections = memory.get(
        "lesson_sections"
    )


    if not isinstance(
        sections,
        list
    ):

        sections = []

        memory[
            "lesson_sections"
        ] = sections


    added = add_unique_value(
        sections,
        key
    )


    if added:

        record_daily_activity(
            state,
            "lesson_section",
            detail=key,
            result="completed"
        )


    return added


# ==========================================
# PLAN DNIA ZAKOŃCZONY
# ==========================================

def mark_daily_plan_completed(
    state
):

    memory = get_daily_learning_memory(
        state
    )


    if not memory:
        return


    memory[
        "daily_plan_completed"
    ] = True


    record_daily_activity(
        state,
        "daily_plan",
        result="completed"
    )


# ==========================================
# CZY PLAN DNIA JEST ZAKOŃCZONY
# ==========================================

def is_daily_plan_completed(
    state
):

    memory = get_daily_learning_memory(
        state
    )


    return bool(
        memory.get(
            "daily_plan_completed",
            False
        )
    )


# ==========================================
# NAJCZĘSTSZY BŁĄD DZISIAJ
# ==========================================

def get_most_common_mistake_today(
    state
):

    memory = get_daily_learning_memory(
        state
    )


    counts = memory.get(
        "mistake_counts",
        {}
    )


    if not isinstance(
        counts,
        dict
    ):

        return None


    if not counts:
        return None


    return max(
        counts,
        key=counts.get
    )


# ==========================================
# PODSUMOWANIE DZISIEJSZEJ NAUKI
# ==========================================

def get_daily_learning_summary(
    state
):

    memory = get_daily_learning_memory(
        state
    )


    return {

        "date":
            memory.get(
                "date"
            ),

        "session_count":
            memory.get(
                "session_count",
                0
            ),

        "completed_exercises":
            memory.get(
                "completed_exercises",
                0
            ),

        "reviewed_words":
            list(
                memory.get(
                    "reviewed_words",
                    []
                )
            ),

        "reviewed_errors":
            list(
                memory.get(
                    "reviewed_errors",
                    []
                )
            ),

        "mistake_counts":
            dict(
                memory.get(
                    "mistake_counts",
                    {}
                )
            ),

        "lesson_recaps":
            list(
                memory.get(
                    "lesson_recaps",
                    []
                )
            ),

        "lesson_reviews":
            list(
                memory.get(
                    "lesson_reviews",
                    []
                )
            ),

        "lesson_sections":
            list(
                memory.get(
                    "lesson_sections",
                    []
                )
            ),

        "daily_plan_completed":
            bool(
                memory.get(
                    "daily_plan_completed",
                    False
                )
            )
  }
