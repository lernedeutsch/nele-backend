import unittest

from brain.logic.learning_progress_engine import update_learning_progress


class ReviewMasteryCoverageTests(unittest.TestCase):
    def test_review_requires_all_required_independent_evidence(self):
        skill = "course:a1:1:multi_part_review"
        state = {"learning_progress_v1": {"version": 1, "skills": {skill: {
            "skill": skill, "status": "needs_review", "attempts": 4,
            "successes": 3, "partials": 0, "not_yet": 1, "success_streak": 0,
            "last_result": "NOT_YET", "mastery_eligible": True,
            "requires_independent_confirmation": True, "independent_confirmations": 0,
            "required_evidence": ["A", "B", "C"], "independent_evidence": [],
        }}}}
        for evidence in ("A", "B"):
            result = update_learning_progress(state, {
                "skill": skill, "status": "SUCCESS", "mastery_eligible": True,
                "requires_independent_confirmation": True, "independent_confirmation": True,
                "review_confirmation": True, "required_evidence": ["A", "B", "C"],
                "evidence": evidence,
            })
            self.assertEqual(result["status"], "needs_review")
        result = update_learning_progress(state, {
            "skill": skill, "status": "SUCCESS", "mastery_eligible": True,
            "requires_independent_confirmation": True, "independent_confirmation": True,
            "review_confirmation": True, "required_evidence": ["A", "B", "C"], "evidence": "C",
        })
        self.assertEqual(result["status"], "mastered")


if __name__ == "__main__":
    unittest.main()
