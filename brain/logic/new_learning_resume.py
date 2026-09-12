# ==========================================
# NELE – KONTYNUACJA NOWEJ NAUKI
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import normalize

from brain.memory.lesson_progress import (
    set_current_section
)

from brain.memory.student_progress import (
    remember_learning_topic
)


# ==========================================
# ODPOWIEDZI TWIERDZĄCE
# ==========================================

YES_ANSWERS = {
    "ja",
    "ja gern",
    "ja gerne",
    "gern",
    "gerne",
    "klar",
    "okay",
    "ok",
    "natürlich",
    "ja bitte",
    "machen wir",
    "los gehts",
    "los geht's",
    "weiter"
}


# ==========================================
# ODPOWIEDZI PRZECZĄCE
# ==========================================

NO_ANSWERS = {
    "nein",
    "nein danke",
    "nein lieber nicht",
    "nicht jetzt",
    "nicht heute",
    "lieber nicht",
    "etwas anderes",
    "was anderes"
}


# ==========================================
# ZAPISANIE PROPOZYCJI NOWEJ NAUKI
# ==========================================

def set_new_learning_offer(
    state,
    plan
):
    """
    Zapamiętuje materiał,
    który Nele właśnie zaproponowała.

    Przykład:

    A1
    Lektion 1
    Ich stelle mich vor
    """

    if state is None:
        return False

    if not isinstance(
        plan,
        dict
    ):
        return False


    section = plan.get(
        "section"
    )

    level = plan.get(
        "level"
    )

    lesson = plan.get(
        "lesson"
    )


    # ======================================
    # NA RAZIE INTERESUJE NAS
    # KONKRETNA CZĘŚĆ LEKCJI
    # ======================================

    if not section:
        return False


    state[
        "pending_new_learning"
    ] = {
        "type":
            plan.get(
                "type"
            ),

        "level":
            level,

        "lesson":
            lesson,

        "section":
            section,

        "topic":
            plan.get(
                "topic"
            )
    }


    # ======================================
    # KOLEJNE "JA" DOTYCZY
    # NOWEGO MATERIAŁU
    # ======================================

    state[
        "last_question"
    ] = "continue_new_learning"


    return True


# ==========================================
# POBRANIE OCZEKUJĄCEJ PROPOZYCJI
# ==========================================

def get_new_learning_offer(
    state
):

    if state is None:
        return None


    offer = state.get(
        "pending_new_learning"
    )


    if not isinstance(
        offer,
        dict
    ):
        return None


    return offer


# ==========================================
# CZY CZEKA NOWA NAUKA
# ==========================================

def has_new_learning_offer(
    state
):

    if state is None:
        return False


    if (
        state.get(
            "last_question"
        )
        !=
        "continue_new_learning"
    ):

        return False


    offer = get_new_learning_offer(
        state
    )


    if not offer:
        return False


    return bool(
        offer.get(
            "section"
        )
    )


# ==========================================
# USUNIĘCIE PROPOZYCJI
# ==========================================

def clear_new_learning_offer(
    state
):

    if state is None:
        return


    state[
        "pending_new_learning"
    ] = None


    if (
        state.get(
            "last_question"
        )
        ==
        "continue_new_learning"
    ):

        state[
            "last_question"
        ] = None


# ==========================================
# ROZPOCZĘCIE NOWEJ CZĘŚCI
# ==========================================

def start_new_learning(
    state,
    offer
):

    if state is None:
        return None

    if not offer:
        return None


    level = offer.get(
        "level"
    )

    lesson = offer.get(
        "lesson"
    )

    section = offer.get(
        "section"
    )


    if not section:
        return None


    # ======================================
    # USTAWIAMY AKTUALNĄ CZĘŚĆ LEKCJI
    # ======================================

    if (
        level
        and
        lesson
    ):

        set_current_section(
            state,
            level,
            lesson,
            section
        )


    # ======================================
    # ZAPAMIĘTANIE AKTYWNOŚCI
    # ======================================

    state[
        "last_activity"
    ] = "lesson"

    state[
        "last_activity_detail"
    ] = section


    # ======================================
    # STUDENT MEMORY 2.0
    # ======================================

    if (
        level
        and
        lesson
    ):

        remember_learning_topic(
            state,
            (
                f"{level} Lektion "
                f"{lesson}: "
                f"{section}"
            )
        )


    # ======================================
    # STARA PROPOZYCJA NIE JEST
    # JUŻ POTRZEBNA
    # ======================================

    clear_new_learning_offer(
        state
    )


    return (
        f"Gerne! Dann beginnen wir mit "
        f"„{section}“."
    )


# ==========================================
# OBSŁUGA "JA" / "NEIN"
# ==========================================

def handle_new_learning_resume(
    user_message,
    state
):
    """
    Obsługuje odpowiedź użytkownika
    po propozycji nowego materiału.

    Przykład:

    Nele:
    Als Nächstes ist
    „Ich stelle mich vor“ dran.

    Benutzer:
    Ja.

    Nele:
    Gerne! Dann beginnen wir mit
    „Ich stelle mich vor“.
    """

    if state is None:
        return None


    if not has_new_learning_offer(
        state
    ):

        return None


    message = normalize(
        user_message
    ).strip(
        " .?!„“\"'"
    )


    if not message:
        return None


    # ======================================
    # JA
    # ======================================

    if message in YES_ANSWERS:

        offer = get_new_learning_offer(
            state
        )

        return start_new_learning(
            state,
            offer
        )


    # ======================================
    # NEIN
    # ======================================

    if message in NO_ANSWERS:

        clear_new_learning_offer(
            state
        )

        return (
            "Kein Problem. "
            "Was möchtest du stattdessen machen?"
        )


    # ======================================
    # INNA ODPOWIEDŹ
    #
    # Nie blokujemy normalnej rozmowy.
    # ======================================

    return None
