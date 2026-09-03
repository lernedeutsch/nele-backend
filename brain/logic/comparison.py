# ==========================================
# NELE – PORÓWNYWANIE ZWROTÓW
# ==========================================

from brain.knowledge.A1.formality import (
    FORMALITY_LEVELS
)


# ==========================================
# POMOCNICZA NAZWA ZWROTU
# ==========================================

def display_expression(
    expression
):

    special_names = {
        "hallo": "Hallo",
        "hi": "Hi",
        "guten morgen": "Guten Morgen",
        "guten tag": "Guten Tag",
        "guten abend": "Guten Abend",
        "tschüss": "Tschüss",
        "auf wiedersehen": "Auf Wiedersehen",
        "du": "du",
        "sie": "Sie",
        "wie heißt du": "Wie heißt du?",
        "wie heißen sie": "Wie heißen Sie?"
    }

    return special_names.get(
        expression,
        expression
    )


# ==========================================
# PORÓWNANIE FORMALNOŚCI
# ==========================================

def compare_formality(
    first,
    second
):

    first_level = FORMALITY_LEVELS.get(
        first
    )

    second_level = FORMALITY_LEVELS.get(
        second
    )

    if first_level is None:
        return None

    if second_level is None:
        return None

    first_name = display_expression(
        first
    )

    second_name = display_expression(
        second
    )


    # ======================================
    # TEN SAM POZIOM
    # ======================================

    if first_level == second_level:

        return (
            f"„{first_name}“ und "
            f"„{second_name}“ sind "
            f"ungefähr gleich formell."
        )


    # ======================================
    # PIERWSZY JEST BARDZIEJ FORMALNY
    # ======================================

    if first_level > second_level:

        return (
            f"„{first_name}“ ist formeller "
            f"als „{second_name}“."
        )


    # ======================================
    # DRUGI JEST BARDZIEJ FORMALNY
    # ======================================

    return (
        f"„{second_name}“ ist formeller "
        f"als „{first_name}“."
    )


# ==========================================
# PORÓWNANIE NIEFORMALNOŚCI
# ==========================================

def compare_informality(
    first,
    second
):

    first_level = FORMALITY_LEVELS.get(
        first
    )

    second_level = FORMALITY_LEVELS.get(
        second
    )

    if first_level is None:
        return None

    if second_level is None:
        return None

    first_name = display_expression(
        first
    )

    second_name = display_expression(
        second
    )


    # ======================================
    # TEN SAM POZIOM
    # ======================================

    if first_level == second_level:

        return (
            f"„{first_name}“ und "
            f"„{second_name}“ sind "
            f"ungefähr gleich informell."
        )


    # ======================================
    # PIERWSZY JEST MNIEJ FORMALNY
    # ======================================

    if first_level < second_level:

        return (
            f"„{first_name}“ ist informeller "
            f"als „{second_name}“."
        )


    # ======================================
    # DRUGI JEST MNIEJ FORMALNY
    # ======================================

    return (
        f"„{second_name}“ ist informeller "
        f"als „{first_name}“."
    )
