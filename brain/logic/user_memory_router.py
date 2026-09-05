# ==========================================
# NELE – ROUTER PAMIĘCI UŻYTKOWNIKA
# ==========================================

from brain.logic.memory_answers import (
    answer_from_memory
)

from brain.logic.user_info import (
    extract_user_information
)


# ==========================================
# OBSŁUGA PAMIĘCI I INFORMACJI O UŻYTKOWNIKU
# ==========================================

def handle_user_memory(
    user_message,
    session_id="default"
):
    """
    Obsługuje informacje związane z użytkownikiem.

    1. Najpierw sprawdza, czy użytkownik
       pyta Nele o zapamiętaną informację.

    2. Następnie sprawdza, czy użytkownik
       podaje nową informację o sobie.
    """

    # ======================================
    # PYTANIA O ZAPAMIĘTANE INFORMACJE
    # ======================================

    memory_answer = answer_from_memory(
        user_message,
        session_id
    )

    if memory_answer:
        return memory_answer


    # ======================================
    # NOWE INFORMACJE O UŻYTKOWNIKU
    # ======================================

    extracted_answer = extract_user_information(
        user_message,
        session_id
    )

    if extracted_answer:
        return extracted_answer


    # ======================================
    # BRAK DOPASOWANIA
    # ======================================

    return None
