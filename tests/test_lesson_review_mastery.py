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
            (1, "Guten Morgen", True),
            (2, "Guten Tag", True),
            (3, "Guten Abend", True),
            (4, "Tschüss", True),
            (4, "Auf Wiedersehen", True),
            (5, "Mein Name ist Anna", True),
            (5, "Ich bin Anna", True),
            (5, "Ich bin 30 Jahre alt", False),
            (5, "Ich bin müde", False),
            (6, "Wie heisst du?", True),
            (7, "Wie heißen Sie?", True),
            (8, "Ü Ö Ä", True),
            (9, "Es Zett", True),
            (1, "Guten Abend", False),
            (6, "Wie geht es dir?", False),
            (8, "A O U", False),
            (9, "Doppel-s", False),
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

    def test_single_greeting_is_correct_but_cannot_restore_broad_greeting_skill(self):
        state = self.base_state()
        skill = "course:a1:1:wir_begrüßen_uns"
        record_review_course_outcome(state, 1, False)
        state["course_mastery_assistance_used"] = False
        result = evaluate_review_answer(1, "Guten Morgen")
        self.assertTrue(result["correct"])
        record_review_course_outcome(state, 1, True)
        self.assertEqual(state["learning_progress_v1"]["skills"][skill]["status"], "needs_review")

        for step in (2, 3, 4):
            record_review_course_outcome(state, step, True)
        self.assertEqual(state["learning_progress_v1"]["skills"][skill]["status"], "mastered")
        self.assertEqual(
            set(state["learning_progress_v1"]["skills"][skill]["independent_evidence"]),
            {"greeting_morning", "greeting_day", "greeting_evening", "greeting_goodbye"},
        )

    def test_greeting_review_advances_one_small_a1_task_per_turn(self):
        state = self.base_state()
        expected = [
            ("Guten Morgen", 2, "am Tag"),
            ("Guten Tag", 3, "am Abend"),
            ("Guten Abend", 4, "gehst jetzt"),
            ("Tschüss", 5, "stell dich"),
        ]
        for answer, next_step, prompt_fragment in expected:
            reply = handle_a1_lesson_1_review(answer, state)
            self.assertEqual(state["lesson_review_training_step"], next_step)
            self.assertIn(prompt_fragment, reply)

    def test_partial_review_answer_is_scaffolded_and_recorded_as_partial(self):
        state = self.base_state()
        state["lesson_review_training_step"] = 6
        skill = "course:a1:1:ich_stelle_mich_vor"

        reply = handle_a1_lesson_1_review("Wie", state)

        self.assertIn("1 von 3", reply)
        self.assertEqual(state["lesson_review_training_step"], 6)
        self.assertEqual(state["course_teacher_action"]["action"], "scaffold_partial")
        item = state["learning_progress_v1"]["skills"][skill]
        self.assertEqual(item["last_result"], "PARTIAL")
        self.assertEqual(item["partials"], 1)
        self.assertEqual(item["not_yet"], 0)
        self.assertNotEqual(item["status"], "mastered")
        self.assertEqual(state["lesson_review_training_wrong"], 0)

    def test_review_wrong_answer_uses_shared_teacher_engine(self):
        state = self.base_state()
        state["lesson_review_training_step"] = 6

        reply = handle_a1_lesson_1_review("Wie geht es dir?", state)

        self.assertTrue(reply)
        self.assertEqual(state["lesson_review_training_step"], 6)
        self.assertEqual(state["course_teacher_action"]["action"], "correct_and_retry")
        self.assertEqual(state["course_teacher_action"]["reason"], "answer_not_yet")
        self.assertEqual(state["course_teacher_action"]["model"], "Wie heißt du?")
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:ich_stelle_mich_vor"
            ]["status"],
            "needs_review",
        )

    def test_exhausted_review_support_routes_to_review_without_restarting_ladder(self):
        state = self.base_state()
        state["lesson_review_training_step"] = 6

        replies = [handle_a1_lesson_1_review("falsch", state) for _ in range(6)]

        self.assertTrue(any("Das ist okay" in reply for reply in replies))
        self.assertIn("festigen", replies[-1].lower())
        self.assertNotIn("course_model_practice_exhausted", state)
        self.assertFalse(state.get("course_pending_speaking_model"))
        self.assertEqual(state["lesson_review_training_step"], 6)
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:ich_stelle_mich_vor"
            ]["status"],
            "needs_review",
        )

    def test_wrong_umlauts_require_retry_before_advancing(self):
        state = self.base_state()
        state["lesson_review_training_step"] = 8

        reply = handle_a1_lesson_1_review("A O U", state)

        self.assertIn("Ä, Ö und Ü", reply)
        self.assertEqual(state["lesson_review_training_step"], 8)
        self.assertTrue(state["lesson_review_training_active"])
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:das_deutsche_alphabet"
            ]["status"],
            "needs_review",
        )

        retry = handle_a1_lesson_1_review("Ä Ö Ü", state)

        self.assertIn("ß", retry)
        self.assertEqual(state["lesson_review_training_step"], 9)
        self.assertEqual(
            state["learning_progress_v1"]["skills"][
                "course:a1:1:das_deutsche_alphabet"
            ]["status"],
            "needs_review",
        )

    def test_wrong_eszett_requires_retry_before_review_can_finish(self):
        state = self.base_state()
        state["lesson_review_training_step"] = 9

        reply = handle_a1_lesson_1_review("Doppel-s", state)

        self.assertIn("Eszett", reply)
        self.assertEqual(state["lesson_review_training_step"], 9)
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

    def test_repaired_review_is_good_even_after_multiple_earlier_errors(self):
        state = self.base_state()
        state["lesson_review_training_wrong"] = 3

        # The learner made several mistakes earlier, but has since supplied
        # the complete independent evidence needed to restore every skill.
        for step in range(1, 10):
            record_review_course_outcome(state, step, True)

        self.assertTrue(all(
            item["status"] == "mastered"
            for item in state["learning_progress_v1"]["skills"].values()
        ))

        result = complete_lesson_review_training(state)

        self.assertIn("geschafft", result)
        self.assertFalse(state["lesson_review_training_active"])

    def test_clean_review_keeps_mastered_skills_and_finishes_good(self):
        state = self.base_state()
        for step in range(1, 10):
            record_review_course_outcome(state, step, True)

        result = complete_lesson_review_training(state)

        self.assertIn("geschafft", result)


if __name__ == "__main__":
    unittest.main()
