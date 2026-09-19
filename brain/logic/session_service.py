"""One canonical service for starting or reopening a Nele conversation."""

from brain.logic.memory import (
    get_conversation_state,
    save_conversation_state,
)
from brain.logic.session_state import prepare_new_conversation
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
    save_conversation_state(session_id)

    return generate_welcome_reply(session_id)
