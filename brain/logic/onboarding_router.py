# ==========================================
# NELE – ROUTER ONBOARDINGU
# ==========================================

from brain.logic.onboarding import (
    is_onboarding_completed,
    is_new_user,
    get_onboarding_step,
    handle_onboarding_answer,
    complete_onboarding
)

from brain.logic.welcome import (
    generate_welcome_reply
)


# ==========================================
# OBSŁUGA PIERWSZEGO SPOTKANIA
# ==========================================

def handle_onboarding(
    user_message,
    state,
    session_id="default"
):

    # ======================================
    # ONBOARDING JUŻ ZAKOŃCZONY
    # ======================================

    if is_onboarding_completed(
        state
    ):

        return None


    # ======================================
    # AKTUALNY ETAP ONBOARDINGU
    # ======================================

    onboarding_step = get_onboarding_step(
        state
    )


    # ======================================
    # ONBOARDING JUŻ TRWA
    # ======================================

    if onboarding_step > 0:

        return handle_onboarding_answer(
            user_message,
            state,
            session_id
        )


    # ======================================
    # ZUPEŁNIE NOWY UŻYTKOWNIK
    # ======================================

    if is_new_user(
        state
    ):

        return generate_welcome_reply(
            session_id
        )


    # ======================================
    # STARY UŻYTKOWNIK
    # SPRZED WPROWADZENIA ONBOARDINGU
    # ======================================

    complete_onboarding(
        state
    )

    return None
