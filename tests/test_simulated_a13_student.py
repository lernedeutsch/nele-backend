import unittest

from brain.logic.generic_lesson_engine import (
    handle_generic_lesson_teaching,
    start_generic_lesson_teaching,
)


class SimulatedA13StudentTests(unittest.TestCase):
    def state(self):
        return {
            "conversation_mode": "course",
            "student_progress": {"current_level": "A1", "current_lesson": 3},
            "learning_progress_v1": {"version": 1, "skills": {}},
        }

    def test_natural_short_answers_complete_clean_age_section(self):
        state = self.state()
        opening = start_generic_lesson_teaching("Wie alt sind Sie?", state)
        self.assertIn("Frag höflich", opening)

        reply = handle_generic_lesson_teaching("Wie alt sind Sie?", state)
        self.assertIn("Freund", reply)
        reply = handle_generic_lesson_teaching("Wie alt bist du?", state)
        self.assertIn("32", reply)
        reply = handle_generic_lesson_teaching("32", state)

        skill = state["learning_progress_v1"]["skills"]["course:a1:3:wie_alt_sind_sie"]
        self.assertEqual(skill["status"], "mastered")
        self.assertEqual(set(skill["independent_evidence"]), {"step:1", "step:2", "step:3"})
        self.assertFalse(state.get("lesson_teaching_active", False))

    def test_partial_answer_stays_on_same_step_and_cannot_master(self):
        state = self.state()
        start_generic_lesson_teaching("Wie alt sind Sie?", state)
        reply = handle_generic_lesson_teaching("Wie alt", state)

        self.assertEqual(state["lesson_teaching_step"], 1)
        skill = state["learning_progress_v1"]["skills"]["course:a1:3:wie_alt_sind_sie"]
        self.assertNotEqual(skill["status"], "mastered")
        self.assertTrue(state.get("course_mastery_assistance_used"))
        self.assertTrue(reply)

    def test_exhausted_support_must_defer_and_later_revisit_exact_a13_step(self):
        state = self.state()
        opening = start_generic_lesson_teaching("Wie alt sind Sie?", state)
        self.assertIn("Frag höflich", opening)
        failed_step = state["lesson_teaching_step"]

        replies = [handle_generic_lesson_teaching("ich weiß nicht", state) for _ in range(5)]
        self.assertTrue(any("später" in str(reply).lower() for reply in replies))
        self.assertNotEqual(state["lesson_teaching_step"], failed_step)

        transfer_reply = handle_generic_lesson_teaching("Wie alt bist du?", state)
        self.assertEqual(
            state["lesson_teaching_step"],
            failed_step,
            msg=f"A1.3 lost deferred step after transfer: {transfer_reply}",
        )
        self.assertIn("Wie alt sind Sie", transfer_reply)


if __name__ == "__main__":
    unittest.main()
