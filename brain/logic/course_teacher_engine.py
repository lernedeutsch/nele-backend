"""Central pedagogical decision engine for course mode.

Course content engines report evidence; this module decides how Nele teaches
next. It intentionally contains no lesson- or dialogue-specific phrases.
"""

from brain.logic.learner_model import build_learner_model
from brain.logic.speaking_support import progressive_course_support, register_course_success


def choose_course_teacher_action(
    state,
    *,
    answer_correct=None,
    partial=None,
    mastery_status=None,
    correct_answer=None,
    retry=None,
):
    """Return one shared course teaching decision from current learner state."""
    model = build_learner_model(state or {})
    course = model.get("course_learning") or {}

    if partial:
        action = {
            "action": "scaffold_partial",
            "reason": "partially_correct",
            "partial": dict(partial),
            "model": correct_answer,
        }
    elif answer_correct is False:
        target = str(correct_answer or "").strip()
        hint = str(retry or "").strip()
        support = progressive_course_support(
            target,
            state,
            first_hint=hint,
        ) if target else (hint or "Fast. Noch einmal.")
        action = {
            "action": "correct_and_retry",
            "reason": "answer_not_yet",
            "model": correct_answer,
            "retry": retry,
            "support": support,
        }
    elif mastery_status and mastery_status != "mastered":
        action = {
            "action": "reinforce",
            "reason": "skill_not_mastered",
            "skill": course.get("next_skill"),
        }
    else:
        if answer_correct is True:
            register_course_success(state)
        decision = course.get("teaching_decision") or "practice"
        action = {
            "action": decision,
            "reason": course.get("next_reason") or "course_progress",
            "skill": course.get("next_skill"),
        }

    state["course_teacher_action"] = dict(action)
    return action


def render_course_teacher_action(action, *, prompt=None):
    """Render generic pedagogical support without owning lesson content."""
    action = action or {}
    kind = action.get("action")

    if kind == "scaffold_partial":
        partial = action.get("partial") or {}
        matched = partial.get("matched")
        total = partial.get("total")
        model = action.get("model")
        if matched is not None and total is not None and model:
            return f"Gut, {matched} von {total} sind richtig. Mach weiter: „{model}“"

    if kind == "correct_and_retry":
        support = str(action.get("support") or "").strip()
        if support:
            return support
        retry = str(action.get("retry") or "").strip()
        if retry:
            return retry
        model = str(action.get("model") or "").strip()
        if model:
            return f"Fast. Richtig ist: „{model}“ Versuch es bitte noch einmal."
        return "Fast. Versuch es bitte noch einmal."

    if kind == "reinforce":
        parts = ["Gut, wir festigen das noch einmal, bevor wir weitergehen."]
        if prompt:
            parts.append(str(prompt).strip())
        return " ".join(part for part in parts if part)

    return str(prompt or "").strip()
