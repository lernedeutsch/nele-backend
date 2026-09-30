import unittest

from brain.logic.curriculum_skill_graph import (
    choose_next_curriculum_skill,
    get_curriculum_state,
)


class CurriculumSkillGraphOrderTests(unittest.TestCase):
    def test_ready_skills_follow_graph_order_not_alphabetical_order(self):
        state = {"conversation_mode": "course", "learning_progress_v1": {"skills": {
            "conversation:supported_answer": {"status": "mastered"},
        }}}

        self.assertEqual(
            choose_next_curriculum_skill(state),
            {
                "skill": "conversation:full_sentence",
                "reason": "prerequisites_met",
            },
        )

    def test_review_priority_also_follows_graph_order(self):
        state = {"conversation_mode": "course", "learning_progress_v1": {"skills": {
            "conversation:supported_answer": {"status": "mastered"},
            "conversation:full_sentence": {"status": "needs_review"},
            "conversation:continue_after_correction": {"status": "needs_review"},
        }}}

        self.assertEqual(
            choose_next_curriculum_skill(state),
            {
                "skill": "conversation:full_sentence",
                "reason": "curriculum_review",
            },
        )


    def test_active_course_mastery_is_routed_before_unrelated_generic_skill(self):
        state = {"conversation_mode": "course", "learning_progress_v1": {"skills": {
            "course:a1:2:zahlen_1–20": {"status": "improving"},
        }}}
        self.assertEqual(
            choose_next_curriculum_skill(state),
            {"skill": "course:a1:2:zahlen_1–20", "reason": "course_mastery_in_progress"},
        )

    def test_course_review_has_priority_in_course_mode(self):
        state = {"conversation_mode": "course", "learning_progress_v1": {"skills": {
            "course:a1:2:zahlen_1–20": {"status": "needs_review"},
            "conversation:supported_answer": {"status": "needs_review"},
        }}}
        self.assertEqual(
            choose_next_curriculum_skill(state),
            {"skill": "course:a1:2:zahlen_1–20", "reason": "course_review"},
        )


if __name__ == "__main__":
    unittest.main()
