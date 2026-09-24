"""Multi-turn integration simulations for Nele free conversation."""
import unittest
from brain.logic.free_conversation import generate_free_conversation_reply

BAD_GERMAN = ("Ich arbeite Kochen.", "Ich arbeiten", "Ich heißen")

class ConversationSimulator:
    def __init__(self, state=None):
        self.state = state or {"free_conversation": {"last_question": "Was machst du gerade?", "recent_questions": ["Was machst du gerade?"], "conversation_facts": {}}}
        self.turns = []

    def say(self, learner):
        reply, meta = generate_free_conversation_reply(learner, self.state)
        self.turns.append({"learner": learner, "reply": reply, "meta": meta})
        if not isinstance(reply, str) or not reply.strip():
            raise AssertionError(f"Empty reply after {learner!r}")
        for bad in BAD_GERMAN:
            if bad in reply:
                raise AssertionError(f"Known bad German: {bad!r} in {reply!r}")
        return reply, meta

    def assert_no_adjacent_duplicate_replies(self, case):
        for left, right in zip(self.turns, self.turns[1:]):
            case.assertNotEqual(left["reply"], right["reply"])

    def assert_turn_plan_shape(self, case):
        plans = [t["meta"].get("turn_plan") for t in self.turns if t["meta"].get("turn_plan")]
        case.assertTrue(plans, "Simulation should expose a Turn Plan")
        for plan in plans:
            case.assertEqual(plan.get("version"), 2)
            case.assertIn(plan.get("action"), {"REPEAT_ERROR","CORRECT_ERROR","SIMPLIFY","MODEL_SENTENCE","REVIEW_WORD","INTRODUCE_WORD","ADVANCE","CONTINUE"})
            case.assertTrue(plan.get("expected_outcome"))

class ConversationSimulationIntegrationTests(unittest.TestCase):
    def test_work_cooking_chain_stays_coherent(self):
        sim = ConversationSimulator()
        r1, _ = sim.say("Arbeit")
        self.assertIn("arbeit", r1.lower())
        r2, _ = sim.say("8")
        self.assertIn("8 Uhr", r2)
        r3, _ = sim.say("kochen")
        self.assertIn("Ich koche.", r3)
        self.assertNotIn("Ich arbeite Kochen", r3)
        r4, _ = sim.say("ja")
        self.assertNotIn("Wann fängst du", r4)
        self.assertIn("kochst du", r4.lower())
        r5, _ = sim.say("Suppe")
        self.assertIn("Suppe", r5)
        r6, _ = sim.say("Pizza")
        self.assertIn("Pizza", r6)
        self.assertNotIn("Was machst du bei der Arbeit?", r6)
        sim.assert_no_adjacent_duplicate_replies(self)
        sim.assert_turn_plan_shape(self)

    def test_weather_typo_and_activity_continue_without_loop(self):
        sim = ConversationSimulator({"free_conversation": {"last_question": "Wie ist das Wetter bei dir?", "recent_questions": ["Wie ist das Wetter bei dir?"], "conversation_facts": {}}})
        r1, _ = sim.say("Sonn8g")
        self.assertIn("sonnig", r1.lower())
        r2, _ = sim.say("warm")
        self.assertIn("warm", r2.lower())
        r3, _ = sim.say("Radfahren")
        self.assertIn("Rad", r3)
        self.assertNotEqual(r2, r3)
        sim.assert_no_adjacent_duplicate_replies(self)
        sim.assert_turn_plan_shape(self)

    def test_beginner_not_understood_gets_support_not_topic_jump(self):
        sim = ConversationSimulator({"free_conversation": {"last_question": "Was machst du gern in deiner Freizeit?", "recent_questions": ["Was machst du gern in deiner Freizeit?"], "conversation_facts": {}}})
        reply, meta = sim.say("Ich verstehe nicht")
        low = reply.lower()
        self.assertTrue("kein problem" in low or "einfach" in low or "noch einmal" in low, reply)
        plan = meta.get("turn_plan") or sim.state.get("turn_plan_v1") or {}
        if plan.get("action") == "SIMPLIFY":
            self.assertTrue(plan.get("keep_topic"))
            self.assertFalse(plan.get("allow_topic_transition"))
            self.assertTrue(plan.get("allow_question_simplifier"))

    def test_explicit_topic_change_is_respected(self):
        sim = ConversationSimulator({"free_conversation": {"last_question": "Was machst du bei der Arbeit?", "recent_questions": ["Was machst du bei der Arbeit?"], "conversation_facts": {"topic": "work"}, "topic": "work"}})
        reply, _ = sim.say("Ich möchte über Urlaub sprechen")
        self.assertTrue(any(word in reply.lower() for word in ("urlaub","reise","meer","berge")), reply)
        self.assertNotIn("Was machst du bei der Arbeit?", reply)

    def test_error_repair_then_correct_form_does_not_get_stuck(self):
        sim = ConversationSimulator({"free_conversation": {"last_question": "Was machst du bei der Arbeit?", "recent_questions": ["Was machst du bei der Arbeit?"], "conversation_facts": {"topic": "work"}, "topic": "work"}})
        r1, m1 = sim.say("ich kochen Suppe")
        self.assertIn("Ich koche Suppe", r1)
        p1 = m1.get("turn_plan") or sim.state.get("turn_plan_v1") or {}
        if p1.get("pedagogy_locked"):
            self.assertTrue(p1.get("keep_topic"))
            self.assertFalse(p1.get("allow_topic_transition"))
        r2, _ = sim.say("Ich koche Suppe")
        self.assertNotIn("Ich kochen Suppe", r2)
        self.assertNotEqual(r1, r2)

    def test_asr_like_hobby_typo_is_understood_in_context(self):
        sim = ConversationSimulator({"free_conversation": {"last_question": "Was machst du gern in deiner Freizeit?", "recent_questions": ["Was machst du gern in deiner Freizeit?"], "conversation_facts": {"topic": "hobby"}, "topic": "hobby"}})
        reply, meta = sim.say("shwimmen")
        self.assertIn("schw", reply.lower())
        understanding = meta.get("response_understanding") or {}
        if understanding:
            normalized = str(understanding.get("normalized") or understanding.get("text") or "").lower()
            self.assertTrue("schw" in normalized or understanding.get("confidence") is not None)
        sim.assert_turn_plan_shape(self)

    def test_every_simulated_turn_keeps_orchestrator_state(self):
        sim = ConversationSimulator()
        for message in ("Arbeit","8","kochen","ja","Suppe"):
            sim.say(message)
        self.assertIn("conversation_orchestrator_v2", sim.state)
        self.assertIn("conversation_orchestrator_v1", sim.state)
        self.assertIn("turn_plan_v1", sim.state)
        self.assertEqual(sim.state["turn_plan_v1"].get("version"), 2)
        sim.assert_no_adjacent_duplicate_replies(self)

if __name__ == "__main__":
    unittest.main()
