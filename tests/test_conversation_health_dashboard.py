import unittest
from brain.logic.conversation_health_dashboard import build_health_dashboard, record_health_dashboard

class ConversationHealthDashboardTests(unittest.TestCase):
    def test_empty_dashboard_is_healthy(self):
        dashboard = build_health_dashboard([])
        self.assertEqual(dashboard["summary"]["health_score"], 100)
        self.assertEqual(dashboard["summary"]["turn_count"], 0)
        self.assertTrue(dashboard["summary"]["healthy"])
        self.assertEqual(dashboard["alerts"], [])

    def test_dashboard_collects_diagnostics(self):
        turns = [{
            "meta": {
                "turn_plan": {"action": "SIMPLIFY", "allow_topic_transition": False},
                "turn_plan_compliance": {"compliant": False, "violations": ["action_mismatch"]},
                "conversation_orchestrator": {"conflicts": ["recovery_override_blocked"]},
                "conversation_quality": {"issues": ["topic_alignment_warning"]},
                "topic_transition": {"transition": False},
            }
        }]
        dashboard = build_health_dashboard(turns)
        self.assertEqual(dashboard["summary"]["turn_count"], 1)
        self.assertEqual(dashboard["summary"]["compliance_violation_count"], 1)
        self.assertEqual(dashboard["summary"]["orchestrator_conflict_count"], 1)
        self.assertEqual(dashboard["actions"]["SIMPLIFY"], 1)
        self.assertEqual(dashboard["quality_issues"]["topic_alignment_warning"], 1)
        self.assertIn("turn_plan_compliance", dashboard["alerts"])
        self.assertIn("orchestrator_conflicts", dashboard["alerts"])

    def test_dashboard_tracks_topic_transitions_and_actions(self):
        turns = [
            {"meta": {"turn_plan": {"action": "CONTINUE"}, "topic_transition": {"transition": True, "topic": "work", "next_topic": "hobby"}}},
            {"meta": {"turn_plan": {"action": "ADVANCE"}, "topic_transition": {"transition": False}}},
        ]
        dashboard = build_health_dashboard(turns)
        self.assertEqual(dashboard["summary"]["topic_transition_count"], 1)
        self.assertEqual(dashboard["actions"], {"CONTINUE": 1, "ADVANCE": 1})
        self.assertEqual(dashboard["topic_transitions"][0]["to"], "hobby")

    def test_records_dashboard_state(self):
        state = {}
        dashboard = {"version": 1, "summary": {"health_score": 97}}
        record_health_dashboard(state, dashboard)
        self.assertEqual(state["conversation_health_dashboard_v1"], dashboard)

if __name__ == "__main__":
    unittest.main()
