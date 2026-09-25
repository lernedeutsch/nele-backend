import unittest
from unittest.mock import patch

from brain.logic.dialogue_engine import handle_dialogue
from brain.logic.new_learning_resume import handle_new_learning_resume


class DialogueCourseIntegrationTests(unittest.TestCase):
    @patch("brain.logic.new_learning_resume.remember_learning_topic")
    @patch("brain.logic.new_learning_resume.set_current_section")
    @patch("brain.logic.new_learning_resume.set_current_lesson")
    @patch("brain.logic.new_learning_resume.set_current_level")
    def test_course_offer_starts_real_a12_dialogue_and_completes_it(
        self,
        _set_level,
        _set_lesson,
        _set_section,
        _remember_topic,
    ):
        state = {
            "pending_new_learning": {
                "type": "new_section",
                "level": "A1",
                "lesson": 2,
                "section": "Woher kommen Sie?",
                "topic": "Woher kommen Sie?",
            },
            "last_question": "continue_new_learning",
        }

        opening = handle_new_learning_resume("ja", state)
        self.assertIn("Woher kommst du", opening)
        self.assertTrue(state["dialogue_active"])
        self.assertEqual(state["dialogue_id"], "woher-kommst-du")
        self.assertIsNone(state["pending_new_learning"])

        # Natural short answer is semantically accepted.
        reply = handle_dialogue("Polen", state)
        self.assertIn("Kommst du aus Polen", reply)
        self.assertIn("give_origin", state["dialogue_completed_intents"])

        reply = handle_dialogue("Ja", state)
        self.assertIn("Anna kommt aus Österreich", reply)

        reply = handle_dialogue("Anna kommt aus Österreich", state)
        self.assertIn("Herkunftsdialog geschafft", reply)
        self.assertFalse(state["dialogue_active"])

    def test_unrelated_answer_does_not_advance_origin_dialogue(self):
        from brain.logic.dialogue_engine import start_dialogue
        state = {}
        start_dialogue("A1", 2, "woher-kommst-du", state)
        reply = handle_dialogue("Ich kaufe Brot", state)
        self.assertIn("Ich komme aus Polen", reply)
        self.assertEqual(state["dialogue_turn"], 1)
        self.assertNotIn("give_origin", state["dialogue_completed_intents"])

    def test_origin_dialogue_has_semantic_contract(self):
        from brain.logic.dialogue_engine import get_dialogue
        dialogue = get_dialogue("A1", 2, "woher-kommst-du")
        self.assertEqual(dialogue["topic"], "Herkunft")
        self.assertEqual(dialogue["register"], "informal")
        self.assertEqual(dialogue["max_variations"], 2)
        self.assertIn("combine_unrelated_topics", dialogue["forbidden_variations"])


if __name__ == "__main__":
    unittest.main()
