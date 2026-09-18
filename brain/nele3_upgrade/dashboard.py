from brain.memory.daily_learning import get_daily_learning_summary
from brain.memory.error_memory import get_error_memory
from brain.memory.next_learning_step import get_teacher_learning_plan
from brain.memory.pronunciation_memory import get_pronunciation_memory
from brain.memory.student_progress import get_progress_summary
from brain.memory.vocabulary_memory import get_vocabulary_memory
from brain.nele3_upgrade.state import ensure_upgrade_state, get_skills


def _count_due_vocabulary(vocabulary):
    count = 0
    for item in (vocabulary or {}).values():
        if isinstance(item, dict) and (item.get("needs_review") or item.get("next_review_at")):
            count += 1
    return count


def build_dashboard(state):
    upgrade = ensure_upgrade_state(state)

    try:
        progress = get_progress_summary(state)
    except Exception:
        progress = {}

    try:
        daily = get_daily_learning_summary(state)
    except Exception:
        daily = {}

    try:
        teacher_plan = get_teacher_learning_plan(state)
    except Exception as error:
        teacher_plan = {"error": str(error)}

    try:
        vocabulary = get_vocabulary_memory(state)
    except Exception:
        vocabulary = {}

    try:
        errors = get_error_memory(state)
    except Exception:
        errors = {}

    try:
        pronunciation = get_pronunciation_memory(state)
    except Exception:
        pronunciation = {}

    return {
        "ok": True,
        "progress": progress,
        "today": daily,
        "skills": get_skills(state),
        "teacher_plan": teacher_plan,
        "memory": {
            "vocabulary_items": len(vocabulary or {}),
            "vocabulary_due_or_scheduled": _count_due_vocabulary(vocabulary),
            "error_types": len(errors or {}),
            "pronunciation_words": len((pronunciation or {}).get("words", {})),
            "pronunciation_sounds": len((pronunciation or {}).get("sounds", {})),
        },
        "session": upgrade.get("session", {}),
        "version": upgrade.get("version"),
    }


def dashboard_text(state):
    data = build_dashboard(state)
    progress = data.get("progress", {})
    today = data.get("today", {})
    skills = data.get("skills", {})

    level = progress.get("current_level", "A1")
    lesson = progress.get("current_lesson", 1)
    exercises = today.get("completed_exercises", 0)

    attempted = [
        (name, item)
        for name, item in skills.items()
        if int(item.get("attempts", 0) or 0) > 0
    ]
    if attempted:
        weakest_name, weakest = min(attempted, key=lambda x: float(x[1].get("score", 0) or 0))
        weak_text = f" Am meisten lohnt sich jetzt: {weakest_name}."
    else:
        weak_text = " Heute sammeln wir zuerst ein paar Lernergebnisse."

    return f"Du bist bei {level}, Lektion {lesson}. Heute hast du {exercises} Übungen abgeschlossen.{weak_text}"
