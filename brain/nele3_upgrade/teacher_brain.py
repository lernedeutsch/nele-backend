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


SKILL_LABELS = {
    "listening": "Hören",
    "writing": "Schreiben",
    "dialogue": "Dialoge",
    "work_german": "Arbeitsdeutsch",
    "pronunciation": "Aussprache",
    "speaking": "Sprechen",
}


def _attempts(data):
    try:
        return max(0, int(data.get("attempts", 0) or 0))
    except (TypeError, ValueError):
        return 0


def _score(data):
    try:
        return max(0.0, min(100.0, float(data.get("score_avg", 0) or 0)))
    except (TypeError, ValueError):
        return 0.0


def _weakest_upgrade_skill(state, excluded=None):
    skills = get_skills(state)
    excluded = set(excluded or [])

    available = [
        name
        for name in UPGRADE_ACTIVITY_ORDER
        if name not in excluded
    ]

    if not available:
        return None

    # Najpierw opieramy się na rzeczywistych wynikach.
    # Jedna przypadkowa odpowiedź nie powinna od razu
    # definiować "słabej strony".
    reliable = [
        name
        for name in available
        if _attempts(skills.get(name, {})) >= 2
    ]

    if reliable:
        weakest = min(
            reliable,
            key=lambda name: _score(skills.get(name, {})),
        )
        if _score(skills.get(weakest, {})) < 85:
            return weakest

    # Jeżeli mamy tylko pojedyncze próby, reagujemy dopiero
    # na wyraźnie słabszy wynik.
    attempted = [
        name
        for name in available
        if _attempts(skills.get(name, {})) > 0
    ]

    if attempted:
        weakest = min(
            attempted,
            key=lambda name: _score(skills.get(name, {})),
        )
        if _score(skills.get(weakest, {})) < 70:
            return weakest

    # Gdy dotychczasowe wyniki są dobre, Nele rozwija obszar,
    # którego uczeń jeszcze prawie nie ćwiczył.
    for name in available:
        if _attempts(skills.get(name, {})) == 0:
            return name

    # Wszystko było już ćwiczone i nie ma wyraźnej słabości:
    # wybieramy najmniej pewny obszar.
    return min(
        available,
        key=lambda name: _score(skills.get(name, {})),
    )


def build_adaptive_recommendation(state, excluded=None):
    """Zbuduj krótką, uzasadnioną propozycję następnego treningu."""
    skills = get_skills(state)
    excluded = list(dict.fromkeys(excluded or []))
    activity = _weakest_upgrade_skill(state, excluded=excluded)

    if not activity:
        return None
    data = skills.get(activity, {})
    attempts = _attempts(data)
    score = _score(data)

    attempted = [
        name
        for name in UPGRADE_ACTIVITY_ORDER
        if _attempts(skills.get(name, {})) > 0
    ]

    strongest = None
    if attempted:
        strongest = max(
            attempted,
            key=lambda name: _score(skills.get(name, {})),
        )

    label = SKILL_LABELS.get(activity, activity)

    if attempts >= 2 and score < 85:
        reason = (
            f"{label} können wir noch etwas üben."
        )
    elif attempts > 0 and score < 70:
        reason = (
            f"{label} haben wir schon ein bisschen geübt. "
            "Das machen wir noch sicherer."
        )
    elif attempts == 0:
        if strongest:
            strong_label = SKILL_LABELS.get(strongest, strongest)
            reason = (
                f"{strong_label} haben wir schon geübt. "
                f"{label} noch kaum."
            )
        else:
            reason = (
                f"{label} haben wir noch kaum trainiert."
            )
    else:
        reason = (
            f"{label} können wir noch ein bisschen üben."
        )

    activity_phrases = {
        "listening": "eine kurze Hörübung",
        "writing": "eine kurze Schreibübung",
        "dialogue": "einen kurzen Alltagsdialog",
        "work_german": "eine kurze Arbeitsdeutsch-Übung",
        "pronunciation": "eine kurze Ausspracheübung",
        "speaking": "eine kurze Sprechübung",
    }

    phrase = activity_phrases.get(activity, "eine kurze Übung")

    return {
        "type": "adaptive_recommendation",
        "activity": activity,
        "label": label,
        "attempts": attempts,
        "score": round(score, 1),
        "reason": reason,
        "excluded": excluded,
        "message": (
            f"{reason} Machen wir jetzt {phrase}?"
        ),
    }


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
    recommendation = build_adaptive_recommendation(state)
    activity = recommendation["activity"]

    action = {
        "type": "upgrade_activity",
        "activity": activity,
        "level": level,
        "message": recommendation.get("reason"),
        "recommendation": recommendation,
        "existing_plan": existing,
    }
    set_last_action(state, action)
    return action
