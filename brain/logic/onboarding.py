# ==========================================
# NELE – PIERWSZE SPOTKANIE Z UŻYTKOWNIKIEM
# ==========================================

from brain.logic.matcher import (
    normalize
)

from brain.memory.user_facts import (
    get_user_fact
)


# ==========================================
# SPRAWDZENIE, CZY ONBOARDING JEST GOTOWY
# ==========================================

def is_onboarding_completed(
    state
):

    return bool(
        state.get(
            "onboarding_completed",
            False
        )
    )


# ==========================================
# POBRANIE AKTUALNEGO ETAPU
# ==========================================

def get_onboarding_step(
    state
):

    return state.get(
        "onboarding_step",
        0
    )


# ==========================================
# USTAWIENIE ETAPU
# ==========================================

def set_onboarding_step(
    state,
    step
):

    state[
        "onboarding_step"
    ] = step


# ==========================================
# ZAKOŃCZENIE ONBOARDINGU
# ==========================================

def complete_onboarding(
    state
):

    state[
        "onboarding_completed"
    ] = True

    state[
        "onboarding_step"
    ] = 0


# ==========================================
# CZY UŻYTKOWNIK JEST NOWY
# ==========================================

def is_new_user(
    state
):

    if is_onboarding_completed(
        state
    ):
        return False

    name = get_user_fact(
        state,
        "name"
    )

    origin = get_user_fact(
        state,
        "origin"
    )

    residence = get_user_fact(
        state,
        "residence"
    )

    hobby = get_user_fact(
        state,
        "hobby"
    )

    learning_goal = get_user_fact(
        state,
        "learning_goal"
    )

    return not any([
        name,
        origin,
        residence,
        hobby,
        learning_goal
    ])


# ==========================================
# ROZPOCZĘCIE PIERWSZEGO SPOTKANIA
# ==========================================

def start_onboarding(
    state
):

    set_onboarding_step(
        state,
        1
    )

    return (
        "Hallo! Ich bin Nele, "
        "deine persönliche Deutschlehrerin. "
        "Schön, dich kennenzulernen! "
        "Wie heißt du?"
    )


# ==========================================
# PYTANIE DLA DANEGO ETAPU
# ==========================================

def get_onboarding_question(
    state
):

    step = get_onboarding_step(
        state
    )


    # ======================================
    # 1. IMIĘ
    # ======================================

    if step == 1:

        return (
            "Wie heißt du?"
        )


    # ======================================
    # 2. POCHODZENIE
    # ======================================

    if step == 2:

        name = get_user_fact(
            state,
            "name"
        )

        if name:

            return (
                f"Schön, dich kennenzulernen, "
                f"{name}! Woher kommst du?"
            )

        return (
            "Schön, dich kennenzulernen! "
            "Woher kommst du?"
        )


    # ======================================
    # 3. MIEJSCE ZAMIESZKANIA
    # ======================================

    if step == 3:

        return (
            "Und wo wohnst du jetzt?"
        )


    # ======================================
    # 4. HOBBY
    # ======================================

    if step == 4:

        return (
            "Was machst du gern "
            "in deiner Freizeit? "
            "Hast du ein Hobby?"
        )


    # ======================================
    # 5. CEL NAUKI
    # ======================================

    if step == 5:

        return (
            "Und was möchtest du "
            "auf Deutsch lernen?"
        )


    return None


# ==========================================
# PRZEJŚCIE DO NASTĘPNEGO PYTANIA
# ==========================================

def advance_onboarding(
    state
):

    step = get_onboarding_step(
        state
    )

    next_step = step + 1

    set_onboarding_step(
        state,
        next_step
    )

    return get_onboarding_question(
        state
    )


# ==========================================
# ZAKOŃCZENIE PIERWSZEGO SPOTKANIA
# ==========================================

def finish_onboarding(
    state
):

    name = get_user_fact(
        state,
        "name"
    )

    complete_onboarding(
        state
    )

    if name:

        return (
            f"Super, {name}! "
            "Jetzt kenne ich dich schon "
            "ein bisschen. "
            "Wir können zusammen Deutsch üben. "
            "Ich passe die Übungen an dich an."
        )

    return (
        "Super! Jetzt kenne ich dich schon "
        "ein bisschen. "
        "Wir können zusammen Deutsch üben. "
        "Ich passe die Übungen an dich an."
    )
