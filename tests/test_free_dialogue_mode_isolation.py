import unittest

from brain.logic.dialogue_engine import start_dialogue, is_dialogue_active
from brain.logic.free_conversation import generate_free_welcome, generate_free_conversation_reply


class FreeDialogueModeIsolationTests(unittest.TestCase):
    def _course_dialogue_state(self):
        state = {}
        start_dialogue("A1", 2, "woher-kommst-du", state)
        state["dialogue_origin"] = "course"
        return state

    def test_free_welcome_clears_inherited_course_dialogue(self):
        state = self._course_dialogue_state()
        reply = generate_free_welcome(state)
        self.assertIsInstance(reply, str)
        self.assertFalse(is_dialogue_active(state))
        self.assertNotIn("Sag bitte", reply)
        self.assertNotIn("Antworte mit einem ganzen Satz", reply)

    def test_free_reply_clears_inherited_dialogue_even_without_welcome(self):
        state = self._course_dialogue_state()
        reply, _meta = generate_free_conversation_reply("Hallo", state)
        self.assertFalse(is_dialogue_active(state))
        self.assertNotIn("Sag bitte", reply)
        self.assertNotIn("Antworte mit einem ganzen Satz", reply)
        self.assertNotIn("Ich komme aus Polen", reply)

    def test_free_welcome_is_safe_for_varied_first_messages_after_course(self):
        for first_message in ("Hallo", "Guten Morgen", "Wie geht es dir?", "Ich lerne Deutsch", "Heute arbeite ich"):
            state = self._course_dialogue_state()
            welcome = generate_free_welcome(state)
            self.assertFalse(is_dialogue_active(state))
            reply, _meta = generate_free_conversation_reply(first_message, state)
            combined = f"{welcome} {reply}"
            self.assertNotIn("Sag bitte", combined)
            self.assertNotIn("Antworte mit einem ganzen Satz", combined)

    def test_dialogue_started_in_free_is_marked_and_can_continue(self):
        state = {"free_conversation": {"turn_count": 0, "recent_questions": [], "conversation_facts": {}}}
        reply, _meta = generate_free_conversation_reply("Woher kommst du?", state)
        if is_dialogue_active(state):
            self.assertEqual(state.get("dialogue_origin"), "free")
            second, _meta = generate_free_conversation_reply("Polen", state)
            self.assertIsInstance(second, str)


if __name__ == "__main__":
    unittest.main()
