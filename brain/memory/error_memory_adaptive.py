# ==========================================
# NELE – ERROR MEMORY ADAPTIVE
# ADAPTIVE REVIEW 2.0
# ==========================================

from brain.memory.error_memory_core import (
    DEFAULT_DIFFICULTY,
    clamp_difficulty,
    get_error_item
)

from brain.memory.error_memory_migration import (
    migrate_error_item
)


# ==========================================
# POBRANIE WPISU Z MIGRACJĄ
# ==========================================

def get_adaptive_error_item(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:

        return None


    return migrate_error_item(
        error_item
    )


# ==========================================
# TRUDNOŚĆ
# ==========================================

def get_error_difficulty(
    state,
    error_type
):

    error_item = get_adaptive_error_item(
        state,
        error_type
    )


    if error_item is None:

        return DEFAULT_DIFFICULTY


    return clamp_difficulty(
        error_item.get(
            "difficulty",
            DEFAULT_DIFFICULTY
        )
    )


# ==========================================
# OSTATNI WYNIK
# ==========================================

def get_error_last_result(
    state,
    error_type
):

    error_item = get_adaptive_error_item(
        state,
        error_type
    )


    if error_item is None:

        return None


    return error_item.get(
        "last_result"
    )


# ==========================================
# OSTATNIA JAKOŚĆ ODPOWIEDZI
# 0–4
# ==========================================

def get_error_last_quality(
    state,
    error_type
):

    error_item = get_adaptive_error_item(
        state,
        error_type
    )


    if error_item is None:

        return None


    quality = error_item.get(
        "last_quality"
    )


    if quality is None:

        return None


    try:

        quality = int(
            quality
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    if not (
        0
        <= quality
        <= 4
    ):

        return None


    return quality


# ==========================================
# TERMIN NASTĘPNEJ POWTÓRKI
# ==========================================

def get_error_next_review_at(
    state,
    error_type
):

    error_item = get_adaptive_error_item(
        state,
        error_type
    )


    if error_item is None:

        return None


    return error_item.get(
        "next_review_at"
    )


# ==========================================
# USTAWIENIE TRUDNOŚCI
# ==========================================

def set_error_difficulty(
    state,
    error_type,
    difficulty
):

    error_item = get_adaptive_error_item(
        state,
        error_type
    )


    if error_item is None:

        return False


    error_item[
        "difficulty"
    ] = clamp_difficulty(
        difficulty
    )


    return True


# ==========================================
# USTAWIENIE OSTATNIEGO WYNIKU
# ==========================================

def set_error_last_result(
    state,
    error_type,
    result
):

    error_item = get_adaptive_error_item(
        state,
        error_type
    )


    if error_item is None:

        return False


    if result is None:

        error_item[
            "last_result"
        ] = None

        return True


    error_item[
        "last_result"
    ] = str(
        result
    )


    return True


# ==========================================
# USTAWIENIE JAKOŚCI
# ==========================================

def set_error_last_quality(
    state,
    error_type,
    quality
):

    error_item = get_adaptive_error_item(
        state,
        error_type
    )


    if error_item is None:

        return False


    if quality is None:

        error_item[
            "last_quality"
        ] = None

        return True


    try:

        quality = int(
            quality
        )

    except (
        TypeError,
        ValueError
    ):

        return False


    if not (
        0
        <= quality
        <= 4
    ):

        return False


    error_item[
        "last_quality"
    ] = quality


    return True


# ==========================================
# USTAWIENIE TERMINU POWTÓRKI
# ==========================================

def set_error_next_review_at(
    state,
    error_type,
    next_review_at
):

    error_item = get_adaptive_error_item(
        state,
        error_type
    )


    if error_item is None:

        return False


    error_item[
        "next_review_at"
    ] = next_review_at


    return True


# ==========================================
# AKTUALIZACJA DANYCH ADAPTACYJNYCH
# ==========================================

def update_error_adaptive_data(
    state,
    error_type,
    difficulty=None,
    last_result=None,
    last_quality=None,
    next_review_at=None,
    update_next_review=True
):

    error_item = get_adaptive_error_item(
        state,
        error_type
    )


    if error_item is None:

        return False


    # ======================================
    # TRUDNOŚĆ
    # ======================================

    if difficulty is not None:

        error_item[
            "difficulty"
        ] = clamp_difficulty(
            difficulty
        )


    # ======================================
    # WYNIK
    # ======================================

    if last_result is not None:

        error_item[
            "last_result"
        ] = str(
            last_result
        )


    # ======================================
    # JAKOŚĆ
    # ======================================

    if last_quality is not None:

        try:

            quality = int(
                last_quality
            )

        except (
            TypeError,
            ValueError
        ):

            quality = None


        if (
            quality is not None
            and
            0 <= quality <= 4
        ):

            error_item[
                "last_quality"
            ] = quality


    # ======================================
    # TERMIN POWTÓRKI
    #
    # update_next_review pozwala również
    # świadomie ustawić None.
    # ======================================

    if update_next_review:

        error_item[
            "next_review_at"
        ] = next_review_at


    return True


# ==========================================
# WYZEROWANIE PLANU POWTÓRKI
# ==========================================

def clear_error_review_schedule(
    state,
    error_type
):

    error_item = get_adaptive_error_item(
        state,
        error_type
    )


    if error_item is None:

        return False


    error_item[
        "next_review_at"
    ] = None


    return True
