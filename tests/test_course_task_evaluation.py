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