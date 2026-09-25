"""Synthetic A1 learner scenarios for Nele.

These tests complement the lower-level conversation tests with realistic
multi-turn learner behaviour. They intentionally assert invariants rather
than exact prose so Nele can vary natural wording without losing safety.
"""
import re
import unittest

from brain.logic.free_conversation import generate_free_conversation_reply


def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip(" ?!.")


class NeleTestStudent:
    def __init__(self, last_question="Wie geht es dir heute?", facts=None, topic=None):
        self.state = {
            "free_conversation": {
                "last_question": last_question,
                "recent_questions": [last_question],
                "conversation_facts": facts or {},
            }
        }
        if topic:
            self.state["free_conversation"]["topic"] = topic
        self.turns = []

    def say(self, learner):
        reply, meta = generate_free_conversation_reply(learner, self.state)
        if not isinstance(reply, str) or not reply.strip():
            raise AssertionError(f"Empty reply after {learner!r}")
        self.turns.append((learner, reply, meta))
        return reply, meta

    def assert_no_reply_loop(self, case):
        normalized = [_norm(reply) for _, reply, _ in self.turns]
        for left, right in zip(normalized, normalized[1:]):
            case.assertNotEqual(left, right, self.turns)
        # A natural A1 conversation must not fall into a short repeating cycle.
        for size in (2, 3):
            if len(normalized) >= size * 2:
                case.assertNotEqual(normalized[-size:], normalized[-2 * size:-size], self.turns)


class NeleTestStudentTests(unittest.TestCase):
    def test_realistic_short_answer_chain_does_not_loop(self):
        sim = NeleTestStudent()
        for answer in ("gut", "Deutsch lernen", "nein", "um 8 Uhr", "zu Hause", "ja"):
            sim.say(answer)
        sim.assert_no_reply_loop(self)

    def test_work_chain_keeps_context_after_short_answers(self):
        sim = NeleTestStudent("Was machst du heute?", {"topic": "work"}, "work")
        r1, _ = sim.say("Arbeit")
        self.assertIn("arbeit", r1.lower())
        r2, _ = sim.say("um 8 Uhr")
        self.assertTrue("8" in r2 or "acht" in r2.lower(), r2)
        r3, _ = sim.say("kochen")
        self.assertIn("koch", r3.lower())
        self.assertNotIn("ich arbeite kochen", r3.lower())
        sim.assert_no_reply_loop(self)

    def test_origin_answer_is_understood_without_reasking_same_question(self):
        sim = NeleTestStudent("Woher kommst du?")
        reply, _ = sim.say("ich komme aus Polen")
        self.assertNotIn("woher kommst du", _norm(reply))
        self.assertTrue(reply.strip(), reply)

    def test_beginner_error_can_be_repaired_without_sticking(self):
        sim = NeleTestStudent("Was machst du bei der Arbeit?", {"topic": "work"}, "work")
        wrong, _ = sim.say("ich kochen Suppe")
        self.assertIn("ich koche suppe", wrong.lower())
        corrected, _ = sim.say("Ich koche Suppe")
        self.assertNotEqual(_norm(wrong), _norm(corrected))
        self.assertNotIn("ich kochen suppe", corrected.lower())
        sim.assert_no_reply_loop(self)

    def test_asr_style_typo_recovers_and_moves_on(self):
        sim = NeleTestStudent("Wie geht es dir heute?")
        first, _ = sim.say("mude")
        second, _ = sim.say("müde")
        self.assertTrue(first)
        self.assertTrue(second)
        self.assertNotEqual(_norm(first), _norm(second))
        sim.assert_no_reply_loop(self)

    def test_long_mixed_a1_session_has_no_short_cycle(self):
        sim = NeleTestStudent()
        messages = [
            "gut", "Deutsch lernen", "ja", "zu Hause", "Arbeit", "8",
            "kochen", "Suppe", "Wetter", "sonnig", "warm", "spazieren",
            "Freizeit", "Musik", "Pop", "Urlaub", "Polen", "mit meinem Mann",
        ]
        for answer in messages:
            sim.say(answer)
        sim.assert_no_reply_loop(self)
        self.assertEqual(len(sim.turns), len(messages))


if __name__ == "__main__":
    unittest.main()
