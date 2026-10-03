import unittest

from brain.logic.conversation_error_training import handle_active_error_practice
from brain.logic.error_practice import start_error_practice
from brain.logic.lesson_review_training import get_current_lesson_review_prompt
from brain.memory.error_memory import remember_error


class ReviewErrorPracticeResumeTests(unittest.TestCase):
    def test_error_practice_returns_to_exact_active_review_step(self):
        state = {
            "conversation_mode": "course",
            "lesson_review_training_active": True,
            "lesson_review_training_level": "A1",
            "lesson_review_training_lesson": 1,
            "lesson_review_training_step": 6,
            "lesson_review_training_correct": 0,
            "lesson_review_training_wrong": 1,
            "learning_progress_v1": {"version": 1, "skills": {}},
        }
        expected_review_prompt = get_current_lesson_review_prompt(state)
        self.assertIn("Freund", expected_review_prompt)

        remember_error(
            state,
            "grammar",
            "Wie heißen du?",
            "Wie heißt du?",
            context="Wie fragst du einen Freund nach seinem Namen?",
        )
        opening = start_error_practice(state, "grammar")
        self.assertIn("Welche Antwort passt hier?", opening)

        reply = handle_active_error_practice("2", state)
        self.assertTrue(state.get("error_practice_used_hint"))
        self.assertIn("Wie heißt du?", reply)

        reply = handle_active_error_practice("Wie heißt du?", state)
        self.assertEqual(state.get("error_practice_step"), 3)
        self.assertIn("ohne Auswahl", reply)

        reply = handle_active_error_practice("Wie heißt du?", state)

        self.assertFalse(state.get("error_practice_active", False))
        self.assertEqual(state["lesson_review_training_step"], 6)
        self.assertIn(expected_review_prompt, reply)
        self.assertIn("Freund", reply)


if __name__ == "__main__":
    unittest.main()
