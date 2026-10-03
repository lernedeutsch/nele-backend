import unittest

from brain.logic.generic_lesson_engine import (
    start_generic_lesson_teaching,
    handle_generic_lesson_teaching,
)


class GenericCourseFullEvidenceCoverageRegressionTests(unittest.TestCase):
    def test_multi_step_section_requires_independent_evidence_from_every_step(self):
        state = {
            "conversation_mode": "course",
            "student_progress": {"current_level": "A1", "current_lesson": 2},
        }
        opening = start_generic_lesson_teaching("Zahlen 1–20", state)
        self.assertIn("1 bis 5", opening)

        handle_generic_lesson_teaching("falsch", state)
        handle_generic_lesson_teaching("eins zwei drei vier fünf", state)

        for answer in (
            "sechs sieben acht neun zehn",
            "elf zwölf dreizehn vierzehn fünfzehn",
            "sechzehn siebzehn achtzehn neunzehn zwanzig",
        ):
            handle_generic_lesson_teaching(answer, state)

        skill = state["learning_progress_v1"]["skills"]["course:a1:2:zahlen_1–20"]
        self.assertNotEqual(skill["status"], "mastered")
        self.assertNotIn("step:1", skill["independent_evidence"])
        self.assertEqual(set(skill["independent_evidence"]), {"step:2", "step:3", "step:4"})
        self.assertEqual(set(skill["required_evidence"]), {"step:1", "step:2", "step:3", "step:4"})
        self.assertEqual(state["lesson_teaching_step"], 1)


def test_clean_full_coverage_can_master_after_many_historical_failures():
    from brain.logic.learning_progress_engine import update_learning_progress

    skill = "course:a1:3:zahlen_11–100"
    required = ["step:1", "step:2", "step:3", "step:4", "step:5"]
    state = {}

    # A difficult first attempt may accumulate many failures.
    for _ in range(6):
        update_learning_progress(state, {
            "skill": skill,
            "status": "NOT_YET",
            "mastery_eligible": False,
            "requires_independent_confirmation": True,
            "required_evidence": required,
        })

    # One later clean pass demonstrates every required part independently.
    result = None
    for index in range(1, 6):
        result = update_learning_progress(state, {
            "skill": skill,
            "status": "SUCCESS",
            "mastery_eligible": index == 5,
            "requires_independent_confirmation": True,
            "independent_confirmation": True,
            "required_evidence": required,
            "evidence": f"step:{index}",
        })

    assert result["status"] == "mastered"
    assert set(result["independent_evidence"]) == set(required)


def test_false_review_confirmation_does_not_trap_clean_course_pass_in_needs_review():
    from brain.logic.learning_progress_engine import update_learning_progress

    skill = "course:a1:3:zahlen_11–100"
    required = ["step:1", "step:2", "step:3", "step:4", "step:5"]
    state = {"learning_progress_v1": {"version": 1, "skills": {skill: {
        "skill": skill,
        "status": "needs_review",
        "attempts": 6,
        "successes": 0,
        "partials": 0,
        "not_yet": 6,
        "success_streak": 0,
        "last_result": "NOT_YET",
        "mastery_eligible": False,
        "requires_independent_confirmation": True,
        "independent_confirmations": 0,
        "required_evidence": required,
        "independent_evidence": [],
    }}}}

    result = None
    for index in range(1, 6):
        result = update_learning_progress(state, {
            "skill": skill,
            "status": "SUCCESS",
            "mastery_eligible": index == 5,
            "requires_independent_confirmation": True,
            "independent_confirmation": True,
            "review_confirmation": False,
            "required_evidence": required,
            "evidence": f"step:{index}",
        })

    assert result["last_review_attempt"] is False
    assert result["status"] == "mastered"
