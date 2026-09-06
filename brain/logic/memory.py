# ==========================================
# NELE – PAMIĘĆ ROZMOWY
# ==========================================

conversation_sessions = {}


# ==========================================
# NOWA PAMIĘĆ SESJI
# ==========================================

def create_empty_state():
    """
    Tworzy pustą pamięć dla nowego użytkownika.
    """

    return {
        "last_question": None,

        # informacje o użytkowniku
        "name": None,
        "origin": None,
        "residence": None,

        # kontekst rozmowy
        "current_topic": None,
        "current_comparison": None,
        "current_expression": None,

        # przykłady
        "last_example_expression": None,
        "example_index": -1,

        # słownictwo
        "current_vocabulary_word": None,
        "current_vocabulary_related_word": None
    }


# ==========================================
# POBIERANIE PAMIĘCI SESJI
# ==========================================

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

    default_state = create_empty_state()

    for key, default_value in default_state.items():

        if key not in state:
            state[key] = default_value


    return state
