import uuid

from brain.logic.user_info import extract_user_information
from brain.logic.memory import get_conversation_state
from brain.memory.user_facts import get_user_fact


def _session():
    return "test-origin-case-" + uuid.uuid4().hex


def test_origin_with_inflected_article_keeps_article_lowercase():
    session_id = _session()
    reply = extract_user_information("Ich komme aus der Schweiz.", session_id)
    state = get_conversation_state(session_id)

    assert "Du kommst aus der Schweiz." in reply
    assert "aus Der Schweiz" not in reply
    assert get_user_fact(state, "origin") == "der Schweiz"


def test_origin_with_plural_article_keeps_article_lowercase_and_acronym_case():
    session_id = _session()
    reply = extract_user_information("Ich komme aus den USA.", session_id)
    state = get_conversation_state(session_id)

    assert "Du kommst aus den USA." in reply
    assert "aus Den USA" not in reply
    assert get_user_fact(state, "origin") == "den USA"


def test_plain_country_origin_is_still_capitalized():
    session_id = _session()
    reply = extract_user_information("ich komme aus polen", session_id)
    state = get_conversation_state(session_id)

    assert "Du kommst aus Polen." in reply
    assert get_user_fact(state, "origin") == "Polen"
