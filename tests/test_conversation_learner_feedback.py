from brain.logic.learner_feedback import (
    prepare_message_with_feedback,
)


def test_mit_mein_mann_is_corrected_and_remembered():
    state = {}

    corrected, feedback = prepare_message_with_feedback(
        "Mit mein Mann",
        state,
    )

    assert corrected == "Mit meinem Mann."
    assert "Mit meinem Mann" in feedback
    assert state.get("error_memory")


def test_fahren_is_corrected_for_conversation():
    state = {}

    corrected, feedback = prepare_message_with_feedback(
        "Ich fahren gern Fahrrad",
        state,
    )

    assert corrected == "Ich fahre gern Fahrrad."
    assert "Ich fahre gern Fahrrad" in feedback


def test_arbeiten_is_corrected_for_conversation():
    corrected, feedback = prepare_message_with_feedback(
        "Ich arbeiten heute",
        {},
    )

    assert corrected == "Ich arbeite heute."
    assert feedback


def test_correct_sentence_is_not_changed():
    corrected, feedback = prepare_message_with_feedback(
        "Ich fahre gern Fahrrad.",
        {},
    )

    assert corrected == "Ich fahre gern Fahrrad."
    assert feedback is None
