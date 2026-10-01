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
