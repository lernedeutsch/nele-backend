import unittest
from unittest.mock import patch

from brain.logic.free_conversation import _model_sentence_from_turn, _model_sentence_from_knowledge, generate_free_conversation_reply


class FreeModelSentencePayloadTests(unittest.TestCase):
    def test_common_short_answers_get_concrete_models(self):
        self.assertEqual(_model_sentence_from_turn("lesen", "hobby"), "Ich lese gern.")
        self.assertEqual(_model_sentence_from_turn("Suppe", "food"), "Ich esse gern Suppe.")
        self.assertEqual(_model_sentence_from_turn("kochen", "work"), "Ich koche.")
        self.assertEqual(_model_sentence_from_turn("Ich lese gern Bücher", "hobby"), "Ich lese gern Bücher.")

    @patch("brain.logic.free_conversation.retrieve")
    def test_retriever_can_supply_model_sentence(self, retrieve):
        from brain.logic.knowledge_retriever import KnowledgeItem
        retrieve.return_value = [
            KnowledgeItem("meine_saetze", "Ich koche gern.", "food", "A1", (), 9.0, "cook")
        ]
        free = {}
        self.assertEqual(_model_sentence_from_knowledge("koche", "food", "A1.1", free), "Ich koche gern.")
        retrieve.assert_called_once()
        self.assertEqual(free["recent_knowledge"], ["cook"])

    @patch("brain.logic.free_conversation.retrieve")
    def test_recent_knowledge_is_passed_back_and_bounded(self, retrieve):
        from brain.logic.knowledge_retriever import KnowledgeItem
        retrieve.return_value = [
            KnowledgeItem("dialogue", "Ich lese gern.", "hobby", "A1", (), 8.0, "reading")
        ]
        free = {"recent_knowledge": [f"old-{i}" for i in range(8)]}
        self.assertEqual(_model_sentence_from_knowledge("lese", "hobby", "A1.1", free), "Ich lese gern.")
        self.assertEqual(free["recent_knowledge"][-1], "reading")
        self.assertEqual(len(free["recent_knowledge"]), 8)
        self.assertEqual(retrieve.call_args.kwargs["recently_used"], tuple(f"old-{i}" for i in range(8)))

    @patch("brain.logic.free_conversation.retrieve", return_value=[])
    def test_existing_model_builder_remains_safe_fallback(self, _retrieve):
        self.assertIsNone(_model_sentence_from_knowledge("Suppe", "food", "A1.1"))
        self.assertEqual(_model_sentence_from_turn("Suppe", "food"), "Ich esse gern Suppe.")

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
            "learning_progress_v1": {
                "skills": {
                    "conversation:supported_answer": {"status": "mastered"},
                }
            },
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
            "next_curriculum_skill": {
                "skill": "conversation:full_sentence",
                "reason": "prerequisites_met",
            },
            "curriculum_skill": "conversation:full_sentence",
            "curriculum_reason": "prerequisites_met",
        }
        # Use an utterance that is not consumed by the early short-answer
        # follow-up route, so the curriculum policy reaches the executor.
        with patch("brain.logic.free_conversation.choose_next_best_learning_action", return_value=forced_policy):
            reply, meta = generate_free_conversation_reply("Ich lese gern Bücher", state)
        policy = state.get("teacher_policy_v2") or {}
        action = state.get("learning_action_executor_v1") or {}
        self.assertEqual(policy.get("action"), "MODEL_SENTENCE")
        self.assertIsNotNone(policy.get("model"))
        self.assertEqual(action.get("action"), "MODEL_SENTENCE")
        self.assertIsNotNone(action.get("model"))
        self.assertNotEqual(action.get("action"), "CONTINUE")


if __name__ == "__main__":
    unittest.main()
