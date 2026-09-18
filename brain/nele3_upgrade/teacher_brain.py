from brain.memory.next_learning_step import get_teacher_learning_plan
from brain.memory.student_progress import get_current_level
from brain.nele3_upgrade.state import get_skills, set_last_action


UPGRADE_ACTIVITY_ORDER = [
    "listening",
    "writing",
    "dialogue",
    "work_german",
    "pronunciation",
    "speaking",
]


def _weakest_upgrade_skill(state):
    skills = get_skills(state)

    # First make sure every important skill has at least one attempt.
    for name in UPGRADE_ACTIVITY_ORDER:
        data = skills.get(name, {})
        if int(data.get("attempts", 0) or 0) == 0:
            return name

    # Afterwards choose the lowest rolling score.
    return min(
        UPGRADE_ACTIVITY_ORDER,
        key=lambda name: float(skills.get(name, {}).get("score", 0) or 0),
    )


def select_next_action(state):
    """Select the next sensible action without replacing Nele 1's existing teacher brain."""

    existing = get_teacher_learning_plan(state)
    priority = str(existing.get("priority", "") or "").strip().lower() if isinstance(existing, dict) else ""

    # Existing Nele 1 memories remain authoritative for due reviews.
    if priority in {"error_review", "vocabulary_review", "lesson_review"}:
        action = {
            "type": "existing_teacher_plan",
            "priority": priority,
            "message": existing.get("message"),
            "plan": existing,
        }
        set_last_action(state, action)
        return action

    level = get_current_level(state) or "A1"
    activity = _weakest_upgrade_skill(state)

    messages = {
        "listening": "Wir machen jetzt eine kurze Hörübung.",
        "writing": "Wir machen jetzt eine kurze Schreibübung.",
        "dialogue": "Wir üben jetzt einen kurzen Alltagsdialog.",
        "work_german": "Wir üben jetzt kurz Deutsch für die Arbeit im Hotel.",
        "pronunciation": "Wir trainieren jetzt kurz deine Aussprache.",
        "speaking": "Wir machen jetzt eine kurze Sprechübung.",
    }

    action = {
        "type": "upgrade_activity",
        "activity": activity,
        "level": level,
        "message": messages.get(activity, "Wir machen jetzt eine kurze Übung."),
        "existing_plan": existing,
    }
    set_last_action(state, action)
    return action
