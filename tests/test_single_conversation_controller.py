import unittest
from unittest.mock import patch

from brain.logic.generic_lesson_engine import (
    start_generic_lesson_teaching,
    handle_generic_lesson_teaching,
)
from brain.logic.dialogue_engine import start_dialogue
from brain.logic.lesson_teaching import handle_lesson_teaching


class SingleConversationControllerTests(unittest.TestCase):
    @patch("brain.logic.generic_lesson_engine.get_current_level", return_value="A1")
    @patch("brain.logic.generic_lesson_engine.get_current_lesson", return_value=2)
    def test_a12_section_uses_shared_lesson_flow_not_legacy_generator(
        self, _lesson, _level
    ):
        state = {}
        reply = start_generic_lesson_teaching("Woher kommen Sie?", state)
        self.assertIn("Jetzt sprechen wir über Länder", reply)
        self.assertNotIn("a1_l2_tutor", state)
        self.assertEqual(state["lesson_teaching_step"], 1)

    @patch("brain.logic.generic_lesson_engine.get_current_level", return_value="A1")
    @patch("brain.logic.generic_lesson_engine.get_current_lesson", return_value=2)
    def test_shared_flow_keeps_control_after_start(self, _lesson, _level):
        state = {}
        start_generic_lesson_teaching("Woher kommen Sie?", state)
        reply = handle_generic_lesson_teaching("Polen", state)
        self.assertIn("Sehr gut", reply)
        self.assertEqual(state["lesson_teaching_step"], 2)
        self.assertNotIn("a1_l2_tutor", state)

    def test_active_dialogue_has_priority_over_lesson_flow(self):
        state = {
            "lesson_teaching_active": True,
            "lesson_teaching_level": "A1",
            "lesson_teaching_lesson": 2,
            "lesson_teaching_section": "Woher kommen Sie?",
            "lesson_teaching_step": 1,
        }
        start_dialogue("A1", 2, "woher-kommst-du", state)
        reply = handle_lesson_teaching("Polen", state)
        self.assertIn("Kommst du aus Polen", reply)
        self.assertEqual(state["lesson_teaching_step"], 1)


if __name__ == "__main__":
    unittest.main()
