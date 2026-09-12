# ==========================================
# NELE – POWTÓRKI BŁĘDÓW
# SPACED REPETITION
# STUDENT MEMORY 2.0
# ==========================================

from datetime import datetime, timezone, timedelta

from brain.memory.error_memory import (
    get_error_memory,
    get_error_item,
    mark_error_for_review
)


# ==========================================
# ODSTĘPY MIĘDZY POWTÓRKAMI
# ==========================================
#
# correct_streak = 1
# -> następna powtórka po 1 dniu
#
# correct_streak = 2
# -> następna powtórka po 3 dniach
#
# correct_streak >= 3
# -> błąd powinien być już mastered
# ==========================================

ERROR_REVIEW_INTERVALS = {

    0: 0,

    1: 24,

    2: 72
}


# ==========================================
# AKTUALNY CZAS UTC
# ==========================================

def get_review_now():

    return datetime.now(
        timezone.utc
    )


# ==========================================
# ODCZYT DATY ISO
# ==========================================

def parse_review_timestamp(
    timestamp
):

    if not timestamp:
        return None


    if isinstance(
        timestamp,
        datetime
    ):

        parsed = timestamp

    else:

        try:

            parsed = datetime.fromisoformat(
                str(
                    timestamp
                ).replace(
                    "Z",
                    "+00:00"
                )
            )

        except (
            TypeError,
            ValueError
        ):

            return None


    # ======================================
    # JEŚLI DATA NIE MA STREFY CZASOWEJ,
    # TRAKTUJEMY JĄ JAK UTC
    # ======================================

    if parsed.tzinfo is None:

        parsed = parsed.replace(
            tzinfo=timezone.utc
        )


    return parsed.astimezone(
        timezone.utc
    )


# ==========================================
# LICZBA GODZIN DO KOLEJNEJ POWTÓRKI
# ==========================================

def get_error_review_interval_hours(
    correct_streak
):

    try:

        correct_streak = int(
            correct_streak
        )

    except (
        TypeError,
        ValueError
    ):

        correct_streak = 0


    if correct_streak >= 3:

        return None


    return ERROR_REVIEW_INTERVALS.get(
        correct_streak,
        24
    )


# ==========================================
# DATA KOLEJNEJ POWTÓRKI
# ==========================================

def get_error_next_review_at(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if not error_item:
        return None


    # ======================================
    # OPANOWANEGO BŁĘDU
    # NIE PLANUJEMY
    # ======================================

    if error_item.get(
        "mastered",
        False
    ):

        return None


    last_practiced = parse_review_timestamp(
        error_item.get(
            "last_practiced"
        )
    )


    correct_streak = error_item.get(
        "correct_streak",
        0
    )


    interval_hours = (
        get_error_review_interval_hours(
            correct_streak
        )
    )


    if interval_hours is None:
        return None


    # ======================================
    # BRAK DATY POPRZEDNIEGO ĆWICZENIA
    #
    # Dotyczy m.in. starszej pamięci,
    # utworzonej przed dodaniem
    # spaced repetition.
    # ======================================

    if last_practiced is None:

        return get_review_now()


    return (
        last_practiced
        +
        timedelta(
            hours=interval_hours
        )
    )


# ==========================================
# CZY BŁĄD JEST JUŻ DO POWTÓRKI
# ==========================================

def is_error_due_for_review(
    state,
    error_type,
    now=None
):

    error_item = get_error_item(
        error_type,
        state
    )


    if not error_item:
        return False


    # ======================================
    # BŁĄD OPANOWANY
    # ======================================

    if error_item.get(
        "mastered",
        False
    ):

        return False


    # ======================================
    # JUŻ JEST OZNACZONY DO ĆWICZENIA
    # ======================================

    if error_item.get(
        "needs_practice",
        False
    ):

        return True


    # ======================================
    # CZAS KOLEJNEJ POWTÓRKI
    # ======================================

    next_review = get_error_next_review_at(
        state,
        error_type
    )


    if next_review is None:
        return False


    if now is None:

        now = get_review_now()


    if now.tzinfo is None:

        now = now.replace(
            tzinfo=timezone.utc
        )


    return now >= next_review


# ==========================================
# ILE CZASU ZOSTAŁO DO POWTÓRKI
# ==========================================

def get_error_review_wait_seconds(
    state,
    error_type,
    now=None
):

    next_review = get_error_next_review_at(
        state,
        error_type
    )


    if next_review is None:
        return None


    if now is None:

        now = get_review_now()


    if now.tzinfo is None:

        now = now.replace(
            tzinfo=timezone.utc
        )


    seconds = (
        next_review
        -
        now
    ).total_seconds()


    return max(
        0,
        int(
            seconds
        )
    )


# ==========================================
# ODSWIEŻENIE JEDNEGO BŁĘDU
# ==========================================

def refresh_error_review(
    state,
    error_type,
    now=None
):

    if not error_type:
        return False


    error_item = get_error_item(
        error_type,
        state
    )


    if not error_item:
        return False


    if error_item.get(
        "mastered",
        False
    ):

        return False


    if error_item.get(
        "needs_practice",
        False
    ):

        return False


    if not is_error_due_for_review(
        state,
        error_type,
        now
    ):

        return False


    return mark_error_for_review(
        state,
        error_type
    )


# ==========================================
# ODSWIEŻENIE WSZYSTKICH BŁĘDÓW
# ==========================================

def refresh_error_reviews(
    state,
    now=None
):

    if state is None:
        return []


    error_memory = get_error_memory(
        state
    )


    if now is None:

        now = get_review_now()


    activated = []


    for error_type in list(
        error_memory.keys()
    ):

        changed = refresh_error_review(
            state,
            error_type,
            now
        )


        if changed:

            activated.append(
                error_type
            )


    return activated


# ==========================================
# BŁĘDY, KTÓRE SĄ TERAZ DO POWTÓRKI
# ==========================================

def get_due_error_reviews(
    state,
    now=None
):

    if state is None:
        return []


    error_memory = get_error_memory(
        state
    )


    if now is None:

        now = get_review_now()


    due_errors = []


    for error_type in error_memory:

        if is_error_due_for_review(
            state,
            error_type,
            now
        ):

            due_errors.append(
                error_type
            )


    return due_errors


# ==========================================
# NAJBLIŻSZA PLANOWANA POWTÓRKA
# ==========================================

def get_next_error_review(
    state
):

    if state is None:
        return None


    error_memory = get_error_memory(
        state
    )

    reviews = []


    for error_type in error_memory:

        error_item = get_error_item(
            error_type,
            state
        )


        if not error_item:
            continue


        if error_item.get(
            "mastered",
            False
        ):

            continue


        if error_item.get(
            "needs_practice",
            False
        ):

            reviews.append(
                (
                    error_type,
                    get_review_now()
                )
            )

            continue


        next_review = get_error_next_review_at(
            state,
            error_type
        )


        if next_review:

            reviews.append(
                (
                    error_type,
                    next_review
                )
            )


    if not reviews:
        return None


    reviews.sort(
        key=lambda item: item[1]
    )


    error_type, review_at = reviews[0]


    return {
        "error_type":
            error_type,

        "review_at":
            review_at.isoformat()
      }
