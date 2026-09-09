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

        return (
            f"Du hast mir erzählt, dass "
            f"dein Hobby {hobby} ist. "
            f"Bilde einen Satz mit "
            f"„{hobby}“."
        )


    # ======================================
    # ULUBIONY KOLOR
    # ======================================

    if favorite_color:

        return (
            f"Deine Lieblingsfarbe ist "
            f"{favorite_color}. "
            f"Bilde einen Satz mit "
            f"„{favorite_color}“."
        )


    # ======================================
    # ULUBIONE SŁOWO
    # ======================================

    if favorite_word:

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

        return (
            f"Dein Lernziel ist "
            f"{learning_goal}. "
            f"Lass uns dafür Deutsch üben."
        )


    # ======================================
    # BRAK DANYCH DO PERSONALIZACJI
    # ======================================

    return (
        "Erzähl mir etwas über dich, "
        "damit ich die Übungen besser "
        "an dich anpassen kann."
    )
