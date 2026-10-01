# ==========================================
# NELE – POWTÓRKA CAŁEJ LEKCJI
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.speaking_support import (
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

from brain.memory.lesson_review import (
    mark_lesson_review_completed,
    mark_lesson_review_difficult
)

from brain.memory.daily_learning import (
    mark_lesson_reviewed_today,
    mark_exercise_completed_today
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
    1: "Wir begrüßen uns",
    2: "Ich stelle mich vor",
    3: "Ich stelle mich vor",
    4: "Ich stelle mich vor",
    5: "Das deutsche Alphabet",
    6: "Das deutsche Alphabet",
}

# A review may restore mastery only after it has independently covered every
# review evidence item required for that course skill.  This prevents one
# narrow success from restoring a broader multi-part skill.
A1_LESSON_1_REVIEW_EVIDENCE = {
    1: "greeting_range",
    2: "introduce_self",
    3: "ask_name_informal",
    4: "ask_name_formal",
    5: "umlauts",
    6: "eszett",
}

A1_LESSON_1_REQUIRED_REVIEW_EVIDENCE = {
    "Wir begrüßen uns": {"greeting_range"},
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


def record_review_course_outcome(state, step, success):
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
    evidence_state = state.setdefault("course_review_evidence", {})
    skill_evidence = set(evidence_state.get(skill) or [])
    if independent and evidence_key:
        skill_evidence.add(evidence_key)
        evidence_state[skill] = sorted(skill_evidence)

    required_evidence = set(
        A1_LESSON_1_REQUIRED_REVIEW_EVIDENCE.get(section) or []
    )
    coverage_complete = bool(
        independent
        and required_evidence
        and required_evidence.issubset(skill_evidence)
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
            "status": "SUCCESS" if success else "NOT_YET",
            "mastery_eligible": bool(success and coverage_complete),
            "requires_independent_confirmation": True,
            "independent_confirmation": coverage_complete,
            "review_confirmation": coverage_complete,
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


    # ======================================
    # NA RAZIE OBSŁUGUJEMY
    # A1 LEKTION 1
    # ======================================

    if not (
        level == "A1"
        and
        lesson == 1
    ):

        return None


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

    state["course_review_evidence"] = {}

    return (
        "Heute ist die Wiederholung von "
        "A1, Lektion 1 dran. "
        "Wir machen eine kurze Wiederholung. "
        "Nenne passende Grüße für morgens, tagsüber, abends "
        "und beim Gehen."
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

def is_valid_name_answer(
    text
):

    answer = clean_normalized_answer(
        text
    )


    starts = [
        "ich heiße ",
        "ich heisse ",
        "ich bin ",
        "mein name ist "
    ]


    return any(
        answer.startswith(
            start
        )
        and
        len(
            answer[
                len(start):
            ].strip()
        ) > 0
        for start in starts
    )


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
    1: {"validator": "review_greeting_range"},
    2: {"validator": "review_name_introduction"},
    3: {"accepted": ["Wie heißt du?", "Wie heisst du?"]},
    4: {"accepted": ["Wie heißen Sie?", "Wie heissen Sie?"]},
    5: {"validator": "review_umlauts"},
    6: {
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

    if wrong <= 1 and _reviewed_course_skills_mastered(state):

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

def handle_a1_lesson_1_review(
    user_message,
    state
):

    pending_before = bool(state.get("course_pending_speaking_model"))
    pending_reply = handle_pending_course_model(user_message, state)
    if pending_reply is not None:
        return pending_reply
    if pending_before:
        # The learner has now produced the supported answer. Continue through
        # the same review step; that step records the success exactly once.
        pass

    step = state.get(
        "lesson_review_training_step",
        1
    )


    # ======================================
    # 1. GUTEN MORGEN
    # ======================================

    if step == 1:

        if evaluate_review_answer(step, user_message)["correct"]:

            remember_correct_answer(
                state
            )
            record_review_course_outcome(state, step, True)

            feedback = (
                "Richtig! Du kannst die Grüße passend zur Situation verwenden."
            )

        else:

            remember_wrong_answer(state)
            record_review_course_outcome(state, step, False)
            action = choose_course_teacher_action(
                state,
                answer_correct=False,
                correct_answer="Guten Morgen, Guten Tag, Guten Abend und Tschüss",
                retry="Nenne noch einmal passende Grüße für morgens, tagsüber, abends und beim Gehen.",
            )
            return render_course_teacher_action(action)


        state[
            "lesson_review_training_step"
        ] = 2


        return (
            f"{feedback} "
            "Jetzt stell dich kurz vor. "
            "Wie heißt du?"
        )


    # ======================================
    # 2. ICH HEISSE ...
    # ======================================

    if step == 2:

        if evaluate_review_answer(step, user_message)["correct"]:

            remember_correct_answer(
                state
            )
            record_review_course_outcome(state, step, True)

            feedback = (
                "Sehr gut!"
            )

        else:

            remember_wrong_answer(state)
            record_review_course_outcome(state, step, False)
            # Review uses the current learner name when available, but the
            # speaking-support policy itself remains vocabulary-independent.
            name = str(
                get_user_fact(state, "name")
                or state.get("name")
                or "Moni"
            ).strip()
            target = f"Ich heiße {name}."
            action = choose_course_teacher_action(
                state,
                answer_correct=False,
                correct_answer=target,
                retry="Stell dich noch einmal kurz vor.",
            )
            return render_course_teacher_action(action)


        state[
            "lesson_review_training_step"
        ] = 3


        return (
            f"{feedback} "
            "Wie fragst du einen Freund "
            "nach seinem Namen?"
        )


    # ======================================
    # 3. WIE HEISST DU?
    # ======================================

    if step == 3:

        if evaluate_review_answer(step, user_message)["correct"]:

            remember_correct_answer(
                state
            )
            record_review_course_outcome(state, step, True)

            feedback = (
                "Genau! „Wie heißt du?“"
            )

        else:

            remember_wrong_answer(state)
            record_review_course_outcome(state, step, False)
            action = choose_course_teacher_action(
                state,
                answer_correct=False,
                correct_answer="Wie heißt du?",
                retry="Frag deinen Freund noch einmal.",
            )
            return render_course_teacher_action(action)


        state[
            "lesson_review_training_step"
        ] = 4


        return (
            f"{feedback} "
            "Und wie fragst du höflich "
            "nach dem Namen?"
        )


    # ======================================
    # 4. WIE HEISSEN SIE?
    # ======================================

    if step == 4:

        if evaluate_review_answer(step, user_message)["correct"]:

            remember_correct_answer(
                state
            )
            record_review_course_outcome(state, step, True)

            feedback = (
                "Richtig! „Wie heißen Sie?“"
            )

        else:

            remember_wrong_answer(state)
            record_review_course_outcome(state, step, False)
            action = choose_course_teacher_action(
                state,
                answer_correct=False,
                correct_answer="Wie heißen Sie?",
                retry="Frag noch einmal höflich.",
            )
            return render_course_teacher_action(action)


        state[
            "lesson_review_training_step"
        ] = 5


        return (
            f"{feedback} "
            "Welche drei Umlaute gibt es "
            "im Deutschen?"
        )


    # ======================================
    # 5. Ä Ö Ü
    # ======================================

    if step == 5:

        if evaluate_review_answer(step, user_message)["correct"]:

            remember_correct_answer(
                state
            )
            record_review_course_outcome(state, step, True)

            feedback = (
                "Perfekt! Ä, Ö und Ü."
            )

        else:

            remember_wrong_answer(
                state
            )
            record_review_course_outcome(state, step, False)

            action = choose_course_teacher_action(
                state,
                answer_correct=False,
                correct_answer="Ä, Ö und Ü",
                retry="Die drei Umlaute sind Ä, Ö und Ü. Sag sie jetzt selbst.",
            )
            return render_course_teacher_action(action)


        state[
            "lesson_review_training_step"
        ] = 6


        return (
            f"{feedback} "
            "Und wie heißt dieses Zeichen: ß?"
        )


    # ======================================
    # 6. ESZETT
    # ======================================

    if step == 6:

        if evaluate_review_answer(step, user_message)["correct"]:

            remember_correct_answer(
                state
            )
            record_review_course_outcome(state, step, True)

            feedback = (
                "Richtig! Das ist das Eszett."
            )

        else:

            remember_wrong_answer(
                state
            )
            record_review_course_outcome(state, step, False)

            action = choose_course_teacher_action(
                state,
                answer_correct=False,
                correct_answer="Eszett",
                retry="Das Zeichen heißt „Eszett“ oder „scharfes S“. Sag es jetzt selbst.",
            )
            return render_course_teacher_action(action)


        result = (
            complete_lesson_review_training(
                state
            )
        )


        return (
            f"{feedback}\n\n"
            f"{result}"
        )


    finish_lesson_review_training(
        state
    )

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
