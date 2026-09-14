# ==========================================
# NELE – PAMIĘĆ SŁOWNICTWA UCZNIA
# STUDENT MEMORY 2.0
# SPACED REPETITION
# ==========================================

from datetime import (
    datetime,
    timezone,
    timedelta
)


# ==========================================
# ODSTĘPY POWTÓREK
#
# po 1 poprawnej odpowiedzi -> 1 dzień
# po 2 poprawnych          -> 3 dni
# po 3 poprawnych          -> 7 dni
# kolejne                  -> 14 dni
# ==========================================

VOCABULARY_REVIEW_INTERVALS = {
    1: 24,
    2: 72,
    3: 168
}


# ==========================================
# AKTUALNY CZAS UTC
# ==========================================

def get_vocabulary_now():

    return datetime.now(
        timezone.utc
    )


# ==========================================
# ODCZYT DATY ISO
# ==========================================

def parse_vocabulary_timestamp(
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


    if parsed.tzinfo is None:

        parsed = parsed.replace(
            tzinfo=timezone.utc
        )


    return parsed.astimezone(
        timezone.utc
    )


# ==========================================
# TERMIN NASTĘPNEJ POWTÓRKI
# ==========================================

def calculate_vocabulary_next_review(
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

        correct_streak = 1


    correct_streak = max(
        1,
        correct_streak
    )


    interval_hours = (
        VOCABULARY_REVIEW_INTERVALS.get(
            correct_streak,
            336
        )
    )


    return (
        get_vocabulary_now()
        +
        timedelta(
            hours=interval_hours
        )
    ).isoformat()


# ==========================================
# POBIERANIE PAMIĘCI SŁOWNICTWA
# ==========================================

def get_vocabulary_memory(
    state
):

    if state is None:
        return {}


    if (
        "vocabulary_memory"
        not in state
        or
        not isinstance(
            state.get(
                "vocabulary_memory"
            ),
            dict
        )
    ):

        state[
            "vocabulary_memory"
        ] = {}


    return state[
        "vocabulary_memory"
    ]


# ==========================================
# POBIERANIE PAMIĘCI JEDNEGO SŁOWA
# ==========================================

def get_word_memory(
    word,
    state
):

    if not word or state is None:
        return None


    word = str(
        word
    ).strip().lower()


    if not word:
        return None


    vocabulary_memory = (
        get_vocabulary_memory(
            state
        )
    )


    if word not in vocabulary_memory:

        vocabulary_memory[
            word
        ] = {

            "seen":
                0,

            "correct":
                0,

            "mistakes":
                0,

            "correct_streak":
                0,

            "needs_review":
                False,

            "last_practiced":
                None,

            "next_review_at":
                None
        }


    word_memory = vocabulary_memory[
        word
    ]


    # ======================================
    # MIGRACJA STARSZEJ PAMIĘCI
    # ======================================

    if "seen" not in word_memory:

        word_memory[
            "seen"
        ] = 0


    if "correct" not in word_memory:

        word_memory[
            "correct"
        ] = 0


    if "mistakes" not in word_memory:

        word_memory[
            "mistakes"
        ] = 0


    if "correct_streak" not in word_memory:

        word_memory[
            "correct_streak"
        ] = 0


    if "needs_review" not in word_memory:

        word_memory[
            "needs_review"
        ] = False


    if "last_practiced" not in word_memory:

        word_memory[
            "last_practiced"
        ] = None


    if "next_review_at" not in word_memory:

        word_memory[
            "next_review_at"
        ] = None


    return word_memory


# ==========================================
# ZAPISANIE ĆWICZONEGO SŁOWA
# ==========================================

def remember_practiced_word(
    word,
    state
):

    word_memory = get_word_memory(
        word,
        state
    )


    if word_memory is None:
        return


    word_memory[
        "seen"
    ] += 1


    word_memory[
        "last_practiced"
    ] = (
        get_vocabulary_now().isoformat()
    )


# ==========================================
# ZAPISANIE POPRAWNEJ ODPOWIEDZI
# ==========================================

def remember_correct_answer(
    word,
    state
):

    word_memory = get_word_memory(
        word,
        state
    )


    if word_memory is None:
        return


    word_memory[
        "correct"
    ] += 1


    word_memory[
        "correct_streak"
    ] += 1


    word_memory[
        "last_practiced"
    ] = (
        get_vocabulary_now().isoformat()
    )


    # ======================================
    # NAJWAŻNIEJSZA ZMIANA
    #
    # Po poprawnej odpowiedzi słowo
    # NIE może wrócić natychmiast.
    # ======================================

    word_memory[
        "needs_review"
    ] = False


    # ======================================
    # PLANUJEMY KOLEJNĄ POWTÓRKĘ
    # ======================================

    word_memory[
        "next_review_at"
    ] = (
        calculate_vocabulary_next_review(
            word_memory[
                "correct_streak"
            ]
        )
    )


# ==========================================
# ZAPISANIE BŁĘDU
# ==========================================

def remember_mistake(
    word,
    state
):

    word_memory = get_word_memory(
        word,
        state
    )


    if word_memory is None:
        return


    word_memory[
        "mistakes"
    ] += 1


    word_memory[
        "correct_streak"
    ] = 0


    # ======================================
    # BŁĄD OZNACZA:
    # TRZEBA ĆWICZYĆ TERAZ
    # ======================================

    word_memory[
        "needs_review"
    ] = True


    # ======================================
    # POPRZEDNI TERMIN PRZESTAJE
    # MIEĆ ZNACZENIE
    # ======================================

    word_memory[
        "next_review_at"
    ] = None


    word_memory[
        "last_practiced"
    ] = (
        get_vocabulary_now().isoformat()
    )


# ==========================================
# CZY ZAPLANOWANA POWTÓRKA
# JUŻ NADSZEDŁA
# ==========================================

def is_vocabulary_review_due(
    word_memory,
    now=None
):

    if not isinstance(
        word_memory,
        dict
    ):

        return False


    # ======================================
    # AKTYWNIE WYMAGA POWTÓRKI
    # ======================================

    if word_memory.get(
        "needs_review",
        False
    ):

        return True


    # ======================================
    # TERMIN SPACED REPETITION
    # ======================================

    next_review_at = (
        parse_vocabulary_timestamp(
            word_memory.get(
                "next_review_at"
            )
        )
    )


    if next_review_at is None:
        return False


    if now is None:

        now = get_vocabulary_now()


    if now.tzinfo is None:

        now = now.replace(
            tzinfo=timezone.utc
        )


    now = now.astimezone(
        timezone.utc
    )


    return now >= next_review_at


# ==========================================
# CZY SŁOWO WYMAGA POWTÓRKI
# ==========================================

def word_needs_review(
    word,
    state
):

    word_memory = get_word_memory(
        word,
        state
    )


    if word_memory is None:
        return False


    return is_vocabulary_review_due(
        word_memory
    )


# ==========================================
# SŁOWA DO POWTÓRKI
# ==========================================

def get_words_for_review(
    state
):

    vocabulary_memory = (
        get_vocabulary_memory(
            state
        )
    )


    words = []

    now = get_vocabulary_now()


    for (
        word,
        word_memory
    ) in vocabulary_memory.items():

        if is_vocabulary_review_due(
            word_memory,
            now
        ):

            words.append(
                word
            )


    return words
