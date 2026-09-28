import unittest

from brain.logic.free_conversation import _correction_followup, generate_free_conversation_reply
from brain.logic.error_engine import process_error


class FreeCorrectionTopicContinuityTests(unittest.TestCase):
    def test_cooking_correction_builds_same_subtopic_followup(self):
        state = {}
        result = process_error("ich kochen Suppe", state, support_level=1, context={"mode": "free", "topic": "work"})
        memory = {}
        question = _correction_followup(result, "work", memory)
        self.assertEqual(question, "Kochst du oft Suppe?")
        self.assertEqual(memory["filled_slots"]["cooked_food"], "Suppe")

    def test_live_reply_corrects_and_continues_cooking(self):
        state = {
            "free_conversation": {
                "last_question": "Was machst du bei der Arbeit?",
                "recent_questions": ["Was machst du bei der Arbeit?"],
                "asked": ["was machst du bei der arbeit"],
                "turn_count": 3,
                "conversation_facts": {},
                "last_topic": "work",
            },
            "student_progress": {"current_level": "A1.1"},
        }
        reply, meta = generate_free_conversation_reply("ich kochen Suppe", state)
        self.assertIn("Ich koche Suppe.", reply)
        self.assertIn("Kochst du oft Suppe?", reply)
        self.assertNotIn("Was möchtest du heute", reply)
        self.assertEqual(meta.get("topic"), "work")


if __name__ == "__main__":
    unittest.main()
