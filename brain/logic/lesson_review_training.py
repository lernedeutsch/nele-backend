# ==========================================
# NELE – POWTÓRKA CAŁEJ LEKCJI
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.speaking_support import (
    consume_course_model_exhaustion,
    handle_pending_course_model,
    register_course_success as register_speaking_course_success,
)

from brain.logic.learning_progress_engine import update_learning_progress
from brain.logic.course_answer_evaluator import evaluate_course_answer
from brain.logic.course_teacher_engine import (
    choose_course_teacher_action,
    render_course_teacher_action,
)
from brain.logic.matcher import normalize
from brain.logic.onboarding import extract_name_sentence

from brain.memory.lesson_review import (
    mark_lesson_review_completed,
    mark_lesson_review_difficult
)

from brain.memory.daily_learning import (
    mark_lesson_reviewed_today,
    mark_exercise_completed_today
)

from brain.memory.error_memory import (
    remember_error,
)

from brain.memory.user_facts import (
    get_user_fact
)


# ==========================================
# DAILY LEARNING MEMORY
# ZAKOŃCZONA POWTÓRKA LEKCJI
# ==========================================

def remember_daily_lesson_review_completion(
    state,
    level,
    lesson,
    result
):

    if state is None:
        return


    # ======================================
    # LEKCJA POWTÓRZONA DZISIAJ
    # ======================================

    try:

        mark_lesson_reviewed_today(
            state,
            level,
            lesson,
            result=result
        )

    except Exception as error:

        print(
            f"Daily lesson review memory error: {error}"
        )


    # ======================================
    # LICZNIK UKOŃCZONYCH ĆWICZEŃ
    # ======================================

    try:

        mark_exercise_completed_today(
            state
        )

    except Exception as error:

        print(
            f"Daily lesson review counter error: {error}"
        )


# ==========================================
# CZYSZCZENIE ODPOWIEDZI
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


def clean_normalized_answer(
    text
):

    return normalize(
        clean_answer(
            text
        )
    ).strip()


# ==========================================
# CZY POWTÓRKA JEST AKTYWNA
# ==========================================

def is_lesson_review_training_active(
    state
):

    if state is None:
        return False

    return bool(
        state.get(
            "lesson_review_training_active",
            False
        )
    )


def get_current_lesson_review_prompt(state):
    """Return the exact prompt for an active purpose-built A1.1 review."""
    if not is_lesson_review_training_active(state):
        return None

    step = int(state.get("lesson_review_training_step") or 1)
    prompts = {
        1: "Wir wiederholen kurz. Was sagst du am Morgen?",
        2: "Was sagst du am Tag?",
        3: "Was sagst du am Abend?",
        4: "Du gehst jetzt. Was sagst du?",
        5: "Jetzt du: Wie stellst du dich vor?",
        6: "Wie fragst du einen Freund nach seinem Namen?",
        7: "Und wie fragst du höflich nach dem Namen?",
        8: "Welche drei Umlaute kennst du?",
        9: "Wie heißt dieses Zeichen: ß?",
    }
    return prompts.get(step)


# ==========================================
# ZAKOŃCZENIE TRYBU POWTÓRKI
# ==========================================

def finish_lesson_review_training(
    state
):

    if state is None:
        return


    state[
        "lesson_review_training_active"
    ] = False

    state[
        "lesson_review_training_level"
    ] = None

    state[
        "lesson_review_training_lesson"
    ] = None

    state[
        "lesson_review_training_step"
    ] = 0

    state[
        "lesson_review_training_correct"
    ] = 0

    state[
        "lesson_review_training_wrong"
    ] = 0


# ==========================================
# REVIEW -> SHARED COURSE MASTERY
# ==========================================

A1_LESSON_1_REVIEW_SECTIONS = {
    1: "Wir begrüßen uns", 2: "Wir begrüßen uns",
    3: "Wir begrüßen uns", 4: "Wir begrüßen uns",
    5: "Ich stelle mich vor", 6: "Ich stelle mich vor", 7: "Ich stelle mich vor",
    8: "Das deutsche Alphabet", 9: "Das deutsche Alphabet",
}

# A review may restore mastery only after it has independently covered every
# review evidence item required for that course skill.  This prevents one
# narrow success from restoring a broader multi-part skill.
A1_LESSON_1_REVIEW_EVIDENCE = {
    1: "greeting_morning", 2: "greeting_day", 3: "greeting_evening", 4: "greeting_goodbye",
    5: "introduce_self", 6: "ask_name_informal", 7: "ask_name_formal",
    8: "umlauts", 9: "eszett",
}

A1_LESSON_1_REQUIRED_REVIEW_EVIDENCE = {
    "Wir begrüßen uns": {"greeting_morning", "greeting_day", "greeting_evening", "greeting_goodbye"},
    "Ich stelle mich vor": {
        "introduce_self",
        "ask_name_informal",
        "ask_name_formal",
    },
    "Das deutsche Alphabet": {"umlauts", "eszett"},
}


def _course_skill_key(level, lesson, section):
    section_key = normalize(str(section or "")).strip(
        " .?!„“\\\"'"
    ).replace(" ", "_")
    if not section_key:
        return None
    return f"course:{str(level).lower()}:{int(lesson)}:{section_key}"


def record_review_course_outcome(state, step, success, partial=False):
    """Feed lesson review evidence into the same course-skill mastery state."""
    if state is None:
        return None

    level = str(state.get("lesson_review_training_level") or "A1").strip().upper()
    lesson = int(state.get("lesson_review_training_lesson") or 1)
    section = A1_LESSON_1_REVIEW_SECTIONS.get(int(step or 0))
    skill = _course_skill_key(level, lesson, section)
    if not skill:
        return None

    assisted = bool(state.get("course_mastery_assistance_used"))
    independent = bool(success and not assisted)

    evidence_key = A1_LESSON_1_REVIEW_EVIDENCE.get(int(step or 0))
    required_evidence = set(
        A1_LESSON_1_REQUIRED_REVIEW_EVIDENCE.get(section) or []
    )

    if success:
        register_speaking_course_success(state)
    else:
        # Any correction/model following this miss is guided evidence.
        state["course_mastery_assistance_used"] = True

    progress = update_learning_progress(
        state,
        {
            "skill": skill,
            "expected_outcome": "course_review",
            "status": "SUCCESS" if success else ("PARTIAL" if partial else "NOT_YET"),
            # Review now uses the same central evidence contract as normal
            # course teaching. The progress engine owns accumulated independent
            # evidence and decides when the required coverage is complete.
            "mastery_eligible": bool(success and independent),
            "requires_independent_confirmation": True,
            "independent_confirmation": independent,
            "review_confirmation": independent,
            "required_evidence": sorted(required_evidence),
            "evidence": evidence_key if independent else "",
        },
    )

    if success:
        # Assistance belongs only to the task that has just been answered.
        state["course_mastery_assistance_used"] = False

    return progress


def _reviewed_course_skills_mastered(state):
    skills = (((state or {}).get("learning_progress_v1") or {}).get("skills") or {})
    wanted = {
        _course_skill_key("A1", 1, section)
        for section in set(A1_LESSON_1_REVIEW_SECTIONS.values())
    }
    return all(
        (skills.get(skill) or {}).get("status") == "mastered"
        for skill in wanted
        if skill
    )


# ==========================================
# POPRAWNA ODPOWIEDŹ
# ==========================================

def remember_correct_answer(
    state
):

    value = state.get(
        "lesson_review_training_correct",
        0
    )

    try:

        value = int(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        value = 0


    state[
        "lesson_review_training_correct"
    ] = value + 1


# ==========================================
# BŁĘDNA ODPOWIEDŹ
# ==========================================

def remember_wrong_answer(
    state
):

    value = state.get(
        "lesson_review_training_wrong",
        0
    )

    try:

        value = int(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        value = 0


    state[
        "lesson_review_training_wrong"
    ] = value + 1


# ==========================================
# START POWTÓRKI
# ==========================================

def start_lesson_review_training(
    state,
    level="A1",
    lesson=1
):

    if state is None:
        return None


    level = str(
        level or "A1"
    ).strip().upper()


    try:

        lesson = int(
            lesson
        )

    except (
        TypeError,
        ValueError
    ):

        lesson = 1


    # A1.1 keeps its purpose-built review content. Newer lessons reuse the
    # generic lesson definitions and the same Teacher/Mastery engine, so review
    # grows with the course instead of requiring another lesson-specific router.
    if not (level == "A1" and lesson == 1):
        from brain.logic.generic_lesson_engine import start_generic_lesson_review
        return start_generic_lesson_review(state, level, lesson)


    state[
        "lesson_review_training_active"
    ] = True

    state[
        "lesson_review_training_level"
    ] = level

    state[
        "lesson_review_training_lesson"
    ] = lesson

    state[
        "lesson_review_training_step"
    ] = 1

    state[
        "lesson_review_training_correct"
    ] = 0

    state[
        "lesson_review_training_wrong"
    ] = 0
    return (
        "Super! Wir wiederholen kurz. "
        "Was sagst du am Morgen?"
    )


# ==========================================
# SPRAWDZENIE POWITANIA
# ==========================================

def is_greeting_range_answer(
    text
):
    """Require independent coverage of the greeting situations taught by the skill."""
    answer = clean_normalized_answer(text)
    has_morning = "guten morgen" in answer or answer.startswith("morgen")
    has_day = "guten tag" in answer
    has_evening = "guten abend" in answer
    has_goodbye = "tschüss" in answer or "auf wiedersehen" in answer
    return has_morning and has_day and has_evening and has_goodbye


# ==========================================
# SPRAWDZENIE PRZEDSTAWIENIA SIĘ
# ==========================================

def is_valid_name_answer(text):
    """Accept only a real self-introduction, not arbitrary Ich bin text.

    Reuse onboarding semantic name extraction so age, wellbeing or other
    statements cannot count as name-introduction evidence in review.
    """
    return bool(extract_name_sentence(text))


# ==========================================
# WIE HEISST DU?
# ==========================================

def is_informal_name_question(
    text
):

    answer = clean_normalized_answer(
        text
    )

    return answer in {
        "wie heißt du",
        "wie heisst du"
    }


# ==========================================
# WIE HEISSEN SIE?
# ==========================================

def is_formal_name_question(
    text
):

    answer = clean_normalized_answer(
        text
    )

    return answer in {
        "wie heißen sie",
        "wie heissen sie"
    }


# ==========================================
# UMLAUTY
# ==========================================

def is_umlaut_answer(
    text
):

    text = str(
        text or ""
    ).lower()


    return (
        "ä" in text
        and
        "ö" in text
        and
        "ü" in text
    )


# ==========================================
# ESZETT
# ==========================================

def is_eszett_answer(
    text
):

    text = str(
        text or ""
    ).lower()


    if "ß" in text:
        return True


    answer = clean_normalized_answer(
        text
    )


    return answer in {
        "eszett",
        "es zett",
        "scharfes s",
        "das eszett",
        "das scharfe s"
    }


# ==========================================
# SHARED COURSE ANSWER EVALUATION
# ==========================================

A1_LESSON_1_REVIEW_ANSWERS = {
    1: {"accepted": ["Guten Morgen"]},
    2: {"accepted": ["Guten Tag", "Hallo"]},
    3: {"accepted": ["Guten Abend"]},
    4: {"accepted": ["Tschüss", "Auf Wiedersehen"]},
    5: {"validator": "review_name_introduction"},
    6: {"accepted": ["Wie heißt du?", "Wie heisst du?"]},
    7: {"accepted": ["Wie heißen Sie?", "Wie heissen Sie?"]},
    8: {"validator": "review_umlauts"},
    9: {
        "accepted": [
            "ß",
            "Eszett",
            "Es Zett",
            "scharfes S",
            "das Eszett",
            "das scharfe S",
        ]
    },
}


def _review_answer_validator(name, user_message):
    """Keep structural review rules behind the shared evaluator contract."""
    if name == "review_greeting_range":
        return is_greeting_range_answer(user_message)
    if name == "review_name_introduction":
        return is_valid_name_answer(user_message)
    if name == "review_umlauts":
        return is_umlaut_answer(user_message)
    return False


def evaluate_review_answer(step, user_message):
    """Evaluate every A1.1 review answer through the shared course evaluator."""
    definition = A1_LESSON_1_REVIEW_ANSWERS.get(int(step or 0))
    if not definition:
        return {"kind": "wrong", "correct": False, "partial": None}
    return evaluate_course_answer(
        user_message,
        definition,
        validator=_review_answer_validator,
    )


def _remember_review_error(state, step, wrong_answer, correct_answer):
    """Store a real review miss in shared Error Memory for later practice."""
    error_type = {
        1: "vocabulary",
        2: "grammar",
        3: "grammar",
        4: "grammar",
        5: "spelling",
        6: "spelling",
    }.get(int(step or 0), "grammar")
    contexts = {
        1: "Was sagst du am Morgen?",
        2: "Was sagst du am Tag?",
        3: "Was sagst du am Abend?",
        4: "Was sagst du beim Gehen?",
        5: "Stell dich kurz vor. Wie heißt du?",
        6: "Wie fragst du einen Freund nach seinem Namen?",
        7: "Wie fragst du höflich nach dem Namen?",
        8: "Welche drei Umlaute gibt es im Deutschen?",
        9: "Wie heißt dieses Zeichen: ß?",
    }
    return remember_error(
        state,
        error_type,
        wrong_answer,
        correct_answer,
        context=contexts.get(int(step or 0)),
    )


def _review_miss_reply(state, step, result, *, correct_answer, retry, wrong_answer=""):
    """Preserve PARTIAL separately from a fully wrong review answer."""
    partial = (result or {}).get("partial") if (result or {}).get("kind") == "partial" else None
    if partial:
        record_review_course_outcome(state, step, False, partial=True)
        action = choose_course_teacher_action(
            state,
            partial=partial,
            correct_answer=correct_answer,
        )
        return render_course_teacher_action(action)

    remember_wrong_answer(state)
    _remember_review_error(state, step, wrong_answer, correct_answer)
    record_review_course_outcome(state, step, False)
    action = choose_course_teacher_action(
        state,
        answer_correct=False,
        correct_answer=correct_answer,
        retry=retry,
    )
    return render_course_teacher_action(action)


# ==========================================
# ZAKOŃCZENIE CAŁEJ POWTÓRKI
# ==========================================

def complete_lesson_review_training(
    state
):

    level = state.get(
        "lesson_review_training_level",
        "A1"
    )

    lesson = state.get(
        "lesson_review_training_lesson",
        1
    )


    wrong = state.get(
        "lesson_review_training_wrong",
        0
    )


    try:

        wrong = int(
            wrong
        )

    except (
        TypeError,
        ValueError
    ):

        wrong = 0


    # ======================================
    # REVIEW IS GOOD ONLY WHEN THE REVIEWED COURSE SKILLS ARE MASTERED.
    # The old "0–1 errors = good" rule is no longer sufficient.
    #
    # lesson_review.py zaplanuje
    # następny termin:
    #
    # 3 / 7 / 14 / 30 dni
    # ======================================

    # Historical mistakes must not outweigh a later complete independent
    # demonstration. The shared mastery state already captures whether errors
    # were actually repaired; review completion should follow that current
    # learning state instead of the raw number of earlier mistakes.
    if _reviewed_course_skills_mastered(state):

        mark_lesson_review_completed(
            state,
            level,
            lesson,
            result="good"
        )


        # ==================================
        # DAILY LEARNING MEMORY
        # ==================================

        remember_daily_lesson_review_completion(
            state,
            level,
            lesson,
            result="good"
        )


        finish_lesson_review_training(
            state
        )

        return (
            "Sehr gut! Du hast die Wiederholung "
            "von A1, Lektion 1 geschafft. "
            "Die nächste Wiederholung wird "
            "automatisch geplant."
        )


    # ======================================
    # WIĘCEJ BŁĘDÓW
    # -> POWTÓRKA JUTRO
    # ======================================

    mark_lesson_review_difficult(
        state,
        level,
        lesson
    )


    # ======================================
    # DAILY LEARNING MEMORY
    #
    # Powtórka została dzisiaj wykonana,
    # mimo że była trudna.
    # Nie uruchamiamy jej ponownie
    # tego samego dnia.
    # ======================================

    remember_daily_lesson_review_completion(
        state,
        level,
        lesson,
        result="difficult"
    )


    finish_lesson_review_training(
        state
    )

    return (
        "Gut gemacht. Einige Dinge waren noch "
        "etwas schwierig. Deshalb wiederholen "
        "wir A1, Lektion 1 morgen noch einmal."
    )


# ==========================================
# OBSŁUGA POWTÓRKI A1 LEKTION 1
# ==========================================

def handle_a1_lesson_1_review(user_message, state):
    if state is None:
        return None
    pending_before = bool(state.get("course_pending_speaking_model"))
    pending_reply = handle_pending_course_model(user_message, state)
    if pending_reply is not None:
        return pending_reply
    step = int(state.get("lesson_review_training_step") or 1)

    exhausted = consume_course_model_exhaustion(state)
    if exhausted:
        state["course_mastery_assistance_used"] = True
        record_review_course_outcome(state, step, False)
        action = choose_course_teacher_action(state, answer_correct=True, mastery_status="needs_review")
        return render_course_teacher_action(action, prompt="Versuch diese Aufgabe später noch einmal.")

    greeting_steps = {
        1: ("Guten Morgen", "Richtig!", "Was sagst du am Tag?"),
        2: ("Guten Tag", "Sehr gut!", "Was sagst du am Abend?"),
        3: ("Guten Abend", "Genau!", "Du gehst jetzt. Was sagst du?"),
        4: ("Tschüss", "Richtig!", "Jetzt stell dich kurz vor. Wie heißt du?"),
    }
    if step in greeting_steps:
        target, feedback, next_prompt = greeting_steps[step]
        result = evaluate_review_answer(step, user_message)
        if not result["correct"]:
            return _review_miss_reply(state, step, result, correct_answer=target,
                                      retry=get_current_lesson_review_prompt(state),
                                      wrong_answer=user_message)
        remember_correct_answer(state)
        record_review_course_outcome(state, step, True)
        state["lesson_review_training_step"] = step + 1
        return f"{feedback} {next_prompt}"

    if step == 5:
        result = evaluate_review_answer(step, user_message)
        if not result["correct"]:
            name = str(get_user_fact(state, "name") or state.get("name") or "Moni").strip()
            target = f"Ich heiße {name}."
            return _review_miss_reply(state, step, result, correct_answer=target,
                                      retry="Stell dich noch einmal kurz vor.", wrong_answer=user_message)
        remember_correct_answer(state); record_review_course_outcome(state, step, True)
        state["lesson_review_training_step"] = 6
        return "Sehr gut! Wie fragst du einen Freund nach seinem Namen?"

    targets = {
        6: ("Wie heißt du?", "Frag deinen Freund noch einmal.", "Genau! „Wie heißt du?“ Und wie fragst du höflich nach dem Namen?"),
        7: ("Wie heißen Sie?", "Frag noch einmal höflich.", "Richtig! „Wie heißen Sie?“ Welche drei Umlaute kennst du?"),
        8: ("Ä, Ö und Ü", "Sag die drei Umlaute noch einmal.", "Perfekt! Ä, Ö und Ü. Wie heißt dieses Zeichen: ß?"),
    }
    if step in targets:
        target, retry, next_prompt = targets[step]
        result = evaluate_review_answer(step, user_message)
        if not result["correct"]:
            return _review_miss_reply(state, step, result, correct_answer=target,
                                      retry=retry, wrong_answer=user_message)
        remember_correct_answer(state); record_review_course_outcome(state, step, True)
        state["lesson_review_training_step"] = step + 1
        return next_prompt

    if step == 9:
        result = evaluate_review_answer(step, user_message)
        if not result["correct"]:
            return _review_miss_reply(state, step, result, correct_answer="Eszett",
                                      retry="Wie heißt das Zeichen ß?", wrong_answer=user_message)
        remember_correct_answer(state); record_review_course_outcome(state, step, True)
        result_text = complete_lesson_review_training(state)
        return f"Richtig! Das ist das Eszett.\n\n{result_text}"

    finish_lesson_review_training(state)
    return None


# ==========================================
# GŁÓWNA OBSŁUGA POWTÓRKI
# ==========================================

def handle_lesson_review_training(
    user_message,
    state
):

    if state is None:
        return None


    if not is_lesson_review_training_active(
        state
    ):

        return None


    level = str(
        state.get(
            "lesson_review_training_level",
            ""
        )
        or
        ""
    ).strip().upper()


    lesson = state.get(
        "lesson_review_training_lesson"
    )


    if (
        level == "A1"
        and
        lesson == 1
    ):

        return handle_a1_lesson_1_review(
            user_message,
            state
        )


    finish_lesson_review_training(
        state
    )

    return None
