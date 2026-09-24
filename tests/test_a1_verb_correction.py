import unittest

from brain.logic.a1_verb_correction import find_a1_verb_correction
from brain.logic.learner_feedback import prepare_message_with_feedback


class GeneratedTests(unittest.TestCase):
    def test_ich_fahren(self):
        result = find_a1_verb_correction("Ich fahren Fahrrad")
        self.assertTrue(result["corrected_message"] == "Ich fahre Fahrrad.")


    def test_du_fahren_irregular(self):
        result = find_a1_verb_correction("Du fahren Fahrrad")
        self.assertTrue(result["corrected_message"] == "Du fährst Fahrrad.")


    def test_du_essen_irregular(self):
        result = find_a1_verb_correction("Du essen Pizza")
        self.assertTrue(result["corrected_message"] == "Du isst Pizza.")


    def test_du_sprechen_irregular(self):
        result = find_a1_verb_correction("Du sprechen Deutsch")
        self.assertTrue(result["corrected_message"] == "Du sprichst Deutsch.")


    def test_sein_and_haben(self):
        self.assertTrue(find_a1_verb_correction("Ich sein müde")["corrected_message"] == "Ich bin müde.")
        self.assertTrue(find_a1_verb_correction("Du haben Zeit")["corrected_message"] == "Du hast Zeit.")


    def test_correct_form_is_untouched(self):
        self.assertTrue(find_a1_verb_correction("Ich fahre Fahrrad") is None)
        self.assertTrue(find_a1_verb_correction("Du sprichst Deutsch") is None)


    def test_unknown_verb_is_untouched(self):
        self.assertTrue(find_a1_verb_correction("Ich fotografieren gern") is None)


    def test_automatic_correction_reaches_student_memory(self):
        state = {}

        corrected, feedback = prepare_message_with_feedback(
        "Du essen Pizza",
        state,
        )

        self.assertTrue(corrected == "Du isst Pizza.")
        self.assertTrue("Du isst Pizza" in feedback)
        self.assertTrue(state.get("error_memory"))
