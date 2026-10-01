import unittest

from brain.logic.context import handle_context_answer
from brain.logic.memory import conversation_sessions
from brain.logic.onboarding import extract_name_sentence, get_onboarding_retry, is_plausible_onboarding_short_value

class OnboardingSlotValidationRegressionTests(unittest.TestCase):
    def test_status_word_is_not_taught_as_residence(self):
        self.assertFalse(is_plausible_onboarding_short_value("gut", 3))
        reply = get_onboarding_retry(3, "gut")
        self.assertNotIn("Ich wohne in Gut", reply)
        self.assertIn("Ich wohne in Heidelberg", reply)

    def test_status_word_is_rejected_for_all_identity_slots(self):
        for step in (1, 2, 3):
            self.assertFalse(is_plausible_onboarding_short_value("gut", step))

    def test_explicit_name_forms_still_work(self):
        self.assertEqual(extract_name_sentence("Ich heiße Anna"), "Anna")
        self.assertEqual(extract_name_sentence("Mein Name ist Anna"), "Anna")

    def test_generic_ich_bin_is_not_a_name_sentence(self):
        self.assertEqual(extract_name_sentence("Ich bin Moni"), "Moni")
        self.assertEqual(extract_name_sentence("Ich bin 30 Jahre alt"), "")
        self.assertEqual(extract_name_sentence("Ich bin müde"), "")

    def test_age_cannot_overwrite_existing_name_or_rewind_origin(self):
        state = {"last_question": "name", "name": "Anna", "origin": "Polen", "residence": "Berlin", "user_facts": {"name": "Anna", "origin": "Polen", "residence": "Berlin"}}
        session_id = "slot-age-30"
        conversation_sessions[session_id] = state
        reply = handle_context_answer("Ich bin 30 Jahre alt", session_id)
        self.assertIsNone(reply)
        self.assertEqual(state["name"], "Anna")
        self.assertEqual(state["origin"], "Polen")
        self.assertEqual(state["residence"], "Berlin")
        self.assertEqual(state["last_question"], "name")

    def test_unexpected_age_variant_is_also_rejected(self):
        state = {"last_question": "name", "name": "Anna", "user_facts": {"name": "Anna"}}
        session_id = "slot-age-46"
        conversation_sessions[session_id] = state
        reply = handle_context_answer("Ich bin 46 Jahre alt", session_id)
        self.assertIsNone(reply)
        self.assertEqual(state["name"], "Anna")
        self.assertNotEqual(state.get("last_question"), "origin")

if __name__ == "__main__":
    unittest.main()
