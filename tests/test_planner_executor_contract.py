import unittest

from brain.logic.teacher_policy import PRIORITY
from brain.logic.learning_action_executor import (
    ACTION_CONTRACT,
    execute_learning_action,
    resolve_learning_action,
    validate_learning_action,
)
from brain.logic.turn_plan_compliance import evaluate_turn_plan_compliance


class PlannerExecutorContractTests(unittest.TestCase):
    def test_every_planner_action_has_executor_handler(self):
        self.assertEqual(set(PRIORITY), set(ACTION_CONTRACT))
        for action in PRIORITY:
            contract = ACTION_CONTRACT[action]
            self.assertTrue(contract["handler"])
            self.assertIn("required", contract)

    def test_required_inputs_are_validated(self):
        result = validate_learning_action({"action": "MODEL_SENTENCE"})
        self.assertFalse(result["valid"])
        self.assertEqual(result["missing"], ("model",))

        result = validate_learning_action(
            {"action": "MODEL_SENTENCE", "model": "Ich lese gern."}
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["handler"], "model_sentence")

    def test_missing_model_becomes_explicit_fallback(self):
        resolved = resolve_learning_action({"action": "MODEL_SENTENCE"})
        self.assertEqual(resolved["planned_action"], "MODEL_SENTENCE")
        self.assertEqual(resolved["action"], "CONTINUE")
        self.assertEqual(resolved["fallback_reason"], "model_required_but_unavailable")

        executed = execute_learning_action(
            resolved, fallback_question="Was machst du gern?"
        )
        self.assertEqual(executed["planned_action"], "MODEL_SENTENCE")
        self.assertEqual(executed["executed_action"], "CONTINUE")
        self.assertEqual(executed["fallback_reason"], "model_required_but_unavailable")

        compliance = evaluate_turn_plan_compliance(
            {"action": "MODEL_SENTENCE", "expected_outcome": "use_full_sentence"},
            learning_action=executed,
        )
        self.assertTrue(compliance["compliant"])
        self.assertEqual(compliance["fallback_reason"], "model_required_but_unavailable")

    def test_missing_execution_is_not_compliant(self):
        compliance = evaluate_turn_plan_compliance(
            {"action": "MODEL_SENTENCE", "expected_outcome": "use_full_sentence"},
            learning_action={},
        )
        self.assertFalse(compliance["compliant"])
        self.assertIn("execution_missing", compliance["violations"])


if __name__ == "__main__":
    unittest.main()
