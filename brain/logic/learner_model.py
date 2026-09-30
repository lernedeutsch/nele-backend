"""Learner Model v2: one pedagogical read model over Nele's student memory.

It does not replace Error Memory or Vocabulary Memory. It summarizes them,
together with conversational independence/support, for Teacher Engine.
"""

from brain.memory.error_memory import get_all_errors, get_unmastered_errors
from brain.memory.vocabulary_memory import get_vocabulary_memory, get_words_for_review
from brain.logic.learning_progress_engine import summarize_learning_progress
from brain.logic.curriculum_skill_graph import get_curriculum_state, choose_next_curriculum_skill


MODEL_VERSION = 2


def _safe_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _course_learning_state(state, curriculum, next_skill):
    """Expose one course-facing truth for mastery, review and routing."""
    progress = ((((state or {}).get("learning_progress_v1") or {}).get("skills")) or {})
    current = (next_skill or {}).get("skill")
    item = dict(progress.get(current) or {}) if current else {}
    reason = (next_skill or {}).get("reason")
    if not current:
        decision = "course_complete"
    elif reason == "course_review":
        decision = "review"
    elif reason == "course_mastery_in_progress":
        decision = "practice"
    elif reason == "course_prerequisites_met":
        decision = "teach_next"
    else:
        decision = "practice"
    return {
        "mastered": list(curriculum.get("course_mastered") or []),
        "in_progress": list(curriculum.get("course_in_progress") or []),
        "review_due": list(curriculum.get("course_needs_review") or []),
        "ready": list(curriculum.get("course_ready") or []),
        "blocked": list(curriculum.get("course_blocked") or []),
        "next_skill": current,
        "next_reason": reason,
        "next_status": item.get("status"),
        "teaching_decision": decision,
    }


def build_learner_model(state):
    state = state or {}
    free = state.get("free_conversation") or {}
    progress = state.get("student_progress") or {}
    vocabulary = get_vocabulary_memory(state)
    review_words = list(get_words_for_review(state))

    mastered_words = []
    learning_words = []
    for word, item in vocabulary.items():
        if not isinstance(item, dict):
            continue
        seen = _safe_int(item.get("seen"))
        correct = _safe_int(item.get("correct"))
        mistakes = _safe_int(item.get("mistakes"))
        streak = _safe_int(item.get("correct_streak"))
        if correct >= 3 and streak >= 2 and mistakes <= correct and not item.get("needs_review"):
            mastered_words.append(word)
        elif seen or correct or mistakes:
            learning_words.append(word)

    all_errors = get_all_errors(state)
    unmastered = get_unmastered_errors(state)
    if not isinstance(all_errors, dict):
        all_errors = {}
    if isinstance(unmastered, dict):
        weak_error_types = list(unmastered.keys())
    else:
        weak_error_types = list(unmastered or [])

    independent = _safe_int(free.get("independent_turns"))
    struggles = _safe_int(free.get("struggle_turns"))
    adaptive_support = _safe_int(free.get("support_level")) or 1

    if adaptive_support >= 3 or struggles >= 2:
        autonomy = "needs_support"
    elif independent >= 3 and struggles == 0:
        autonomy = "independent"
    else:
        autonomy = "developing"

    learning_progress = summarize_learning_progress(state)
    curriculum = get_curriculum_state(state)
    next_curriculum_skill = choose_next_curriculum_skill(state)
    course_learning = _course_learning_state(state, curriculum, next_curriculum_skill)
    recent_outcomes = list(state.get("learning_outcomes") or [])[-10:]
    recent_knowledge_usage = list(free.get("knowledge_usage") or [])[-10:]
    outcome_successes = sum(1 for item in recent_outcomes if item.get("status") == "SUCCESS")
    outcome_not_yet = sum(1 for item in recent_outcomes if item.get("status") == "NOT_YET")
    outcome_partials = sum(1 for item in recent_outcomes if item.get("status") == "PARTIAL")

    strengths = []
    if outcome_successes >= 3 and outcome_successes > outcome_not_yet:
        strengths.append("learning_response")
    if mastered_words:
        strengths.append("vocabulary")
    if autonomy == "independent":
        strengths.append("conversation_independence")

    weaknesses = []
    if review_words:
        weaknesses.append("vocabulary_review")
    if weak_error_types:
        weaknesses.append("recurring_errors")
    if autonomy == "needs_support":
        weaknesses.append("conversation_support")
    if outcome_not_yet >= 2 and outcome_not_yet > outcome_successes:
        weaknesses.append("learning_actions_not_yet_effective")

    model = {
        "version": MODEL_VERSION,
        "course_level": str(progress.get("current_level") or "A1.1"),
        "autonomy": autonomy,
        "adaptive_support": adaptive_support,
        "independent_turns": independent,
        "struggle_turns": struggles,
        "vocabulary": {
            "mastered": sorted(mastered_words),
            "learning": sorted(learning_words),
            "review_due": sorted(review_words),
            "mastered_count": len(mastered_words),
            "learning_count": len(learning_words),
        },
        "errors": {
            "known_types": sorted(all_errors.keys()),
            "unmastered_types": sorted(weak_error_types),
            "unmastered_count": len(weak_error_types),
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "learning_progress": learning_progress,
        "curriculum": curriculum,
        "next_curriculum_skill": next_curriculum_skill,
        "course_learning": course_learning,
        "knowledge_usage": {
            "recent_count": len(recent_knowledge_usage),
            "recent": [dict(item) for item in recent_knowledge_usage if isinstance(item, dict)],
        },
        "learning_outcomes": {
            "recent_count": len(recent_outcomes),
            "success": outcome_successes,
            "partial": outcome_partials,
            "not_yet": outcome_not_yet,
            "last": dict(state.get("last_learning_outcome") or {}),
        },
    }
    state["learner_model_v2"] = model
    state["learner_model_v1"] = model  # compatibility for existing consumers
    return model


def get_learner_model(state):
    state = state or {}
    return dict(state.get("learner_model_v2") or state.get("learner_model_v1") or {})
