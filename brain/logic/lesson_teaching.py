# ==========================================
# NELE – AKTIVES UNTERRICHTEN EINER LEKTION
# ==========================================

from brain.logic.matcher import normalize


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
            message[len(start):].strip()
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
            "Genau! So klingt das ganz natürlich. "
            "Und jetzt andersherum: "
            "Wie fragst du jemanden nach dem Namen?"
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
                "Fast. Unter Freunden oder "
                "wenn ihr euch duzt, sagst du: "
                "„Wie heißt du?“ "
                "Versuch es noch einmal."
            )


        state[
            "lesson_teaching_step"
        ] = 3


        return (
            "Perfekt! „Wie heißt du?“ "
            "ist ganz normal im Alltag. "
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


        finish_lesson_teaching(
            state
        )


        return (
            "Sehr gut! Jetzt kannst du dich "
            "vorstellen und sowohl informell "
            "als auch höflich nach dem Namen fragen."
        )


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
