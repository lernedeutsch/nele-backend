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

    # First let every important extra skill get at least one result.
    for name in UPGRADE_ACTIVITY_ORDER:
        data = skills.get(name, {})
        if int(data.get("attempts", 0) or 0) == 0:
            return name

    # Afterwards choose the lowest rolling average.
    return min(
        UPGRADE_ACTIVITY_ORDER,
        key=lambda name: float(
            skills.get(name, {}).get("score_avg", 0) or 0
        ),
    )


def _existing_plan_should_go_first(existing):
    if not isinstance(existing, dict):
        return False

    priority = str(existing.get("priority", "") or "").strip().lower()
    if priority in {"error_review", "vocabulary_review", "lesson_review"}:
        return True

    plan_type = str(existing.get("type", "") or "").strip().lower()

    # The normal course remains the main path.
    # Nele-3 activities supplement it instead of interrupting it.
    return plan_type in {
        "start",
        "new_learning",
        "new_section",
        "new_lesson",
        "continue_lesson",
    }


def select_next_action(state):
    """Choose the next learning action while keeping Nele 1's course authoritative."""

    existing = get_teacher_learning_plan(state)

    if _existing_plan_should_go_first(existing):
        action = {
            "type": "existing_teacher_plan",
            "priority": (
                str(existing.get("priority", "") or "").strip().lower()
                if isinstance(existing, dict)
                else ""
            ),
            "message": (
                existing.get("message")
                if isinstance(existing, dict)
                else None
            ),
            "plan": existing,
        }
        set_last_action(state, action)
        return action

    # Once the current course step is completed, use Nele-3 activities
    # to strengthen the weakest / not-yet-practised skill.
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
        "message": messages.get(
            activity,
            "Wir machen jetzt eine kurze Übung.",
        ),
        "existing_plan": existing,
    }
    set_last_action(state, action)
    return action
