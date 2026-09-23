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

from brain.logic.session_state import (
    prepare_page_reopen
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
    """Compatibility wrapper. Session state now has one central owner."""

    prepare_page_reopen(
        state
    )


def clear_old_active_exercises(
    state
):
    """Prepare a normal page reopen without deleting learning memory."""

    prepare_page_reopen(
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
                    "Hallo! Ich bin Nele. "
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

                # --------------------------
                # ETAP 2 – POWRÓT PO IMIENIU
                #
                # get_onboarding_question()
                # dla kroku 2 zawiera tekst
                # "Schön, dich kennenzulernen".
                # Przy ponownym wejściu nie
                # dokładamy go do
                # "Schön, dass du wieder da bist",
                # bo brzmiałoby to sprzecznie.
                # --------------------------

                if onboarding_step == 2:

                    if name:

                        answer = (
                            f"Hallo {name}! "
                            "Schön, dass du wieder da bist. "
                            "Woher kommst du?"
                        )

                    else:

                        answer = (
                            "Hallo! "
                            "Schön, dass du wieder da bist. "
                            "Woher kommst du?"
                        )

                    return save_and_return(
                        answer,
                        session_id
                    )

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
                "Hallo! Ich bin Nele. "
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
