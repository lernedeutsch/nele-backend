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

        curriculum = get_curriculum_state(state)

        self.assertEqual(
            curriculum["ready"][:2],
            [
                "conversation:full_sentence",
                "conversation:continue_after_correction",
            ],
        )
        self.assertEqual(
            choose_next_curriculum_skill(state),
            {
                "skill": "conversation:full_sentence",
                "reason": "prerequisites_met",
            },
        )

    def test_review_priority_also_follows_graph_order(self):
        state = {"learning_progress_v1": {"skills": {
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


if __name__ == "__main__":
    unittest.main()
