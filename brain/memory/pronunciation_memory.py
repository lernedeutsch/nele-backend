# ==========================================
# NELE – PRONUNCIATION MEMORY
# STUDENT MEMORY 2.0
# ==========================================
#
# Pamięć wymowy ucznia.
#
# Ten moduł NIE analizuje jeszcze audio.
#
# Jego zadanie:
#
# - zapamiętywać wyniki wymowy
# - śledzić postęp
# - wykrywać słabsze dźwięki i słowa
# - wskazywać elementy do powtórki
#
# Przykładowe cele:
#
# sound -> "ch"
# sound -> "r"
# sound -> "ü"
#
# word -> "ich"
# word -> "lernen"
# word -> "heute"
#
# ==========================================

from datetime import datetime, timezone


# ==========================================
# USTAWIENIA
# ==========================================

MAX_PRONUNCIATION_HISTORY = 20

GOOD_SCORE = 80
MASTERED_SCORE = 88

MASTERED_CORRECT_STREAK = 3


# ==========================================
# AKTUALNY CZAS
# ==========================================

def get_current_timestamp():

    return datetime.now(
        timezone.utc
    ).isoformat()


# ==========================================
# PUSTY WPIS WYMOWY
# ==========================================

def create_empty_pronunciation_item():

    return {
        "attempts": 0,

        "correct": 0,

        "mistakes": 0,

        "correct_streak": 0,

        "best_score": None,

        "last_score": None,

        "average_score": None,

        "score_total": 0.0,

        "scored_attempts": 0,

        "needs_review": False,

        "mastered": False,

        "last_feedback": None,

        "last_practiced": None,

        "history": []
    }


# ==========================================
# PUSTA GŁÓWNA PAMIĘĆ
# ==========================================

def create_empty_pronunciation_memory():

    return {
        "sounds": {},
        "words": {}
    }


# ==========================================
# BEZPIECZNY WYNIK 0–100
# ==========================================

def normalize_pronunciation_score(
    score
):

    if score is None:
        return None


    try:

        score = float(
            score
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    score = max(
        0.0,
        min(
            100.0,
            score
        )
    )


    return round(
        score,
        2
    )


# ==========================================
# NORMALIZACJA CELU
# ==========================================

def normalize_pronunciation_target(
    target
):

    if target is None:
        return ""


    target = str(
        target
    ).strip()


    return target


# ==========================================
# NORMALIZACJA TYPU
# ==========================================

def normalize_pronunciation_target_type(
    target_type
):

    if not target_type:
        return None


    target_type = str(
        target_type
    ).strip().lower()


    if target_type in {
        "sound",
        "sounds",
        "phoneme",
        "phonemes"
    }:

        return "sounds"


    if target_type in {
        "word",
        "words"
    }:

        return "words"


    return None


# ==========================================
# UZUPEŁNIENIE STAREGO WPISU
# ==========================================

def normalize_pronunciation_item(
    item
):

    if not isinstance(
        item,
        dict
    ):

        item = {}


    defaults = (
        create_empty_pronunciation_item()
    )


    for key, value in defaults.items():

        if key in item:
            continue


        if isinstance(
            value,
            list
        ):

            item[
                key
            ] = []

        else:

            item[
                key
            ] = value


    # ======================================
    # LICZNIKI
    # ======================================

    integer_fields = (
        "attempts",
        "correct",
        "mistakes",
        "correct_streak",
        "scored_attempts"
    )


    for field in integer_fields:

        value = item.get(
            field,
            0
        )


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


        item[
            field
        ] = max(
            0,
            value
        )


    # ======================================
    # SCORE TOTAL
    # ======================================

    try:

        item[
            "score_total"
        ] = float(
            item.get(
                "score_total",
                0.0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        item[
            "score_total"
        ] = 0.0


    # ======================================
    # WYNIKI
    # ======================================

    item[
        "best_score"
    ] = normalize_pronunciation_score(
        item.get(
            "best_score"
        )
    )


    item[
        "last_score"
    ] = normalize_pronunciation_score(
        item.get(
            "last_score"
        )
    )


    item[
        "average_score"
    ] = normalize_pronunciation_score(
        item.get(
            "average_score"
        )
    )


    # ======================================
    # BOOLEAN
    # ======================================

    item[
        "needs_review"
    ] = bool(
        item.get(
            "needs_review",
            False
        )
    )


    item[
        "mastered"
    ] = bool(
        item.get(
            "mastered",
            False
        )
    )


    # ======================================
    # HISTORIA
    # ======================================

    history = item.get(
        "history"
    )


    if not isinstance(
        history,
        list
    ):

        item[
            "history"
        ] = []


    return item


# ==========================================
# GŁÓWNA PAMIĘĆ WYMOWY
# ==========================================

def get_pronunciation_memory(
    state
):

    if state is None:
        return create_empty_pronunciation_memory()


    memory = state.get(
        "pronunciation_memory"
    )


    if not isinstance(
        memory,
        dict
    ):

        memory = (
            create_empty_pronunciation_memory()
        )

        state[
            "pronunciation_memory"
        ] = memory


    if not isinstance(
        memory.get(
            "sounds"
        ),
        dict
    ):

        memory[
            "sounds"
        ] = {}


    if not isinstance(
        memory.get(
            "words"
        ),
        dict
    ):

        memory[
            "words"
        ] = {}


    # ======================================
    # NORMALIZACJA STARYCH WPISÓW
    # ======================================

    for bucket_name in (
        "sounds",
        "words"
    ):

        bucket = memory[
            bucket_name
        ]


        for target in list(
            bucket.keys()
        ):

            bucket[
                target
            ] = (
                normalize_pronunciation_item(
                    bucket[
                        target
                    ]
                )
            )


    return memory


# ==========================================
# POBRANIE JEDNEGO WPISU
# ==========================================

def get_pronunciation_item(
    state,
    target_type,
    target
):

    if state is None:
        return None


    bucket_name = (
        normalize_pronunciation_target_type(
            target_type
        )
    )


    if not bucket_name:
        return None


    target = normalize_pronunciation_target(
        target
    )


    if not target:
        return None


    memory = get_pronunciation_memory(
        state
    )


    bucket = memory[
        bucket_name
    ]


    if target not in bucket:

        bucket[
            target
        ] = (
            create_empty_pronunciation_item()
        )


    bucket[
        target
    ] = normalize_pronunciation_item(
        bucket[
            target
        ]
    )


    return bucket[
        target
    ]


# ==========================================
# HISTORIA PRÓB
# ==========================================

def add_pronunciation_history(
    item,
    score=None,
    correct=None,
    feedback=None
):

    if not item:
        return


    history = item.get(
        "history"
    )


    if not isinstance(
        history,
        list
    ):

        history = []

        item[
            "history"
        ] = history


    history.append(
        {
            "score":
                normalize_pronunciation_score(
                    score
                ),

            "correct":
                correct,

            "feedback":
                feedback,

            "timestamp":
                get_current_timestamp()
        }
    )


    if len(
        history
    ) > MAX_PRONUNCIATION_HISTORY:

        item[
            "history"
        ] = history[
            -MAX_PRONUNCIATION_HISTORY:
        ]


# ==========================================
# AKTUALIZACJA ŚREDNIEGO WYNIKU
# ==========================================

def update_average_score(
    item,
    score
):

    score = normalize_pronunciation_score(
        score
    )


    if score is None:
        return


    item[
        "score_total"
    ] += score


    item[
        "scored_attempts"
    ] += 1


    scored_attempts = item.get(
        "scored_attempts",
        0
    )


    if scored_attempts <= 0:
        return


    average = (
        item[
            "score_total"
        ]
        /
        scored_attempts
    )


    item[
        "average_score"
    ] = round(
        average,
        2
    )


# ==========================================
# CZY PRÓBA JEST POPRAWNA
# ==========================================

def resolve_pronunciation_correct(
    score=None,
    correct=None
):

    if correct is not None:

        return bool(
            correct
        )


    score = normalize_pronunciation_score(
        score
    )


    if score is None:
        return None


    return score >= GOOD_SCORE


# ==========================================
# ZAPIS PRÓBY WYMOWY
# ==========================================

def remember_pronunciation_attempt(
    state,
    target_type,
    target,
    score=None,
    correct=None,
    feedback=None
):

    item = get_pronunciation_item(
        state,
        target_type,
        target
    )


    if item is None:
        return False


    score = normalize_pronunciation_score(
        score
    )


    correct = resolve_pronunciation_correct(
        score,
        correct
    )


    # ======================================
    # LICZBA PRÓB
    # ======================================

    item[
        "attempts"
    ] += 1


    # ======================================
    # SCORE
    # ======================================

    if score is not None:

        item[
            "last_score"
        ] = score


        best_score = item.get(
            "best_score"
        )


        if (
            best_score is None
            or
            score > best_score
        ):

            item[
                "best_score"
            ] = score


        update_average_score(
            item,
            score
        )


    # ======================================
    # FEEDBACK
    # ======================================

    if feedback:

        item[
            "last_feedback"
        ] = str(
            feedback
        ).strip()


    # ======================================
    # POPRAWNIE
    # ======================================

    if correct is True:

        item[
            "correct"
        ] += 1


        item[
            "correct_streak"
        ] += 1


        item[
            "needs_review"
        ] = False


    # ======================================
    # BŁĘDNIE
    # ======================================

    elif correct is False:

        item[
            "mistakes"
        ] += 1


        item[
            "correct_streak"
        ] = 0


        item[
            "needs_review"
        ] = True


        item[
            "mastered"
        ] = False


    # ======================================
    # DATA
    # ======================================

    item[
        "last_practiced"
    ] = get_current_timestamp()


    # ======================================
    # CZY OPANOWANE
    # ======================================

    average_score = item.get(
        "average_score"
    )


    if (
        item.get(
            "correct_streak",
            0
        )
        >= MASTERED_CORRECT_STREAK

        and

        average_score is not None

        and

        average_score >= MASTERED_SCORE
    ):

        item[
            "mastered"
        ] = True

        item[
            "needs_review"
        ] = False


    # ======================================
    # HISTORIA
    # ======================================

    add_pronunciation_history(
        item,
        score=score,
        correct=correct,
        feedback=feedback
    )


    return True


# ==========================================
# ZAPIS PRÓBY DŹWIĘKU
# ==========================================

def remember_sound_pronunciation(
    state,
    sound,
    score=None,
    correct=None,
    feedback=None
):

    return remember_pronunciation_attempt(
        state,
        "sound",
        sound,
        score,
        correct,
        feedback
    )


# ==========================================
# ZAPIS PRÓBY SŁOWA
# ==========================================

def remember_word_pronunciation(
    state,
    word,
    score=None,
    correct=None,
    feedback=None
):

    return remember_pronunciation_attempt(
        state,
        "word",
        word,
        score,
        correct,
        feedback
    )


# ==========================================
# PODSUMOWANIE
# ==========================================

def get_pronunciation_summary(
    state,
    target_type,
    target
):

    item = get_pronunciation_item(
        state,
        target_type,
        target
    )


    if item is None:
        return None


    return {
        "target_type":
            normalize_pronunciation_target_type(
                target_type
            ),

        "target":
            normalize_pronunciation_target(
                target
            ),

        "attempts":
            item.get(
                "attempts",
                0
            ),

        "correct":
            item.get(
                "correct",
                0
            ),

        "mistakes":
            item.get(
                "mistakes",
                0
            ),

        "correct_streak":
            item.get(
                "correct_streak",
                0
            ),

        "best_score":
            item.get(
                "best_score"
            ),

        "last_score":
            item.get(
                "last_score"
            ),

        "average_score":
            item.get(
                "average_score"
            ),

        "needs_review":
            item.get(
                "needs_review",
                False
            ),

        "mastered":
            item.get(
                "mastered",
                False
            ),

        "last_feedback":
            item.get(
                "last_feedback"
            ),

        "last_practiced":
            item.get(
                "last_practiced"
            )
    }


# ==========================================
# ELEMENTY DO POWTÓRKI
# ==========================================

def get_pronunciation_items_for_review(
    state,
    target_type=None
):

    memory = get_pronunciation_memory(
        state
    )


    result = []


    if target_type:

        bucket_name = (
            normalize_pronunciation_target_type(
                target_type
            )
        )


        if not bucket_name:
            return []


        bucket_names = [
            bucket_name
        ]

    else:

        bucket_names = [
            "sounds",
            "words"
        ]


    for bucket_name in bucket_names:

        bucket = memory.get(
            bucket_name,
            {}
        )


        for target, item in bucket.items():

            if not isinstance(
                item,
                dict
            ):

                continue


            if item.get(
                "needs_review",
                False
            ):

                result.append(
                    {
                        "target_type":
                            bucket_name,

                        "target":
                            target,

                        "average_score":
                            item.get(
                                "average_score"
                            ),

                        "mistakes":
                            item.get(
                                "mistakes",
                                0
                            ),

                        "last_feedback":
                            item.get(
                                "last_feedback"
                            )
                    }
                )


    # ======================================
    # NAJPIERW NAJSŁABSZE
    # ======================================

    result.sort(
        key=lambda item: (
            item.get(
                "average_score"
            )
            if item.get(
                "average_score"
            )
            is not None
            else 0
        )
    )


    return result


# ==========================================
# NAJSŁABSZE ELEMENTY
# ==========================================

def get_weakest_pronunciation_items(
    state,
    limit=5
):

    memory = get_pronunciation_memory(
        state
    )


    result = []


    for bucket_name in (
        "sounds",
        "words"
    ):

        bucket = memory.get(
            bucket_name,
            {}
        )


        for target, item in bucket.items():

            if not isinstance(
                item,
                dict
            ):

                continue


            attempts = item.get(
                "attempts",
                0
            )


            if attempts <= 0:
                continue


            result.append(
                {
                    "target_type":
                        bucket_name,

                    "target":
                        target,

                    "average_score":
                        item.get(
                            "average_score"
                        ),

                    "mistakes":
                        item.get(
                            "mistakes",
                            0
                        ),

                    "mastered":
                        item.get(
                            "mastered",
                            False
                        ),

                    "needs_review":
                        item.get(
                            "needs_review",
                            False
                        )
                }
            )


    # ======================================
    # NAJSŁABSZY ŚREDNI SCORE NA POCZĄTKU
    # ======================================

    result.sort(
        key=lambda item: (
            item.get(
                "average_score"
            )
            if item.get(
                "average_score"
            )
            is not None
            else 0
        )
    )


    return result[
        :limit
  ]
