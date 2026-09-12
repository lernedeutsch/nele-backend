# ==========================================
# NELE – POWTÓRKI BŁĘDÓW
# ADAPTIVE REVIEW 2.0
# STUDENT MEMORY 2.0
# ==========================================

from datetime import datetime, timezone, timedelta

from brain.memory.error_memory import (
    get_error_memory,
    get_error_item,
    get_error_next_review_at as get_stored_error_next_review_at,
    mark_error_for_review
)


# ==========================================
# STARE ODSTĘPY
# TYLKO DLA DAWNYCH WPISÓW
# ==========================================
#
# Adaptive Review 2.0 używa teraz:
#
# next_review_at
#
# Ten słownik zostaje wyłącznie jako
# zabezpieczenie dla starszej pamięci,
# która nie ma jeszcze next_review_at.
# ==========================================

LEGACY_ERROR_REVIEW_INTERVALS = {

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
    # DATA BEZ STREFY
    # -> TRAKTUJEMY JAK UTC
    # ======================================

    if parsed.tzinfo is None:

        parsed = parsed.replace(
            tzinfo=timezone.utc
        )


    return parsed.astimezone(
        timezone.utc
    )


# ==========================================
# STARY ODSTĘP
# TYLKO DLA LEGACY MEMORY
# ==========================================

def get_legacy_review_interval_hours(
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


    correct_streak = max(
        0,
        correct_streak
    )


    if correct_streak >= 3:

        return None


    return LEGACY_ERROR_REVIEW_INTERVALS.get(
        correct_streak,
        24
    )


# ==========================================
# STARA DATA POWTÓRKI
# TYLKO DLA LEGACY MEMORY
# ==========================================

def get_legacy_error_next_review_at(
    error_item
):

    if not error_item:
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
        get_legacy_review_interval_hours(
            correct_streak
        )
    )


    if interval_hours is None:
        return None


    # ======================================
    # BRAK DATY
    # -> POWTÓRKA MOŻE BYĆ TERAZ
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
# DATA KOLEJNEJ POWTÓRKI
# ==========================================
#
# PRIORYTET:
#
# 1. next_review_at z Adaptive Review 2.0
#
# 2. stary harmonogram tylko wtedy,
#    gdy wpis nie ma jeszcze nowej daty
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
    # OPANOWANY BŁĄD
    # ======================================

    if error_item.get(
        "mastered",
        False
    ):

        return None


    # ======================================
    # ADAPTIVE REVIEW 2.0
    # ======================================

    stored_review = (
        get_stored_error_next_review_at(
            state,
            error_type
        )
    )


    adaptive_review_at = (
        parse_review_timestamp(
            stored_review
        )
    )


    if adaptive_review_at is not None:

        return adaptive_review_at


    # ======================================
    # LEGACY FALLBACK
    # ======================================

    return get_legacy_error_next_review_at(
        error_item
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
    # JUŻ CZEKA NA ĆWICZENIE
    # ======================================

    if error_item.get(
        "needs_practice",
        False
    ):

        return True


    # ======================================
    # TERMIN POWTÓRKI
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


    now = now.astimezone(
        timezone.utc
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


    now = now.astimezone(
        timezone.utc
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


    # ======================================
    # OPANOWANEGO NIE AKTYWUJEMY
    # ======================================

    if error_item.get(
        "mastered",
        False
    ):

        return False


    # ======================================
    # JUŻ CZEKA NA ĆWICZENIE
    # ======================================

    if error_item.get(
        "needs_practice",
        False
    ):

        return False


    # ======================================
    # JESZCZE NIE CZAS
    # ======================================

    if not is_error_due_for_review(
        state,
        error_type,
        now
    ):

        return False


    # ======================================
    # TERMIN NADSZEDŁ
    # -> BŁĄD WRACA DO ĆWICZENIA
    # ======================================

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


    if now.tzinfo is None:

        now = now.replace(
            tzinfo=timezone.utc
        )


    now = now.astimezone(
        timezone.utc
    )


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
# BŁĘDY TERAZ DO POWTÓRKI
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


    if now.tzinfo is None:

        now = now.replace(
            tzinfo=timezone.utc
        )


    now = now.astimezone(
        timezone.utc
    )


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


        # ==================================
        # OPANOWANE
        # ==================================

        if error_item.get(
            "mastered",
            False
        ):

            continue


        # ==================================
        # JUŻ DO ĆWICZENIA
        # ==================================

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


        # ==================================
        # ADAPTIVE REVIEW / LEGACY FALLBACK
        # ==================================

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
