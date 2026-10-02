import unittest

from brain.logic.course_answer_evaluator import answer_matches_course_definition


class CourseQuestionOrderRegressionTests(unittest.TestCase):
    def test_question_word_order_is_not_treated_as_unordered_tokens(self):
        definition = {"accepted": ["Woher kommst du?"]}
        self.assertTrue(answer_matches_course_definition("Woher kommst du?", definition))
        self.assertFalse(answer_matches_course_definition("Kommst woher du?", definition))


if __name__ == "__main__":
    unittest.main()
