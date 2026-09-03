# ==========================================
# NELE – PAMIĘĆ ROZMOWY
# ==========================================

conversation_sessions = {}


def create_empty_state():
    """
    Tworzy pustą pamięć dla nowego użytkownika.
    """

    return {
        "last_question": None,
        "name": None,
        "origin": None,
        "residence": None
    }


def get_conversation_state(
    session_id="default"
):
    """
    Pobiera pamięć konkretnego użytkownika.

    Jeżeli użytkownik jeszcze nie istnieje,
    tworzy dla niego nową pamięć.
    """

    if not session_id:
        session_id = "default"

    if session_id not in conversation_sessions:

        conversation_sessions[
            session_id
        ] = create_empty_state()

    return conversation_sessions[
        session_id
  ]
