# ==========================================
# NELE – POWITANIE UŻYTKOWNIKA
# ==========================================

from brain.logic.memory import (
    get_conversation_state,
    save_conversation_state
)

from brain.logic.onboarding import (
    is_onboarding_completed,
    is_new_user,
    get_onboarding_step,
    get_onboarding_question,
    set_onboarding_step,
    complete_onboarding
)

from brain.memory.user_facts import (
    get_user_fact
)

from brain.memory.daily_learning import (
    start_daily_session
)


# ==========================================
# ZAPIS I ZWROT ODPOWIEDZI
# ==========================================

def save_and_return(
    answer,
    session_id
):

    try:

        save_conversation_state(
            session_id
        )

    except Exception as error:

        print(
            f"Welcome save error: {error}"
        )

    return answer


# ==========================================
# NOWA SEKWENCJA STARTOWA SESJI
#
# Kolejność:
#
# 1. należne słówka
# 2. należne błędy
# 3. krótkie przypomnienie ostatniej lekcji
# 4. należna powtórka lekcji
# 5. dalsza nauka
#
# Te znaczniki dotyczą tylko jednego
# otwarcia Nele.
# ==========================================

def reset_session_start_flow(
    state
):

    if state is None:
        return

    state[
        "session_start_flow"
    ] = {

        "active":
            True,

        "vocabulary_done":
            False,

        "errors_done":
            False,

        "last_lesson_recap_done":
            False,

        "lesson_review_done":
            False
    }


# ==========================================
# WYCZYSZCZENIE STAREJ AKTYWNEJ SESJI
# ==========================================

def clear_old_active_exercises(
    state
):

    # ======================================
    # PERSONALIZOWANE ĆWICZENIE
    # ======================================

    state[
        "personalization_exercise"
    ] = None


    # ======================================
    # AKTYWNE ĆWICZENIE SŁOWNICTWA
    # ======================================

    state[
        "vocabulary_practice_active"
    ] = False

    state[
        "vocabulary_practice_word"
    ] = None

    state[
        "vocabulary_practice_type"
    ] = None


    # ======================================
    # AKTYWNY TRENING BŁĘDU
    #
    # Po ponownym otwarciu strony Nele
    # najpierw pyta "Wie geht es dir?".
    # Stary krok Fehlertraining nie może
    # przechwycić tej odpowiedzi. Sam błąd
    # zostaje w Error Memory i Session Coach
    # uruchomi go ponownie po powitaniu.
    # ======================================

    state[
        "error_practice_active"
    ] = False

    state[
        "error_practice_type"
    ] = None

    state[
        "error_practice_step"
    ] = 0

    state[
        "error_practice_attempts"
    ] = 0

    state[
        "error_practice_used_hint"
    ] = False

    state[
        "error_practice_example_wrong"
    ] = None

    state[
        "error_practice_example_correct"
    ] = None


    # ======================================
    # AKTYWNE PROWADZENIE LEKCJI
    #
    # Zachowujemy dokładny punkt przerwania:
    # sekcję i krok. Dzięki temu po ponownym
    # otwarciu Nele wróci np. do "Guten Tag",
    # a nie do początku "Guten Morgen".
    # ======================================


    # ======================================
    # NOWY START SESJI
    #
    # Resetujemy tylko informację o tym,
    # które etapy początku NOWEJ sesji
    # zostały już wykonane.
    #
    # Nie kasujemy historii nauki.
    # ======================================

    reset_session_start_flow(
        state
    )


# ==========================================
# ZAPIS NOWEJ SESJI W PAMIĘCI DNIA
# ==========================================

def remember_new_daily_session(
    state
):

    if state is None:
        return


    try:

        start_daily_session(
            state
        )

    except Exception as error:

        print(
            f"Daily session start error: {error}"
        )


# ==========================================
# AUTOMATYCZNE POWITANIE
# ==========================================

def generate_welcome_reply(
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )


    # ======================================
    # UZUPEŁNIENIE PÓL
    # ======================================

    if "onboarding_completed" not in state:

        state[
            "onboarding_completed"
        ] = False

    if "onboarding_step" not in state:

        state[
            "onboarding_step"
        ] = 0

    if "user_facts" not in state:

        state[
            "user_facts"
        ] = {}


    # ======================================
    # POBRANIE IMIENIA
    # ======================================

    name = get_user_fact(
        state,
        "name"
    )

    if not name:

        name = state.get(
            "name"
        )


    # ======================================
    # ONBOARDING NIEZAKOŃCZONY
    # ======================================

    if not is_onboarding_completed(
        state
    ):

        onboarding_step = get_onboarding_step(
            state
        )


        # ==================================
        # ONBOARDING JUŻ TRWA
        # ==================================

        if onboarding_step > 0:

            question = get_onboarding_question(
                state
            )


            # ------------------------------
            # ETAP 1 – IMIĘ
            # ------------------------------

            if onboarding_step == 1:

                answer = (
                    "Hallo! Ich bin Nele, "
                    "deine persönliche "
                    "Deutschtrainerin. "
                    "Schön, dich kennenzulernen! "
                    "Wie heißt du?"
                )

                return save_and_return(
                    answer,
                    session_id
                )


            # ------------------------------
            # POWRÓT W TRAKCIE ONBOARDINGU
            # ------------------------------

            if question:

                if name:

                    answer = (
                        f"Hallo {name}! "
                        "Schön, dass du wieder da bist. "
                        f"{question}"
                    )

                else:

                    answer = (
                        "Hallo! "
                        "Schön, dass du wieder da bist. "
                        f"{question}"
                    )

                return save_and_return(
                    answer,
                    session_id
                )


        # ==================================
        # ZUPEŁNIE NOWY UŻYTKOWNIK
        # ==================================

        if is_new_user(
            state
        ):

            set_onboarding_step(
                state,
                1
            )

            answer = (
                "Hallo! Ich bin Nele, "
                "deine persönliche Deutschtrainerin. "
                "Schön, dich kennenzulernen! "
                "Wie heißt du?"
            )

            return save_and_return(
                answer,
                session_id
            )


        # ==================================
        # STARY UŻYTKOWNIK
        # ==================================

        complete_onboarding(
            state
        )


    # ======================================
    # NOWE SPOTKANIE
    #
    # Czyścimy tylko stare aktywne tryby.
    #
    # Pamięć ucznia, postęp lekcji
    # i Daily Learning Memory zostają.
    # ======================================

    clear_old_active_exercises(
        state
    )


    # ======================================
    # DAILY LEARNING MEMORY
    #
    # Każde ponowne wejście do Nele
    # zapisujemy jako nową sesję.
    #
    # Jeżeli jest ten sam dzień:
    # poprzednia nauka NIE jest kasowana.
    #
    # Jeżeli zaczął się nowy dzień:
    # daily_learning.py automatycznie
    # utworzy nową pamięć dnia.
    # ======================================

    remember_new_daily_session(
        state
    )


    # ======================================
    # ZNANY UŻYTKOWNIK
    # ======================================

    state[
        "last_question"
    ] = "wellbeing"


    if name:

        answer = (
            f"Hallo {name}! "
            "Schön, dich wiederzusehen. "
            "Wie geht es dir?"
        )

    else:

        answer = (
            "Hallo! "
            "Schön, dich wiederzusehen. "
            "Wie geht es dir?"
        )


    return save_and_return(
        answer,
        session_id
        )
