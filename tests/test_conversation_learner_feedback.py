import unittest

from brain.logic.learner_feedback import (
    prepare_message_with_feedback,
)


class GeneratedTests(unittest.TestCase):
    def test_mit_mein_mann_is_corrected_and_remembered(self):
        state = {}

        corrected, feedback = prepare_message_with_feedback(
        "Mit mein Mann",
        state,
        )

        self.assertTrue(corrected == "Mit meinem Mann.")
        self.assertTrue("Mit meinem Mann" in feedback)
        self.assertTrue(state.get("error_memory"))


    def test_fahren_is_corrected_for_conversation(self):
        state = {}

        corrected, feedback = prepare_message_with_feedback(
        "Ich fahren gern Fahrrad",
        state,
        )

        self.assertTrue(corrected == "Ich fahre gern Fahrrad.")
        self.assertTrue("Ich fahre gern Fahrrad" in feedback)


    def test_arbeiten_is_corrected_for_conversation(self):
        corrected, feedback = prepare_message_with_feedback(
        "Ich arbeiten heute",
        {},
        )

        self.assertTrue(corrected == "Ich arbeite heute.")
        self.assertTrue(feedback)


    def test_correct_sentence_is_not_changed(self):
        corrected, feedback = prepare_message_with_feedback(
        "Ich fahre gern Fahrrad.",
        {},
        )

        self.assertTrue(corrected == "Ich fahre gern Fahrrad.")
        self.assertTrue(feedback is None)
