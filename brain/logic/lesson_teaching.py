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
    mark_daily_plan_completed,
    record_mistake_today
)

from brain.memory.error_memory import (
    remember_error
)


from brain.memory.user_facts import (
    get_user_fact
)

from brain.nele3_upgrade.teacher_brain import (
    build_adaptive_recommendation
)

from brain.nele3_upgrade.state import (
    set_pending_recommendation
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
# FEHLER AUS LEKTIONEN MERKEN
# ==========================================

def remember_lesson_mistake(
    state,
    error_type,
    wrong_text,
    correct_text
):

    if state is None:
        return False

    wrong_text = str(
        wrong_text or ""
    ).strip()

    correct_text = str(
        correct_text or ""
    ).strip()

    if not (
        error_type
        and
        wrong_text
        and
        correct_text
    ):
        return False


    try:

        saved = remember_error(
            state,
            error_type,
            wrong_text,
            correct_text
        )

    except Exception as error:

        print(
            f"Lesson error memory error: {error}"
        )

        saved = False


    try:

        record_mistake_today(
            state,
            error_type,
            wrong=wrong_text,
            correct=correct_text
        )

    except Exception as error:

        print(
            f"Daily lesson mistake error: {error}"
        )


    return saved


# ==========================================
# NAME DES LERNENDEN
# ==========================================

def get_student_name(
    state
):

    if state is None:
        return ""

    name = get_user_fact(
        state,
        "name"
    )

    if not name:
        name = state.get(
            "name"
        )

    return str(
        name or ""
    ).strip()


# ==========================================
# NAME BUCHSTABIERT?
# ==========================================

def is_student_name_spelled(
    user_message,
    state
):

    name = get_student_name(
        state
    )

    if not name:
        return False

    target = "".join(
        char.lower()
        for char in name
        if char.isalnum()
    )

    raw = str(
        user_message or ""
    ).strip()

    compact = "".join(
        char.lower()
        for char in raw
        if char.isalnum()
    )

    if compact != target:
        return False

    # "Moni" allein ist noch kein Buchstabieren.
    # Akzeptiert werden z.B.:
    # M O N I / M-O-N-I / M, O, N, I
    separators = sum(
        1
        for char in raw
        if char in " -,_./"
    )

    return separators >= max(
        1,
        len(target) - 1
    )


# ==========================================
# HILFE ZUM BUCHSTABIEREN
# ==========================================

def get_spelled_name_hint(
    state
):

    name = get_student_name(
        state
    )

    if not name:
        return ""

    letters = [
        char.upper()
        for char in name
        if char.isalnum()
    ]

    return " – ".join(
        letters
    )


# ==========================================
# LEKTIONSENDE + ADAPTIVE EMPFEHLUNG
# ==========================================

def create_lesson_completion_answer(
    state
):

    base = (
        "Sehr gut! Du kennst jetzt wichtige "
        "Grundlagen aus A1, Lektion 1. "
        "Damit hast du die Lektion abgeschlossen. "
        "Die erste Wiederholung ist für morgen geplant."
    )

    try:

        recommendation = (
            build_adaptive_recommendation(
                state
            )
        )

    except Exception as error:

        print(
            f"Adaptive lesson completion error: {error}"
        )

        recommendation = None


    if isinstance(
        recommendation,
        dict
    ):

        set_pending_recommendation(
            state,
            recommendation
        )

        message = str(
            recommendation.get(
                "message",
                ""
            )
            or
            ""
        ).strip()

        if message:

            return (
                f"{base} "
                f"{message}"
            )


    return base


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
        # NÄCHSTE SEKTION ZUM FORTSETZEN
        #
        # Wenn Nele sagt "Als Nächstes kommt ..."
        # und der Nutzer danach "Ja" sagt,
        # muss dieses "Ja" eindeutig zur nächsten
        # Lektionssektion gehören.
        # ==================================

        if next_section:

            state[
                "pending_new_learning"
            ] = {
                "type": "new_section",
                "level": level,
                "lesson": lesson,
                "section": next_section,
                "topic": next_section
            }

            state[
                "last_question"
            ] = "continue_new_learning"


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
            "Jetzt machen wir einen kurzen Mini-Dialog. "
            "Stell dir vor, wir treffen uns morgens "
            "zum ersten Mal. Guten Morgen!"
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
# AKTUELLE LEKTION GENAU FORTSETZEN
# ==========================================

def get_current_lesson_prompt(
    state
):

    if state is None:
        return ""

    if not state.get(
        "lesson_teaching_active",
        False
    ):
        return ""

    section = str(
        state.get(
            "lesson_teaching_section"
        )
        or
        ""
    ).strip()

    try:
        step = int(
            state.get(
                "lesson_teaching_step",
                1
            )
            or
            1
        )
    except (TypeError, ValueError):
        step = 1


    if normalize(section) == normalize(
        "Wir begrüßen uns"
    ):

        prompts = {
            1: (
                "Wir machen genau dort weiter. "
                "Stell dir vor, es ist morgens. "
                "Was sagst du?"
            ),
            2: (
                "Wir machen genau dort weiter. "
                "Jetzt ist es tagsüber. "
                "Was sagst du?"
            ),
            3: (
                "Wir machen genau dort weiter. "
                "Jetzt ist es Abend. "
                "Was sagst du?"
            ),
            4: (
                "Wir machen genau dort weiter. "
                "Wenn du jemanden ganz locker begrüßt, "
                "was kannst du sagen?"
            ),
            5: (
                "Wir machen genau dort weiter. "
                "Du verabschiedest dich von einem Freund. "
                "Was sagst du?"
            ),
            6: (
                "Wir machen mit dem Mini-Dialog weiter. "
                "Du kommst morgens zur Arbeit. "
                "Ich sage: „Guten Morgen!“ "
                "Was antwortest du?"
            ),
        }

        return prompts.get(
            step,
            prompts[1]
        )


    if normalize(section) == normalize(
        "Ich stelle mich vor"
    ):

        name = get_student_name(
            state
        ) or "Moni"

        prompts = {
            1: (
                "Wir machen mit dem Mini-Dialog weiter. "
                "Wir treffen uns morgens zum ersten Mal. "
                "Guten Morgen!"
            ),
            2: (
                "Guten Morgen! Ich heiße Nele. "
                "Wie heißt du?"
            ),
            3: (
                f"Freut mich, {name}! "
                "Wie fragst du mich nach meinem Namen?"
            ),
            4: (
                "Ich heiße Nele. "
                "Kannst du deinen Namen bitte buchstabieren?"
            ),
            5: (
                "Jetzt sind wir in einer höflichen Situation "
                "im Hotel. Wie fragst du einen Gast "
                "nach dem Namen?"
            ),
        }

        return prompts.get(
            step,
            prompts[1]
        )


    if normalize(section) == normalize(
        "Das deutsche Alphabet"
    ):

        prompts = {
            1: (
                "Wir machen genau dort weiter. "
                "Welcher Buchstabe kommt nach A?"
            ),
            2: (
                "Wir machen genau dort weiter. "
                "Welcher Buchstabe kommt nach M?"
            ),
            3: (
                "Wir machen genau dort weiter. "
                "Welcher Buchstabe kommt vor Z?"
            ),
            4: (
                "Wir machen genau dort weiter. "
                "Welche drei Umlaute gibt es im Deutschen?"
            ),
            5: (
                "Wir machen genau dort weiter. "
                "Welches besondere Zeichen gibt es "
                "außerdem im Deutschen?"
            ),
            6: (
                "Wir machen genau dort weiter. "
                "Buchstabiere bitte deinen Namen."
            ),
        }

        return prompts.get(
            step,
            prompts[1]
        )


    return ""


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

            remember_lesson_mistake(
                state,
                "vocabulary",
                user_message,
                "Guten Morgen"
            )

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

            remember_lesson_mistake(
                state,
                "vocabulary",
                user_message,
                "Guten Tag"
            )

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

            remember_lesson_mistake(
                state,
                "vocabulary",
                user_message,
                "Guten Abend"
            )

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

            remember_lesson_mistake(
                state,
                "vocabulary",
                user_message,
                "Hallo"
            )

            return (
                "Fast. Ganz einfach kannst du sagen: "
                "„Hallo.“ "
                "Versuch es noch einmal."
            )


        state[
            "lesson_teaching_step"
        ] = 5


        spoken_greeting = clean_answer(
            user_message
        )

        if not spoken_greeting:
            spoken_greeting = "Hallo"


        return (
            f"Sehr gut! „{spoken_greeting}“ passt perfekt. "
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

            remember_lesson_mistake(
                state,
                "vocabulary",
                user_message,
                "Tschüss"
            )

            return (
                "Fast. Zu einem Freund kannst du "
                "zum Beispiel sagen: "
                "„Tschüss.“ "
                "Sag es bitte noch einmal."
            )


        state[
            "lesson_teaching_step"
        ] = 6


        return (
            "Sehr gut. Jetzt noch ein kurzer Mini-Dialog. "
            "Du kommst morgens zur Arbeit. "
            "Ich sage: „Guten Morgen!“ "
            "Was antwortest du?"
        )


    # ======================================
    # SCHRITT 6
    # MINI-DIALOG
    # ======================================

    if step == 6:

        if not is_morning_greeting(
            user_message
        ):

            remember_lesson_mistake(
                state,
                "vocabulary",
                user_message,
                "Guten Morgen"
            )

            return (
                "Fast. Wir treffen uns morgens. "
                "Antworte einfach: „Guten Morgen.“"
            )


        next_section = complete_active_section(
            state
        )


        if next_section:

            return (
                "Perfekt. So klingt eine echte kurze "
                "Begrüßung im Alltag. "
                f"Als Nächstes kommt "
                f"„{next_section}“. "
                "Möchtest du weitermachen?"
            )


        return (
            "Perfekt. So klingt eine echte kurze "
            "Begrüßung im Alltag."
        )


    finish_lesson_teaching(
        state
    )

    return None


# ==========================================
# IMIĘ – POPRAWNA ODPOWIEDŹ
# ==========================================

def is_valid_name_answer(
    user_message,
    state=None
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


    spoken_name = ""


    for start in valid_starts:

        if not message.startswith(
            start
        ):
            continue

        spoken_name = message[
            len(start):
        ].strip()

        break


    if not spoken_name:
        return False


    expected_name = get_student_name(
        state
    )


    if not expected_name:
        return True


    expected_name = normalize(
        expected_name
    ).strip(
        " .?!„“\"'"
    )


    return spoken_name == expected_name


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
    # MINI-DIALOG: BEGRÜSSUNG
    # ======================================

    if step == 1:

        if not is_morning_greeting(
            user_message
        ):

            remember_lesson_mistake(
                state,
                "vocabulary",
                user_message,
                "Guten Morgen"
            )

            return (
                "Wir treffen uns morgens. "
                "Sag einfach: „Guten Morgen.“"
            )


        state[
            "lesson_teaching_step"
        ] = 2


        return (
            "Guten Morgen! Ich heiße Nele. "
            "Wie heißt du?"
        )


    # ======================================
    # SCHRITT 2
    # SICH VORSTELLEN
    # ======================================

    if step == 2:

        if not is_valid_name_answer(
            user_message,
            state
        ):

            name = get_student_name(
                state
            ) or "Moni"

            remember_lesson_mistake(
                state,
                "grammar",
                user_message,
                f"Ich heiße {name}."
            )

            return (
                "Fast! Sag es bitte als "
                "ganzen Satz, zum Beispiel: "
                f"„Ich heiße {name}.“"
            )


        state[
            "lesson_teaching_step"
        ] = 3


        name = get_student_name(
            state
        )

        if name:

            return (
                f"Freut mich, {name}! "
                "Und wie fragst du mich nach meinem Namen?"
            )


        return (
            "Freut mich! "
            "Und wie fragst du mich nach meinem Namen?"
        )


    # ======================================
    # SCHRITT 3
    # WIE HEISST DU?
    # ======================================

    if step == 3:

        if not is_informal_name_question(
            user_message
        ):

            remember_lesson_mistake(
                state,
                "grammar",
                user_message,
                "Wie heißt du?"
            )

            return (
                "Wenn wir uns duzen, fragst du: "
                "„Wie heißt du?“ "
                "Versuch es noch einmal."
            )


        state[
            "lesson_teaching_step"
        ] = 4


        return (
            "Ich heiße Nele. "
            "Kannst du deinen Namen bitte buchstabieren?"
        )


    # ======================================
    # SCHRITT 4
    # EIGENEN NAMEN BUCHSTABIEREN
    # ======================================

    if step == 4:

        if not is_student_name_spelled(
            user_message,
            state
        ):

            hint = get_spelled_name_hint(
                state
            )

            remember_lesson_mistake(
                state,
                "spelling",
                user_message,
                hint or "Name Buchstabe für Buchstabe"
            )

            if hint:

                return (
                    "Fast. Buchstabiere deinen Namen "
                    "Buchstabe für Buchstabe, zum Beispiel: "
                    f"„{hint}“"
                )


            return (
                "Buchstabiere deinen Namen bitte "
                "Buchstabe für Buchstabe."
            )


        state[
            "lesson_teaching_step"
        ] = 5


        return (
            "Sehr gut. Jetzt wechseln wir in eine "
            "höfliche Situation im Hotel. "
            "Wie fragst du einen Gast nach dem Namen?"
        )


    # ======================================
    # SCHRITT 5
    # WIE HEISSEN SIE?
    # ======================================

    if step == 5:

        if not is_formal_name_question(
            user_message
        ):

            remember_lesson_mistake(
                state,
                "grammar",
                user_message,
                "Wie heißen Sie?"
            )

            return (
                "Wenn du den Gast siezt, fragst du: "
                "„Wie heißen Sie?“ "
                "Versuch es noch einmal."
            )


        next_section = complete_active_section(
            state
        )


        if next_section:

            return (
                "Sehr gut! Du hast jetzt Begrüßung, "
                "Vorstellung, Namensfrage und "
                "Buchstabieren in einem kleinen Dialog benutzt. "
                f"Als Nächstes kommt "
                f"„{next_section}“. "
                "Möchtest du weitermachen?"
            )


        return (
            "Sehr gut! Das war ein kompletter "
            "kleiner Vorstellungsdialog."
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

            remember_lesson_mistake(
                state,
                "spelling",
                user_message,
                "B"
            )

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

            remember_lesson_mistake(
                state,
                "spelling",
                user_message,
                "N"
            )

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

            remember_lesson_mistake(
                state,
                "spelling",
                user_message,
                "Y"
            )

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

            remember_lesson_mistake(
                state,
                "spelling",
                user_message,
                "Ä, Ö und Ü"
            )

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

            remember_lesson_mistake(
                state,
                "spelling",
                user_message,
                "Eszett"
            )

            return (
                "Fast. Das besondere Zeichen ist ß. "
                "Man nennt es „Eszett“ oder "
                "„scharfes S“. "
                "Sag bitte: „Eszett“."
            )


        state[
            "lesson_teaching_step"
        ] = 6


        return (
            "Genau. Und jetzt wenden wir das Alphabet "
            "direkt an: Buchstabiere bitte deinen Namen."
        )


    # ======================================
    # SCHRITT 6
    # NAME BUCHSTABIEREN
    # ======================================

    if step == 6:

        if not is_student_name_spelled(
            user_message,
            state
        ):

            hint = get_spelled_name_hint(
                state
            )

            remember_lesson_mistake(
                state,
                "spelling",
                user_message,
                hint or "Name Buchstabe für Buchstabe"
            )

            if hint:

                return (
                    "Fast. Sag die Buchstaben einzeln, "
                    f"zum Beispiel: „{hint}“"
                )


            return (
                "Sag deinen Namen bitte "
                "Buchstabe für Buchstabe."
            )


        next_section = complete_active_section(
            state
        )


        if next_section:

            return (
                "Sehr gut! Du hast das Alphabet "
                "direkt praktisch benutzt. "
                f"Als Nächstes kommt "
                f"„{next_section}“."
            )


        return create_lesson_completion_answer(
            state
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
