# ==========================================
# NELE – GENERISCHER LEKTIONSMOTOR
# STUDENT MEMORY 2.0
# ==========================================
#
# Neue Lektionen müssen ihre Unterrichtslogik
# nicht mehr direkt in lesson_teaching.py
# einbauen.
#
# Eine Lektionsdatei kann zusätzlich zu
# LESSON / LESSON_RESPONSES definieren:
#
# LESSON_FLOW = {
#     "sections": {
#         "Name der Sektion": {
#             "intro": "...",
#             "steps": [
#                 {
#                     "prompt": "...",
#                     "accepted": ["..."],
#                     "correct_answer": "...",
#                     "error_type": "grammar",
#                     "retry": "...",
#                     "success": "..."
#                 }
#             ],
#             "complete": "..."
#         }
#     }
# }
#
# Unterstützte Antwortregeln pro Schritt:
# - accepted: exakte normalisierte Antworten
# - regex: reguläre Ausdrücke
# - contains_all: alle Begriffe müssen vorkommen
# - contains_any: mindestens ein Begriff
# - validator: "nonempty", "student_name",
#              "spell_student_name"
# - allow_any: jede nichtleere Antwort
#
# Platzhalter in Texten:
# {name}
# {spelled_name}
# {level}
# {lesson}
# {section}
# ==========================================

import re

from brain.logic.matcher import normalize
from brain.logic.lesson_loader import (
    load_lesson_module
)

from brain.memory.student_progress import (
    get_current_level,
    get_current_lesson,
    remember_completed_lesson
)

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

from brain.logic.speaking_support import (
    assess_course_answer,
    build_course_support_reply,
    handle_pending_course_model,
)

from brain.logic.learning_progress_engine import update_learning_progress
from brain.logic.course_teacher_engine import (
    choose_course_teacher_action,
    render_course_teacher_action,
)


# ==========================================
# TEXT
# ==========================================

def clean_text(
    value
):

    return str(
        value or ""
    ).strip()


def normalize_text(
    value
):

    return normalize(
        clean_text(
            value
        )
    ).strip(
        " .?!„“\"'"
    )


# ==========================================
# PERSONALISIERUNG
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

    return clean_text(
        name
    )


def get_spelled_name(
    state
):

    name = get_student_name(
        state
    )

    if not name:
        return ""

    return " – ".join(
        char.upper()
        for char in name
        if char.isalnum()
    )


def get_template_values(
    state,
    level=None,
    lesson=None,
    section=None
):

    if level is None:

        level = (
            state.get(
                "lesson_teaching_level"
            )
            if state
            else None
        )

    if not level:

        level = get_current_level(
            state
        )


    if lesson is None:

        lesson = (
            state.get(
                "lesson_teaching_lesson"
            )
            if state
            else None
        )

    if not lesson:

        lesson = get_current_lesson(
            state
        )


    return {
        "name":
            get_student_name(
                state
            ),

        "spelled_name":
            get_spelled_name(
                state
            ),

        "level":
            clean_text(
                level
            ),

        "lesson":
            clean_text(
                lesson
            ),

        "section":
            clean_text(
                section
                or (
                    state.get(
                        "lesson_teaching_section"
                    )
                    if state
                    else ""
                )
            )
    }


def render_text(
    value,
    state,
    level=None,
    lesson=None,
    section=None
):

    text = clean_text(
        value
    )

    if not text:
        return ""

    values = get_template_values(
        state,
        level,
        lesson,
        section
    )


    try:

        return text.format(
            **values
        )

    except Exception:

        return text


# ==========================================
# LESSON FLOW LADEN
# ==========================================

def get_lesson_flow(
    level,
    lesson
):

    module = load_lesson_module(
        str(
            level or "A1"
        ).strip().upper(),
        lesson
    )

    if module is None:
        return None


    flow = getattr(
        module,
        "LESSON_FLOW",
        None
    )


    if not isinstance(
        flow,
        dict
    ):

        return None


    return flow


def get_flow_sections(
    level,
    lesson
):

    flow = get_lesson_flow(
        level,
        lesson
    )

    if not flow:
        return {}


    sections = flow.get(
        "sections",
        {}
    )


    # Bevorzugte Form:
    # "sections": {"Name": {...}}
    if isinstance(
        sections,
        dict
    ):

        return sections


    # Alternative Form:
    # "sections": [{"name": "...", ...}]
    if isinstance(
        sections,
        list
    ):

        result = {}


        for item in sections:

            if not isinstance(
                item,
                dict
            ):

                continue


            name = clean_text(
                item.get(
                    "name"
                )
            )


            if name:

                result[
                    name
                ] = item


        return result


    return {}


def find_generic_section(
    level,
    lesson,
    section
):

    wanted = normalize_text(
        section
    )

    if not wanted:
        return None, None


    for name, definition in (
        get_flow_sections(
            level,
            lesson
        ).items()
    ):

        if (
            normalize_text(
                name
            )
            ==
            wanted
        ):

            if isinstance(
                definition,
                dict
            ):

                return name, definition


    return None, None


def has_generic_section(
    level,
    lesson,
    section
):

    name, definition = (
        find_generic_section(
            level,
            lesson,
            section
        )
    )


    return bool(
        name
        and
        definition
    )


# ==========================================
# SCHRITTE
# ==========================================

def get_steps(
    section_definition
):

    if not isinstance(
        section_definition,
        dict
    ):

        return []


    steps = section_definition.get(
        "steps",
        []
    )


    if not isinstance(
        steps,
        list
    ):

        return []


    return [
        step
        for step in steps
        if isinstance(
            step,
            dict
        )
    ]


def get_step(
    section_definition,
    step_number
):

    steps = get_steps(
        section_definition
    )


    try:

        step_number = int(
            step_number
        )

    except (
        TypeError,
        ValueError
    ):

        step_number = 1


    index = step_number - 1


    if (
        index < 0
        or
        index >= len(
            steps
        )
    ):

        return None


    return steps[
        index
    ]


# ==========================================
# BENANNTE VALIDATOREN
# ==========================================

def validate_student_name(
    user_message,
    state
):

    expected = normalize_text(
        get_student_name(
            state
        )
    )


    if not expected:
        return bool(
            normalize_text(
                user_message
            )
        )


    message = normalize_text(
        user_message
    )


    prefixes = (
        "ich heiße ",
        "ich heisse ",
        "ich bin ",
        "mein name ist "
    )


    for prefix in prefixes:

        if message.startswith(
            prefix
        ):

            return (
                message[
                    len(
                        prefix
                    ):
                ].strip()
                ==
                expected
            )


    return False


def validate_spelled_student_name(
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


    raw = clean_text(
        user_message
    )


    compact = "".join(
        char.lower()
        for char in raw
        if char.isalnum()
    )


    if compact != target:
        return False


    separators = sum(
        1
        for char in raw
        if char in " -,_./"
    )


    return separators >= max(
        1,
        len(
            target
        ) - 1
    )


def validate_named(
    validator,
    user_message,
    state
):

    validator = clean_text(
        validator
    ).lower()


    if validator == "nonempty":

        return bool(
            normalize_text(
                user_message
            )
        )


    if validator == "student_name":

        return validate_student_name(
            user_message,
            state
        )


    if validator == "spell_student_name":

        return validate_spelled_student_name(
            user_message,
            state
        )


    return False


# ==========================================
# GEMEINSAME ANTWORTPRÜFUNG
# ==========================================

from brain.logic.course_answer_evaluator import (
    answer_matches_course_definition,
    evaluate_course_answer,
    sequence_partial_progress as _shared_sequence_partial_progress,
    semantic_tokens as _semantic_tokens,
)



def _sequence_partial_progress(user_message, accepted_values, state=None, render=None):
    """Compatibility wrapper; shared evaluator owns the actual logic."""
    return _shared_sequence_partial_progress(
        user_message,
        accepted_values,
        state=state,
        render=render,
    )


# ==========================================
# ANTWORT PRÜFEN
# ==========================================

def evaluate_step_answer(
    user_message,
    step,
    state
):
    return evaluate_course_answer(
        user_message,
        step,
        render=lambda value: render_text(value, state),
        validator=lambda name, message: validate_named(name, message, state),
    )


def answer_matches_step(
    user_message,
    step,
    state
):
    return evaluate_step_answer(user_message, step, state)["correct"]


# ==========================================
# KURS-DYGRSJA ERKENNEN
# ==========================================

_COURSE_QUESTION_WORDS = {
    "wer", "was", "wann", "wo", "woher", "wohin", "warum", "wieso", "weshalb",
    "wie", "welche", "welcher", "welches", "kann", "kannst", "ist", "sind", "hast",
}


def is_course_digression_question(user_message, step, state):
    """Recognize an off-task learner question without consuming lesson progress.

    A question that substantially reuses the current target remains a normal
    lesson attempt (for example turning a statement into a question). A clearly
    unrelated question is a digression and must not be recorded as a mistake.
    """
    raw = clean_text(user_message)
    low = normalize_text(raw)
    if not low:
        return False

    words = low.split()
    looks_like_question = raw.rstrip().endswith("?") or (
        words and words[0] in _COURSE_QUESTION_WORDS
    )
    if not looks_like_question:
        return False

    target = render_text((step or {}).get("correct_answer"), state)
    target_words = set(_semantic_tokens(target))
    learner_words = set(_semantic_tokens(raw))

    # If the learner is using the lesson's own content, let the normal answer
    # evaluator decide whether the grammatical form is correct.
    if target_words and learner_words:
        overlap = len(target_words & learner_words) / max(1, len(target_words))
        if overlap >= 0.5:
            return False

    return True


def build_course_digression_resume(step, state, level, lesson, section, user_message=None):
    prompt = render_text(
        (step or {}).get("prompt"), state, level, lesson, section
    )

    # A digression should be answered without handing control to free mode.
    # Reuse its A1 social/question understanding against isolated temporary
    # state, so course progress and the exact active step cannot be mutated.
    digression_reply = ""
    if user_message:
        try:
            from brain.logic.free_conversation import _social_a1_reply
            digression_reply = clean_text(
                _social_a1_reply(user_message, {}, {})
            )
        except Exception:
            digression_reply = ""

    if not digression_reply:
        digression_reply = "Gute Frage."

    if prompt:
        return f"{digression_reply} Jetzt machen wir genau hier weiter: {prompt}"
    return f"{digression_reply} Jetzt machen wir genau hier weiter."


# ==========================================
# FEHLER MERKEN
# ==========================================

def remember_generic_mistake(
    state,
    step,
    user_message
):

    if not isinstance(
        step,
        dict
    ):

        return


    error_type = clean_text(
        step.get(
            "error_type"
        )
    )


    correct_answer = render_text(
        step.get(
            "correct_answer"
        ),
        state
    )


    wrong_answer = clean_text(
        user_message
    )


    if not (
        error_type
        and
        correct_answer
        and
        wrong_answer
    ):

        return


    try:

        context_text = render_text(
            step.get(
                "context"
            )
            or
            step.get(
                "prompt"
            ),
            state
        )


        remember_error(
            state,
            error_type,
            wrong_answer,
            correct_answer,
            context=context_text
        )

    except Exception as error:

        print(
            f"Generic lesson error memory: {error}"
        )


    try:

        record_mistake_today(
            state,
            error_type,
            wrong=wrong_answer,
            correct=correct_answer
        )

    except Exception as error:

        print(
            f"Generic daily mistake memory: {error}"
        )


# ==========================================
# AKTIVER GENERISCHER FLOW?
# ==========================================

def is_generic_lesson_active(
    state
):

    if not state:
        return False


    if not state.get(
        "lesson_teaching_active",
        False
    ):

        return False


    level = state.get(
        "lesson_teaching_level"
    )

    lesson = state.get(
        "lesson_teaching_lesson"
    )

    section = state.get(
        "lesson_teaching_section"
    )


    if not (
        level
        and
        lesson
        and
        section
    ):

        return False


    return has_generic_section(
        level,
        lesson,
        section
    )


# ==========================================
# GENERISCHE SEKTION STARTEN
# ==========================================

def start_generic_lesson_teaching(
    section,
    state
):

    if state is None:
        return None

    level = get_current_level(
        state
    )

    lesson = get_current_lesson(
        state
    )


    real_section, definition = (
        find_generic_section(
            level,
            lesson,
            section
        )
    )


    if not real_section:
        return None


    steps = get_steps(
        definition
    )


    if not steps:
        return None


    state[
        "lesson_teaching_active"
    ] = True

    state[
        "lesson_teaching_level"
    ] = level

    state[
        "lesson_teaching_lesson"
    ] = lesson

    state[
        "lesson_teaching_section"
    ] = real_section

    state[
        "lesson_teaching_step"
    ] = 1

    state[
        "last_activity"
    ] = "lesson"

    state[
        "last_activity_detail"
    ] = real_section


    intro = render_text(
        definition.get(
            "intro"
        ),
        state,
        level,
        lesson,
        real_section
    )


    first_prompt = render_text(
        steps[0].get(
            "prompt"
        ),
        state,
        level,
        lesson,
        real_section
    )


    parts = [
        part
        for part in (
            intro,
            first_prompt
        )
        if part
    ]


    return " ".join(
        parts
    )


# ==========================================
# AKTUELLEN PROMPT WIEDERHERSTELLEN
# ==========================================

def get_generic_current_prompt(
    state
):

    if not is_generic_lesson_active(
        state
    ):

        return ""

    level = state.get(
        "lesson_teaching_level"
    )

    lesson = state.get(
        "lesson_teaching_lesson"
    )

    section = state.get(
        "lesson_teaching_section"
    )

    step_number = state.get(
        "lesson_teaching_step",
        1
    )


    real_section, definition = (
        find_generic_section(
            level,
            lesson,
            section
        )
    )


    if not real_section:
        return ""


    step = get_step(
        definition,
        step_number
    )


    if not step:
        return ""


    resume = render_text(
        step.get(
            "resume"
        ),
        state,
        level,
        lesson,
        real_section
    )


    if resume:
        return resume


    prompt = render_text(
        step.get(
            "prompt"
        ),
        state,
        level,
        lesson,
        real_section
    )


    if not prompt:
        return ""


    return (
        "Wir machen genau dort weiter. "
        + prompt
    )


# ==========================================
# AKTIVEN FLOW BEENDEN
# ==========================================

def clear_generic_lesson_activity(
    state
):

    if state is None:
        return


    state[
        "lesson_teaching_active"
    ] = False

    state[
        "lesson_teaching_level"
    ] = None

    state[
        "lesson_teaching_lesson"
    ] = None

    state[
        "lesson_teaching_section"
    ] = None

    state[
        "lesson_teaching_step"
    ] = 0


# ==========================================
# LEKTIONSABSCHNITT ABSCHLIESSEN
# ==========================================

def complete_generic_section(
    state,
    definition
):

    level = state.get(
        "lesson_teaching_level"
    )

    lesson = state.get(
        "lesson_teaching_lesson"
    )

    section = state.get(
        "lesson_teaching_section"
    )


    if not (
        level
        and
        lesson
        and
        section
    ):

        clear_generic_lesson_activity(
            state
        )

        return ""


    mark_section_completed(
        state,
        level,
        lesson,
        section
    )


    try:

        mark_lesson_section_today(
            state,
            level,
            lesson,
            section
        )

    except Exception as error:

        print(
            f"Generic daily lesson section: {error}"
        )


    try:

        mark_daily_plan_completed(
            state
        )

    except Exception as error:

        print(
            f"Generic daily plan completion: {error}"
        )


    next_section = get_next_incomplete_section(
        state,
        level,
        lesson
    )


    section_complete = render_text(
        definition.get(
            "complete"
        ),
        state,
        level,
        lesson,
        section
    )


    lesson_completed = is_lesson_fully_completed(
        state,
        level,
        lesson
    )


    if lesson_completed:

        remember_completed_lesson(
            state,
            lesson
        )


        try:

            schedule_lesson_review(
                state,
                level,
                lesson
            )

        except Exception as error:

            print(
                f"Generic lesson review scheduling: {error}"
            )


    clear_generic_lesson_activity(
        state
    )


    if next_section:

        state[
            "pending_new_learning"
        ] = {
            "type":
                "new_section",

            "level":
                level,

            "lesson":
                lesson,

            "section":
                next_section,

            "topic":
                next_section
        }

        state[
            "last_question"
        ] = "continue_new_learning"


        base = (
            section_complete
            or
            "Sehr gut! Diesen Teil hast du geschafft."
        )


        return (
            f"{base} "
            f"Als Nächstes kommt „{next_section}“. "
            "Möchtest du weitermachen?"
        )


    base = (
        section_complete
        or
        "Sehr gut!"
    )


    completion = (
        f"{base} Lektion {lesson} ist fertig. "
        "Morgen wiederholen wir sie kurz."
    )


    try:

        recommendation = build_adaptive_recommendation(
            state
        )

    except Exception as error:

        print(
            f"Generic adaptive recommendation: {error}"
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

        recommendation_message = clean_text(
            recommendation.get(
                "message"
            )
        )


        if recommendation_message:

            return (
                f"{completion} "
                f"{recommendation_message}"
            )


    return completion




# ==========================================
# KURS-UMIEJĘTNOŚĆ / MASTERY EVIDENCE
# ==========================================

def _course_skill_key(level, lesson, section):
    slug = normalize_text(section).replace(" ", "_")
    return f"course:{str(level).strip().lower()}:{lesson}:{slug}"


def record_course_step_outcome(state, level, lesson, section, success, final_step=False, partial=False, independent_confirmation=False):
    """Feed real course answers into the shared learner progress model.

    A course skill cannot become mastered before the final step of its section.
    Wrong and partial attempts remain evidence, so Learner Model sees the same
    classification that Course Answer Evaluator used for the learner response.
    """
    status = "PARTIAL" if partial else ("SUCCESS" if success else "NOT_YET")
    outcome = {
        "skill": _course_skill_key(level, lesson, section),
        "expected_outcome": "course_step",
        "status": status,
        "mastery_eligible": bool(success and final_step and not partial),
        "requires_independent_confirmation": True,
        "independent_confirmation": bool(success and independent_confirmation),
    }
    progress = update_learning_progress(state, outcome)
    state["last_course_learning_outcome"] = dict(outcome, progress=progress)
    return progress


# ==========================================
# GENERISCHE ANTWORT VERARBEITEN
# ==========================================

def handle_generic_lesson_teaching(
    user_message,
    state
):

    if not is_generic_lesson_active(
        state
    ):

        return None

    pending_reply = handle_pending_course_model(user_message, state)
    if pending_reply is not None:
        return pending_reply


    level = state.get(
        "lesson_teaching_level"
    )

    lesson = state.get(
        "lesson_teaching_lesson"
    )

    section = state.get(
        "lesson_teaching_section"
    )

    step_number = state.get(
        "lesson_teaching_step",
        1
    )


    real_section, definition = (
        find_generic_section(
            level,
            lesson,
            section
        )
    )


    if not real_section:

        clear_generic_lesson_activity(
            state
        )

        return None


    step = get_step(
        definition,
        step_number
    )


    if not step:

        return complete_generic_section(
            state,
            definition
        )


    support = assess_course_answer(
        user_message,
        step,
        state,
        answer_matches=answer_matches_step(
            user_message,
            step,
            state
        ),
    )

    if support.get("intercept"):
        return build_course_support_reply(
            support,
            step,
            state,
        )

    # An unrelated learner question is a temporary digression, not a wrong
    # grammar/vocabulary answer. Keep the exact lesson step and resume it.
    if (
        not support.get("answer_matches")
        and is_course_digression_question(user_message, step, state)
    ):
        return build_course_digression_resume(
            step, state, level, lesson, real_section, user_message=user_message
        )

    if not support.get("answer_matches"):
        accepted_values = step.get("accepted", [])
        if isinstance(accepted_values, str):
            accepted_values = [accepted_values]
        partial = _sequence_partial_progress(
            user_message,
            accepted_values if isinstance(accepted_values, list) else [],
            state,
        )
        if partial:
            # A partially correct answer is real learning evidence. Previously
            # Nele rendered scaffolding here and returned before the shared
            # learning_progress_v1 store ever saw the PARTIAL result.
            record_course_step_outcome(
                state,
                level,
                lesson,
                real_section,
                False,
                final_step=False,
                partial=True,
            )
            correct_answer = render_text(
                step.get("correct_answer"), state, level, lesson, real_section
            )
            action = choose_course_teacher_action(
                state,
                answer_correct=False,
                partial=partial,
                correct_answer=correct_answer,
            )
            return render_course_teacher_action(action)

        record_course_step_outcome(
            state, level, lesson, real_section, False, final_step=False
        )

        remember_generic_mistake(
            state,
            step,
            user_message
        )


        retry = render_text(
            step.get("retry"),
            state,
            level,
            lesson,
            real_section,
        )
        correct_answer = render_text(
            step.get("correct_answer"),
            state,
            level,
            lesson,
            real_section,
        )
        action = choose_course_teacher_action(
            state,
            answer_correct=False,
            correct_answer=correct_answer,
            retry=retry,
        )
        return render_course_teacher_action(action)


    success = render_text(
        step.get(
            "success"
        ),
        state,
        level,
        lesson,
        real_section
    )


    next_step_number = int(
        step_number
    ) + 1


    next_step = get_step(
        definition,
        next_step_number
    )

    course_progress = record_course_step_outcome(
        state,
        level,
        lesson,
        real_section,
        True,
        final_step=(next_step is None),
    )


    if next_step:

        state[
            "lesson_teaching_step"
        ] = next_step_number


        next_prompt = render_text(
            next_step.get(
                "prompt"
            ),
            state,
            level,
            lesson,
            real_section
        )


        parts = [
            part
            for part in (
                success,
                next_prompt
            )
            if part
        ]


        return " ".join(
            parts
        )


    # The last correct click is not enough by itself. If the shared learner
    # model still says this course skill is not mastered (for example after
    # repeated mistakes), keep the learner in this section and review it.
    if (course_progress or {}).get("status") != "mastered":
        state["lesson_teaching_step"] = 1
        first_step = get_step(definition, 1)
        first_prompt = render_text(
            (first_step or {}).get("prompt"),
            state,
            level,
            lesson,
            real_section,
        )
        action = choose_course_teacher_action(
            state,
            answer_correct=True,
            mastery_status=(course_progress or {}).get("status"),
        )
        reinforcement = render_course_teacher_action(action, prompt=first_prompt)
        return " ".join(part for part in (success, reinforcement) if part)

    completion_answer = complete_generic_section(
        state,
        definition
    )


    parts = [
        part
        for part in (
            success,
            completion_answer
        )
        if part
    ]


    return " ".join(
        parts
    )
