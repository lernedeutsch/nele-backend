# ==========================================
# NELE – AKTIVES UNTERRICHTEN EINER LEKTION
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import normalize

from brain.memory.lesson_progress import (
    mark_section_completed,
    get_next_incomplete_section
)


# ==========================================
# TEXT BEREINIGEN
# ==========================================

def clean_answer(
    text
):

    text = str(
        text or ""
    ).strip()

    return text.strip(
        " .?!„“\"'"
    )


# ==========================================
# KONTEXT DER LEKTION FINDEN
# ==========================================

def get_lesson_context_for_section(
    state,
    section
):

    if state is None:
        return (
            None,
            None
        )

    if not section:
        return (
            None,
            None
        )


    lesson_memory = state.get(
        "lesson_progress",
        {}
    )

    if not isinstance(
        lesson_memory,
        dict
    ):

        return (
            None,
            None
        )


    lessons = lesson_memory.get(
        "lessons",
        {}
    )

    if not isinstance(
        lessons,
        dict
    ):

        return (
            None,
            None
        )


    # ======================================
    # 1. ZUERST AKTUELLE SEKTION SUCHEN
    # ======================================

    for lesson_data in lessons.values():

        if not isinstance(
            lesson_data,
            dict
        ):

            continue


        current_section = lesson_data.get(
            "current_section"
        )


        if current_section != section:

            continue


        level = lesson_data.get(
            "level"
        )

        lesson = lesson_data.get(
            "lesson"
        )


        if level and lesson:

            return (
                level,
                lesson
            )


    # ======================================
    # 2. FALLBACK:
    # SEKTION IN DER LEKTION SUCHEN
    # ======================================

    for lesson_data in lessons.values():

        if not isinstance(
            lesson_data,
            dict
        ):

            continue


        sections = lesson_data.get(
            "sections",
            []
        )


        if not isinstance(
            sections,
            list
        ):

            continue


        if section not in sections:

            continue


        level = lesson_data.get(
            "level"
        )

        lesson = lesson_data.get(
            "lesson"
        )


        if level and lesson:

            return (
                level,
                lesson
            )


    return (
        None,
        None
    )


# ==========================================
# UNTERRICHT BEENDEN
# ==========================================

def finish_lesson_teaching(
    state
):

    if state is None:
        return


    state[
        "lesson_teaching_active"
    ] = False

    state[
        "lesson_teaching_section"
    ] = None

    state[
        "lesson_teaching_step"
    ] = 0


# ==========================================
# UNTERRICHT STARTEN
# ==========================================

def start_lesson_teaching(
    section,
    state
):

    if state is None:
        return None

    if not section:
        return None


    section = str(
        section
    ).strip()


    # ======================================
    # TEIL:
    # ICH STELLE MICH VOR
    # ======================================

    if normalize(
        section
    ) == normalize(
        "Ich stelle mich vor"
    ):

        state[
            "lesson_teaching_active"
        ] = True

        state[
            "lesson_teaching_section"
        ] = "Ich stelle mich vor"

        state[
            "lesson_teaching_step"
        ] = 1


        state[
            "last_activity"
        ] = "lesson"

        state[
            "last_activity_detail"
        ] = "Ich stelle mich vor"


        return (
            "Super, dann legen wir los! "
            "Wir üben jetzt, wie du dich "
            "auf Deutsch vorstellst. "
            "Zum Beispiel: „Ich heiße Anna.“ "
            "Und jetzt du: Wie heißt du?"
        )


    return None


# ==========================================
# CZY AKTYWNA JEST LEKCJA
# ==========================================

def is_lesson_teaching_active(
    state
):

    if state is None:
        return False


    return bool(
        state.get(
            "lesson_teaching_active",
            False
        )
    )


# ==========================================
# IMIĘ – POPRAWNA ODPOWIEDŹ
# ==========================================

def is_valid_name_answer(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!„“\"'"
    )


    valid_starts = [
        "ich heiße ",
        "ich heisse ",
        "ich bin ",
        "mein name ist "
    ]


    return any(
        message.startswith(
            start
        )
        and len(
            message[
                len(start):
            ].strip()
        ) > 0
        for start in valid_starts
    )


# ==========================================
# PYTANIE INFORMALNE
# ==========================================

def is_informal_name_question(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!„“\"'"
    )


    return message in {
        "wie heißt du",
        "wie heisst du"
    }


# ==========================================
# PYTANIE FORMALNE
# ==========================================

def is_formal_name_question(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!„“\"'"
    )


    return message in {
        "wie heißen sie",
        "wie heissen sie"
    }


# ==========================================
# TEIL:
# ICH STELLE MICH VOR
# ==========================================

def handle_introduction_section(
    user_message,
    state
):

    step = state.get(
        "lesson_teaching_step",
        1
    )


    # ======================================
    # SCHRITT 1
    # SICH VORSTELLEN
    # ======================================

    if step == 1:

        if not is_valid_name_answer(
            user_message
        ):

            return (
                "Fast! Sag es bitte als "
                "ganzen Satz, zum Beispiel: "
                "„Ich heiße Moni.“"
            )


        state[
            "lesson_teaching_step"
        ] = 2


        return (
            "Genau! Das klingt ganz natürlich. "
            "Jetzt bist du dran: "
            "Wie fragst du nach dem Namen?"
        )


    # ======================================
    # SCHRITT 2
    # WIE HEISST DU?
    # ======================================

    if step == 2:

        if not is_informal_name_question(
            user_message
        ):

            return (
                "Fast. Wenn ihr euch duzt, "
                "sagst du: "
                "„Wie heißt du?“ "
                "Versuch es noch einmal."
            )


        state[
            "lesson_teaching_step"
        ] = 3


        return (
            "Perfekt! „Wie heißt du?“ "
            "sagt man im Alltag sehr oft. "
            "Jetzt noch die höfliche Form: "
            "Wie fragst du zum Beispiel "
            "einen Gast im Hotel nach dem Namen?"
        )


    # ======================================
    # SCHRITT 3
    # WIE HEISSEN SIE?
    # ======================================

    if step == 3:

        if not is_formal_name_question(
            user_message
        ):

            return (
                "Fast. Wenn du jemanden siezt, "
                "sagst du: "
                "„Wie heißen Sie?“ "
                "Versuch es noch einmal."
            )


        # ==================================
        # AKTUELLE LEKTION FINDEN
        # ==================================

        section = state.get(
            "lesson_teaching_section"
        )

        level, lesson = (
            get_lesson_context_for_section(
                state,
                section
            )
        )


        # ==================================
        # STUDENT MEMORY 2.0
        # TEIL ALS ABGESCHLOSSEN SPEICHERN
        # ==================================

        next_section = None


        if (
            level
            and
            lesson
            and
            section
        ):

            mark_section_completed(
                state,
                level,
                lesson,
                section
            )


            next_section = (
                get_next_incomplete_section(
                    state,
                    level,
                    lesson
                )
            )


        # ==================================
        # AKTIVES TRAINING BEENDEN
        # ==================================

        finish_lesson_teaching(
            state
        )


        # ==================================
        # ES GIBT NOCH EINEN NÄCHSTEN TEIL
        # ==================================

        if next_section:

            return (
                "Sehr gut! Jetzt kannst du dich "
                "vorstellen und sowohl informell "
                "als auch höflich nach dem Namen fragen. "
                f"Als Nächstes kommt "
                f"„{next_section}“."
            )


        # ==================================
        # KEIN WEITERER TEIL
        # ==================================

        return (
            "Sehr gut! Jetzt kannst du dich "
            "vorstellen und sowohl informell "
            "als auch höflich nach dem Namen fragen. "
            "Diesen Teil hast du geschafft!"
        )


    # ======================================
    # UNBEKANNTER SCHRITT
    # ======================================

    finish_lesson_teaching(
        state
    )

    return None


# ==========================================
# GŁÓWNA OBSŁUGA AKTYWNEJ LEKCJI
# ==========================================

def handle_lesson_teaching(
    user_message,
    state
):

    if state is None:
        return None


    if not is_lesson_teaching_active(
        state
    ):

        return None


    section = state.get(
        "lesson_teaching_section"
    )


    if not section:

        finish_lesson_teaching(
            state
        )

        return None


    if normalize(
        section
    ) == normalize(
        "Ich stelle mich vor"
    ):

        return handle_introduction_section(
            user_message,
            state
        )


    finish_lesson_teaching(
        state
    )

    return None
