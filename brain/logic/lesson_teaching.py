# ==========================================
# NELE – AKTIVES UNTERRICHTEN EINER LEKTION
# STUDENT MEMORY 2.0
# DAILY LEARNING MEMORY
# ==========================================

from brain.logic.matcher import normalize

from brain.memory.lesson_progress import (
    mark_section_completed,
    get_next_incomplete_section,
    is_lesson_fully_completed
)

from brain.memory.lesson_review import (
    schedule_lesson_review
)

from brain.memory.daily_learning import (
    mark_lesson_section_today,
    mark_daily_plan_completed
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
# DAILY LEARNING MEMORY:
# ABSCHLUSS EINER LEKTIONSEKTION
# ==========================================

def remember_daily_lesson_section_completion(
    state,
    level,
    lesson,
    section
):

    if state is None:
        return


    if not (
        level
        and
        lesson
        and
        section
    ):

        return


    try:

        mark_lesson_section_today(
            state,
            level,
            lesson,
            section
        )

    except Exception as error:

        print(
            f"Daily lesson section memory error: {error}"
        )


# ==========================================
# SESSION COACH:
# TAGESPLAN NACH LEKTIONSABSCHLUSS
# ==========================================

def complete_session_coach_daily_plan(
    state
):

    if state is None:
        return


    flow = state.get(
        "session_start_flow"
    )


    if not isinstance(
        flow,
        dict
    ):

        return


    # ======================================
    # NUR DANN ABSCHLIESSEN,
    # WENN SESSION COACH AUF DEN
    # ABSCHLUSS DES NEUEN LERNSTOFFS WARTET
    # ======================================

    if not flow.get(
        "waiting_for_new_learning_completion",
        False
    ):

        return


    try:

        mark_daily_plan_completed(
            state
        )

    except Exception as error:

        print(
            f"Daily plan completion error: {error}"
        )

        return


    flow[
        "waiting_for_new_learning_completion"
    ] = False


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

        # ==================================
        # AKTUELLE SEKTION ABSCHLIESSEN
        # ==================================

        mark_section_completed(
            state,
            level,
            lesson,
            section
        )


        # ==================================
        # DAILY LEARNING MEMORY
        #
        # MERKEN:
        # DIESE SEKTION WURDE HEUTE
        # TATSÄCHLICH ABGESCHLOSSEN.
        # ==================================

        remember_daily_lesson_section_completion(
            state,
            level,
            lesson,
            section
        )


        # ==================================
        # SESSION COACH
        #
        # WENN DIES DIE GEPLANTE
        # LERNAKTIVITÄT WAR,
        # IST DER TAGESPLAN JETZT FERTIG.
        # ==================================

        complete_session_coach_daily_plan(
            state
        )


        # ==================================
        # NÄCHSTE SEKTION
        # ==================================

        next_section = (
            get_next_incomplete_section(
                state,
                level,
                lesson
            )
        )


        # ==================================
        # GANZE LEKTION ABGESCHLOSSEN
        #
        # Erste Wiederholung:
        # nach 1 Tag.
        # ==================================

        if is_lesson_fully_completed(
            state,
            level,
            lesson
        ):

            try:

                schedule_lesson_review(
                    state,
                    level,
                    lesson
                )

            except Exception as error:

                print(
                    f"Lesson review scheduling error: {error}"
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


    # ======================================
    # TEIL:
    # DAS DEUTSCHE ALPHABET
    # ======================================

    if normalize(
        section
    ) == normalize(
        "Das deutsche Alphabet"
    ):

        state[
            "lesson_teaching_active"
        ] = True

        state[
            "lesson_teaching_section"
        ] = "Das deutsche Alphabet"

        state[
            "lesson_teaching_step"
        ] = 1


        state[
            "last_activity"
        ] = "lesson"

        state[
            "last_activity_detail"
        ] = "Das deutsche Alphabet"


        return (
            "Super, dann machen wir eine kurze "
            "Übung zum deutschen Alphabet. "
            "Welcher Buchstabe kommt nach A?"
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


    finish_lesson_teaching(
        state
    )

    return None


# ==========================================
# ALPHABET:
# EINZELNER BUCHSTABE
# ==========================================

def is_letter_answer(
    user_message,
    expected_letter
):

    message = clean_normalized_answer(
        user_message
    )

    expected = normalize(
        expected_letter
    )


    accepted = {
        expected,
        f"buchstabe {expected}",
        f"der buchstabe {expected}",
        f"es ist {expected}"
    }


    return message in accepted


# ==========================================
# ALPHABET:
# UMLAUTE
# ==========================================

def is_umlaut_answer(
    user_message
):

    message = str(
        user_message or ""
    ).lower()


    if (
        "ä" in message
        and
        "ö" in message
        and
        "ü" in message
    ):

        return True


    normalized = normalize(
        message
    )


    has_a = (
        "a umlaut" in normalized
        or
        "ae" in normalized
    )

    has_o = (
        "o umlaut" in normalized
        or
        "oe" in normalized
    )

    has_u = (
        "u umlaut" in normalized
        or
        "ue" in normalized
    )


    return (
        has_a
        and
        has_o
        and
        has_u
    )


# ==========================================
# ALPHABET:
# ESZETT
# ==========================================

def is_eszett_answer(
    user_message
):

    message = str(
        user_message or ""
    ).lower().strip(
        " .?!„“\"'"
    )


    if "ß" in message:
        return True


    normalized = normalize(
        message
    )


    return normalized in {
        "eszett",
        "es zett",
        "scharfes s",
        "das eszett",
        "das scharfe s"
    }


# ==========================================
# TEIL:
# DAS DEUTSCHE ALPHABET
# ==========================================

def handle_alphabet_section(
    user_message,
    state
):

    step = state.get(
        "lesson_teaching_step",
        1
    )


    # ======================================
    # SCHRITT 1
    # NACH A -> B
    # ======================================

    if step == 1:

        if not is_letter_answer(
            user_message,
            "B"
        ):

            return (
                "Fast. Nach A kommt B. "
                "Sag bitte: „B“."
            )


        state[
            "lesson_teaching_step"
        ] = 2


        return (
            "Richtig! Nach A kommt B. "
            "Welcher Buchstabe kommt nach M?"
        )


    # ======================================
    # SCHRITT 2
    # NACH M -> N
    # ======================================

    if step == 2:

        if not is_letter_answer(
            user_message,
            "N"
        ):

            return (
                "Fast. Nach M kommt N. "
                "Sag bitte: „N“."
            )


        state[
            "lesson_teaching_step"
        ] = 3


        return (
            "Sehr gut! Nach M kommt N. "
            "Welcher Buchstabe kommt vor Z?"
        )


    # ======================================
    # SCHRITT 3
    # VOR Z -> Y
    # ======================================

    if step == 3:

        if not is_letter_answer(
            user_message,
            "Y"
        ):

            return (
                "Fast. Vor Z kommt Y. "
                "Sag bitte: „Y“."
            )


        state[
            "lesson_teaching_step"
        ] = 4


        return (
            "Genau! Vor Z kommt Y. "
            "Im Deutschen gibt es auch drei Umlaute. "
            "Welche sind das?"
        )


    # ======================================
    # SCHRITT 4
    # Ä Ö Ü
    # ======================================

    if step == 4:

        if not is_umlaut_answer(
            user_message
        ):

            return (
                "Fast. Die drei Umlaute sind "
                "Ä, Ö und Ü. "
                "Sag sie bitte noch einmal."
            )


        state[
            "lesson_teaching_step"
        ] = 5


        return (
            "Perfekt! Ä, Ö und Ü sind die drei Umlaute. "
            "Und welches besondere Zeichen "
            "gibt es außerdem im Deutschen?"
        )


    # ======================================
    # SCHRITT 5
    # ß
    # ======================================

    if step == 5:

        if not is_eszett_answer(
            user_message
        ):

            return (
                "Fast. Das besondere Zeichen ist ß. "
                "Man nennt es „Eszett“ oder "
                "„scharfes S“. "
                "Sag bitte: „Eszett“."
            )


        next_section = complete_active_section(
            state
        )


        if next_section:

            return (
                "Sehr gut! Du kennst jetzt wichtige "
                "Grundlagen des deutschen Alphabets. "
                f"Als Nächstes kommt "
                f"„{next_section}“."
            )


        return (
            "Sehr gut! Du kennst jetzt wichtige "
            "Grundlagen des deutschen Alphabets. "
            "Damit hast du A1, Lektion 1 abgeschlossen. "
            "Die erste Wiederholung ist für morgen geplant."
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
    # DAS DEUTSCHE ALPHABET
    # ======================================

    if normalize(
        section
    ) == normalize(
        "Das deutsche Alphabet"
    ):

        return handle_alphabet_section(
            user_message,
            state
        )


    finish_lesson_teaching(
        state
    )

    return None
