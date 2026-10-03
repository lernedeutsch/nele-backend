import unittest
from unittest.mock import patch

from brain.logic.error_practice import is_equivalent_correct_answer
from brain.logic.conversation import generate_conversation_reply
from brain.logic.memory import get_conversation_state
from brain.logic.dialogue_engine import start_dialogue


class RealCourseConversationRegressionTests(unittest.TestCase):
    def test_vocabulary_transfer_accepts_natural_full_sentence(self):
        self.assertTrue(
            is_equivalent_correct_answer(
                "Ja, sie ist Niederländerin.",
                "Niederländerin",
                "vocabulary",
            )
        )

    @patch("brain.logic.conversation.create_teacher_directed_follow_up")
    def test_completed_course_dialogue_continues_instead_of_fallback(self, follow_up):
        follow_up.return_value = "Wir machen mit dem nächsten Schritt weiter."
        session_id = "regression-course-dialogue-completion"
        state = get_conversation_state(session_id)
        state.clear()
        state["onboarding_completed"] = True
        state["lesson_teaching_active"] = True

        opening = start_dialogue("A1", 2, "woher-kommst-du", state)
        self.assertIn("Woher kommst du", opening)

        generate_conversation_reply("Ich komme aus Polen", "A1", 2, session_id)
        generate_conversation_reply("Ja", "A1", 2, session_id)
        reply = generate_conversation_reply(
            "Anna kommt aus Österreich",
            "A1",
            2,
            session_id,
        )

        self.assertIn("Herkunftsdialog geschafft", reply)
        self.assertIn("nächsten Schritt", reply)
        self.assertFalse(state["dialogue_active"])


if __name__ == "__main__":
    unittest.main()
