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

        reply = handle_dialogue("Ich komme aus Polen", state)
        self.assertIn("Kommst du aus Polen", reply)

        reply = handle_dialogue("Ja", state)
        self.assertIn("Anna kommt aus Österreich", reply)

        reply = handle_dialogue("Anna kommt aus Österreich", state)
        self.assertIn("Herkunftsdialog geschafft", reply)
        self.assertFalse(state["dialogue_active"])


if __name__ == "__main__":
    unittest.main()
