# ==========================================
# NELE – PAMIĘĆ BŁĘDÓW UCZNIA
# STUDENT MEMORY 2.0
# ==========================================

from datetime import datetime, timezone


# ==========================================
# USTAWIENIA
# ==========================================

MASTERED_CORRECT_STREAK = 3
MAX_PRACTICE_HISTORY = 20


# ==========================================
# AKTUALNY CZAS
# ==========================================

def get_current_timestamp():

    return datetime.now(
        timezone.utc
    ).isoformat()


# ==========================================
# DOMYŚLNA STRUKTURA BŁĘDU
# ==========================================

def create_empty_error_item():

    return {
        "count": 0,
        "last_wrong": None,
        "last_correct": None,

        "needs_practice": False,

        "practice_count": 0,
        "correct_streak": 0,

        "mastered": False,

        "last_practiced": None,

        "practice_history": []
    }


# ==========================================
# UZUPEŁNIENIE STAREJ PAMIĘCI
# ==========================================

def normalize_error_item(
    error_item
):

    if not isinstance(
        error_item,
        dict
    ):

        error_item = {}


    defaults = create_empty_error_item()


    for key, value in defaults.items():

        if key not in error_item:

            if isinstance(
                value,
                list
            ):

                error_item[
                    key
                ] = []

            else:

                error_item[
                    key
                ] = value


    # ======================================
    # BEZPIECZNE TYPY
    # ======================================

    if not isinstance(
        error_item.get(
            "count"
        ),
        int
    ):

        error_item[
            "count"
        ] = 0


    if not isinstance(
        error_item.get(
            "practice_count"
        ),
        int
    ):

        error_item[
            "practice_count"
        ] = 0


    if not isinstance(
        error_item.get(
            "correct_streak"
        ),
        int
    ):

        error_item[
            "correct_streak"
        ] = 0


    if not isinstance(
        error_item.get(
            "practice_history"
        ),
        list
    ):

        error_item[
            "practice_history"
        ] = []


    error_item[
        "needs_practice"
    ] = bool(
        error_item.get(
            "needs_practice",
            False
        )
    )


    error_item[
        "mastered"
    ] = bool(
        error_item.get(
            "mastered",
            False
        )
    )


    return error_item


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


    # ======================================
    # AKTUALIZACJA STARYCH WPISÓW
    # ======================================

    for error_type in list(
        error_memory.keys()
    ):

        error_memory[
            error_type
        ] = normalize_error_item(
            error_memory[
                error_type
            ]
        )


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
        ] = create_empty_error_item()


    error_memory[
        error_type
    ] = normalize_error_item(
        error_memory[
            error_type
        ]
    )


    return error_memory[
        error_type
    ]


# ==========================================
# DODANIE WPISU DO HISTORII ĆWICZEŃ
# ==========================================

def add_practice_history(
    error_item,
    result
):

    if not error_item:
        return


    history = error_item.get(
        "practice_history"
    )


    if not isinstance(
        history,
        list
    ):

        history = []

        error_item[
            "practice_history"
        ] = history


    history.append(
        {
            "result": result,
            "timestamp": get_current_timestamp()
        }
    )


    # ======================================
    # NIE POZWALAMY HISTORII ROSNĄĆ
    # W NIESKOŃCZONOŚĆ
    # ======================================

    if len(
        history
    ) > MAX_PRACTICE_HISTORY:

        error_item[
            "practice_history"
        ] = history[
            -MAX_PRACTICE_HISTORY:
        ]


# ==========================================
# ZAPISANIE NOWEGO BŁĘDU
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


    # ======================================
    # LICZNIK WYSTĄPIEŃ
    # ======================================

    error_item[
        "count"
    ] += 1


    # ======================================
    # OSTATNI BŁĘDNY PRZYKŁAD
    # ======================================

    if wrong_text:

        error_item[
            "last_wrong"
        ] = str(
            wrong_text
        ).strip()


    # ======================================
    # OSTATNIA POPRAWNA WERSJA
    # ======================================

    if correct_text:

        error_item[
            "last_correct"
        ] = str(
            correct_text
        ).strip()


    # ======================================
    # BŁĄD POJAWIŁ SIĘ PONOWNIE
    #
    # Czyli wcześniejsza dobra seria
    # nie jest już aktualna.
    # ======================================

    error_item[
        "needs_practice"
    ] = True

    error_item[
        "correct_streak"
    ] = 0

    error_item[
        "mastered"
    ] = False


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
# LICZBA ĆWICZEŃ DANEGO BŁĘDU
# ==========================================

def get_error_practice_count(
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
        "practice_count",
        0
    )


# ==========================================
# POPRAWNA SERIA
# ==========================================

def get_error_correct_streak(
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
        "correct_streak",
        0
    )


# ==========================================
# CZY BŁĄD JEST OPANOWANY
# ==========================================

def is_error_mastered(
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
            "mastered",
            False
        )
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
# POPRAWNIE PRZEĆWICZONY BŁĄD
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


    # ======================================
    # LICZNIK ĆWICZEŃ
    # ======================================

    error_item[
        "practice_count"
    ] += 1


    # ======================================
    # SERIA POPRAWNYCH ODPOWIEDZI
    # ======================================

    error_item[
        "correct_streak"
    ] += 1


    # ======================================
    # DATA OSTATNIEGO ĆWICZENIA
    # ======================================

    error_item[
        "last_practiced"
    ] = get_current_timestamp()


    # ======================================
    # HISTORIA
    # ======================================

    add_practice_history(
        error_item,
        "correct"
    )


    # ======================================
    # PO JEDNYM DOBRYM ĆWICZENIU
    # NIE MUSI BYĆ POWTARZANY NATYCHMIAST
    # ======================================

    error_item[
        "needs_practice"
    ] = False


    # ======================================
    # OPANOWANIE DOPIERO PO 3
    # POPRAWNYCH POWTÓRKACH Z RZĘDU
    # ======================================

    if (
        error_item[
            "correct_streak"
        ]
        >= MASTERED_CORRECT_STREAK
    ):

        error_item[
            "mastered"
        ] = True

    else:

        error_item[
            "mastered"
        ] = False


    return True


# ==========================================
# PONOWNE DODANIE BŁĘDU DO POWTÓRKI
# ==========================================

def mark_error_for_review(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:
        return False


    if error_item.get(
        "mastered",
        False
    ):

        return False


    error_item[
        "needs_practice"
    ] = True


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
# BŁĘDY JESZCZE NIEOPANOWANE
# ==========================================

def get_unmastered_errors(
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


        if (
            error_item.get(
                "count",
                0
            ) > 0
            and
            not error_item.get(
                "mastered",
                False
            )
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
# HISTORIA ĆWICZEŃ
# ==========================================

def get_error_practice_history(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:
        return []


    history = error_item.get(
        "practice_history",
        []
    )


    if not isinstance(
        history,
        list
    ):

        return []


    return history


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
            ),

        "practice_count":
            error_item.get(
                "practice_count",
                0
            ),

        "correct_streak":
            error_item.get(
                "correct_streak",
                0
            ),

        "mastered":
            error_item.get(
                "mastered",
                False
            ),

        "last_practiced":
            error_item.get(
                "last_practiced"
            ),

        "practice_history":
            error_item.get(
                "practice_history",
                []
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
