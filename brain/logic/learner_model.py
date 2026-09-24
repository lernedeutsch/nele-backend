"""Learner Model v1: one read model over Nele's existing student memory.

It does not replace Error Memory or Vocabulary Memory. It summarizes them,
together with conversational independence/support, for Teacher Engine.
"""

from brain.memory.error_memory import get_all_errors, get_unmastered_errors
from brain.memory.vocabulary_memory import get_vocabulary_memory, get_words_for_review


MODEL_VERSION = 1


def _safe_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


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

    strengths = []
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
    }
    state["learner_model_v1"] = model
    return model


def get_learner_model(state):
    return dict((state or {}).get("learner_model_v1") or {})
