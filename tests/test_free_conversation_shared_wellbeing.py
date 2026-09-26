import unittest

from brain.logic.free_conversation import generate_free_conversation_reply
from brain.logic.wellbeing_feedback import analyze_wellbeing_response


def _wellbeing_state():
    return {"free_conversation": {
        "last_question": "Wie geht es dir?",
        "recent_questions": ["Wie geht es dir?"],
        "conversation_facts": {},
    }}


class FreeConversationSharedWellbeingEngineTests(unittest.TestCase):
    """Regression tests for the shared wellbeing recognizer used by free mode."""

    def test_gut_still_gets_original_reply(self):
        reply, _ = generate_free_conversation_reply("gut", _wellbeing_state())
        self.assertEqual(
            reply,
            "Das freut mich! Du kannst auch sagen: „Mir geht es gut.“ Was machst du heute?",
        )

    def test_prima_still_echoes_prima(self):
        reply, _ = generate_free_conversation_reply("prima", _wellbeing_state())
        self.assertTrue(reply.startswith("Prima!"))

    def test_super_still_echoes_super(self):
        reply, _ = generate_free_conversation_reply("super", _wellbeing_state())
        self.assertTrue(reply.startswith("Super!"))

    def test_schlecht_still_asks_why(self):
        reply, _ = generate_free_conversation_reply("schlecht", _wellbeing_state())
        self.assertIn("Warum geht es dir nicht gut?", reply)
        self.assertIn("Mir geht es schlecht", reply)

    def test_muede_still_asks_about_the_day(self):
        reply, _ = generate_free_conversation_reply("müde", _wellbeing_state())
        self.assertIn("War dein Tag anstrengend?", reply)
        self.assertIn("Ich bin müde", reply)

    def test_es_geht_still_gets_original_model(self):
        reply, _ = generate_free_conversation_reply("es geht", _wellbeing_state())
        self.assertIn("Es geht.", reply)

    def test_free_mode_now_understands_stress(self):
        reply, _ = generate_free_conversation_reply("gestresst", _wellbeing_state())
        self.assertIn("War dein Tag anstrengend?", reply)

    def test_free_mode_now_understands_sadness(self):
        reply, _ = generate_free_conversation_reply("traurig", _wellbeing_state())
        self.assertIn("Warum geht es dir nicht gut?", reply)

    def test_free_mode_now_understands_illness(self):
        reply, _ = generate_free_conversation_reply("krank", _wellbeing_state())
        self.assertIn("Fühlst du dich schon besser?", reply)

    def test_free_mode_now_corrects_common_spelling_mistake(self):
        reply, _ = generate_free_conversation_reply("gutt", _wellbeing_state())
        self.assertIn("gut", reply.lower())
        self.assertIn("Was machst du heute?", reply)

    def test_full_sentence_good_answer_is_not_wrapped_again(self):
        reply, _ = generate_free_conversation_reply("Mir geht es gut.", _wellbeing_state())
        self.assertNotIn("mir geht es mir geht es", reply.lower())
        self.assertIn("Was machst du heute?", reply)

    def test_full_sentence_bad_answer_is_not_wrapped_again(self):
        reply, _ = generate_free_conversation_reply("Mir geht es schlecht.", _wellbeing_state())
        self.assertNotIn("mir geht es mir geht es", reply.lower())
        self.assertIn("Warum geht es dir nicht gut?", reply)

    def test_unseen_example_viel_stress(self):
        reply, _ = generate_free_conversation_reply("viel Stress", _wellbeing_state())
        self.assertIn("Ich habe Stress.", reply)
        self.assertIn("War dein Tag anstrengend?", reply)

    def test_longer_conversation_moves_on_after_wellbeing(self):
        state = _wellbeing_state()
        reply1, _ = generate_free_conversation_reply("gut", state)
        self.assertIn("Was machst du heute?", reply1)

        state["free_conversation"]["last_question"] = "Was machst du heute?"
        reply2, _ = generate_free_conversation_reply("Ich arbeite heute.", state)
        self.assertNotIn("Wie geht es dir?", reply2)

    def test_shared_engine_recognises_the_same_new_moods(self):
        analysis = analyze_wellbeing_response("gestresst")
        self.assertTrue(analysis["recognized"])
        self.assertEqual(analysis["type"], "stressed")


if __name__ == "__main__":
    unittest.main()
