"""Central state management for a Nele conversation session.

This module separates transient conversation state from durable learning memory.
It never deletes Student Memory, lesson progress, vocabulary, errors,
pronunciation history, Daily Learning Memory, user facts, or learner identity.
"""

from brain.nele3_upgrade.state import (
    clear_pending_recommendation,
    record_event,
    set_active_task,
)


def reset_session_start_flow(state):
    if not isinstance(state, dict):
        return

    state["session_start_flow"] = {
        "active": True,
        "vocabulary_done": False,
        "errors_done": False,
        "last_lesson_recap_done": False,
        "lesson_review_done": False,
    }


def _clear_common_transient_state(state):
    """Clear old one-turn/session modes that must not consume wellbeing."""

    if not isinstance(state, dict):
        return

    # Personalization exercise.
    state["personalization_exercise"] = None

    # Vocabulary exercise.
    state["vocabulary_practice_active"] = False
    state["vocabulary_practice_word"] = None
    state["vocabulary_practice_type"] = None

    # Error exercise.
    state["error_practice_active"] = False
    state["error_practice_type"] = None
    state["error_practice_step"] = 0
    state["error_practice_attempts"] = 0
    state["error_practice_used_hint"] = False
    state["error_practice_example_context"] = None
    state["error_practice_example_wrong"] = None
    state["error_practice_example_correct"] = None

    # Lesson review exercise.
    state["lesson_review_training_active"] = False
    state["lesson_review_training_level"] = None
    state["lesson_review_training_lesson"] = None
    state["lesson_review_training_step"] = 0
    state["lesson_review_training_correct"] = 0
    state["lesson_review_training_wrong"] = 0

    # Old offers must be recalculated for the new session.
    state["pending_new_learning"] = None
    state["pending_error_review"] = None
    clear_pending_recommendation(state)

    # Short-lived conversation references.
    state["current_topic"] = None
    state["current_comparison"] = None
    state["current_expression"] = None
    state["last_example_expression"] = None
    state["example_index"] = -1

    reset_session_start_flow(state)


def prepare_page_reopen(state):
    """Start a normal page visit while preserving resumable learning.

    A currently active Nele-3 task and an unfinished lesson step are preserved.
    Old vocabulary/error/review modes are cleared so the wellbeing answer cannot
    accidentally be interpreted as an exercise answer.
    """

    _clear_common_transient_state(state)


def prepare_new_conversation(state):
    """Start a genuinely fresh conversation for the same learner.

    Durable learning memory stays intact. Every transient active exercise,
    including old lesson-teaching state and Nele-3 active_task, is cleared.
    """

    if not isinstance(state, dict):
        return

    _clear_common_transient_state(state)

    # Nele-3 active activity.
    set_active_task(state, None)

    # Legacy lesson engine active step. Lesson progress itself is preserved.
    state["lesson_teaching_active"] = False
    state["lesson_teaching_section"] = None
    state["lesson_teaching_step"] = 0

    # The next response will be the new wellbeing flow.
    state["last_question"] = None

    record_event(
        state,
        "new_conversation",
        detail={"learning_memory_preserved": True},
    )
