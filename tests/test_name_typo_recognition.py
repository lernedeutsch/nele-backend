import unittest

from brain.logic.conversation import generate_conversation_reply


class NameTypoDoesNotBlockSessionTests(unittest.TestCase):
    def test_common_heise_typo_is_still_recognized_as_a_name(self):
        sid = "test-heise-typo"
        generate_conversation_reply("Hallo", level="A1.1", lesson=1, session_id=sid)
        reply = generate_conversation_reply("Ich heise Nina", level="A1.1", lesson=1, session_id=sid)
        self.assertIn("Nina", reply)
        self.assertIn("Woher kommst du", reply)

    def test_session_continues_normally_after_the_typo(self):
        sid = "test-heise-typo-continue"
        generate_conversation_reply("Hallo", level="A1.1", lesson=1, session_id=sid)
        generate_conversation_reply("Ich heise Nina", level="A1.1", lesson=1, session_id=sid)
        generate_conversation_reply("Ich komme aus Italien", level="A1.1", lesson=1, session_id=sid)
        reply = generate_conversation_reply("Ich wohne in Rom", level="A1.1", lesson=1, session_id=sid)
        self.assertNotIn("Ich heiße Anna", reply)


if __name__ == "__main__":
    unittest.main()
