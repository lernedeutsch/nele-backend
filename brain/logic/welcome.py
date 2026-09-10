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
        #
        # Użytkownik ma zapisane dane
        # z czasu sprzed onboardingu.
        # Nie pytamy go ponownie.
        # ==================================

        complete_onboarding(
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
