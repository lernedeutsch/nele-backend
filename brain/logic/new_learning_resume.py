# ==========================================
# NELE – KONTYNUACJA NOWEJ NAUKI
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import normalize

from brain.logic.lesson_teaching import (
    start_lesson_teaching
)
from brain.logic.dialogue_engine import start_dialogue_for_section

from brain.memory.lesson_progress import (
    set_current_section
)

from brain.memory.student_progress import (
    remember_learning_topic,
    get_current_level,
    get_current_lesson,
    set_current_level,
    set_current_lesson
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
    # MUSIMY MIEĆ KONKRETNĄ CZĘŚĆ LEKCJI
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
    # WŁAŚNIE TEJ PROPOZYCJI
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
    # AKTUALNY POZIOM / LEKCJA
    #
    # Przy przejściu np. z Lektion 1
    # do Lektion 2 aktualizujemy Student
    # Progress zanim uruchomimy silnik lekcji.
    # ======================================

    if level:

        set_current_level(
            state,
            level
        )


    if lesson:

        set_current_lesson(
            state,
            lesson
        )


    # ======================================
    # AKTUALNA CZĘŚĆ LEKCJI
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
    # OSTATNIA AKTYWNOŚĆ
    # ======================================

    state[
        "last_activity"
    ] = "lesson"

    state[
        "last_activity_detail"
    ] = section


    # ======================================
    # STUDENT MEMORY 2.0
    # HISTORIA NAUKI
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
    # PROPOZYCJA ZOSTAŁA PRZYJĘTA
    # ======================================

    clear_new_learning_offer(
        state
    )


    # ======================================
    # FAKTYCZNE ROZPOCZĘCIE NAUCZANIA
    # ======================================

    # If this lesson section owns a reusable dialogue, start it automatically.
    # No dialogue ID is hard-coded here: lesson content declares the mapping.
    dialogue_answer = start_dialogue_for_section(
        level or get_current_level(state),
        lesson or get_current_lesson(state),
        section,
        state,
    )
    if dialogue_answer:
        return dialogue_answer

    teaching_answer = (
        start_lesson_teaching(
            section,
            state
        )
    )


    if teaching_answer:

        return teaching_answer


    # ======================================
    # FALLBACK DLA CZĘŚCI, KTÓRYCH
    # LESSON_TEACHING JESZCZE NIE OBSŁUGUJE
    # ======================================

    return (
        f"Super, dann legen wir los! "
        f"Wir machen jetzt mit "
        f"„{section}“ weiter."
    )


# ==========================================
# OBSŁUGA "JA" / "NEIN"
# ==========================================

def handle_new_learning_resume(
    user_message,
    state
):

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
            "Alles klar. "
            "Was möchtest du stattdessen machen?"
        )


    # ======================================
    # INNA ODPOWIEDŹ
    #
    # Nie blokujemy normalnej rozmowy.
    # ======================================

    return None
