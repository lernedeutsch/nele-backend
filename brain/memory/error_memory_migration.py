# ==========================================
# NELE – ERROR MEMORY MIGRATION
# STUDENT MEMORY 2.0
# ADAPTIVE REVIEW 2.0
# ==========================================

from brain.memory.error_memory_core import (
    get_current_timestamp,
    ensure_error_item_structure,
    get_error_memory
)


# ==========================================
# MIGRACJA STAREGO PRZEĆWICZONEGO BŁĘDU
# ==========================================
#
# Starszy system potrafił:
#
# - zapisać błąd
# - oznaczyć go jako przećwiczony
#
# ale nie posiadał jeszcze:
#
# - practice_count
# - correct_streak
# - last_practiced
# - practice_history
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
# uznajemy, że błąd został wcześniej
# poprawnie przećwiczony jeden raz.
# ==========================================

def migrate_legacy_practiced_error(
    error_item
):

    if not isinstance(
        error_item,
        dict
    ):

        return error_item


    error_item = ensure_error_item_structure(
        error_item
    )


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
# UZUPEŁNIENIE STAREGO WYNIKU
# ==========================================
#
# Jeżeli istnieje już stary poprawny trening,
# ale last_result nie został zapisany,
# możemy bezpiecznie ustawić "correct".
# ==========================================

def migrate_missing_last_result(
    error_item
):

    if not isinstance(
        error_item,
        dict
    ):

        return error_item


    error_item = ensure_error_item_structure(
        error_item
    )


    if error_item.get(
        "last_result"
    ):

        return error_item


    if (
        error_item.get(
            "practice_count",
            0
        ) > 0
        and
        error_item.get(
            "correct_streak",
            0
        ) > 0
    ):

        error_item[
            "last_result"
        ] = "correct"


    return error_item


# ==========================================
# MIGRACJA JEDNEGO WPISU
# ==========================================

def migrate_error_item(
    error_item
):

    error_item = ensure_error_item_structure(
        error_item
    )


    error_item = migrate_legacy_practiced_error(
        error_item
    )


    error_item = migrate_missing_last_result(
        error_item
    )


    return error_item


# ==========================================
# MIGRACJA CAŁEJ PAMIĘCI BŁĘDÓW
# ==========================================

def migrate_error_memory(
    state
):

    if state is None:

        return {}


    error_memory = get_error_memory(
        state
    )


    for error_type in list(
        error_memory.keys()
    ):

        error_memory[
            error_type
        ] = migrate_error_item(
            error_memory[
                error_type
            ]
        )


    return error_memory
