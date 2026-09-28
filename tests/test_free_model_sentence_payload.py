import unittest
from unittest.mock import patch

from brain.logic.free_conversation import _model_sentence_from_turn, generate_free_conversation_reply


class FreeModelSentencePayloadTests(unittest.TestCase):
    def test_common_short_answers_get_concrete_models(self):
        self.assertEqual(_model_sentence_from_turn("lesen", "hobby"), "Ich lese gern.")
        self.assertEqual(_model_sentence_from_turn("Suppe", "food"), "Ich esse gern Suppe.")
        self.assertEqual(_model_sentence_from_turn("kochen", "work"), "Ich koche.")

    def test_curriculum_model_sentence_reaches_executor_with_model(self):
        state = {
            "free_conversation": {
                "last_question": "Was machst du gern in deiner Freizeit?",
                "recent_questions": ["Was machst du gern in deiner Freizeit?"],
                "asked": ["was machst du gern in deiner freizeit"],
                "turn_count": 10,
                "conversation_facts": {},
                "last_topic": "hobby",
            },
            "student_progress": {"current_level": "A1.1"},
        }
        forced_policy = {
            "version": 3,
            "action": "MODEL_SENTENCE",
            "priority": 70,
            "reason": "curriculum_next_ready_skill",
            "continue_conversation": True,
            "topic": "hobby",
            "subtopic": "leisure",
            "model": None,
        }
        with patch("brain.logic.free_conversation.choose_next_best_learning_action", return_value=forced_policy):
            reply, meta = generate_free_conversation_reply("lesen", state)
        action = meta.get("learning_action") or state.get("learning_action_executor_v1") or {}
        self.assertEqual(action.get("action"), "MODEL_SENTENCE")
        self.assertEqual(action.get("model"), "Ich lese gern.")
        self.assertIn("Ich lese gern.", reply)
        self.assertNotEqual(action.get("action"), "CONTINUE")


if __name__ == "__main__":
    unittest.main()
