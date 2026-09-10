# ==========================================
# NELE – PAMIĘĆ ROZMOWY
# ==========================================

from brain.memory.persistent_memory import (
    initialize_persistent_memory,
    load_persistent_memory,
    save_persistent_memory,
    delete_persistent_memory
)

from brain.memory.student_progress import (
    create_empty_student_progress
)


conversation_sessions = {}

persistent_memory_initialized = False


# ==========================================
# INICJALIZACJA TRWAŁEJ PAMIĘCI
# ==========================================

def ensure_persistent_memory():

    global persistent_memory_initialized

    if persistent_memory_initialized:
        return

    try:

        initialize_persistent_memory()

        persistent_memory_initialized = True

    except Exception as error:

        print(
            f"Persistent memory initialization error: {error}"
        )


# ==========================================
# NOWA PAMIĘĆ SESJI
# ==========================================

def create_empty_state():
    """
    Tworzy pustą pamięć dla nowego użytkownika.
    """

    return {

        # ==================================
        # OGÓLNY KONTEKST ROZMOWY
        # ==================================

        "last_question": None,


        # ==================================
        # PIERWSZE SPOTKANIE Z NELE
        # ==================================

        "onboarding_completed": False,
        "onboarding_step": 0,


        # ==================================
        # INFORMACJE O UŻYTKOWNIKU
        # ==================================

        "name": None,
        "origin": None,
        "residence": None,

        "user_facts": {},


        # ==================================
        # STUDENT MEMORY 2.0
        # OGÓLNY POSTĘP UCZNIA
        # ==================================

        "student_progress":
            create_empty_student_progress(),


        # ==================================
        # KONTEKST ROZMOWY
        # ==================================

        "current_topic": None,
        "current_comparison": None,
        "current_expression": None,


        # ==================================
        # PRZYKŁADY
        # ==================================

        "last_example_expression": None,
        "example_index": -1,


        # ==================================
        # SŁOWNICTWO – KONTEKST
        # ==================================

        "current_vocabulary_word": None,
        "current_vocabulary_related_word": None,


        # ==================================
        # SŁOWNICTWO – POSTĘPY
        # ==================================

        "vocabulary_memory": {},


        # ==================================
        # AKTYWNE ĆWICZENIE SŁOWNICTWA
        # ==================================

        "vocabulary_practice_active": False,
        "vocabulary_practice_word": None,
        "vocabulary_practice_type": None,


        # ==================================
        # OSTATNIA AKTYWNOŚĆ
        # ==================================

        "last_activity": None,
        "last_activity_detail": None,


        # ==================================
        # PERSONALIZACJA
        # ==================================

        "personalization_exercise": None
    }


# ==========================================
# UZUPEŁNIENIE BRAKUJĄCYCH PÓL
# ==========================================

def complete_state(
    state
):

    if not isinstance(
        state,
        dict
    ):

        state = {}

    default_state = create_empty_state()

    for key, default_value in default_state.items():

        if key not in state:

            state[
                key
            ] = default_value

    return state


# ==========================================
# POBIERANIE PAMIĘCI SESJI
# ==========================================

def get_conversation_state(
    session_id="default"
):
    """
    Pobiera pamięć konkretnego użytkownika.

    Najpierw sprawdza pamięć bieżącego procesu.

    Jeżeli jej tam nie ma,
    próbuje pobrać ją z PostgreSQL.

    Jeżeli użytkownik jeszcze nie istnieje,
    tworzy nową pamięć.
    """

    if not session_id:

        session_id = "default"

    ensure_persistent_memory()


    # ======================================
    # PAMIĘĆ JUŻ JEST W RAM
    # ======================================

    if session_id in conversation_sessions:

        state = conversation_sessions[
            session_id
        ]

        state = complete_state(
            state
        )

        conversation_sessions[
            session_id
        ] = state

        return state


    # ======================================
    # PRÓBA POBRANIA Z POSTGRESQL
    # ======================================

    try:

        persistent_state = (
            load_persistent_memory(
                session_id
            )
        )

    except Exception as error:

        print(
            f"Persistent memory load error: {error}"
        )

        persistent_state = {}


    # ======================================
    # NOWY LUB ISTNIEJĄCY UCZEŃ
    # ======================================

    if persistent_state:

        state = complete_state(
            persistent_state
        )

    else:

        state = create_empty_state()


    conversation_sessions[
        session_id
    ] = state

    return state


# ==========================================
# ZAPISANIE PAMIĘCI SESJI
# ==========================================

def save_conversation_state(
    session_id="default"
):
    """
    Zapisuje aktualną pamięć ucznia
    do PostgreSQL.
    """

    if not session_id:

        session_id = "default"

    ensure_persistent_memory()

    if session_id not in conversation_sessions:

        return False

    state = conversation_sessions[
        session_id
    ]

    state = complete_state(
        state
    )

    conversation_sessions[
        session_id
    ] = state

    try:

        return save_persistent_memory(
            session_id,
            state
        )

    except Exception as error:

        print(
            f"Conversation memory save error: {error}"
        )

        return False


# ==========================================
# CAŁKOWITY RESET UŻYTKOWNIKA
# ==========================================

def reset_conversation_state(
    session_id="default"
):
    """
    Usuwa całą pamięć użytkownika:

    - dane użytkownika
    - onboarding
    - Student Memory 2.0
    - postępy słownictwa
    - aktywne ćwiczenia
    - ostatnią aktywność
    - kontekst rozmowy

    Dane są usuwane zarówno z PostgreSQL,
    jak i z pamięci RAM.
    """

    if not session_id:

        session_id = "default"

    ensure_persistent_memory()


    # ======================================
    # USUNIĘCIE Z POSTGRESQL
    # ======================================

    try:

        deleted = delete_persistent_memory(
            session_id
        )

    except Exception as error:

        print(
            f"Conversation reset error: {error}"
        )

        return False


    if not deleted:

        return False


    # ======================================
    # USUNIĘCIE Z RAM
    # ======================================

    conversation_sessions.pop(
        session_id,
        None
    )


    return True
