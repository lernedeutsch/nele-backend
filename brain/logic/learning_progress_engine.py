"""Learning Progress Engine v1.

Turns individual learning outcomes into durable skill mastery states.
It does not choose the next teaching action; Teacher Policy consumes the
progress summary through Learner Model.
"""

PROGRESS_VERSION = 1
STATES = ("introduced", "practicing", "improving", "mastered", "needs_review")


def _skill_key(outcome):
    explicit = (outcome or {}).get("skill")
    if explicit:
        return str(explicit).strip()
    expected = (outcome or {}).get("expected_outcome")
    target = (outcome or {}).get("target_word")
    model = (outcome or {}).get("model")
    if expected in {"recall_target_word", "notice_new_word"} and target:
        return f"vocabulary:{str(target).strip().lower()}"
    if expected == "repeat_correct_form" and model:
        return f"correct_form:{str(model).strip().lower()}"
    mapping = {
        "use_full_sentence": "conversation:full_sentence",
        "answer_with_support": "conversation:supported_answer",
        "independent_answer": "conversation:independent_answer",
        "continue_after_correction": "conversation:continue_after_correction",
        "continue_conversation": "conversation:continuation",
    }
    return mapping.get(expected)


def _derive_status(item):
    attempts = int(item.get("attempts", 0) or 0)
    successes = int(item.get("successes", 0) or 0)
    partials = int(item.get("partials", 0) or 0)
    failures = int(item.get("not_yet", 0) or 0)
    streak = int(item.get("success_streak", 0) or 0)
    previous = item.get("status")

    # A failure after mastery deliberately reopens the skill for review.
    if previous == "mastered" and item.get("last_result") == "NOT_YET":
        return "needs_review"
    mastery_eligible = item.get("mastery_eligible", True)
    requires_independent_confirmation = bool(item.get("requires_independent_confirmation", False))
    independent_confirmations = int(item.get("independent_confirmations", 0) or 0)
    confirmation_ok = (
        not requires_independent_confirmation
        or independent_confirmations >= 1
    )
    if mastery_eligible and confirmation_ok and successes >= 3 and streak >= 2 and successes > failures:
        return "mastered"
    if failures >= 2 and failures >= successes:
        return "needs_review"
    if successes >= 2 or (successes >= 1 and partials >= 1):
        return "improving"
    if attempts >= 2 or successes or partials:
        return "practicing"
    return "introduced"


def update_learning_progress(state, outcome):
    if not outcome:
        return None
    key = _skill_key(outcome)
    if not key:
        return None

    store = state.setdefault("learning_progress_v1", {"version": PROGRESS_VERSION, "skills": {}})
    skills = store.setdefault("skills", {})
    item = skills.setdefault(key, {
        "skill": key,
        "status": "introduced",
        "attempts": 0,
        "successes": 0,
        "partials": 0,
        "not_yet": 0,
        "success_streak": 0,
        "last_result": None,
        "target_word": outcome.get("target_word"),
        "model": outcome.get("model"),
        "mastery_eligible": bool(outcome.get("mastery_eligible", True)),
        "requires_independent_confirmation": bool(outcome.get("requires_independent_confirmation", False)),
        "independent_confirmations": 0,
    })

    result = outcome.get("status")
    if "mastery_eligible" in outcome:
        item["mastery_eligible"] = bool(outcome.get("mastery_eligible"))
    if "requires_independent_confirmation" in outcome:
        item["requires_independent_confirmation"] = bool(outcome.get("requires_independent_confirmation"))
    if outcome.get("independent_confirmation") and outcome.get("status") == "SUCCESS":
        item["independent_confirmations"] = int(item.get("independent_confirmations", 0) or 0) + 1
    item["attempts"] += 1
    item["last_result"] = result
    if result == "SUCCESS":
        item["successes"] += 1
        item["success_streak"] += 1
    elif result == "PARTIAL":
        item["partials"] += 1
        item["success_streak"] = 0
    elif result == "NOT_YET":
        item["not_yet"] += 1
        item["success_streak"] = 0

    item["status"] = _derive_status(item)
    state["last_learning_progress"] = dict(item)
    return dict(item)


def get_learning_progress(state):
    store = (state or {}).get("learning_progress_v1") or {}
    return dict(store.get("skills") or {})


def summarize_learning_progress(state):
    skills = get_learning_progress(state)
    by_status = {status: [] for status in STATES}
    for key, item in skills.items():
        status = item.get("status", "introduced")
        by_status.setdefault(status, []).append(key)
    for values in by_status.values():
        values.sort()
    return {
        "version": PROGRESS_VERSION,
        "skill_count": len(skills),
        "by_status": by_status,
        "mastered_count": len(by_status.get("mastered", [])),
        "review_count": len(by_status.get("needs_review", [])),
    }
