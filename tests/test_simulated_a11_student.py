import unittest

from brain.logic.course_teacher_engine import course_teacher_language_issues
from brain.logic.lesson_review_training import (
    get_current_lesson_review_prompt,
    handle_a1_lesson_1_review,
)


class SimulatedA11StudentTests(unittest.TestCase):
    """Conversation-level contract for a beginner, not isolated helper tests."""

    def state(self):
        return {
            "conversation_mode": "course",
            "lesson_review_training_active": True,
            "lesson_review_training_level": "A1",
            "lesson_review_training_lesson": 1,
            "lesson_review_training_step": 1,
            "lesson_review_training_correct": 0,
            "lesson_review_training_wrong": 0,
            "learning_progress_v1": {"version": 1, "skills": {}},
        }

    def assert_beginner_turn(self, text):
        self.assertTrue(str(text or "").strip())
        self.assertEqual(course_teacher_language_issues(text, level="A1"), [])

    def test_happy_path_keeps_one_small_action_per_turn(self):
        state = self.state()
        prompt = get_current_lesson_review_prompt(state)
        self.assertIn("Morgen", prompt)
        self.assertNotIn("Abend", prompt)
        self.assertNotIn("beim Gehen", prompt)
        self.assert_beginner_turn(prompt)

        transcript = []
        for answer, expected_step, expected_fragment in (
            ("Guten Morgen", 2, "am Tag"),
            ("Guten Tag", 3, "am Abend"),
            ("Guten Abend", 4, "gehst jetzt"),
            ("Tschüss", 5, "stell dich"),
        ):
            reply = handle_a1_lesson_1_review(answer, state)
            transcript.append(reply)
            self.assertEqual(state["lesson_review_training_step"], expected_step)
            self.assertIn(expected_fragment.casefold(), reply.casefold())
            self.assert_beginner_turn(reply)

        joined = " ".join(transcript)
        self.assertNotIn(
            "Nenne passende Grüße für morgens, tagsüber, abends und beim Gehen",
            joined,
        )

    def test_wrong_greeting_does_not_skip_the_active_microstep(self):
        state = self.state()
        reply = handle_a1_lesson_1_review("Guten Abend", state)
        self.assertEqual(state["lesson_review_training_step"], 1)
        self.assert_beginner_turn(reply)

    def test_each_greeting_is_independent_evidence(self):
        state = self.state()
        handle_a1_lesson_1_review("Guten Morgen", state)
        skill = state["learning_progress_v1"]["skills"]["course:a1:1:wir_begrüßen_uns"]
        self.assertNotEqual(skill["status"], "mastered")
        self.assertEqual(
            set(skill.get("independent_evidence") or []),
            {"greeting_morning"},
        )

        handle_a1_lesson_1_review("Guten Tag", state)
        handle_a1_lesson_1_review("Guten Abend", state)
        handle_a1_lesson_1_review("Tschüss", state)
        skill = state["learning_progress_v1"]["skills"]["course:a1:1:wir_begrüßen_uns"]
        self.assertEqual(skill["status"], "mastered")
        self.assertEqual(
            set(skill.get("independent_evidence") or []),
            {"greeting_morning", "greeting_day", "greeting_evening", "greeting_goodbye"},
        )


if __name__ == "__main__":
    unittest.main()
