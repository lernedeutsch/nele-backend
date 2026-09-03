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
        "residence": None,
        "current_topic": None,
        "current_comparison": None,
        "current_expression": None,
        "last_example_expression": None,
        "example_index": -1
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

    state = conversation_sessions[
        session_id
    ]

    # ======================================
    # ZABEZPIECZENIE STARSZYCH SESJI
    # ======================================

    if "last_question" not in state:
        state["last_question"] = None

    if "name" not in state:
        state["name"] = None

    if "origin" not in state:
        state["origin"] = None

    if "residence" not in state:
        state["residence"] = None

    if "current_topic" not in state:
        state["current_topic"] = None

    if "current_comparison" not in state:
        state["current_comparison"] = None

    if "current_expression" not in state:
        state["current_expression"] = None

    if "last_example_expression" not in state:
        state["last_example_expression"] = None

    if "example_index" not in state:
        state["example_index"] = -1

    return state
