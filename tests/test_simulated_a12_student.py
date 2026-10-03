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


if __name__ == "__main__":
    unittest.main()
