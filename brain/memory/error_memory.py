# ==========================================
# NELE – PAMIĘĆ BŁĘDÓW UCZNIA
# STUDENT MEMORY 2.0
# ==========================================


# ==========================================
# POBRANIE GŁÓWNEJ PAMIĘCI BŁĘDÓW
# ==========================================

def get_error_memory(
    state
):

    if state is None:
        return {}

    if "error_memory" not in state:

        state[
            "error_memory"
        ] = {}


    error_memory = state[
        "error_memory"
    ]


    if not isinstance(
        error_memory,
        dict
    ):

        error_memory = {}

        state[
            "error_memory"
        ] = error_memory


    return error_memory


# ==========================================
# POBRANIE JEDNEGO TYPU BŁĘDU
# ==========================================

def get_error_item(
    error_type,
    state
):

    if state is None:
        return None

    if not error_type:
        return None


    error_type = str(
        error_type
    ).strip()


    if not error_type:
        return None


    error_memory = get_error_memory(
        state
    )


    if error_type not in error_memory:

        error_memory[
            error_type
        ] = {
            "count": 0,
            "last_wrong": None,
            "last_correct": None,
            "needs_practice": False
        }


    error_item = error_memory[
        error_type
    ]


    # ======================================
    # ZGODNOŚĆ ZE STARSZĄ PAMIĘCIĄ
    # ======================================

    defaults = {
        "count": 0,
        "last_wrong": None,
        "last_correct": None,
        "needs_practice": False
    }


    for key, value in defaults.items():

        if key not in error_item:

            error_item[
                key
            ] = value


    return error_item


# ==========================================
# ZAPISANIE BŁĘDU
# ==========================================

def remember_error(
    state,
    error_type,
    wrong_text,
    correct_text
):

    if state is None:
        return False

    if not error_type:
        return False


    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:
        return False


    error_item[
        "count"
    ] += 1


    if wrong_text:

        error_item[
            "last_wrong"
        ] = str(
            wrong_text
        ).strip()


    if correct_text:

        error_item[
            "last_correct"
        ] = str(
            correct_text
        ).strip()


    error_item[
        "needs_practice"
    ] = True


    return True


# ==========================================
# LICZBA BŁĘDÓW DANEGO TYPU
# ==========================================

def get_error_count(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:
        return 0


    return error_item.get(
        "count",
        0
    )


# ==========================================
# CZY BŁĄD WYMAGA ĆWICZENIA
# ==========================================

def error_needs_practice(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:
        return False


    return bool(
        error_item.get(
            "needs_practice",
            False
        )
    )


# ==========================================
# OZNACZENIE BŁĘDU JAKO PRZEĆWICZONEGO
# ==========================================

def mark_error_practiced(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:
        return False


    error_item[
        "needs_practice"
    ] = False


    return True


# ==========================================
# BŁĘDY DO POWTÓRKI
# ==========================================

def get_errors_for_practice(
    state
):

    error_memory = get_error_memory(
        state
    )

    errors = []


    for error_type, error_item in error_memory.items():

        if not isinstance(
            error_item,
            dict
        ):

            continue


        if error_item.get(
            "needs_practice",
            False
        ):

            errors.append(
                error_type
            )


    return errors


# ==========================================
# NAJCZĘSTSZE BŁĘDY
# ==========================================

def get_most_common_errors(
    state,
    limit=5
):

    error_memory = get_error_memory(
        state
    )

    errors = []


    for error_type, error_item in error_memory.items():

        if not isinstance(
            error_item,
            dict
        ):

            continue


        errors.append(
            (
                error_type,
                error_item.get(
                    "count",
                    0
                )
            )
        )


    errors.sort(
        key=lambda item: item[1],
        reverse=True
    )


    return [
        error_type
        for error_type, count
        in errors[:limit]
        if count > 0
    ]


# ==========================================
# PODSUMOWANIE JEDNEGO BŁĘDU
# ==========================================

def get_error_summary(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:
        return None


    return {
        "type":
            error_type,

        "count":
            error_item.get(
                "count",
                0
            ),

        "last_wrong":
            error_item.get(
                "last_wrong"
            ),

        "last_correct":
            error_item.get(
                "last_correct"
            ),

        "needs_practice":
            error_item.get(
                "needs_practice",
                False
            )
    }


# ==========================================
# WSZYSTKIE ZAPISANE BŁĘDY
# ==========================================

def get_all_errors(
    state
):

    error_memory = get_error_memory(
        state
    )

    result = {}


    for error_type in error_memory:

        summary = get_error_summary(
            state,
            error_type
        )


        if summary:

            result[
                error_type
            ] = summary


    return result
