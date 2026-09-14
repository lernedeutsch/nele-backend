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
# NORMALISIERTE ANTWORT
# ==========================================

def clean_normalized_answer(
    text
):

    return normalize(
        clean_answer(
            text
        )
    ).strip()


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
    # 1. AKTUELLE SEKTION
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
# AKTUELLE SEKTION ABSCHLIESSEN
# ==========================================

def complete_active_section(
    state
):

    if state is None:
        return None


    section = state.get(
        "lesson_teaching_section"
    )


    if not section:
        return None


    level, lesson = (
        get_lesson_context_for_section(
            state,
            section
        )
    )


    next_section = None


    if (
        level
        and
        lesson
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


    finish_lesson_teaching(
        state
    )


    return next_section


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
    # WIR BEGRÜSSEN UNS
    # ======================================

    if normalize(
        section
    ) == normalize(
        "Wir begrüßen uns"
    ):

        state[
            "lesson_teaching_active"
        ] = True

        state[
            "lesson_teaching_section"
        ] = "Wir begrüßen uns"

        state[
            "lesson_teaching_step"
        ] = 1


        state[
            "last_activity"
        ] = "lesson"

        state[
            "last_activity_detail"
        ] = "Wir begrüßen uns"


        return (
            "Super, dann legen wir los! "
            "Wir üben jetzt Begrüßungen. "
            "Stell dir vor, es ist morgens. "
            "Was sagst du?"
        )


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
# BEGRÜSSUNG:
# GUTEN MORGEN
# ==========================================

def is_morning_greeting(
    user_message
):

    message = clean_normalized_answer(
        user_message
    )


    return message in {
        "guten morgen",
        "morgen"
    }


# ==========================================
# BEGRÜSSUNG:
# GUTEN TAG
# ==========================================

def is_day_greeting(
    user_message
):

    message = clean_normalized_answer(
        user_message
    )


    return message in {
        "guten tag",
        "tag"
    }


# ==========================================
# BEGRÜSSUNG:
# GUTEN ABEND
# ==========================================

def is_evening_greeting(
    user_message
):

    message = clean_normalized_answer(
        user_message
    )


    return message in {
        "guten abend",
        "abend"
    }


# ==========================================
# INFORMELLE BEGRÜSSUNG
# ==========================================

def is_informal_greeting(
    user_message
):

    message = clean_normalized_answer(
        user_message
    )


    return message in {
        "hallo",
        "hi",
        "hey"
    }


# ==========================================
# INFORMELLE VERABSCHIEDUNG
# ==========================================

def is_informal_goodbye(
    user_message
):

    message = clean_normalized_answer(
        user_message
    )


    return message in {
        "tschüss",
        "tschuss",
        "tschüs",
        "bis bald",
        "bis später"
    }


# ==========================================
# TEIL:
# WIR BEGRÜSSEN UNS
# ==========================================

def handle_greeting_section(
    user_message,
    state
):

    step = state.get(
        "lesson_teaching_step",
        1
    )


    # ======================================
    # SCHRITT 1
    # MORGEN
    # ======================================

    if step == 1:

        if not is_morning_greeting(
            user_message
        ):

            return (
                "Fast. Am Morgen sagt man: "
                "„Guten Morgen.“ "
                "Sag es bitte noch einmal."
            )


        state[
            "lesson_teaching_step"
        ] = 2


        return (
            "Sehr gut! „Guten Morgen“ ist richtig. "
            "Jetzt ist es tagsüber. "
            "Was sagst du?"
        )


    # ======================================
    # SCHRITT 2
    # TAG
    # ======================================

    if step == 2:

        if not is_day_greeting(
            user_message
        ):

            return (
                "Fast. Tagsüber kannst du sagen: "
                "„Guten Tag.“ "
                "Versuch es noch einmal."
            )


        state[
            "lesson_teaching_step"
        ] = 3


        return (
            "Genau! „Guten Tag“ ist richtig. "
            "Jetzt ist es Abend. "
            "Was sagst du?"
        )


    # ======================================
    # SCHRITT 3
    # ABEND
    # ======================================

    if step == 3:

        if not is_evening_greeting(
            user_message
        ):

            return (
                "Fast. Am Abend sagt man: "
                "„Guten Abend.“ "
                "Sag es bitte noch einmal."
            )


        state[
            "lesson_teaching_step"
        ] = 4


        return (
            "Perfekt! „Guten Abend“ ist richtig. "
            "Und wenn du jemanden ganz locker "
            "begrüßt, was kannst du sagen?"
        )


    # ======================================
    # SCHRITT 4
    # HALLO
    # ======================================

    if step == 4:

        if not is_informal_greeting(
            user_message
        ):

            return (
                "Fast. Ganz einfach kannst du sagen: "
                "„Hallo.“ "
                "Versuch es noch einmal."
            )


        state[
            "lesson_teaching_step"
        ] = 5


        return (
            "Sehr gut! „Hallo“ passt perfekt. "
            "Und jetzt verabschiedest du dich "
            "von einem Freund. "
            "Was sagst du?"
        )


    # ======================================
    # SCHRITT 5
    # TSCHÜSS
    # ======================================

    if step == 5:

        if not is_informal_goodbye(
            user_message
        ):

            return (
                "Fast. Zu einem Freund kannst du "
                "zum Beispiel sagen: "
                "„Tschüss.“ "
                "Sag es bitte noch einmal."
            )


        # ==================================
        # TEIL ABSCHLIESSEN
        # ==================================

        next_section = complete_active_section(
            state
        )


        if next_section:

            return (
                "Sehr gut! Jetzt kennst du wichtige "
                "Begrüßungen und kannst dich auch "
                "verabschieden. "
                f"Als Nächstes kommt "
                f"„{next_section}“."
            )


        return (
            "Sehr gut! Jetzt kennst du wichtige "
            "Begrüßungen und kannst dich auch "
            "verabschieden. "
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
        # TEIL ABSCHLIESSEN
        # ==================================

        next_section = complete_active_section(
            state
        )


        if next_section:

            return (
                "Sehr gut! Jetzt kannst du dich "
                "vorstellen und sowohl informell "
                "als auch höflich nach dem Namen fragen. "
                f"Als Nächstes kommt "
                f"„{next_section}“."
            )


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


    # ======================================
    # WIR BEGRÜSSEN UNS
    # ======================================

    if normalize(
        section
    ) == normalize(
        "Wir begrüßen uns"
    ):

        return handle_greeting_section(
            user_message,
            state
        )


    # ======================================
    # ICH STELLE MICH VOR
    # ======================================

    if normalize(
        section
    ) == normalize(
        "Ich stelle mich vor"
    ):

        return handle_introduction_section(
            user_message,
            state
        )


    # ======================================
    # NIEZNANA SEKCJA
    # ======================================

    finish_lesson_teaching(
        state
    )

    return None
