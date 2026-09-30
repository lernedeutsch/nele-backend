import unittest

from brain.nele3_upgrade.activities import answer_active_task
from brain.nele3_upgrade.content import DIALOGUES

class CourseTaskEvaluationTests(unittest.TestCase):
    def test_weak_keyword_overlap_does_not_complete_dialogue(self):
        item = next(x for x in DIALOGUES if x['id'] == 'bakery')
        state = {'nele3_upgrade': {'active_task': {'type': 'dialogue', 'title': item['title'], 'prompt': item['prompt'], 'keywords': item['keywords'], 'model_answer': item['model_answer']}}}
        result = answer_active_task(state, "ich möchte abfallen")
        self.assertFalse(result['completed'])

    def test_natural_non_exact_answer_can_complete_dialogue(self):
        item = next(x for x in DIALOGUES if x['id'] == 'bakery')
        state = {'nele3_upgrade': {'active_task': {'type': 'dialogue', 'title': item['title'], 'prompt': item['prompt'], 'keywords': item['keywords'], 'model_answer': item['model_answer']}}}
        result = answer_active_task(state, 'Ich möchte zwei Brötchen')
        self.assertTrue(result['completed'])

if __name__ == '__main__':
    unittest.main()

class GenericCourseSemanticAnswerTests(unittest.TestCase):
    def test_word_order_variant_is_accepted_by_shared_course_matcher(self):
        from brain.logic.generic_lesson_engine import answer_matches_step
        step = {
            "accepted": ["Du kommst aus Frankreich."],
            "correct_answer": "Du kommst aus Frankreich.",
        }
        self.assertTrue(
            answer_matches_step("Aus Frankreich kommst du.", step, {})
        )

    def test_wrong_conjugation_is_not_semantically_accepted(self):
        from brain.logic.generic_lesson_engine import answer_matches_step
        step = {
            "accepted": ["Ich komme aus Spanien."],
            "correct_answer": "Ich komme aus Spanien.",
        }
        self.assertFalse(
            answer_matches_step("Ich kommen aus Spanien.", step, {})
        )

    def test_unrelated_answer_is_not_semantically_accepted(self):
        from brain.logic.generic_lesson_engine import answer_matches_step
        step = {
            "accepted": ["Wir kommen aus der Schweiz."],
            "correct_answer": "Wir kommen aus der Schweiz.",
        }
        self.assertFalse(
            answer_matches_step("Wir wohnen in der Schweiz.", step, {})
        )
