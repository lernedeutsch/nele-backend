# ==========================================
# NELE – PIERWSZE SPOTKANIE Z UŻYTKOWNIKIEM
# ==========================================

from brain.memory.user_facts import (
    get_user_fact
)

from brain.logic.user_info import (
    extract_user_information
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
            "Was ist dein Hobby?"
        )


    # ======================================
    # 5. CEL NAUKI
    # ======================================

    if step == 5:

        return (
            "Was ist dein Lernziel?"
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
# ODPOWIEDŹ, GDY NELE NIE ROZUMIE
# ==========================================

def get_onboarding_retry(
    step
):

    if step == 1:

        return (
            "Sag bitte zum Beispiel: "
            "„Ich heiße Anna.“"
        )

    if step == 2:

        return (
            "Sag bitte zum Beispiel: "
            "„Ich komme aus Polen.“"
        )

    if step == 3:

        return (
            "Sag bitte zum Beispiel: "
            "„Ich wohne in Heidelberg.“"
        )

    if step == 4:

        return (
            "Sag bitte zum Beispiel: "
            "„Mein Hobby ist Radfahren.“"
        )

    if step == 5:

        return (
            "Sag bitte zum Beispiel: "
            "„Mein Lernziel ist Deutsch B1.“"
        )

    return (
        "Versuch es bitte noch einmal."
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


# ==========================================
# OBSŁUGA ODPOWIEDZI PODCZAS ONBOARDINGU
# ==========================================

def handle_onboarding_answer(
    user_message,
    state,
    session_id="default"
):

    if is_onboarding_completed(
        state
    ):
        return None

    step = get_onboarding_step(
        state
    )

    if step == 0:
        return None


    # ======================================
    # ZAPAMIĘTANIE ODPOWIEDZI
    # ======================================

    extract_user_information(
        user_message,
        session_id
    )


    # ======================================
    # ETAP 1 – IMIĘ
    # ======================================

    if step == 1:

        name = get_user_fact(
            state,
            "name"
        )

        if not name:

            return get_onboarding_retry(
                step
            )

        set_onboarding_step(
            state,
            2
        )

        return (
            f"Schön, dich kennenzulernen, "
            f"{name}! Woher kommst du?"
        )


    # ======================================
    # ETAP 2 – POCHODZENIE
    # ======================================

    if step == 2:

        origin = get_user_fact(
            state,
            "origin"
        )

        if not origin:

            return get_onboarding_retry(
                step
            )

        set_onboarding_step(
            state,
            3
        )

        return (
            "Und wo wohnst du jetzt?"
        )


    # ======================================
    # ETAP 3 – MIEJSCE ZAMIESZKANIA
    # ======================================

    if step == 3:

        residence = get_user_fact(
            state,
            "residence"
        )

        if not residence:

            return get_onboarding_retry(
                step
            )

        set_onboarding_step(
            state,
            4
        )

        return (
            "Was ist dein Hobby?"
        )


    # ======================================
    # ETAP 4 – HOBBY
    # ======================================

    if step == 4:

        hobby = get_user_fact(
            state,
            "hobby"
        )

        if not hobby:

            return get_onboarding_retry(
                step
            )

        set_onboarding_step(
            state,
            5
        )

        return (
            "Schön! Und was ist dein Lernziel?"
        )


    # ======================================
    # ETAP 5 – CEL NAUKI
    # ======================================

    if step == 5:

        learning_goal = get_user_fact(
            state,
            "learning_goal"
        )

        if not learning_goal:

            return get_onboarding_retry(
                step
            )

        return finish_onboarding(
            state
        )


    return None
