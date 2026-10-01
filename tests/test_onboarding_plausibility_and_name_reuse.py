import uuid

from brain.logic.memory import get_conversation_state
from brain.logic.onboarding import get_onboarding_retry
from brain.logic.user_info import extract_user_information


def _session():
    return "test-onboarding-plausibility-" + uuid.uuid4().hex


def test_gut_is_not_fabricated_as_residence():
    reply = get_onboarding_retry(3, "gut")

    assert reply == (
        "Sag bitte als ganzen Satz, "
        "zum Beispiel: "
        "„Ich wohne in Heidelberg.“"
    )
    assert "Gut" not in reply


def test_age_does_not_replace_known_name_or_reset_to_origin():
    session_id = _session()
    state = get_conversation_state(session_id)
    state["name"] = "Anna"
    state["last_question"] = None

    reply = extract_user_information("Ich bin 30 Jahre alt", session_id)

    assert reply is None
    assert state["name"] == "Anna"
    assert state["last_question"] is None
