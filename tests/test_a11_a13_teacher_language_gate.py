import unittest
from unittest.mock import patch

from brain.logic.content_validation import ContentValidationError, _validate_a1_teacher_text


class A11A13TeacherLanguageGateTests(unittest.TestCase):
    def test_rejects_heavy_beginner_instruction(self):
        heavy = " ".join(["Wort"] * 24) + "."
        with self.assertRaises(ContentValidationError):
            _validate_a1_teacher_text(heavy, "A1 lesson 2 prompt", 2)

    def test_accepts_small_beginner_action(self):
        _validate_a1_teacher_text("Es ist Morgen. Was sagst du?", "A1 lesson 1 prompt", 1)

    def test_scope_stops_before_a14(self):
        heavy = " ".join(["Wort"] * 24) + "."
        _validate_a1_teacher_text(heavy, "A1 lesson 4 prompt", 4)


if __name__ == "__main__":
    unittest.main()
