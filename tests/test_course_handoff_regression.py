import unittest

from brain.logic.new_learning_resume import handle_new_learning_resume


class CourseHandoffRegressionTests(unittest.TestCase):
    def test_unrelated_reply_keeps_pending_course_section_active(self):
        state = {
            "conversation_mode": "course",
            "pending_new_learning": {
                "type": "new_section",
                "level": "A1",
                "lesson": 2,
                "section": "Länder und Nationalitäten",
                "topic": "Länder und Nationalitäten",
            },
            "last_question": "continue_new_learning",
        }

        reply = handle_new_learning_resume("Ich komme aus Italien", state)

        self.assertIn("Länder und Nationalitäten", reply)
        self.assertIn("ja", reply)
        self.assertIn("nein", reply)
        self.assertIsNotNone(state["pending_new_learning"])
        self.assertEqual(state["last_question"], "continue_new_learning")


if __name__ == "__main__":
    unittest.main()
