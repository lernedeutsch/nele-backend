import unittest

from brain.logic.turn_plan_compliance import (
    evaluate_turn_plan_compliance,
    record_turn_plan_compliance,
)
from brain.logic.free_conversation import generate_free_conversation_reply


class TurnPlanComplianceMonitorTests(unittest.TestCase):
    def test_compliant_execution(self):
        plan = {
            "action": "SIMPLIFY",
            "expected_outcome": "answer_with_support",
            "allow_topic_transition": False,
            "allow_personalization": False,
            "allow_question_simplifier": True,
            "allow_recovery_override": False,
        }
        result = evaluate_turn_plan_compliance(
            plan,
            learning_action={"action": "SIMPLIFY", "expects_outcome": "answer_with_support"},
            topic_transition={"transition": False},
            question_support={"question": "Arbeitest du?"},
            recovery={"recovered": False},
            orchestration={"conflicts": []},
        )
        self.assertTrue(result["compliant"])
        self.assertEqual(result["status"], "COMPLIANT")
        self.assertEqual(result["violations"], [])

    def test_detects_action_and_expected_outcome_mismatch(self):
        result = evaluate_turn_plan_compliance(
            {"action": "CORRECT_ERROR", "expected_outcome": "continue_after_correction"},
            learning_action={"action": "ADVANCE", "expects_outcome": "independent_answer"},
        )
        self.assertFalse(result["compliant"])
        self.assertIn("action_mismatch", result["violations"])
        self.assertIn("expected_outcome_mismatch", result["violations"])

    def test_detects_forbidden_downstream_overrides(self):
        plan = {
            "action": "SIMPLIFY",
            "expected_outcome": "answer_with_support",
            "allow_topic_transition": False,
            "allow_personalization": False,
            "allow_question_simplifier": True,
            "allow_recovery_override": False,
        }
        result = evaluate_turn_plan_compliance(
            plan,
            learning_action={"action": "SIMPLIFY", "expects_outcome": "answer_with_support"},
            topic_transition={"transition": True},
            personalized_followup={"question": "Wo wohnst du?"},
            recovery={"recovered": True},
        )
        self.assertFalse(result["compliant"])
        self.assertIn("forbidden_topic_transition", result["violations"])
        self.assertIn("forbidden_personalization", result["violations"])
        self.assertIn("forbidden_recovery_override", result["violations"])

    def test_records_bounded_history(self):
        state = {}
        for index in range(55):
            record_turn_plan_compliance(state, {"status": "COMPLIANT", "index": index})
        self.assertEqual(len(state["turn_plan_compliance_history"]), 50)
        self.assertEqual(state["turn_plan_compliance_history"][0]["index"], 5)
        self.assertEqual(state["turn_plan_compliance_v1"]["index"], 54)

    def test_real_free_turn_exposes_compliance(self):
        state = {"free_conversation": {
            "last_question": "Was machst du bei der Arbeit?",
            "recent_questions": ["Was machst du bei der Arbeit?"],
            "conversation_facts": {"topic": "work"},
            "topic": "work",
        }}
        reply, meta = generate_free_conversation_reply("ich kochen Suppe", state)
        self.assertTrue(reply)
        compliance = meta.get("turn_plan_compliance")
        self.assertIsNotNone(compliance)
        self.assertEqual(compliance["version"], 1)
        self.assertIn(compliance["status"], {"COMPLIANT", "VIOLATION"})
        self.assertEqual(state["turn_plan_compliance_v1"], compliance)
        self.assertTrue(state["turn_plan_compliance_history"])


if __name__ == "__main__":
    unittest.main()
