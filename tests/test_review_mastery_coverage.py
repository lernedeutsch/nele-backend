import unittest

from brain.logic.learning_progress_engine import update_learning_progress
from brain.logic.lesson_review_training import record_review_course_outcome


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


class ReviewIntegrationEvidenceCoverageTests(unittest.TestCase):
    def test_a11_review_records_required_evidence_in_shared_progress_store(self):
        state = {
            "lesson_review_training_level": "A1",
            "lesson_review_training_lesson": 1,
        }

        first = record_review_course_outcome(state, 2, True)
        skill = "course:a1:1:ich_stelle_mich_vor"
        item = state["learning_progress_v1"]["skills"][skill]

        self.assertEqual(first["status"], "introduced")
        self.assertEqual(
            set(item["required_evidence"]),
            {"introduce_self", "ask_name_informal", "ask_name_formal"},
        )
        self.assertEqual(set(item["independent_evidence"]), {"introduce_self"})
        self.assertNotIn("course_review_evidence", state)

        record_review_course_outcome(state, 3, True)
        final = record_review_course_outcome(state, 4, True)

        self.assertEqual(final["status"], "mastered")
        self.assertEqual(
            set(item["independent_evidence"]),
            {"introduce_self", "ask_name_informal", "ask_name_formal"},
        )

    def test_assisted_review_success_does_not_add_independent_evidence(self):
        state = {
            "lesson_review_training_level": "A1",
            "lesson_review_training_lesson": 1,
            "course_mastery_assistance_used": True,
        }

        result = record_review_course_outcome(state, 5, True)
        skill = "course:a1:1:das_deutsche_alphabet"
        item = state["learning_progress_v1"]["skills"][skill]

        self.assertNotEqual(result["status"], "mastered")
        self.assertEqual(
            set(item["required_evidence"]),
            {"umlauts", "eszett"},
        )
        self.assertEqual(item["independent_evidence"], [])
