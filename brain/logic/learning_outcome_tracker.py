"""Learning Outcome Tracker v1.

Evaluates the learner's next message against the previous Learning Action
Executor expectation and writes a compact outcome history into state.
"""

import re

from brain.memory.vocabulary_memory import remember_correct_answer, remember_mistake
from brain.logic.learning_progress_engine import update_learning_progress


TRACKER_VERSION = 1


def _norm(text):
    return re.sub(r"[^a-zäöüß0-9 ]+", "", str(text or "").strip().lower())


def _words(text):
    return [w for w in _norm(text).split() if w]


def _model_matches(user_message, model):
    return bool(model) and _norm(user_message) == _norm(model)


def evaluate_learning_outcome(user_message, state):
    state = state or {}
    previous = state.get("learning_action_executor_v1") or {}
    expected = previous.get("expects_outcome")
    action = previous.get("action")
    target_word = previous.get("target_word")
    model = previous.get("model")

    if not expected:
        return None

    text_words = _words(user_message)
    word_count = len(text_words)
    status = "PARTIAL"
    reason = "response_received"

    if expected == "repeat_correct_form":
        if _model_matches(user_message, model):
            status, reason = "SUCCESS", "correct_form_repeated"
        else:
            status, reason = "NOT_YET", "correct_form_not_repeated"

    elif expected == "use_full_sentence":
        if _model_matches(user_message, model) or word_count >= 3:
            status, reason = "SUCCESS", "full_sentence_used"
        elif word_count >= 1:
            status, reason = "PARTIAL", "answer_still_short"
        else:
            status, reason = "NOT_YET", "no_usable_answer"

    elif expected == "recall_target_word":
        if target_word and _norm(target_word) in text_words:
            status, reason = "SUCCESS", "target_word_recalled"
            remember_correct_answer(target_word, state)
        else:
            status, reason = "NOT_YET", "target_word_not_recalled"
            if target_word:
                remember_mistake(target_word, state)

    elif expected == "notice_new_word":
        if target_word and _norm(target_word) in text_words:
            status, reason = "SUCCESS", "new_word_used"
            remember_correct_answer(target_word, state)
        else:
            status, reason = "PARTIAL", "new_word_presented_not_used_yet"

    elif expected == "answer_with_support":
        if word_count >= 1 and _norm(user_message) not in {"?", "ich weiß nicht", "weiss nicht", "weiß nicht"}:
            status, reason = "SUCCESS", "answered_with_support"
        else:
            status, reason = "NOT_YET", "still_needs_support"

    elif expected == "independent_answer":
        if word_count >= 3:
            status, reason = "SUCCESS", "independent_full_answer"
        elif word_count:
            status, reason = "PARTIAL", "independent_answer_short"
        else:
            status, reason = "NOT_YET", "no_independent_answer"

    elif expected in {"continue_after_correction", "continue_conversation"}:
        if word_count:
            status, reason = "SUCCESS", "conversation_continued"
        else:
            status, reason = "NOT_YET", "conversation_not_continued"

    outcome = {
        "version": TRACKER_VERSION,
        "source_action": action,
        "expected_outcome": expected,
        "status": status,
        "reason": reason,
        "target_word": target_word,
        "model": model,
    }

    history = state.setdefault("learning_outcomes", [])
    history.append(outcome)
    if len(history) > 50:
        del history[:-50]
    state["last_learning_outcome"] = outcome
    outcome["progress"] = update_learning_progress(state, outcome)
    return outcome
