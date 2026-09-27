import unittest

from brain.logic.wellbeing_feedback import analyze_wellbeing_response


class WellbeingFeedbackContractTests(unittest.TestCase):
    def test_contract_always_contains_model_sentence(self):
        for message in ("gut", "schlecht", "gestresst", "xyz"):
            result = analyze_wellbeing_response(message)
            self.assertIn("model_sentence", result, message)

    def test_bad_reply_preserves_natural_model(self):
        result = analyze_wellbeing_response("schlecht")
        self.assertTrue(result["recognized"])
        self.assertEqual(result["model_sentence"], "Mir geht es schlecht.")

    def test_stressed_reply_preserves_natural_model(self):
        result = analyze_wellbeing_response("gestresst")
        self.assertTrue(result["recognized"])
        self.assertEqual(result["model_sentence"], "Ich bin gestresst.")


if __name__ == "__main__":
    unittest.main()
