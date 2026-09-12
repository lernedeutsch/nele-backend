# ==========================================
# NELE – ERROR MEMORY CORE
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

        "difficulty":
            DEFAULT_DIFFICULTY,

        "last_result":
            None,

        "last_quality":
            None,

        "next_review_at":
            None,

        "lapses":
            0,

        "spoken_successes":
            0
    }


# ==========================================
# UZUPEŁNIENIE BRAKUJĄCYCH PÓL
# ==========================================

def ensure_error_item_structure(
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

        value = error_item.get(
            field
        )


        if isinstance(
            value,
            bool
        ):

            value = 0


        if not isinstance(
            value,
            int
        ):

            try:

                value = int(
                    value
                )

            except (
                TypeError,
                ValueError
            ):

                value = 0


        error_item[
            field
        ] = max(
            0,
            value
        )


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
    # JAKOŚĆ ODPOWIEDZI 0–4
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
            not (
                0
                <= last_quality
                <= 4
            )
        ):

            last_quality = None


    error_item[
        "last_quality"
    ] = last_quality


    return error_item


# ==========================================
# GŁÓWNY SŁOWNIK ERROR MEMORY
# ==========================================

def get_error_memory(
    state
):

    if state is None:

        return {}


    error_memory = state.get(
        "error_memory"
    )


    if not isinstance(
        error_memory,
        dict
    ):

        error_memory = {}

        state[
            "error_memory"
        ] = error_memory


    # ======================================
    # UZUPEŁNIAMY STRUKTURĘ ISTNIEJĄCYCH
    # WPISÓW
    # ======================================

    for error_type in list(
        error_memory.keys()
    ):

        error_memory[
            error_type
        ] = ensure_error_item_structure(
            error_memory[
                error_type
            ]
        )


    return error_memory


# ==========================================
# POJEDYNCZY TYP BŁĘDU
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
    ] = ensure_error_item_structure(
        error_memory[
            error_type
        ]
    )


    return error_memory[
        error_type
    ]


# ==========================================
# CZY ISTNIEJE ZAPISANY BŁĄD
# ==========================================

def has_error(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )


    if not error_item:

        return False


    return (
        error_item.get(
            "count",
            0
        )
        > 0
    )


# ==========================================
# WSZYSTKIE TYPY BŁĘDÓW
# ==========================================

def get_error_types(
    state
):

    error_memory = get_error_memory(
        state
    )


    return list(
        error_memory.keys()
  )
