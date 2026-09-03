# ==========================================
# NELE – PORÓWNYWANIE ZWROTÓW
# ==========================================

from brain.knowledge.A1.formality import (
    FORMALITY_LEVELS
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


    # ======================================
    # TEN SAM POZIOM
    # ======================================

    if first_level == second_level:

        return (
            f"„{first.title()}“ und "
            f"„{second.title()}“ sind "
            f"ungefähr gleich formell."
        )


    # ======================================
    # PIERWSZY JEST BARDZIEJ FORMALNY
    # ======================================

    if first_level > second_level:

        return (
            f"„{first.title()}“ ist formeller "
            f"als „{second.title()}“."
        )


    # ======================================
    # DRUGI JEST BARDZIEJ FORMALNY
    # ======================================

    return (
        f"„{second.title()}“ ist formeller "
        f"als „{first.title()}“."
    )
