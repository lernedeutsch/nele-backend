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
        progress = record_course_step_outcome(
            state, "A1", 2, "Das Verb kommen", True,
            final_step=True, independent_confirmation=True,
        )
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


class GenericCourseReviewRestorationTests(unittest.TestCase):
    def test_complete_independent_generic_review_restores_reopened_mastery(self):
        from brain.logic.generic_lesson_engine import record_course_step_outcome

        state = {}
        required = ["step:1", "step:2", "step:3"]

        # First prove the skill independently.
        for index in (1, 2, 3):
            progress = record_course_step_outcome(
                state,
                "A1",
                2,
                "Test section",
                True,
                final_step=index == 3,
                independent_confirmation=True,
                required_evidence=required,
                evidence=f"step:{index}",
            )
        self.assertEqual(progress["status"], "mastered")

        # A later failure reopens it and invalidates old coverage.
        progress = record_course_step_outcome(
            state,
            "A1",
            2,
            "Test section",
            False,
            required_evidence=required,
        )
        self.assertEqual(progress["status"], "needs_review")
        self.assertEqual(progress["independent_evidence"], [])

        # Review must rebuild the complete evidence coverage. Earlier review
        # steps alone cannot restore mastery.
        for index in (1, 2):
            progress = record_course_step_outcome(
                state,
                "A1",
                2,
                "Test section",
                True,
                independent_confirmation=True,
                required_evidence=required,
                evidence=f"step:{index}",
                review_confirmation=True,
            )
            self.assertEqual(progress["status"], "needs_review")

        progress = record_course_step_outcome(
            state,
            "A1",
            2,
            "Test section",
            True,
            final_step=True,
            independent_confirmation=True,
            required_evidence=required,
            evidence="step:3",
            review_confirmation=True,
        )
        self.assertEqual(progress["status"], "mastered")


class SharedMasteryIndependentConfirmationTests(unittest.TestCase):
    def test_old_independent_proof_cannot_authorize_later_assisted_final(self):
        from brain.logic.learning_progress_engine import update_learning_progress

        state = {}
        base = {
            "skill": "course:a1:2:das_verb_kommen",
            "expected_outcome": "course_step",
            "status": "SUCCESS",
            "requires_independent_confirmation": True,
            "mastery_eligible": False,
        }
        # Earlier independent evidence is remembered, but it was not a final
        # mastery-eligible answer.
        first = dict(base)
        first["independent_confirmation"] = True
        update_learning_progress(state, first)
        update_learning_progress(state, dict(base))

        # A later final answer reached with assistance must not borrow the old
        # independent confirmation and become mastered.
        assisted_final = dict(base)
        assisted_final["mastery_eligible"] = True
        progress = update_learning_progress(state, assisted_final)
        self.assertEqual(progress["independent_confirmations"], 1)
        self.assertNotEqual(progress["status"], "mastered")

        # A fresh independent final answer can still confirm mastery normally.
        clean_final = dict(assisted_final)
        clean_final["independent_confirmation"] = True
        progress = update_learning_progress(state, clean_final)
        self.assertEqual(progress["status"], "mastered")


class SharedMasteryFreshConfirmationTests(unittest.TestCase):
    def test_assisted_final_needs_fresh_independent_confirmation(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        state = {}
        base = {
            "skill": "course:a1:2:das_verb_kommen",
            "expected_outcome": "course_step",
            "status": "SUCCESS",
            "requires_independent_confirmation": True,
            "mastery_eligible": False,
        }
        earlier = dict(base)
        earlier["independent_confirmation"] = True
        update_learning_progress(state, earlier)
        update_learning_progress(state, dict(base))
        final = dict(base)
        final["mastery_eligible"] = True
        progress = update_learning_progress(state, final)
        self.assertNotEqual(progress["status"], "mastered")
        final["independent_confirmation"] = True
        progress = update_learning_progress(state, final)
        self.assertEqual(progress["status"], "mastered")


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


class IndependentCourseMasteryTests(unittest.TestCase):
    def test_success_count_alone_cannot_master_course_skill(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        state = {}
        outcome = {
            "skill": "course:a1:2:test_skill",
            "status": "SUCCESS",
            "mastery_eligible": True,
            "requires_independent_confirmation": True,
        }
        for _ in range(5):
            progress = update_learning_progress(state, dict(outcome))
        self.assertNotEqual(progress["status"], "mastered")
        self.assertEqual(progress["independent_confirmations"], 0)

    def test_independent_confirmation_unlocks_mastery_after_real_success_evidence(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        state = {}
        base = {
            "skill": "course:a1:2:test_skill",
            "status": "SUCCESS",
            "mastery_eligible": False,
            "requires_independent_confirmation": True,
        }
        update_learning_progress(state, dict(base))
        update_learning_progress(state, dict(base))
        final = dict(base)
        final["mastery_eligible"] = True
        final["independent_confirmation"] = True
        progress = update_learning_progress(state, final)
        self.assertEqual(progress["independent_confirmations"], 1)
        self.assertEqual(progress["status"], "mastered")

    def test_assisted_final_step_is_success_but_not_mastery_confirmation(self):
        from brain.logic.generic_lesson_engine import record_course_step_outcome
        state = {"course_mastery_assistance_used": True}
        record_course_step_outcome(state, "A1", 2, "Das Verb kommen", True)
        record_course_step_outcome(state, "A1", 2, "Das Verb kommen", True)
        progress = record_course_step_outcome(
            state, "A1", 2, "Das Verb kommen", True,
            final_step=True, independent_confirmation=False,
        )
        self.assertEqual(progress["successes"], 3)
        self.assertEqual(progress["independent_confirmations"], 0)
        self.assertNotEqual(progress["status"], "mastered")


class CourseNumberWordMasteryTests(unittest.TestCase):
    def test_digits_are_not_accepted_as_number_word_mastery(self):
        from brain.logic.generic_lesson_engine import answer_matches_step
        import importlib
        lesson2 = importlib.import_module("brain.responses.A1.2")

        section = lesson2.LESSON_FLOW["sections"]["Zahlen 1–20"]
        digit_answers = ["1 2 3 4 5", "6 7 8 9 10", "11 12 13 14 15", "16 17 18 19 20"]
        word_answers = [
            "eins zwei drei vier fünf",
            "sechs sieben acht neun zehn",
            "elf zwölf dreizehn vierzehn fünfzehn",
            "sechzehn siebzehn achtzehn neunzehn zwanzig",
        ]
        for step, digits, words in zip(section["steps"], digit_answers, word_answers):
            self.assertFalse(answer_matches_step(digits, step, {}))
            self.assertTrue(answer_matches_step(words, step, {}))



class SharedMasteryEvidenceCoverageTests(unittest.TestCase):
    def test_repeated_success_on_one_evidence_unit_cannot_master_multi_part_skill(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        state = {}
        required = ["a", "b", "c"]
        for _ in range(3):
            progress = update_learning_progress(state, {
                "skill": "course:a1:99:multi",
                "status": "SUCCESS",
                "mastery_eligible": True,
                "requires_independent_confirmation": True,
                "independent_confirmation": True,
                "required_evidence": required,
                "evidence": "a",
            })
        self.assertNotEqual(progress["status"], "mastered")
        self.assertEqual(progress["independent_evidence"], ["a"])

    def test_complete_independent_evidence_coverage_unlocks_mastery(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        state = {}
        required = ["a", "b", "c"]
        progress = None
        for evidence in required:
            progress = update_learning_progress(state, {
                "skill": "course:a1:99:multi",
                "status": "SUCCESS",
                "mastery_eligible": True,
                "requires_independent_confirmation": True,
                "independent_confirmation": True,
                "required_evidence": required,
                "evidence": evidence,
            })
        self.assertEqual(progress["status"], "mastered")
        self.assertEqual(set(progress["independent_evidence"]), set(required))

    def test_skills_without_declared_evidence_keep_existing_mastery_behavior(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        state = {}
        progress = None
        for _ in range(3):
            progress = update_learning_progress(state, {
                "skill": "course:a1:99:legacy-compatible",
                "status": "SUCCESS",
                "mastery_eligible": True,
                "requires_independent_confirmation": True,
                "independent_confirmation": True,
            })
        self.assertEqual(progress["status"], "mastered")


class Lesson2SupportExhaustionTests(unittest.TestCase):
    def test_lesson2_consumes_exhausted_support_as_review_evidence(self):
        from brain.logic.a1_lesson2_conversation import start, handle

        state = {}
        prompt = start("Zahlen 1-20", state)
        self.assertTrue(prompt)
        state["course_model_practice_exhausted"] = "eins"

        reply = handle("falsch", state)

        self.assertNotIn("course_model_practice_exhausted", state)
        self.assertTrue(state["course_mastery_assistance_used"])
        self.assertEqual(
            state["last_course_learning_outcome"]["status"],
            "NOT_YET",
        )
        self.assertIn("festigen", reply.lower())


class CourseSemanticGrammarRegressionTests(unittest.TestCase):
    def test_semantic_equivalence_does_not_drop_required_preposition(self):
        from brain.logic.course_answer_evaluator import answer_matches_course_definition
        definition={"accepted":["Ich komme aus Polen."]}
        self.assertFalse(answer_matches_course_definition("Ich komme Polen.", definition))

    def test_semantic_equivalence_does_not_drop_required_article(self):
        from brain.logic.course_answer_evaluator import answer_matches_course_definition
        definition={"accepted":["Ich komme aus der Schweiz."]}
        self.assertFalse(answer_matches_course_definition("Ich komme aus Schweiz.", definition))

    def test_semantic_equivalence_still_accepts_safe_word_order_variant(self):
        from brain.logic.course_answer_evaluator import answer_matches_course_definition
        definition={"accepted":["Ich komme heute aus Polen."]}
        self.assertTrue(answer_matches_course_definition("Heute komme ich aus Polen.", definition))

    def test_semantic_equivalence_rejects_broken_subject_first_word_order(self):
        from brain.logic.course_answer_evaluator import answer_matches_course_definition

        cases = [
            ("Ich komme aus Italien.", "Ich aus Italien komme."),
            ("Du kommst aus Frankreich.", "Du aus Frankreich kommst."),
            ("Wir kommen aus der Schweiz.", "Wir aus der Schweiz kommen."),
        ]
        for accepted, malformed in cases:
            self.assertFalse(
                answer_matches_course_definition(
                    malformed,
                    {"accepted": [accepted]},
                )
            )

    def test_semantic_equivalence_keeps_fronted_constituent_variant(self):
        from brain.logic.course_answer_evaluator import answer_matches_course_definition

        self.assertTrue(
            answer_matches_course_definition(
                "Aus Frankreich kommst du.",
                {"accepted": ["Du kommst aus Frankreich."]},
            )
        )

    def test_fronting_requires_finite_verb_in_second_position(self):
        from brain.logic.course_answer_evaluator import answer_matches_course_definition

        definition = {"accepted": ["Ich komme aus Italien."]}
        self.assertTrue(
            answer_matches_course_definition("Aus Italien komme ich.", definition)
        )
        self.assertFalse(
            answer_matches_course_definition("Aus Italien ich komme.", definition)
        )

    def test_fronting_cannot_split_a_prepositional_phrase(self):
        from brain.logic.course_answer_evaluator import answer_matches_course_definition

        definition = {"accepted": ["Ich komme aus Italien."]}
        self.assertTrue(
            answer_matches_course_definition("Aus Italien komme ich.", definition)
        )
        self.assertFalse(
            answer_matches_course_definition("Aus komme ich Italien.", definition)
        )

    def test_subject_drop_preserves_remaining_word_order(self):
        from brain.logic.course_answer_evaluator import answer_matches_course_definition

        definition = {"accepted": ["Ich komme aus Italien."]}
        self.assertTrue(
            answer_matches_course_definition("Komme aus Italien.", definition)
        )
        for malformed in ("Komme Italien aus.", "Aus komme Italien."):
            self.assertFalse(
                answer_matches_course_definition(malformed, definition)
            )


class CourseGapFillShortAnswerTests(unittest.TestCase):
    def test_shared_evaluator_accepts_exact_missing_gap_fragment(self):
        from brain.logic.course_answer_evaluator import evaluate_course_answer

        cases = [
            (
                {
                    "prompt": "Zuerst „ich“. Ergänze: „Ich … aus Spanien.“",
                    "accepted": ["Ich komme aus Spanien."],
                    "correct_answer": "Ich komme aus Spanien.",
                },
                "komme",
            ),
            (
                {
                    "prompt": "Jetzt „du“. Ergänze: „Du … aus Frankreich.“",
                    "accepted": ["Du kommst aus Frankreich."],
                    "correct_answer": "Du kommst aus Frankreich.",
                },
                "kommst",
            ),
            (
                {
                    "prompt": "Anna kommt aus Polen. Ergänze: „Anna ist …“",
                    "accepted": ["Anna ist Polin.", "Polin"],
                    "correct_answer": "Anna ist Polin.",
                },
                "Polin",
            ),
        ]
        for definition, answer in cases:
            self.assertEqual(
                evaluate_course_answer(answer, definition)["kind"],
                "correct",
            )

    def test_gap_fill_does_not_accept_wrong_or_incomplete_fragment(self):
        from brain.logic.course_answer_evaluator import evaluate_course_answer

        definition = {
            "prompt": "Zuerst „ich“. Ergänze: „Ich … aus Spanien.“",
            "accepted": ["Ich komme aus Spanien."],
            "correct_answer": "Ich komme aus Spanien.",
        }
        for answer in ("kommst", "kommen", "aus Spanien", "Spanien"):
            self.assertEqual(
                evaluate_course_answer(answer, definition)["kind"],
                "wrong",
            )


class SharedMasteryStaleEvidenceRegressionTests(unittest.TestCase):
    def test_failure_invalidates_old_multi_part_evidence_before_remastery(self):
        from brain.logic.learning_progress_engine import update_learning_progress

        state = {}
        required = ["a", "b", "c"]

        # First prove the whole skill independently.
        for evidence in required:
            progress = update_learning_progress(state, {
                "skill": "course:a1:99:multi-review",
                "status": "SUCCESS",
                "mastery_eligible": True,
                "requires_independent_confirmation": True,
                "independent_confirmation": True,
                "required_evidence": required,
                "evidence": evidence,
            })
        self.assertEqual(progress["status"], "mastered")

        # A later real error means the old breadth proof is stale.
        progress = update_learning_progress(state, {
            "skill": "course:a1:99:multi-review",
            "status": "NOT_YET",
            "mastery_eligible": False,
            "requires_independent_confirmation": True,
            "required_evidence": required,
            "evidence": "a",
        })
        self.assertEqual(progress["status"], "needs_review")
        self.assertEqual(progress["independent_evidence"], [])

        # Repeating only one different part must not recycle the old a/b proof.
        for _ in range(3):
            progress = update_learning_progress(state, {
                "skill": "course:a1:99:multi-review",
                "status": "SUCCESS",
                "mastery_eligible": True,
                "requires_independent_confirmation": True,
                "independent_confirmation": True,
                "required_evidence": required,
                "evidence": "c",
            })
        self.assertNotEqual(progress["status"], "mastered")
        self.assertEqual(progress["independent_evidence"], ["c"])
