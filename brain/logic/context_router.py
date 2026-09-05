# ==========================================
# NELE – ROUTER KONTEKSTU
# ==========================================

from brain.logic.context import (
    handle_context_answer
)


# ==========================================
# GŁÓWNA OBSŁUGA KONTEKSTU
# ==========================================

def handle_context(
    user_message,
    session_id="default"
):
    """
    Obsługuje odpowiedzi zależne
    od wcześniejszego kontekstu rozmowy.
    """

    context_answer = handle_context_answer(
        user_message,
        session_id
    )

    if context_answer:
        return context_answer

    return None
