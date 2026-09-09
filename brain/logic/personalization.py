# ==========================================
# NELE – PERSONALIZACJA NAUKI
# ==========================================

from brain.memory.user_facts import (
    get_user_fact
)


# ==========================================
# POBRANIE PROFILU DO PERSONALIZACJI
# ==========================================

def get_learning_profile(
    state
):

    return {
        "name": get_user_fact(
            state,
            "name"
        ),

        "origin": get_user_fact(
            state,
            "origin"
        ),

        "residence": get_user_fact(
            state,
            "residence"
        ),

        "favorite_word": get_user_fact(
            state,
            "favorite_word"
        ),

        "favorite_color": get_user_fact(
            state,
            "favorite_color"
        ),

        "hobby": get_user_fact(
            state,
            "hobby"
        ),

        "learning_goal": get_user_fact(
            state,
            "learning_goal"
        )
    }


# ==========================================
# ZAPIS AKTYWNEGO ĆWICZENIA
# ==========================================

def remember_personalized_exercise(
    state,
    exercise_type,
    topic,
    value
):

    state[
        "personalization_exercise"
    ] = {
        "type": exercise_type,
        "topic": topic,
        "value": value
    }


# ==========================================
# WYCZYSZCZENIE AKTYWNEGO ĆWICZENIA
# ==========================================

def clear_personalized_exercise(
    state
):

    state[
        "personalization_exercise"
    ] = None


# ==========================================
# POBRANIE AKTYWNEGO ĆWICZENIA
# ==========================================

def get_personalized_exercise(
    state
):

    exercise = state.get(
        "personalization_exercise"
    )

    if not isinstance(
        exercise,
        dict
    ):
        return None

    return exercise


# ==========================================
# PERSONALIZOWANE ĆWICZENIE
# ==========================================

def create_personalized_exercise(
    state
):

    hobby = get_user_fact(
        state,
        "hobby"
    )

    favorite_color = get_user_fact(
        state,
        "favorite_color"
    )

    favorite_word = get_user_fact(
        state,
        "favorite_word"
    )

    learning_goal = get_user_fact(
        state,
        "learning_goal"
    )


    # ======================================
    # HOBBY
    # ======================================

    if hobby:

        remember_personalized_exercise(
            state,
            "sentence",
            "hobby",
            hobby
        )

        return (
            f"Du hast mir erzählt, dass "
            f"dein Hobby {hobby} ist. "
            f"Bilde einen Satz über "
            f"dein Hobby."
        )


    # ======================================
    # ULUBIONY KOLOR
    # ======================================

    if favorite_color:

        remember_personalized_exercise(
            state,
            "sentence",
            "favorite_color",
            favorite_color
        )

        return (
            f"Deine Lieblingsfarbe ist "
            f"{favorite_color}. "
            f"Bilde einen Satz über "
            f"deine Lieblingsfarbe."
        )


    # ======================================
    # ULUBIONE SŁOWO
    # ======================================

    if favorite_word:

        remember_personalized_exercise(
            state,
            "sentence",
            "favorite_word",
            favorite_word
        )

        return (
            f"Dein Lieblingswort ist "
            f"„{favorite_word}“. "
            f"Bilde einen Satz mit "
            f"diesem Wort."
        )


    # ======================================
    # CEL NAUKI
    # ======================================

    if learning_goal:

        remember_personalized_exercise(
            state,
            "learning",
            "learning_goal",
            learning_goal
        )

        return (
            f"Dein Lernziel ist "
            f"{learning_goal}. "
            f"Lass uns dafür Deutsch üben."
        )


    # ======================================
    # BRAK DANYCH DO PERSONALIZACJI
    # ======================================

    clear_personalized_exercise(
        state
    )

    return (
        "Erzähl mir etwas über dich, "
        "damit ich die Übungen besser "
        "an dich anpassen kann."
    )
