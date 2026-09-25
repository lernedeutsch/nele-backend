import unittest

from brain.logic.content_validation import validate_all_learning_content, validate_lesson
from brain.logic.personal_sentences import validate_personal_sentence_catalog


class LearningContentGateTests(unittest.TestCase):
    def test_personal_sentence_catalog_is_valid(self):
        self.assertTrue(validate_personal_sentence_catalog())

    def test_all_publishable_a1_lessons_pass_gate(self):
        result = validate_all_learning_content("A1")
        self.assertTrue(result["lessons"])

    def test_known_lessons_load_through_production_loader(self):
        self.assertTrue(validate_lesson("A1", 1))
        self.assertTrue(validate_lesson("A1", 2))


if __name__ == "__main__":
    unittest.main()
