import unittest

from brain.logic.conversation_wellbeing import handle_wellbeing_reply


class CourseWellbeingGateTests(unittest.TestCase):
    def test_course_continue_releases_optional_wellbeing_gate(self):
        state = {"conversation_mode": "course", "last_question": "wellbeing"}
        handled, answer, feedback = handle_wellbeing_reply("ja", state)
        self.assertFalse(handled)
        self.assertIsNone(answer)
        self.assertIsNone(feedback)
        self.assertIsNone(state["last_question"])

    def test_clear_course_sentence_releases_optional_wellbeing_gate(self):
        state = {"conversation_mode": "course", "last_question": "wellbeing"}
        handled, answer, feedback = handle_wellbeing_reply(
            "ich komme aus Deutschland", state
        )
        self.assertFalse(handled)
        self.assertIsNone(answer)
        self.assertIsNone(feedback)
        self.assertIsNone(state["last_question"])

    def test_unclear_short_answer_still_gets_wellbeing_help(self):
        state = {"conversation_mode": "course", "last_question": "wellbeing"}
        handled, answer, _ = handle_wellbeing_reply("gu", state)
        self.assertTrue(handled)
        self.assertIn("Wie geht es dir", answer)
        self.assertEqual(state["last_question"], "wellbeing")


if __name__ == "__main__":
    unittest.main()
