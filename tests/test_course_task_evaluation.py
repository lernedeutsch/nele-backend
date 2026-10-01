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

    def test_natural_subject_drop_keeps_tested_verb_and_is_accepted(self):
        from brain.logic.generic_lesson_engine import answer_matches_step
        step = {
            "accepted": ["Ich komme aus Spanien."],
            "correct_answer": "Ich komme aus Spanien.",
        }
        self.assertTrue(answer_matches_step("Komme aus Spanien.", step, {}))
        self.assertFalse(answer_matches_step("aus Spanien", step, {}))
        self.assertFalse(answer_matches_step("Kommen aus Spanien", step, {}))

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


class GenericCourseDigressionTests(unittest.TestCase):
    def test_unrelated_question_is_course_digression(self):
        from brain.logic.generic_lesson_engine import is_course_digression_question
        step = {
            "prompt": "Jetzt du. Ergänze: Du … aus Frankreich.",
            "correct_answer": "Du kommst aus Frankreich.",
        }
        self.assertTrue(
            is_course_digression_question("Wie ist das Wetter heute?", step, {})
        )

    def test_digression_is_answered_then_resumes_exact_prompt(self):
        from brain.logic.generic_lesson_engine import build_course_digression_resume
        step = {
            "prompt": "Jetzt „du“. Ergänze: „Du … aus Frankreich.“",
            "correct_answer": "Du kommst aus Frankreich.",
        }
        reply = build_course_digression_resume(
            step, {}, "A1", 2, "Das Verb kommen",
            user_message="Wie ist das Wetter heute?",
        )
        self.assertIn("Wie ist das Wetter bei dir?", reply)
        self.assertIn("Du … aus Frankreich", reply)
        self.assertNotIn("Wir kommen gleich darauf zurück", reply)

    def test_question_using_target_content_remains_lesson_attempt(self):
        from brain.logic.generic_lesson_engine import is_course_digression_question
        step = {
            "prompt": "Jetzt du. Ergänze: Du … aus Frankreich.",
            "correct_answer": "Du kommst aus Frankreich.",
        }
        self.assertFalse(
            is_course_digression_question("Kommst du aus Frankreich?", step, {})
        )


class GenericCourseMasteryEvidenceTests(unittest.TestCase):
    def test_course_skill_cannot_master_before_final_step(self):
        from brain.logic.generic_lesson_engine import record_course_step_outcome
        state = {}
        for _ in range(5):
            progress = record_course_step_outcome(state, "A1", 2, "Das Verb kommen", True, final_step=False)
        self.assertNotEqual(progress["status"], "mastered")
        progress = record_course_step_outcome(state, "A1", 2, "Das Verb kommen", True, final_step=True)
        self.assertEqual(progress["status"], "mastered")

    def test_wrong_course_attempt_is_recorded_and_not_mastered(self):
        from brain.logic.generic_lesson_engine import record_course_step_outcome
        state = {}
        progress = record_course_step_outcome(state, "A1", 2, "Das Verb kommen", False, final_step=False)
        self.assertEqual(progress["not_yet"], 1)
        self.assertNotEqual(progress["status"], "mastered")

    def test_partial_course_attempt_is_recorded_in_shared_progress(self):
        from brain.logic.generic_lesson_engine import record_course_step_outcome
        state = {}
        progress = record_course_step_outcome(
            state, "A1", 2, "Zahlen 1–20", False, final_step=False, partial=True
        )
        self.assertEqual(progress["partials"], 1)
        self.assertEqual(progress["last_result"], "PARTIAL")
        self.assertEqual(
            state["last_course_learning_outcome"]["status"],
            "PARTIAL",
        )
        self.assertNotEqual(progress["status"], "mastered")


class GenericCourseMasteryRoutingGateTests(unittest.TestCase):
    def test_many_failures_prevent_mastery_even_after_final_success(self):
        from brain.logic.generic_lesson_engine import record_course_step_outcome
        state = {}
        for _ in range(7):
            record_course_step_outcome(state, "A1", 2, "Das Verb kommen", False, final_step=False)
        for _ in range(5):
            record_course_step_outcome(state, "A1", 2, "Das Verb kommen", True, final_step=False)
        progress = record_course_step_outcome(state, "A1", 2, "Das Verb kommen", True, final_step=True)
        self.assertNotEqual(progress["status"], "mastered")


class GenericCoursePartialSequenceTests(unittest.TestCase):
    def test_correct_prefix_of_number_sequence_is_partial_not_complete(self):
        from brain.logic.generic_lesson_engine import _sequence_partial_progress, answer_matches_step
        step = {
            "accepted": ["eins, zwei, drei, vier, fünf", "1 2 3 4 5"],
            "correct_answer": "eins, zwei, drei, vier, fünf",
        }
        self.assertFalse(answer_matches_step("eins zwei drei", step, {}))
        partial = _sequence_partial_progress("eins zwei drei", step["accepted"], {})
        self.assertEqual(partial["matched"], 3)
        self.assertEqual(partial["total"], 5)

    def test_wrong_or_out_of_order_sequence_is_not_partial(self):
        from brain.logic.generic_lesson_engine import _sequence_partial_progress
        accepted = ["eins, zwei, drei, vier, fünf"]
        self.assertIsNone(_sequence_partial_progress("eins drei", accepted, {}))
        self.assertIsNone(_sequence_partial_progress("zwölf", accepted, {}))



class SharedCourseAnswerClassificationTests(unittest.TestCase):
    def test_shared_evaluator_classifies_correct_partial_and_wrong(self):
        from brain.logic.course_answer_evaluator import evaluate_course_answer
        definition = {
            "accepted": ["eins, zwei, drei, vier, fünf"],
            "correct_answer": "eins, zwei, drei, vier, fünf",
        }
        self.assertEqual(
            evaluate_course_answer("eins zwei drei vier fünf", definition)["kind"],
            "correct",
        )
        partial = evaluate_course_answer("eins zwei drei", definition)
        self.assertEqual(partial["kind"], "partial")
        self.assertEqual(partial["partial"]["matched"], 3)
        self.assertEqual(partial["partial"]["total"], 5)
        self.assertEqual(
            evaluate_course_answer("eins drei", definition)["kind"],
            "wrong",
        )

    def test_lesson_wrapper_uses_shared_classification(self):
        from brain.logic.generic_lesson_engine import evaluate_step_answer
        step = {
            "accepted": ["eins, zwei, drei, vier, fünf"],
            "correct_answer": "eins, zwei, drei, vier, fünf",
        }
        self.assertEqual(evaluate_step_answer("eins zwei drei", step, {})["kind"], "partial")
