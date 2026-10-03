# ==========================================
# NELE – ERROR MEMORY PROGRESS
# STUDENT MEMORY 2.0
# ==========================================

from brain.memory.error_memory_core import (
    MASTERED_CORRECT_STREAK,
    MAX_PRACTICE_HISTORY,
    DEFAULT_DIFFICULTY,
    get_current_timestamp,
    clamp_difficulty,
    get_error_item
)

from brain.memory.error_memory_migration import (
    migrate_error_item,
    migrate_error_memory
)


# ==========================================
# POBRANIE WPISU Z MIGRACJĄ
# ==========================================

def get_progress_error_item(
    state,
    error_type
):

    error_item = get_error_item(
        error_type,
        state
    )

    if error_item is None:
        return None

    error_item = migrate_error_item(
        error_item
    )

    return error_item


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


    entry = {
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

        entry[
            "quality"
        ] = quality


    if next_review_at:

        entry[
            "next_review_at"
        ] = next_review_at


    history.append(
        entry
    )


    if len(
        history
    ) > MAX_PRACTICE_HISTORY:

        error_item[
            "practice_history"
        ] = history[
            -MAX_PRACTICE_HISTORY:
        ]


# ==========================================
# KONKRETNE PRZYKŁADY BŁĘDÓW
# ==========================================

def _normalize_example_text(
    value
):

    return " ".join(
        str(
            value or ""
        )
        .strip()
        .lower()
        .split()
    )


def _ensure_error_examples(
    error_item
):

    examples = error_item.get(
        "examples"
    )

    if not isinstance(
        examples,
        list
    ):

        examples = []

        error_item[
            "examples"
        ] = examples


    clean_examples = []


    for example in examples:

        if not isinstance(
            example,
            dict
        ):

            continue


        wrong = str(
            example.get(
                "wrong"
            )
            or
            ""
        ).strip()

        correct = str(
            example.get(
                "correct"
            )
            or
            ""
        ).strip()


        if not wrong or not correct:
            continue


        example.setdefault(
            "count",
            1
        )

        example.setdefault(
            "practice_count",
            0
        )

        example.setdefault(
            "correct_streak",
            0
        )

        example.setdefault(
            "mastered",
            False
        )

        example.setdefault(
            "needs_practice",
            True
        )

        example.setdefault(
            "last_seen",
            None
        )

        example.setdefault(
            "last_practiced",
            None
        )

        example.setdefault(
            "context",
            None
        )

        example.setdefault(
            "ignored",
            False
        )

        clean_examples.append(
            example
        )


    error_item[
        "examples"
    ] = clean_examples


    return clean_examples


def _find_error_example(
    error_item,
    wrong_text,
    correct_text
):

    wrong_key = _normalize_example_text(
        wrong_text
    )

    correct_key = _normalize_example_text(
        correct_text
    )


    for index, example in enumerate(
        _ensure_error_examples(
            error_item
        )
    ):

        if (
            _normalize_example_text(
                example.get(
                    "wrong"
                )
            )
            == wrong_key
            and
            _normalize_example_text(
                example.get(
                    "correct"
                )
            )
            == correct_key
        ):

            return index, example


    return None, None


def _backfill_examples_from_daily_memory(
    state,
    error_type,
    error_item
):

    daily = state.get(
        "daily_learning"
    )


    if not isinstance(
        daily,
        dict
    ):

        return


    mistakes = daily.get(
        "mistakes",
        []
    )


    if not isinstance(
        mistakes,
        list
    ):

        return


    normalized_type = str(
        error_type or ""
    ).strip().lower()


    for item in mistakes:

        if not isinstance(
            item,
            dict
        ):

            continue


        if (
            str(
                item.get(
                    "type"
                )
                or
                ""
            ).strip().lower()
            != normalized_type
        ):

            continue


        wrong = str(
            item.get(
                "wrong"
            )
            or
            ""
        ).strip()

        correct = str(
            item.get(
                "correct"
            )
            or
            ""
        ).strip()


        if not wrong or not correct:
            continue


        index, example = _find_error_example(
            error_item,
            wrong,
            correct
        )


        if example is None:

            error_item[
                "examples"
            ].append(
                {
                    "wrong":
                        wrong,

                    "correct":
                        correct,

                    "count":
                        1,

                    "practice_count":
                        0,

                    "correct_streak":
                        0,

                    "mastered":
                        False,

                    "needs_practice":
                        True,

                    "last_seen":
                        item.get(
                            "at"
                        ),

                    "last_practiced":
                        None
                }
            )


def get_error_examples(
    state,
    error_type
):

    error_item = get_progress_error_item(
        state,
        error_type
    )


    if error_item is None:
        return []


    # Ważne:
    # konkretne błędy zapisuje bezpośrednio
    # remember_error(). Nie tworzymy nowych
    # przykładów z daily_learning, ponieważ
    # daily_learning zawiera także nieudane
    # próby podczas samego Fehlertraining.
    #
    # Gdyby je kopiować z powrotem do
    # Error Memory, odpowiedź typu "weißt du"
    # podczas powtórki "Wie heißt du?"
    # stawałaby się nowym osobnym błędem.
    # To powodowałoby sztuczne duplikaty.
    return list(
        _ensure_error_examples(
            error_item
        )
    )


def get_next_error_example(
    state,
    error_type
):

    examples = get_error_examples(
        state,
        error_type
    )


    if not examples:
        return None


    candidates = [
        example
        for example in examples
        if (
            example.get(
                "needs_practice",
                False
            )
            and
            not example.get(
                "mastered",
                False
            )
            and
            not example.get(
                "ignored",
                False
            )
        )
    ]


    if not candidates:

        candidates = [
            example
            for example in examples
            if (
                not example.get(
                    "mastered",
                    False
                )
                and
                not example.get(
                    "ignored",
                    False
                )
            )
        ]


    if not candidates:
        return None


    candidates.sort(
        key=lambda example: (
            int(
                example.get(
                    "count",
                    0
                )
                or
                0
            ),
            -int(
                example.get(
                    "practice_count",
                    0
                )
                or
                0
            )
        ),
        reverse=True
    )


    return candidates[0]


def mark_error_example_practiced(
    state,
    error_type,
    wrong_text,
    correct_text,
    result="correct"
):

    error_item = get_progress_error_item(
        state,
        error_type
    )


    if error_item is None:
        return False


    index, example = _find_error_example(
        error_item,
        wrong_text,
        correct_text
    )


    if example is None:
        return False


    example[
        "practice_count"
    ] = int(
        example.get(
            "practice_count",
            0
        )
        or
        0
    ) + 1


    if result == "correct":

        example[
            "correct_streak"
        ] = int(
            example.get(
                "correct_streak",
                0
            )
            or
            0
        ) + 1

        example[
            "needs_practice"
        ] = False

        example[
            "mastered"
        ] = (
            example[
                "correct_streak"
            ]
            >= 2
        )

    else:

        example[
            "correct_streak"
        ] = 0

        example[
            "needs_practice"
        ] = True

        example[
            "mastered"
        ] = False


    example[
        "last_practiced"
    ] = get_current_timestamp()


    error_item[
        "examples"
    ][
        index
    ] = example


    pending_examples = [
        item
        for item in _ensure_error_examples(
            error_item
        )
        if (
            item.get(
                "needs_practice",
                False
            )
            and
            not item.get(
                "mastered",
                False
            )
        )
    ]


    if pending_examples:

        error_item[
            "needs_practice"
        ] = True

        error_item[
            "mastered"
        ] = False

    else:

        # Po poprawnym przećwiczeniu ostatniego
        # oczekującego przykładu kategoria nie może
        # pozostać aktywna tylko dlatego, że istnieją
        # inne przykłady odłożone do późniejszej powtórki.
        error_item[
            "needs_practice"
        ] = False


    return True


# ==========================================
# ZAPISANIE BŁĘDU
# ==========================================

def remember_error(
    state,
    error_type,
    wrong_text,
    correct_text,
    context=None,
    accepted_values=None
):

    if state is None:
        return False

    if not error_type:
        return False


    error_item = get_progress_error_item(
        state,
        error_type
    )


    if error_item is None:
        return False


    # ======================================
    # CZY BŁĄD WRÓCIŁ
    # PO WCZEŚNIEJSZEJ NAUCE?
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
    # LICZNIK BŁĘDÓW
    # ======================================

    error_item[
        "count"
    ] += 1


    # ======================================
    # OSTATNIE ZDANIA
    # ======================================

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


    # ======================================
    # KONKRETNY PRZYKŁAD BŁĘDU
    # ======================================

    wrong_value = str(
        wrong_text or ""
    ).strip()

    correct_value = str(
        correct_text or ""
    ).strip()

    context_value = str(
        context or ""
    ).strip()

    accepted_list = []
    for value in (accepted_values or []):
        clean_value = str(value or "").strip()
        if clean_value and clean_value not in accepted_list:
            accepted_list.append(clean_value)


    if wrong_value and correct_value:

        index, example = _find_error_example(
            error_item,
            wrong_value,
            correct_value
        )


        if example is None:

            example = {
                "wrong":
                    wrong_value,

                "correct":
                    correct_value,

                "count":
                    1,

                "practice_count":
                    0,

                "correct_streak":
                    0,

                "mastered":
                    False,

                "needs_practice":
                    True,

                "last_seen":
                    get_current_timestamp(),

                "last_practiced":
                    None,

                "context":
                    context_value or None,

                "accepted":
                    accepted_list
            }

            error_item[
                "examples"
            ].append(
                example
            )

        else:

            example[
                "count"
            ] = int(
                example.get(
                    "count",
                    0
                )
                or
                0
            ) + 1

            example[
                "correct_streak"
            ] = 0

            example[
                "mastered"
            ] = False

            example[
                "needs_practice"
            ] = True

            example[
                "last_seen"
            ] = get_current_timestamp()

            example[
                "ignored"
            ] = False

            if context_value:

                example[
                    "context"
                ] = context_value

            if accepted_list:

                example[
                    "accepted"
                ] = accepted_list

            error_item[
                "examples"
            ][
                index
            ] = example


    # ======================================
    # BŁĄD WRÓCIŁ
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

    error_item[
        "next_review_at"
    ] = None


    # ======================================
    # BŁĄD WRACAJĄCY JEST TROCHĘ
    # TRUDNIEJSZY DLA UCZNIA
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
# POPRAWNIE PRZEĆWICZONY BŁĄD
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

    error_item = get_progress_error_item(
        state,
        error_type
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
    # POPRAWNA SERIA
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
    # DATA
    # ======================================

    error_item[
        "last_practiced"
    ] = get_current_timestamp()


    # ======================================
    # WYNIK
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
    # TERMIN NASTĘPNEJ POWTÓRKI
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
    # NIE POWTARZAMY NATYCHMIAST
    # ======================================

    error_item[
        "needs_practice"
    ] = False


    # ======================================
    # OPANOWANIE
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
# PONOWNE DODANIE DO POWTÓRKI
# ==========================================

def mark_error_for_review(
    state,
    error_type
):

    error_item = get_progress_error_item(
        state,
        error_type
    )


    if error_item is None:
        return False


    if error_item.get(
        "mastered",
        False
    ):

        return False


    # Adaptive Review działa na kategorii błędu,
    # ale ćwiczymy zawsze konkretny przykład.
    # Kiedy nadejdzie termin powtórki, oznaczamy
    # jeden sensowny, nieopanowany przykład jako
    # oczekujący. Dzięki temu stan kategorii i
    # stan examples[] nie rozjeżdżają się.
    candidates = [
        example
        for example in _ensure_error_examples(
            error_item
        )
        if (
            not example.get(
                "mastered",
                False
            )
            and
            not example.get(
                "ignored",
                False
            )
        )
    ]


    if not candidates:

        error_item[
            "needs_practice"
        ] = False

        return False


    candidates.sort(
        key=lambda example: (
            int(
                example.get(
                    "practice_count",
                    0
                )
                or
                0
            ),
            -int(
                example.get(
                    "count",
                    0
                )
                or
                0
            )
        )
    )


    candidates[0][
        "needs_practice"
    ] = True

    error_item[
        "needs_practice"
    ] = True


    return True


# ==========================================
# LICZBA BŁĘDÓW
# ==========================================

def get_error_count(
    state,
    error_type
):

    error_item = get_progress_error_item(
        state,
        error_type
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

    error_item = get_progress_error_item(
        state,
        error_type
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

    error_item = get_progress_error_item(
        state,
        error_type
    )


    if error_item is None:
        return 0


    return error_item.get(
        "correct_streak",
        0
    )


# ==========================================
# POPRAWNE ODPOWIEDZI GŁOSOWE
# ==========================================

def get_spoken_successes(
    state,
    error_type
):

    error_item = get_progress_error_item(
        state,
        error_type
    )


    if error_item is None:
        return 0


    return error_item.get(
        "spoken_successes",
        0
    )


# ==========================================
# POWROTY BŁĘDU
# ==========================================

def get_error_lapses(
    state,
    error_type
):

    error_item = get_progress_error_item(
        state,
        error_type
    )


    if error_item is None:
        return 0


    return error_item.get(
        "lapses",
        0
    )


# ==========================================
# CZY OPANOWANE
# ==========================================

def is_error_mastered(
    state,
    error_type
):

    error_item = get_progress_error_item(
        state,
        error_type
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
# CZY WYMAGA ĆWICZENIA
# ==========================================

def error_needs_practice(
    state,
    error_type
):

    error_item = get_progress_error_item(
        state,
        error_type
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
# BŁĘDY DO ĆWICZENIA
# ==========================================

def get_errors_for_practice(
    state
):

    error_memory = migrate_error_memory(
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

    error_memory = migrate_error_memory(
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

    error_memory = migrate_error_memory(
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

    error_item = get_progress_error_item(
        state,
        error_type
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
# PODSUMOWANIE BŁĘDU
# ==========================================

def get_error_summary(
    state,
    error_type
):

    error_item = get_progress_error_item(
        state,
        error_type
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

        "examples":
            list(
                _ensure_error_examples(
                    error_item
                )
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
# WSZYSTKIE BŁĘDY
# ==========================================

def get_all_errors(
    state
):

    error_memory = migrate_error_memory(
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
