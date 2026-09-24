"""Long-horizon conversation simulations and diagnostic reports for Nele."""
import re
import unittest

from brain.logic.free_conversation import generate_free_conversation_reply
from brain.logic.conversation_health_score import score_conversation, score_turn
from brain.logic.conversation_health_dashboard import build_health_dashboard

BAD_GERMAN = ("Ich arbeite Kochen.", "Ich arbeiten", "Ich heißen")
ACTIONS = {"REPEAT_ERROR","CORRECT_ERROR","SIMPLIFY","MODEL_SENTENCE","REVIEW_WORD","INTRODUCE_WORD","ADVANCE","CONTINUE"}

def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip(" ?!.")

class LongConversationSimulator:
    def __init__(self, state=None):
        self.state = state or {
            "free_conversation": {
                "last_question": "Was machst du gerade?",
                "recent_questions": ["Was machst du gerade?"],
                "conversation_facts": {},
            }
        }
        self.turns = []

    def say(self, learner):
        reply, meta = generate_free_conversation_reply(learner, self.state)
        if not isinstance(reply, str) or not reply.strip():
            raise AssertionError(f"Empty reply after {learner!r}")
        for bad in BAD_GERMAN:
            if bad in reply:
                raise AssertionError(f"Known bad German: {bad!r} in {reply!r}")
        self.turns.append({"learner": learner, "reply": reply, "meta": meta})
        return reply, meta

    def run(self, messages):
        for message in messages:
            self.say(message)
        return self.report()

    def report(self):
        adjacent_duplicates = []
        for index in range(1, len(self.turns)):
            if _norm(self.turns[index-1]["reply"]) == _norm(self.turns[index]["reply"]):
                adjacent_duplicates.append(index)

        compliance_violations = []
        orchestrator_conflicts = []
        invalid_plans = []
        unexpected_transitions = []
        for index, turn in enumerate(self.turns):
            meta = turn["meta"]
            plan = meta.get("turn_plan") or {}
            if plan and (plan.get("version") != 2 or plan.get("action") not in ACTIONS or not plan.get("expected_outcome")):
                invalid_plans.append(index)
            compliance = meta.get("turn_plan_compliance")
            if compliance and not compliance.get("compliant"):
                compliance_violations.append({"turn": index, "violations": compliance.get("violations") or []})
            orchestration = meta.get("conversation_orchestrator") or {}
            if orchestration.get("conflicts"):
                orchestrator_conflicts.append({"turn": index, "conflicts": orchestration["conflicts"]})
            transition = meta.get("topic_transition") or {}
            if transition.get("transition") and plan and not plan.get("allow_topic_transition", True):
                unexpected_transitions.append(index)

        health = score_conversation(self.turns)
        dashboard = build_health_dashboard(self.turns)
        return {
            "turn_count": len(self.turns),
            "conversation_health": health,
            "conversation_health_dashboard": dashboard,
            "adjacent_duplicate_replies": adjacent_duplicates,
            "compliance_violations": compliance_violations,
            "orchestrator_conflicts": orchestrator_conflicts,
            "invalid_turn_plans": invalid_plans,
            "unexpected_topic_transitions": unexpected_transitions,
        }

class ConversationSimulationV2Tests(unittest.TestCase):
    def assert_clean_report(self, report):
        self.assertGreaterEqual(report["turn_count"], 15)
        self.assertEqual(report["adjacent_duplicate_replies"], [], report)
        self.assertEqual(report["compliance_violations"], [], report)
        self.assertEqual(report["orchestrator_conflicts"], [], report)
        self.assertEqual(report["invalid_turn_plans"], [], report)
        self.assertEqual(report["unexpected_topic_transitions"], [], report)
        self.assertTrue(report["conversation_health"]["healthy"], report)
        self.assertGreaterEqual(report["conversation_health"]["score"], 80, report)
        dashboard = report["conversation_health_dashboard"]
        self.assertEqual(dashboard["summary"]["turn_count"], report["turn_count"])
        self.assertEqual(dashboard["summary"]["compliance_violation_count"], 0, report)
        self.assertEqual(dashboard["summary"]["orchestrator_conflict_count"], 0, report)

    def test_20_turn_everyday_conversation_has_no_engine_conflicts(self):
        sim = LongConversationSimulator()
        report = sim.run([
            "Arbeit", "8", "kochen", "ja", "Suppe",
            "Pizza", "Ich koche Suppe", "Wetter", "sonnig", "warm",
            "Radfahren", "ja", "Freizeit", "Musik", "Pop",
            "ja", "Urlaub", "Meer", "schwimmen", "gern",
        ])
        self.assert_clean_report(report)

    def test_18_turn_beginner_recovery_and_topic_changes_remain_safe(self):
        sim = LongConversationSimulator({
            "free_conversation": {
                "last_question": "Was machst du gern in deiner Freizeit?",
                "recent_questions": ["Was machst du gern in deiner Freizeit?"],
                "conversation_facts": {"topic": "hobby"},
                "topic": "hobby",
            }
        })
        report = sim.run([
            "Ich verstehe nicht", "Musik", "ja", "Pop",
            "Arbeit", "ich kochen Suppe", "Ich koche Suppe", "8",
            "Wetter", "Sonn8g", "warm", "shwimmen",
            "Urlaub", "Meer", "ja", "Freizeit", "lesen", "Buch",
        ])
        self.assert_clean_report(report)

    def test_30_turn_stress_simulation_keeps_turn_plan_and_compliance_state(self):
        sim = LongConversationSimulator()
        messages = [
            "Arbeit", "8", "kochen", "ja", "Suppe", "Pizza",
            "Wetter", "sonnig", "warm", "Radfahren",
            "Freizeit", "Musik", "Pop", "ja", "lesen",
            "Urlaub", "Meer", "schwimmen", "gern", "Reise",
            "Arbeit", "Hotel", "8", "kochen", "Nudeln",
            "Wetter", "kalt", "nein", "Freizeit", "Sport",
        ]
        report = sim.run(messages)
        self.assertEqual(report["turn_count"], 30)
        self.assert_clean_report(report)
        self.assertIn("turn_plan_compliance_v1", sim.state)
        self.assertIn("turn_plan_compliance_history", sim.state)
        self.assertLessEqual(len(sim.state["turn_plan_compliance_history"]), 50)
        self.assertIn("conversation_orchestrator_v2", sim.state)

if __name__ == "__main__":
    unittest.main()
