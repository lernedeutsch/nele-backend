import unittest

from brain.logic.global_conversation_guard import (
    record_answer, select_question, question_intent,
)
from brain.logic.free_conversation import generate_free_conversation_reply


class GlobalConversationGuardTests(unittest.TestCase):
    def test_blocks_exact_question_after_answer(self):
        state = {}
        record_answer(state, "warm", "Wie ist das Wetter bei dir?")
        result = select_question(
            state,
            "Wie ist das Wetter bei dir?",
            ["Was machst du bei diesem Wetter gern?"],
        )
        self.assertTrue(result["changed"])
        self.assertEqual(result["reason"], "ok")

    def test_blocks_semantic_paraphrase_for_known_information(self):
        state = {}
        record_answer(state, "Italien", "Wohin fährst du im Urlaub?")
        result = select_question(
            state,
            "Wohin fährst du gern im Urlaub?",
            ["Mit wem fährst du gern in den Urlaub?"],
        )
        self.assertTrue(result["changed"])
        self.assertIn("Mit wem", result["selected"])

    def test_generalizes_to_unlisted_topic_family(self):
        state = {}
        record_answer(state, "Meine Schwester", "Mit wem gehst du ins Kino?")
        result = select_question(
            state,
            "Mit wem gehst du gern ins Kino?",
            ["Wie oft gehst du ins Kino?"],
        )
        self.assertTrue(result["changed"])
        self.assertIn("Wie oft", result["selected"])

    def test_generalizes_to_unlisted_topic_pet(self):
        state = {}
        record_answer(state, "Luna", "Wie heißt dein Hund?")
        result = select_question(
            state,
            "Wie heißt dein Hund denn?",
            ["Wie alt ist dein Hund?"],
        )
        self.assertTrue(result["changed"])
        self.assertIn("Wie alt", result["selected"])

    def test_question_intents_are_topic_agnostic(self):
        self.assertEqual(question_intent("Wo wohnst du?"), "place")
        self.assertEqual(question_intent("Wann kommt deine Schwester?"), "time")
        self.assertEqual(question_intent("Mit wem gehst du ins Kino?"), "person")
        self.assertEqual(question_intent("Wie oft hörst du Musik?"), "frequency")

    def test_weather_social_early_return_uses_global_guard(self):
        state = {"free_conversation": {
            "last_question": "Wie ist das Wetter bei dir?",
            "recent_questions": ["Wie ist das Wetter bei dir?"],
            "conversation_facts": {},
        }}
        reply, meta = generate_free_conversation_reply("warm", state)
        guard = meta.get("global_conversation_guard") or {}
        self.assertIn("global_conversation_guard_v1", state)
        self.assertTrue(guard)
        self.assertNotIn("Wie ist das Wetter bei dir?", reply)

    def test_multiple_turns_expose_guard_every_time(self):
        state = {"free_conversation": {
            "last_question": "Was machst du gerade?",
            "recent_questions": ["Was machst du gerade?"],
            "conversation_facts": {},
        }}
        for message in ("Arbeit", "8", "kochen", "ja", "Suppe", "Pizza"):
            reply, meta = generate_free_conversation_reply(message, state)
            self.assertTrue(reply)
            self.assertIn("global_conversation_guard", meta)


if __name__ == "__main__":
    unittest.main()
