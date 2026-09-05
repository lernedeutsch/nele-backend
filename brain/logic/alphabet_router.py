# ==========================================
# NELE – ROUTER ALFABETU
# ==========================================

from brain.logic.alphabet import (
    handle_alphabet_question
)

from brain.logic.lesson_loader import (
    load_lesson_module
)


# ==========================================
# OBSŁUGA PYTAŃ O ALFABET
# ==========================================

def handle_alphabet(
    user_message,
    level="A1",
    lesson=1
):
    """
    Obsługuje pytania dotyczące alfabetu
    i przekazuje je do modułu alphabet.py.
    """

    alphabet_answer = handle_alphabet_question(
        user_message,
        load_lesson_module,
        level,
        lesson
    )

    if alphabet_answer:
        return alphabet_answer

    return None
