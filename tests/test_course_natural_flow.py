import unittest

from brain.logic.wellbeing_feedback import analyze_wellbeing_response
from brain.nele3_upgrade.router import handle_upgrade_message
from brain.nele3_upgrade.state import (
    get_active_task,
    get_pending_recommendation,
    set_pending_recommendation,
)
from brain.nele3_upgrade.activities import start_activity
from brain.nele3_upgrade.teacher_brain import build_adaptive_recommendation


class NaturalCourseFlowTests(unittest.TestCase):
    def test_wellbeing_accepts_time_modifiers(self):
        for answer in ("Mir geht es heute gut", "Heute geht es mir gut", "Mir geht's heute gut", "Mir geht es gerade gut"):
            result = analyze_wellbeing_response(answer)
            self.assertTrue(result["recognized"])
            self.assertEqual(result["type"], "good")

    def test_decline_stops_recommendation_chain(self):
        state = {}
        set_pending_recommendation(state, build_adaptive_recommendation(state))
        handled, answer, meta = handle_upgrade_message("nein", state)
        self.assertTrue(handled)
        self.assertTrue(meta.get("recommendation_chain_stopped"))
        self.assertIsNone(get_pending_recommendation(state))
        self.assertEqual(answer, "Okay, kein Problem. Wir machen später weiter.")

    def test_decline_cancels_active_addon(self):
        state = {}
        start_activity(state, "speaking", "A1")
        handled, answer, meta = handle_upgrade_message("nein", state)
        self.assertTrue(handled)
        self.assertTrue(meta.get("activity_cancelled"))
        self.assertIsNone(get_active_task(state))
        self.assertNotIn("Versuch es noch einmal", answer)

    def test_course_mode_never_offers_adaptive_addon(self):
        state = {"conversation_mode": "course"}
        self.assertIsNone(build_adaptive_recommendation(state))

    def test_course_mode_clears_stale_addon_and_returns_to_course(self):
        state = {"conversation_mode": "course"}
        set_pending_recommendation(state, {"activity": "work_german"})
        start_activity(state, "speaking", "A1")
        handled, answer, meta = handle_upgrade_message("ja", state)
        self.assertFalse(handled)
        self.assertIsNone(answer)
        self.assertTrue(meta.get("course_only"))
        self.assertIsNone(get_pending_recommendation(state))
        self.assertIsNone(get_active_task(state))


if __name__ == "__main__":
    unittest.main()
