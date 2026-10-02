import importlib
import unittest

from brain.knowledge.A1.lessons import (
    get_available_lessons,
    get_lesson,
    get_next_lesson_number,
)
from brain.logic.generic_lesson_engine import (
    find_generic_section,
    start_generic_lesson_teaching,
)


class A13CourseContentTests(unittest.TestCase):
    def test_a13_is_registered_after_a12(self):
        self.assertEqual(get_available_lessons()[:3], [1, 2, 3])
        self.assertEqual(get_next_lesson_number(2), 3)
        lesson = get_lesson(3)
        self.assertEqual(lesson["title"], "Wie alt sind Sie?")
        self.assertEqual(
            lesson["sections"],
            ["Wie alt sind Sie?", "Zahlen 11–100", "Das Verb sein", "Persönliche Daten"],
        )

    def test_a13_source_has_real_generic_teaching_sections(self):
        lesson3 = importlib.import_module("brain.responses.A1.3")
        self.assertEqual(lesson3.LESSON["lesson"], 3)
        self.assertEqual(
            list(lesson3.LESSON_FLOW["sections"]),
            ["Wie alt sind Sie?", "Zahlen 11–100", "Das Verb sein", "Persönliche Daten"],
        )
        for section in lesson3.LESSON_FLOW["sections"].values():
            self.assertGreaterEqual(len(section["steps"]), 3)

    def test_a13_starts_through_shared_generic_engine(self):
        state = {
            "conversation_mode": "course",
            "student_progress": {"current_level": "A1", "current_lesson": 3},
        }
        reply = start_generic_lesson_teaching("Wie alt sind Sie?", state)
        self.assertIn("Alter", reply)
        self.assertIn("Frag höflich", reply)
        self.assertTrue(state["lesson_teaching_active"])
        self.assertEqual(state["lesson_teaching_lesson"], 3)
        self.assertEqual(state["lesson_teaching_step"], 1)

    def test_a13_accepts_natural_short_age_answer(self):
        _, section = find_generic_section("A1", 3, "Wie alt sind Sie?")
        step = section["steps"][2]
        self.assertIn("32", step["accepted"])
        self.assertIn("Ich bin 32.", step["accepted"])


if __name__ == "__main__":
    unittest.main()
