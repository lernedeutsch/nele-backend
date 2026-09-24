import unittest
from brain.logic.conversation_health_score import score_turn, score_conversation, record_conversation_health

class ConversationHealthScoreTests(unittest.TestCase):
    def test_clean_turn_scores_100(self):
        result = score_turn(
            compliance={"compliant": True, "violations": []},
            orchestration={"conflicts": []},
            quality={"issues": []},
            topic_transition={"transition": False},
            turn_plan={"allow_topic_transition": True},
        )
        self.assertEqual(result["score"], 100)
        self.assertTrue(result["healthy"])

    def test_compliance_and_conflict_reduce_score(self):
        result = score_turn(
            compliance={"compliant": False, "violations": ["action_mismatch"]},
            orchestration={"conflicts": ["recovery_override_blocked"]},
            quality={"issues": []},
        )
        self.assertLess(result["score"], 80)
        self.assertFalse(result["healthy"])
        signals = {item["signal"] for item in result["deductions"]}
        self.assertIn("turn_plan_compliance", signals)
        self.assertIn("orchestrator_conflict", signals)

    def test_quality_warning_is_small_diagnostic_penalty(self):
        result = score_turn(quality={"issues": ["topic_alignment_warning"]})
        self.assertEqual(result["score"], 98)
        self.assertTrue(result["healthy"])

    def test_conversation_aggregates_turns(self):
        turns = [
            {"meta": {"turn_plan_compliance": {"compliant": True}, "conversation_orchestrator": {"conflicts": []}, "conversation_quality": {"issues": []}}},
            {"meta": {"turn_plan_compliance": {"compliant": True}, "conversation_orchestrator": {"conflicts": []}, "conversation_quality": {"issues": ["response_alignment_warning"]}}},
        ]
        result = score_conversation(turns)
        self.assertEqual(result["turn_count"], 2)
        self.assertEqual(result["average_turn_score"], 99.0)
        self.assertTrue(result["healthy"])

    def test_records_state(self):
        state = {}
        result = {"version": 1, "score": 96, "healthy": True}
        record_conversation_health(state, result)
        self.assertEqual(state["conversation_health_score_v1"], result)

if __name__ == "__main__":
    unittest.main()
