"""One canonical service for starting or reopening a Nele conversation."""

from brain.logic.memory import (
    get_conversation_state,
    save_conversation_state,
)
from brain.logic.session_state import prepare_new_conversation
from brain.logic.activity_resume import resume_current_training
from brain.logic.welcome import generate_welcome_reply
from brain.nele3_upgrade.state import (
    ensure_upgrade_state,
    start_upgrade_session,
)


def start_conversation_session(
    session_id,
    *,
    new_conversation=False,
):
    """Start Nele for one learner through the single production session flow."""

    state = get_conversation_state(session_id)
    ensure_upgrade_state(state)

    if new_conversation:
        prepare_new_conversation(state)

    start_upgrade_session(state)

    # A normal page reopen must show the prompt that will actually own the
    # learner's next answer. Otherwise Nele can ask a generic wellbeing
    # question while an unfinished course dialogue silently consumes the turn.
    if not new_conversation:
        resume_reply = resume_current_training(state)
        if resume_reply:
            save_conversation_state(session_id)
            return resume_reply

    save_conversation_state(session_id)
    return generate_welcome_reply(session_id)
