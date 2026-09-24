from brain.logic.topic_follow_up_engine import (
    next_topic_follow_up,
    reset_topic_questions,
)


def test_follow_ups_do_not_repeat():
    state = {"conversation_vocabulary_topic": "freizeit"}

    first = next_topic_follow_up(state)
    second = next_topic_follow_up(state)

    assert first
    assert second
    assert first != second


def test_topic_has_finite_sequence():
    state = {"conversation_vocabulary_topic": "wetter"}

    answers = [
        next_topic_follow_up(state)
        for _ in range(5)
    ]

    assert len([item for item in answers if item]) == 4
    assert answers[-1] is None


def test_topics_keep_separate_history():
    state = {}

    freizeit = next_topic_follow_up(state, "freizeit")
    wetter = next_topic_follow_up(state, "wetter")

    assert freizeit
    assert wetter
    assert freizeit != wetter


def test_reset_topic_questions():
    state = {"conversation_vocabulary_topic": "essen"}

    first = next_topic_follow_up(state)
    next_topic_follow_up(state)

    reset_topic_questions(state, "essen")

    assert next_topic_follow_up(state) == first
