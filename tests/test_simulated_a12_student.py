import unittest

from brain.logic.a1_lesson2_conversation import start, handle


class SimulatedA12StudentTests(unittest.TestCase):
    def state(self):
        return {
            "conversation_mode": "course",
            "learning_progress_v1": {"version": 1, "skills": {}},
        }

    def test_exhausted_support_defers_target_instead_of_repeating_it(self):
        state = self.state()
        first_prompt = start("Verb kommen", state)
        first_intent = state["a1_l2_tutor"]["task"]["intent"]

        replies = []
        # Five failed attempts traverse hint -> starter -> model -> slow model
        # -> bounded exhaustion. The sixth turn lets the owning lesson consume
        # the exhaustion signal and must route away from the failed target.
        for _ in range(5):
            replies.append(handle("ich weiß nicht", state))

        self.assertIn("später noch einmal", replies[-1])
        reply_after_exhaustion = handle("okay", state)

        self.assertNotEqual(reply_after_exhaustion, first_prompt)
        self.assertNotEqual(state["a1_l2_tutor"]["task"]["intent"], first_intent)
        self.assertEqual(state.get("course_speaking_support_level"), 0)
        self.assertIsNone(state.get("course_pending_speaking_model"))


    def test_exhausted_support_revisits_the_exact_deferred_task_after_transfer(self):
        state = self.state()
        first_prompt = start("Verb kommen", state)
        first_task = dict(state["a1_l2_tutor"]["task"])

        for _ in range(5):
            last = handle("ich weiß nicht", state)
        self.assertIn("später noch einmal", last)

        transfer_prompt = handle("okay", state)
        transfer_task = dict(state["a1_l2_tutor"]["task"])
        self.assertNotEqual(transfer_task["intent"], first_task["intent"])
        self.assertNotEqual(transfer_prompt, first_prompt)
        self.assertEqual(state["course_deferred_tasks"], [first_task])

        reply = handle(transfer_task["expected"], state)

        self.assertIn(first_task["prompt"], reply)
        self.assertEqual(state["a1_l2_tutor"]["task"], first_task)
        self.assertNotIn("course_deferred_tasks", state)
        self.assertFalse(state.get("course_mastery_assistance_used", False))


if __name__ == "__main__":
    unittest.main()
