import unittest

from brain.logic.lesson_review_training import (
    complete_lesson_review_training,
    handle_a1_lesson_1_review,
    record_review_course_outcome,
    evaluate_review_answer,
)


def mastered_item(skill):
    return {
        "skill": skill,
        "status": "mastered",
        "attempts": 3,
        "successes": 3,
        "partials": 0,
        "not_yet": 0,
        "success_streak": 3,
        "last_result": "SUCCESS",
        "mastery_eligible": True,
        "requires_independent_confirmation": True,
        "independent_confirmations": 1,
    }


class LessonReviewMasteryTests(unittest.TestCase):
    def base_state(self):
        skills = {}
        for suffix in (
            "wir_begrüßen_uns",
            "ich_stelle_mich_vor",
            "das_deutsche_alphabet",
        ):
            key = f"course:a1:1:{suffix}"
            skills[key] = mastered_item(key)
        return {
            "conversation_mode": "course",
            "lesson_review_training_active": True,
            "lesson_review_training_level": "A1",
            "lesson_review_training_lesson": 1,
            "lesson_review_training_step": 1,
            "lesson_review_training_correct": 0,
            "lesson_review_training_wrong": 0,
            "learning_progress_v1": {"version": 1, "skills": skills},
        }


    def test_all_review_steps_use_shared_answer_definitions(self):
        cases = (
            (1, "Guten Morgen, Guten Tag, Guten Abend, Tschüss", True),
            (2, "Mein Name ist Anna", True),
            (3, "Wie heisst du?", True),
            (4, "Wie heißen Sie?", True),
            (5, "Ü Ö Ä", True),
            (6, "Es Zett", True),
            (1, "Guten Morgen", False),
            (1, "Guten Abend", False),
            (3, "Wie geht es dir?", False),
            (5, "A O U", False),
            (6, "Doppel-s", False),
        )
        for step, answer, expected in cases:
            with self.subTest(step=step, answer=answer):
                result = evaluate_review_answer(step, answer)
                self.assertEqual(result["correct"], expected)

    def test_one_wrong_answer_no_longer_means_good_review(self):
        state = self.base_state()
        state["lesson_review_training_wrong"] = 1
        record_review_course_outcome(state, 1, False)

        result = complete_lesson_review_training(state)

        self.assertIn("morgen noch einmal", result)
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:wir_begrüßen_uns"
            ]["status"],
            "needs_review",
        )

    def test_guided_correction_cannot_restore_review_mastery(self):
        state = self.base_state()
        record_review_course_outcome(state, 2, False)
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:ich_stelle_mich_vor"
            ]["status"],
            "needs_review",
        )

        record_review_course_outcome(state, 2, True)
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:ich_stelle_mich_vor"
            ]["status"],
            "needs_review",
        )

    def test_one_independent_review_answer_cannot_restore_multi_part_skill(self):
        state = self.base_state()
        skill = "course:a1:1:ich_stelle_mich_vor"
        record_review_course_outcome(state, 2, False)
        record_review_course_outcome(state, 2, True)  # guided correction
        record_review_course_outcome(state, 3, True)  # only one fresh evidence item

        self.assertEqual(
            state["learning_progress_v1"]["skills"][skill]["status"],
            "needs_review",
        )

    def test_complete_independent_review_evidence_restores_multi_part_skill(self):
        state = self.base_state()
        skill = "course:a1:1:ich_stelle_mich_vor"
        record_review_course_outcome(state, 2, False)
        record_review_course_outcome(state, 2, True)  # guided correction
        record_review_course_outcome(state, 2, True)  # fresh introduce-self evidence
        record_review_course_outcome(state, 3, True)
        record_review_course_outcome(state, 4, True)

        self.assertEqual(
            state["learning_progress_v1"]["skills"][skill]["status"],
            "mastered",
        )

    def test_single_greeting_cannot_restore_broad_greeting_skill(self):
        state = self.base_state()
        skill = "course:a1:1:wir_begrüßen_uns"
        record_review_course_outcome(state, 1, False)
        state["course_mastery_assistance_used"] = False
        result = evaluate_review_answer(1, "Guten Morgen")
        self.assertFalse(result["correct"])
        record_review_course_outcome(state, 1, True)

        self.assertEqual(
            state["learning_progress_v1"]["skills"][skill]["status"],
            "mastered",
        )
        self.assertEqual(
            state["course_review_evidence"][skill],
            ["greeting_range"],
        )

    def test_review_wrong_answer_uses_shared_teacher_engine(self):
        state = self.base_state()
        state["lesson_review_training_step"] = 3

        reply = handle_a1_lesson_1_review("Wie geht es dir?", state)

        self.assertTrue(reply)
        self.assertEqual(state["lesson_review_training_step"], 3)
        self.assertEqual(state["course_teacher_action"]["action"], "correct_and_retry")
        self.assertEqual(state["course_teacher_action"]["reason"], "answer_not_yet")
        self.assertEqual(state["course_teacher_action"]["model"], "Wie heißt du?")
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:ich_stelle_mich_vor"
            ]["status"],
            "needs_review",
        )

    def test_wrong_umlauts_require_retry_before_advancing(self):
        state = self.base_state()
        state["lesson_review_training_step"] = 5

        reply = handle_a1_lesson_1_review("A O U", state)

        self.assertIn("Ä, Ö und Ü", reply)
        self.assertEqual(state["lesson_review_training_step"], 5)
        self.assertTrue(state["lesson_review_training_active"])
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:das_deutsche_alphabet"
            ]["status"],
            "needs_review",
        )

        retry = handle_a1_lesson_1_review("Ä Ö Ü", state)

        self.assertIn("ß", retry)
        self.assertEqual(state["lesson_review_training_step"], 6)
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:das_deutsche_alphabet"
            ]["status"],
            "needs_review",
        )

    def test_wrong_eszett_requires_retry_before_review_can_finish(self):
        state = self.base_state()
        state["lesson_review_training_step"] = 6

        reply = handle_a1_lesson_1_review("Doppel-s", state)

        self.assertIn("Eszett", reply)
        self.assertEqual(state["lesson_review_training_step"], 6)
        self.assertTrue(state["lesson_review_training_active"])
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:das_deutsche_alphabet"
            ]["status"],
            "needs_review",
        )

        retry = handle_a1_lesson_1_review("scharfes S", state)

        self.assertIn("morgen noch einmal", retry)
        self.assertFalse(state["lesson_review_training_active"])
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:das_deutsche_alphabet"
            ]["status"],
            "needs_review",
        )

    def test_clean_review_keeps_mastered_skills_and_finishes_good(self):
        state = self.base_state()
        for step in range(1, 7):
            record_review_course_outcome(state, step, True)

        result = complete_lesson_review_training(state)

        self.assertIn("geschafft", result)


if __name__ == "__main__":
    unittest.main()
