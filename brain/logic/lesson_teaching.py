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


from brain.logic.generic_lesson_engine import (
    start_generic_lesson_teaching,
    handle_generic_lesson_teaching,
    get_generic_current_prompt,
    is_generic_lesson_active
)

from brain.logic.personal_sentences import handle_personal_sentence_practice
from brain.logic.dialogue_engine import handle_dialogue, is_dialogue_active

from brain.logic.speaking_support import (
    legacy_course_support,
    handle_pending_course_model,
    progressive_course_support,
    register_course_success,
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

def get_lesson_mistake_context(
    state
):

    if state is None:
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

    except (
        TypeError,
        ValueError
    ):

        step = 1


    normalized_section = normalize(
        section
    )


    contexts = {
        normalize(
            "Wir begrüßen uns"
        ): {
            1:
                (
                    "Es ist Morgen. "
                    "Was sagst du zur Begrüßung?"
                ),
            2:
                (
                    "Es ist Tag. "
                    "Was sagst du zur Begrüßung?"
                ),
            3:
                (
                    "Es ist Abend. "
                    "Was sagst du zur Begrüßung?"
                ),
            4:
                (
                    "Du sprichst mit einem Freund. "
                    "Was sagst du?"
                ),
            5:
                (
                    "Du gehst. "
                    "Was sagst du?"
                ),
            6:
                (
                    "Du kommst morgens zur Arbeit. "
                    "Jemand sagt: „Guten Morgen!“. "
                    "Was antwortest du?"
                )
        },

        normalize(
            "Ich stelle mich vor"
        ): {
            1:
                (
                    "Wir treffen uns morgens zum ersten Mal. "
                    "Ich sage: „Guten Morgen!“. "
                    "Was antwortest du?"
                ),
            2:
                (
                    "Ich sage: „Ich heiße Nele. Wie heißt du?“. "
                    "Wie stellst du dich vor?"
                ),
            3:
                (
                    "Du möchtest mich nach meinem Namen fragen. "
                    "Wie fragst du informell?"
                ),
            4:
                (
                    "Du sollst deinen Namen buchstabieren. "
                    "Wie sagst du ihn Buchstabe für Buchstabe?"
                ),
            5:
                (
                    "Du bist in einer höflichen Situation im Hotel. "
                    "Wie fragst du einen Gast nach dem Namen?"
                )
        },

        normalize(
            "Das deutsche Alphabet"
        ): {
            1:
                "Hör zu: A. Sag: A.",
            2:
                "Sehr gut. Jetzt B. Sag: B.",
            3:
                "Wie heißt dieser Buchstabe: M?",
            4:
                "Welche drei Umlaute gibt es im Deutschen?",
            5:
                (
                    "Welches besondere Zeichen gibt es "
                    "außerdem im Deutschen?"
                ),
            6:
                "Buchstabiere bitte deinen Namen."
        }
    }


    section_contexts = contexts.get(
        normalized_section,
        {}
    )


    return str(
        section_contexts.get(
            step,
            ""
        )
        or
        ""
    ).strip()


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
            correct_text,
            context=get_lesson_mistake_context(
                state
            )
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
        "Super! Lektion 1 ist fertig. "
        "Beim nächsten Mal wiederholen wir sie kurz."
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
    # NOWY WSPÓLNY SILNIK LEKCJI
    #
    # Najpierw próbujemy LESSON_FLOW z pliku
    # konkretnej lekcji. Dzięki temu nowa
    # Lektion 2/3 może nawet mieć nazwę
    # sekcji podobną do Lektion 1 i nie
    # wpadnie do starego hard-coded flow.
    # ======================================

    generic_answer = start_generic_lesson_teaching(
        section,
        state
    )

    if generic_answer:
        return generic_answer


    # ======================================
    # LEGACY: A1 LEKTION 1
    # ======================================


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
            "Los geht’s! "
            "Es ist Morgen. "
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
            "Jetzt stellen wir uns vor. "
            "Guten Morgen!"
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
            "Wir üben jetzt das Alphabet. "
            "Hör zu: A. Sag: A."
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


    if is_generic_lesson_active(
        state
    ):

        generic_prompt = get_generic_current_prompt(
            state
        )

        if generic_prompt:
            return generic_prompt

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
                "Es ist Morgen. "
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
                "Du gehst. "
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
                "Buchstabiere bitte deinen Namen."
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
                "Hör zu: A. Sag: A."
            ),
            2: (
                "Wir machen genau dort weiter. "
                "Sehr gut. Jetzt B. Sag: B."
            ),
            3: (
                "Wir machen genau dort weiter. "
                "Wie heißt dieser Buchstabe: M?"
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


    return message == "guten morgen"


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


    return message == "guten tag"


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


    return message == "guten abend"


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
# CZY BŁĘDNA ODPOWIEDŹ JEST ZWIĄZANA
# Z ĆWICZONYM POWITANIEM?
# ==========================================

def is_relevant_greeting_mistake(
    user_message
):

    message = clean_normalized_answer(
        user_message
    )

    if not message:
        return False

    greeting_words = {
        "guten",
        "morgen",
        "tag",
        "abend",
        "hallo",
        "hi",
        "hey",
        "tschüss",
        "tschuss",
        "tschüs",
        "wiedersehen",
    }

    tokens = set(
        message.split()
    )


    if (
        tokens
        &
        greeting_words
    ):

        return True


    # W aktywnym ćwiczeniu uczeń może odpowiedzieć bardzo
    # krótko, np. "h", "k", "p". To nadal jest realna
    # błędna próba na konkretne pytanie i powinna trafić
    # do Fehlertraining. Dłuższych, niezwiązanych zdań
    # nadal nie zapisujemy jako błędu powitania.
    words = message.split()

    return bool(
        1 <= len(words) <= 2
        and
        len(message) <= 12
    )


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

            if is_relevant_greeting_mistake(
                user_message
            ):

                remember_lesson_mistake(
                    state,
                    "vocabulary",
                    user_message,
                    "Guten Morgen"
                )

            return progressive_course_support(
                "Guten Morgen", state,
                first_hint="Denk an die Begrüßung am Morgen.",
                prefix="Fast. ",
            )


        register_course_success(state)

        state[
            "lesson_teaching_step"
        ] = 2


        return (
            "Richtig! Es ist Tag. Was sagst du?"
        )


    # ======================================
    # SCHRITT 2
    # TAG
    # ======================================

    if step == 2:

        if not is_day_greeting(
            user_message
        ):

            if is_relevant_greeting_mistake(
                user_message
            ):

                remember_lesson_mistake(
                    state,
                    "vocabulary",
                    user_message,
                    "Guten Tag"
                )

            return progressive_course_support(
                "Guten Tag", state,
                first_hint="Denk an die Begrüßung am Tag.",
                prefix="Fast. ",
            )


        register_course_success(state)

        state[
            "lesson_teaching_step"
        ] = 3


        return (
            "Sehr gut! Es ist Abend. Was sagst du?"
        )


    # ======================================
    # SCHRITT 3
    # ABEND
    # ======================================

    if step == 3:

        if not is_evening_greeting(
            user_message
        ):

            if is_relevant_greeting_mistake(
                user_message
            ):

                remember_lesson_mistake(
                    state,
                    "vocabulary",
                    user_message,
                    "Guten Abend"
                )

            return progressive_course_support(
                "Guten Abend", state,
                first_hint="Denk an die Begrüßung am Abend.",
                prefix="Fast. ",
            )


        register_course_success(state)

        state[
            "lesson_teaching_step"
        ] = 4


        return (
            "Sehr gut! Und zu einem Freund?"
        )


    # ======================================
    # SCHRITT 4
    # HALLO
    # ======================================

    if step == 4:

        if not is_informal_greeting(
            user_message
        ):

            if is_relevant_greeting_mistake(
                user_message
            ):

                remember_lesson_mistake(
                    state,
                    "vocabulary",
                    user_message,
                    "Hallo"
                )

            return progressive_course_support(
                "Hallo", state,
                first_hint="Wie begrüßt du einen Freund?",
                prefix="Fast. ",
            )


        register_course_success(state)

        state[
            "lesson_teaching_step"
        ] = 5


        spoken_greeting = clean_answer(
            user_message
        )

        if not spoken_greeting:
            spoken_greeting = "Hallo"

        else:

            spoken_greeting = (
                spoken_greeting[:1].upper()
                + spoken_greeting[1:]
            )


        return (
            "Genau! Du gehst. Was sagst du?"
        )


    # ======================================
    # SCHRITT 5
    # TSCHÜSS
    # ======================================

    if step == 5:

        if not is_informal_goodbye(
            user_message
        ):

            if is_relevant_greeting_mistake(
                user_message
            ):

                remember_lesson_mistake(
                    state,
                    "vocabulary",
                    user_message,
                    "Tschüss"
                )

            return progressive_course_support(
                "Tschüss", state,
                first_hint="Was sagst du zu einem Freund beim Gehen?",
                prefix="Fast. ",
            )


        register_course_success(state)

        state[
            "lesson_teaching_step"
        ] = 6


        return (
            "Sehr gut! Ich sage: „Guten Morgen!“ Was sagst du?"
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

            return progressive_course_support(
                "Guten Morgen", state,
                first_hint="Wir treffen uns morgens. Wie begrüßt du mich?",
                prefix="Fast. ",
            )


        register_course_success(state)

        next_section = complete_active_section(
            state
        )


        if next_section:

            return (
                f"Sehr gut! Jetzt: „{next_section}“. "
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

            return progressive_course_support(
                "Guten Morgen",
                state,
                first_hint="Wir treffen uns morgens. Wie begrüßt du mich?",
            )


        register_course_success(state)

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

            support = legacy_course_support(
                user_message,
                f"Ich heiße {name}.",
                state,
                context="name",
            )
            if support:
                return support

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


        register_course_success(state)

        state[
            "lesson_teaching_step"
        ] = 3


        name = get_student_name(
            state
        )

        if name:

            return (
                "Sehr gut! Frag mich: „Wie heißt du?“"
            )


        return (
            "Sehr gut! Frag mich: „Wie heißt du?“"
        )


    # ======================================
    # SCHRITT 3
    # WIE HEISST DU?
    # ======================================

    if step == 3:

        if not is_informal_name_question(
            user_message
        ):

            semantic_attempt = normalize(user_message).strip(" .?!„“\"'") in {
                "wer bist du",
                "wer sind sie",
            }
            support = legacy_course_support(
                user_message,
                "Wie heißt du?",
                state,
                context="question",
                semantic_attempt=semantic_attempt,
            )
            if support:
                return support

            remember_lesson_mistake(
                state,
                "grammar",
                user_message,
                "Wie heißt du?"
            )

            return (
                "Fast. Richtig: „Wie heißt du?“ "
                "Sag es bitte noch einmal."
            )


        register_course_success(state)

        state[
            "lesson_teaching_step"
        ] = 4


        return (
            "Ich heiße Nele. "
            "Buchstabiere bitte deinen Namen."
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
                return progressive_course_support(
                    hint,
                    state,
                    first_hint="Sag deinen Namen Buchstabe für Buchstabe.",
                    prefix="Fast. ",
                )

            return (
                "Buchstabiere deinen Namen bitte "
                "Buchstabe für Buchstabe."
            )


        register_course_success(state)

        state[
            "lesson_teaching_step"
        ] = 5


        return (
            "Jetzt höflich. Du sprichst mit einem Gast. "
            "Frag nach dem Namen."
        )


    # ======================================
    # SCHRITT 5
    # WIE HEISSEN SIE?
    # ======================================

    if step == 5:

        if not is_formal_name_question(
            user_message
        ):

            support = legacy_course_support(
                user_message,
                "Wie heißen Sie?",
                state,
                context="question",
            )
            if support:
                return support

            remember_lesson_mistake(
                state,
                "grammar",
                user_message,
                "Wie heißen Sie?"
            )

            return (
                "Fast. Richtig: „Wie heißen Sie?“ "
                "Sag es bitte noch einmal."
            )


        register_course_success(state)

        next_section = complete_active_section(
            state
        )


        if next_section:

            return (
                f"Sehr gut! Jetzt: „{next_section}“. "
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

    if step == 1:

        if not is_letter_answer(
            user_message,
            "A"
        ):

            remember_lesson_mistake(
                state,
                "spelling",
                user_message,
                "A"
            )

            return (
                "Hör zu: A. Sag bitte: „A“."
            )

        register_course_success(state)

        state["lesson_teaching_step"] = 2

        return (
            "Sehr gut. Jetzt B. Sag: B."
        )

    if step == 2:

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
                "Hör zu: B. Sag bitte: „B“."
            )

        register_course_success(state)

        state["lesson_teaching_step"] = 3

        return (
            "Sehr gut. Wie heißt dieser Buchstabe: M?"
        )

    if step == 3:

        if not is_letter_answer(
            user_message,
            "M"
        ):

            remember_lesson_mistake(
                state,
                "spelling",
                user_message,
                "M"
            )

            return (
                "Das ist M. Sag bitte: „M“."
            )

        register_course_success(state)

        state["lesson_teaching_step"] = 4

        return (
            "Genau! Welche drei Umlaute gibt es?"
        )

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

        register_course_success(state)

        state["lesson_teaching_step"] = 5

        return (
            "Sehr gut! Wie heißt dieses Zeichen: ß?"
        )

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
                "Das ist ß. Es heißt „Eszett“. "
                "Sag bitte: „Eszett“."
            )

        register_course_success(state)

        state["lesson_teaching_step"] = 6

        return (
            "Genau. Buchstabiere bitte deinen Namen."
        )

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
                return progressive_course_support(
                    hint,
                    state,
                    first_hint="Sag deinen Namen Buchstabe für Buchstabe.",
                    prefix="Fast. ",
                )

            return (
                "Sag deinen Namen bitte "
                "Buchstabe für Buchstabe."
            )

        register_course_success(state)

        next_section = complete_active_section(
            state
        )

        if next_section:

            return (
                "Sehr gut! "
                f"Als Nächstes kommt „{next_section}“."
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

    # A started dialogue owns the conversation until it is completed.
    # Never let an incidental/stale Meine Sätze drill interrupt a lesson dialogue.
    if is_dialogue_active(state):
        state.pop("personal_sentence_practice", None)
        dialogue_reply = handle_dialogue(user_message, state)
        if dialogue_reply is not None:
            return dialogue_reply

    # Meine Sätze may run only when no lesson dialogue currently owns the turn.
    personal_practice = handle_personal_sentence_practice(user_message, state)
    if personal_practice:
        return personal_practice.get("reply")


    if not is_lesson_teaching_active(
        state
    ):

        return None


    # Global speaking-support contract for legacy A1 sections too.
    # A pending model must be resolved before the lesson step can advance.
    if not is_generic_lesson_active(
        state
    ):
        pending_before = state.get("course_pending_speaking_model")
        if pending_before:
            pending_reply = handle_pending_course_model(
                user_message,
                state
            )
            if pending_reply is not None:
                return pending_reply
            # The learner produced the requested model. Continue processing
            # the same utterance in the active legacy step exactly once.


    if is_generic_lesson_active(
        state
    ):

        generic_answer = handle_generic_lesson_teaching(
            user_message,
            state
        )

        if generic_answer is not None:
            return generic_answer


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
