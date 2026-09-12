# ==========================================
# NELE – PAMIĘĆ BŁĘDÓW UCZNIA
# STUDENT MEMORY 2.0
# ADAPTIVE REVIEW 2.0
# ==========================================

from datetime import datetime, timezone


# ==========================================
# USTAWIENIA
# ==========================================

MASTERED_CORRECT_STREAK = 3
MAX_PRACTICE_HISTORY = 20

DEFAULT_DIFFICULTY = 0.5


# ==========================================
# AKTUALNY CZAS
# ==========================================

def get_current_timestamp():

    return datetime.now(
        timezone.utc
    ).isoformat()


# ==========================================
# OGRANICZENIE TRUDNOŚCI
# ==========================================

def clamp_difficulty(
    value
):

    try:

        value = float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        value = DEFAULT_DIFFICULTY


    return max(
        0.0,
        min(
            1.0,
            value
        )
    )


# ==========================================
# DOMYŚLNA STRUKTURA BŁĘDU
# ==========================================

def create_empty_error_item():

    return {

        # ==================================
        # BŁĄD
        # ==================================

        "count": 0,

        "last_wrong": None,
        "last_correct": None,

        "needs_practice": False,


        # ==================================
        # POSTĘP
        # ==================================

        "practice_count": 0,

        "correct_streak": 0,

        "mastered": False,

        "last_practiced": None,

        "practice_history": [],


        # ==================================
        # ADAPTIVE REVIEW 2.0
        # ==================================

        # 0.0 = łatwe
        # 0.5 = normalne
        # 1.0 = trudne

        "difficulty":
            DEFAULT_DIFFICULTY,


        # Ostatni wynik:
        #
        # wrong
        # correct_with_help
        # correct_with_difficulty
        # correct
        # correct_easy

        "last_result":
            None,


        # Jakość 0–4

        "last_quality":
            None,


        # Termin kolejnej powtórki

        "next_review_at":
            None,


        # Ile razy błąd wrócił
        # po wcześniejszej nauce

        "lapses":
            0,


        # Poprawne odpowiedzi
        # w ćwiczeniach mówienia

        "spoken_successes":
            0
    }


# ==========================================
# MIGRACJA STAREGO WPISU
# ==========================================
#
# Starsza wersja pamięci mogła już
# oznaczyć błąd jako przećwiczony,
# ale nie posiadała nowych pól.
#
# Jeżeli mamy:
#
# count > 0
# needs_practice = False
# practice_count = 0
# correct_streak = 0
# last_practiced = None
# practice_history = []
#
# traktujemy to jako jedno poprawnie
# wykonane ćwiczenie starego systemu.
# ==========================================

def migrate_legacy_error_item(
    error_item
):

    if not isinstance(
        error_item,
        dict
    ):

        return error_item


    count = error_item.get(
        "count",
        0
    )

    needs_practice = error_item.get(
        "needs_practice",
        False
    )

    practice_count = error_item.get(
        "practice_count",
        0
    )

    correct_streak = error_item.get(
        "correct_streak",
        0
    )

    last_practiced = error_item.get(
        "last_practiced"
    )

    practice_history = error_item.get(
        "practice_history",
        []
    )


    is_legacy_practiced_error = (

        count > 0

        and

        needs_practice is False

        and

        practice_count == 0

        and

        correct_streak == 0

        and

        not last_practiced

        and

        not practice_history
    )


    if not is_legacy_practiced_error:

        return error_item


    migrated_at = get_current_timestamp()


    error_item[
        "practice_count"
    ] = 1


    error_item[
        "correct_streak"
    ] = 1


    error_item[
        "mastered"
    ] = False


    error_item[
        "needs_practice"
    ] = False


    error_item[
        "last_practiced"
    ] = migrated_at


    error_item[
        "last_result"
    ] = "correct"


    error_item[
        "practice_history"
    ] = [
        {
            "result":
                "correct",

            "timestamp":
                migrated_at,

            "legacy":
                True
        }
    ]


    return error_item


# ==========================================
# UZUPEŁNIENIE / NORMALIZACJA PAMIĘCI
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


    # ======================================
    # BRAKUJĄCE POLA
    # ======================================

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
    # LICZNIKI
    # ======================================

    integer_fields = (

        "count",
        "practice_count",
        "correct_streak",
        "lapses",
        "spoken_successes"
    )


    for field in integer_fields:

        if not isinstance(
            error_item.get(
                field
            ),
            int
        ):

            error_item[
                field
            ] = 0


        if error_item[
            field
        ] < 0:

            error_item[
                field
            ] = 0


    # ======================================
    # HISTORIA
    # ======================================

    if not isinstance(
        error_item.get(
            "practice_history"
        ),
        list
    ):

        error_item[
            "practice_history"
        ] = []


    # ======================================
    # BOOLEAN
    # ======================================

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


    # ======================================
    # TRUDNOŚĆ
    # ======================================

    error_item[
        "difficulty"
    ] = clamp_difficulty(
        error_item.get(
            "difficulty",
            DEFAULT_DIFFICULTY
        )
    )


    # ======================================
    # JAKOŚĆ
    # ======================================

    last_quality = error_item.get(
        "last_quality"
    )


    if last_quality is not None:

        try:

            last_quality = int(
                last_quality
            )

        except (
            TypeError,
            ValueError
        ):

            last_quality = None


        if (
            last_quality is not None
            and
            (
                last_quality < 0
                or
                last_quality > 4
            )
        ):

            last_quality = None


    error_item[
        "last_quality"
    ] = last_quality


    # ======================================
    # MIGRACJA STARYCH DANYCH
    # ======================================

    error_item = migrate_legacy_error_item(
        error_item
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
    # AKTUALIZACJA WSZYSTKICH WPISÓW
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
# HISTORIA ĆWICZEŃ
# ==========================================

def add_practice_history(
    error_item,
    result,
    quality=None,
    spoken=False,
    next_review_at=None
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


    history_entry = {

        "result":
            result,

        "timestamp":
            get_current_timestamp(),

        "spoken":
            bool(
                spoken
            )
    }


    if quality is not None:

        history_entry[
            "quality"
        ] = quality


    if next_review_at:

        history_entry[
            "next_review_at"
        ] = next_review_at


    history.append(
        history_entry
    )


    # ======================================
    # HISTORIA NIE ROŚNIE BEZ KOŃCA
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
    # CZY BŁĄD WRÓCIŁ PO WCZEŚNIEJSZEJ
    # NAUCE?
    # ======================================

    was_already_learned = (

        error_item.get(
            "practice_count",
            0
        ) > 0

        or

        error_item.get(
            "correct_streak",
            0
        ) > 0

        or

        error_item.get(
            "mastered",
            False
        )
    )


    if was_already_learned:

        error_item[
            "lapses"
        ] += 1


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
    # POPRAWNA WERSJA
    # ======================================

    if correct_text:

        error_item[
            "last_correct"
        ] = str(
            correct_text
        ).strip()


    # ======================================
    # BŁĄD POJAWIŁ SIĘ PONOWNIE
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


    error_item[
        "last_result"
    ] = "wrong"


    error_item[
        "last_quality"
    ] = 0


    # ======================================
    # STARY TERMIN JUŻ NIE OBOWIĄZUJE
    # ======================================

    error_item[
        "next_review_at"
    ] = None


    # ======================================
    # BŁĄD WRÓCIŁ -> LEKKO PODNOSIMY
    # OCENĘ TRUDNOŚCI
    # ======================================

    error_item[
        "difficulty"
    ] = clamp_difficulty(

        error_item.get(
            "difficulty",
            DEFAULT_DIFFICULTY
        )
        +
        0.08
    )


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
    next_review_at=None
):

    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:

        return False


    if difficulty is not None:

        error_item[
            "difficulty"
        ] = clamp_difficulty(
            difficulty
        )


    if last_result is not None:

        error_item[
            "last_result"
        ] = str(
            last_result
        )


    if last_quality is not None:

        try:

            last_quality = int(
                last_quality
            )

        except (
            TypeError,
            ValueError
        ):

            last_quality = None


        if (
            last_quality is not None
            and
            0 <= last_quality <= 4
        ):

            error_item[
                "last_quality"
            ] = last_quality


    # ======================================
    # next_review_at może być również None
    # przy świadomym wyzerowaniu terminu.
    # ======================================

    error_item[
        "next_review_at"
    ] = next_review_at


    return True


# ==========================================
# LICZBA BŁĘDÓW
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
# LICZBA ĆWICZEŃ
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
# LICZBA POPRAWNYCH ODPOWIEDZI GŁOSOWYCH
# ==========================================

def get_spoken_successes(
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
        "spoken_successes",
        0
    )


# ==========================================
# LICZBA POWROTÓW BŁĘDU
# ==========================================

def get_error_lapses(
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
        "lapses",
        0
    )


# ==========================================
# TRUDNOŚĆ
# ==========================================

def get_error_difficulty(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:

        return DEFAULT_DIFFICULTY


    return error_item.get(
        "difficulty",
        DEFAULT_DIFFICULTY
    )


# ==========================================
# TERMIN NASTĘPNEJ POWTÓRKI
# ==========================================

def get_error_next_review_at(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if error_item is None:

        return None


    return error_item.get(
        "next_review_at"
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
#
# Parametry Adaptive Review są opcjonalne,
# więc dotychczasowe wywołanie:
#
# mark_error_practiced(
#     state,
#     error_type
# )
#
# nadal działa.
# ==========================================

def mark_error_practiced(
    state,
    error_type,
    result="correct",
    spoken=False,
    quality=None,
    next_review_at=None,
    difficulty=None
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
    # ODPOWIEDŹ GŁOSOWA
    # ======================================

    if spoken:

        error_item[
            "spoken_successes"
        ] += 1


    # ======================================
    # DATA OSTATNIEGO ĆWICZENIA
    # ======================================

    error_item[
        "last_practiced"
    ] = get_current_timestamp()


    # ======================================
    # OSTATNI WYNIK
    # ======================================

    error_item[
        "last_result"
    ] = result


    # ======================================
    # JAKOŚĆ 0–4
    # ======================================

    if quality is not None:

        try:

            quality = int(
                quality
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
    # TRUDNOŚĆ
    # ======================================

    if difficulty is not None:

        error_item[
            "difficulty"
        ] = clamp_difficulty(
            difficulty
        )


    # ======================================
    # TERMIN KOLEJNEJ POWTÓRKI
    # ======================================

    error_item[
        "next_review_at"
    ] = next_review_at


    # ======================================
    # HISTORIA
    # ======================================

    add_practice_history(
        error_item,
        result,
        quality,
        spoken,
        next_review_at
    )


    # ======================================
    # PO DOBRYM ĆWICZENIU
    # NIE POWTARZAMY NATYCHMIAST
    # ======================================

    error_item[
        "needs_practice"
    ] = False


    # ======================================
    # OPANOWANIE
    #
    # Na tym etapie zachowujemy istniejącą
    # zasadę 3 poprawnych powtórek.
    #
    # W kolejnym kroku połączymy ją
    # z Adaptive Review i odpowiedziami
    # w różne dni.
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


    for (
        error_type,
        error_item
    ) in error_memory.items():

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


    for (
        error_type,
        error_item
    ) in error_memory.items():

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


    for (
        error_type,
        error_item
    ) in error_memory.items():

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

        for (
            error_type,
            count
        ) in errors[:limit]

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
            ),


        # ==================================
        # ADAPTIVE REVIEW 2.0
        # ==================================

        "difficulty":
            error_item.get(
                "difficulty",
                DEFAULT_DIFFICULTY
            ),


        "last_result":
            error_item.get(
                "last_result"
            ),


        "last_quality":
            error_item.get(
                "last_quality"
            ),


        "next_review_at":
            error_item.get(
                "next_review_at"
            ),


        "lapses":
            error_item.get(
                "lapses",
                0
            ),


        "spoken_successes":
            error_item.get(
                "spoken_successes",
                0
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
