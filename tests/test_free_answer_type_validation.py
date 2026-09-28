import unittest

from brain.logic.free_conversation import _content_question_repair, generate_free_conversation_reply


class FreeAnswerTypeValidationTests(unittest.TestCase):
    def test_yes_does_not_answer_which_music(self):
        self.assertEqual(
            _content_question_repair("ja", "Welche Musik hörst du gern?"),
            "Ich meine: Welche Musik? Zum Beispiel Pop, Rock oder Klassik.",
        )

    def test_no_does_not_answer_where_question(self):
        reply = _content_question_repair("nein", "Wo machst du gern Urlaub?")
        self.assertIn("Wo genau", reply)

    def test_yes_is_allowed_for_yes_no_question(self):
        self.assertIsNone(_content_question_repair("ja", "Hörst du gern Musik?"))

    def test_live_router_repairs_answer_shape_without_topic_jump(self):
        state = {
            "free_conversation": {
                "last_question": "Welche Musik hörst du gern?",
                "recent_questions": ["Welche Musik hörst du gern?"],
                "asked": ["welche musik hörst du gern"],
                "turn_count": 4,
                "conversation_facts": {},
            },
            "student_progress": {"current_level": "A1.1"},
        }
        reply, meta = generate_free_conversation_reply("ja", state)
        self.assertIn("Welche Musik", reply)
        self.assertIn("Pop", reply)
        self.assertTrue(meta.get("answer_type_repair"))
        self.assertNotIn("Was machst du heute", reply)
        self.assertNotIn("Sport", reply)


if __name__ == "__main__":
    unittest.main()
