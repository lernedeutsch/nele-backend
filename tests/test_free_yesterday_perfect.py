import unittest

from brain.logic.free_conversation import _perfect_sentence, _short_answer_followup, generate_free_conversation_reply


class FreeYesterdayPerfectTests(unittest.TestCase):
    def test_sentence_builder_uses_haben_and_sein(self):
        self.assertEqual(_perfect_sentence("lesen"), "Ich habe gestern gelesen.")
        self.assertEqual(_perfect_sentence("gehen"), "Ich bin gestern gegangen.")
        self.assertEqual(_perfect_sentence("fahren"), "Ich bin gestern gefahren.")

    def test_gestern_lesen_builds_perfekt_and_keeps_reading_thread(self):
        memory = {}
        reply = _short_answer_followup("lesen", "Was hast du gestern gemacht?", memory)
        self.assertIn("Ich habe gestern gelesen.", reply)
        self.assertIn("Was hast du gelesen?", reply)
        self.assertEqual(memory["filled_slots"]["yesterday_activity"], "lesen")

    def test_full_perfekt_is_accepted_and_followed_up(self):
        memory = {}
        reply = _short_answer_followup("Ich habe gestern gelesen.", "Was hast du gestern gemacht?", memory)
        self.assertEqual(reply, "Was hast du gelesen?")

    def test_live_router_does_not_turn_gestern_lesen_into_ich_lese_gern(self):
        state = {
            "free_conversation": {
                "last_question": "Was hast du gestern gemacht?",
                "recent_questions": ["Was hast du gestern gemacht?"],
                "asked": ["was hast du gestern gemacht"],
                "turn_count": 3,
                "conversation_facts": {},
            },
            "student_progress": {"current_level": "A1.2"},
        }
        reply, _meta = generate_free_conversation_reply("lesen", state)
        self.assertIn("Ich habe gestern gelesen.", reply)
        self.assertIn("Was hast du gelesen?", reply)
        self.assertNotIn("Ich lese gern", reply)


if __name__ == "__main__":
    unittest.main()
