# ==========================================
# NELE – ERROR MEMORY
# STUDENT MEMORY 2.0
# ADAPTIVE REVIEW 2.0
#
# GŁÓWNA FASADA PAMIĘCI BŁĘDÓW
# ==========================================
#
# Ten plik nie przechowuje już całej logiki.
#
# Logika została podzielona na:
#
# error_memory_core.py
# -> struktura i podstawowy dostęp
#
# error_memory_migration.py
# -> migracja starszych danych
#
# error_memory_progress.py
# -> błędy, ćwiczenia i postęp
#
# error_memory_adaptive.py
# -> Adaptive Review 2.0
#
# Pozostałe moduły mogą nadal importować
# funkcje z:
#
# brain.memory.error_memory
#
# dzięki czemu nie trzeba zmieniać
# istniejącego kodu Nele.
# ==========================================


# ==========================================
# CORE
# ==========================================

from brain.memory.error_memory_core import (
    MASTERED_CORRECT_STREAK,
    MAX_PRACTICE_HISTORY,
    DEFAULT_DIFFICULTY,
    get_current_timestamp,
    clamp_difficulty,
    create_empty_error_item,
    ensure_error_item_structure,
    get_error_memory as core_get_error_memory,
    get_error_item as core_get_error_item,
    has_error,
    get_error_types
)


# ==========================================
# MIGRATION
# ==========================================

from brain.memory.error_memory_migration import (
    migrate_legacy_practiced_error,
    migrate_missing_last_result,
    migrate_error_item,
    migrate_error_memory
)


# ==========================================
# PROGRESS
# ==========================================

from brain.memory.error_memory_progress import (
    add_practice_history,
    remember_error,
    mark_error_practiced,
    mark_error_for_review,
    get_error_count,
    get_error_practice_count,
    get_error_correct_streak,
    get_spoken_successes,
    get_error_lapses,
    is_error_mastered,
    error_needs_practice,
    get_errors_for_practice,
    get_unmastered_errors,
    get_most_common_errors,
    get_error_practice_history,
    get_error_summary,
    get_all_errors
)


# ==========================================
# ADAPTIVE REVIEW
# ==========================================

from brain.memory.error_memory_adaptive import (
    get_error_difficulty,
    get_error_last_result,
    get_error_last_quality,
    get_error_next_review_at,
    set_error_difficulty,
    set_error_last_result,
    set_error_last_quality,
    set_error_next_review_at,
    update_error_adaptive_data,
    clear_error_review_schedule
)


# ==========================================
# GŁÓWNA PAMIĘĆ BŁĘDÓW
# ==========================================
#
# Zachowujemy stare zachowanie:
# przy odczycie pamięci wykonujemy również
# migrację starszych danych.
# ==========================================

def get_error_memory(
    state
):

    return migrate_error_memory(
        state
    )


# ==========================================
# POJEDYNCZY BŁĄD
# ==========================================

def get_error_item(
    error_type,
    state
):

    error_item = core_get_error_item(
        error_type,
        state
    )


    if error_item is None:

        return None


    return migrate_error_item(
        error_item
    )


# ==========================================
# NORMALIZACJA WPISU
# ==========================================
#
# Funkcja zachowana dla kompatybilności
# ze starszym kodem.
# ==========================================

def normalize_error_item(
    error_item
):

    error_item = ensure_error_item_structure(
        error_item
    )


    return migrate_error_item(
        error_item
    )


# ==========================================
# STARA NAZWA FUNKCJI MIGRACJI
# ==========================================
#
# Zachowujemy alias, aby ewentualny starszy
# kod nadal działał.
# ==========================================

def migrate_legacy_error_item(
    error_item
):

    return migrate_legacy_practiced_error(
        error_item
    )
