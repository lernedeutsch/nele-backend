# ==========================================
# NELE – ROUTER PERSONALIZOWANYCH ĆWICZEŃ
# ==========================================

from brain.logic.matcher import (
    normalize
)

from brain.logic.personalization import (
    create_personalized_exercise,
    get_personalized_exercise,
    clear_personalized_exercise,
    validate_personalized_answer,
    set_personalized_exercise_step,
    get_personalized_follow_up
)


# ==========================================
# KOMENDY ROZPOCZYNAJĄCE ĆWICZENIE
# ==========================================

PERSONALIZED_EXERCISE_COMMANDS = [
    "übe mit mir",
    "üb mit mir",
    "lass uns üben",
    "lass uns deutsch üben",
    "mach eine übung mit mir",
    "gib mir eine persönliche übung"
]


# ==========================================
# ODPOWIEDŹ KOŃCOWA PERSONALIZOWANEJ LEKCJI
# ==========================================

def create_personalized_final_answer(
    answer,
    topic,
    value
):

    normalized_answer = normalize(
        answer
    )


    # ======================================
    # HOBBY – RADFAHREN
    # ======================================

    if (
        topic == "hobby"
        and normalize(
            value or ""
        ) == "radfahren"
    ):

        if "wochenende" in normalized_answer:

            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre am Wochenende Rad.“"
            )

        if "morgens" in normalized_answer:

            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre morgens Rad.“"
            )

        if "nachmittags" in normalized_answer:

            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre nachmittags Rad.“"
            )

        if "abends" in normalized_answer:

            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre abends Rad.“"
            )

        if "samstag" in normalized_answer:

            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre am Samstag Rad.“"
            )

        if "sonntag" in normalized_answer:

            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre am Sonntag Rad.“"
            )

        return (
            f"Sehr gut! "
            f"Du hast gesagt: "
            f"„{answer}“ "
            f"Das passt gut zu deinem Hobby "
            f"{value}."
        )


    # ======================================
    # INNY TEMAT
    # ======================================

    return (
        f"Sehr gut! "
        f"Du hast gesagt: "
        f"„{answer}“"
    )


# ==========================================
# ODPOWIEDŹ NA AKTYWNE ĆWICZENIE
# ==========================================

def handle_personalized_exercise_answer(
    user_message,
    state
):

    exercise = get_personalized_exercise(
        state
    )

    if not exercise:

        return None


    # ======================================
    # WALIDACJA ODPOWIEDZI
    # ======================================

    validation = validate_personalized_answer(
        user_message,
        state
    )

    if not validation:

        return None


    status = validation.get(
        "status"
    )


    # ======================================
    # ODPOWIEDŹ DO PONOWIENIA
    # ======================================

    if status == "retry":

        return validation.get(
            "answer"
        )


    answer = validation.get(
        "answer",
        user_message.strip()
    )

    topic = validation.get(
        "topic"
    )

    value = validation.get(
        "value"
    )


    # ======================================
    # ETAP 1
    # ======================================

    if status == "step_1_accepted":

        set_personalized_exercise_step(
            state,
            2
        )

        follow_up = get_personalized_follow_up(
            state
        )

        if follow_up:

            return follow_up

        return (
            "Sehr gut! "
            "Machen wir weiter."
        )


    # ======================================
    # ETAP 2
    # ======================================

    if status == "step_2_accepted":

        set_personalized_exercise_step(
            state,
            3
        )

        follow_up = get_personalized_follow_up(
            state
        )

        if follow_up:

            return follow_up

        return (
            "Super! "
            "Machen wir weiter."
        )


    # ======================================
    # ETAP 3
    # ======================================

    if status == "step_3_accepted":

        clear_personalized_exercise(
            state
        )

        return create_personalized_final_answer(
            answer,
            topic,
            value
        )


    # ======================================
    # STARSZY / INNY TYP ĆWICZENIA
    # ======================================

    if status == "accepted":

        clear_personalized_exercise(
            state
        )

        if topic == "learning_goal":

            return (
                f"Sehr gut! "
                f"Wir arbeiten weiter an "
                f"deinem Lernziel {value}."
            )

        return (
            f"Sehr gut! "
            f"Deine Antwort lautet: "
            f"„{answer}“"
        )


    return None


# ==========================================
# GŁÓWNY ROUTER PERSONALIZACJI
# ==========================================

def handle_personalization(
    user_message,
    state
):

    message = normalize(
        user_message
    )


    # ======================================
    # NOWE PERSONALIZOWANE ĆWICZENIE
    # ======================================

    if message in PERSONALIZED_EXERCISE_COMMANDS:

        return create_personalized_exercise(
            state
        )


    # ======================================
    # ODPOWIEDŹ NA AKTYWNE ĆWICZENIE
    # ======================================

    if get_personalized_exercise(
        state
    ):

        return handle_personalized_exercise_answer(
            user_message,
            state
        )


    return None
