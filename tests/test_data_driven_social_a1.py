import unittest

from brain.knowledge.social_a1_topics import SOCIAL_TOPICS, social_topic_reply
from brain.logic.free_conversation import generate_free_conversation_reply, generate_free_welcome


class DataDrivenSocialA1Tests(unittest.TestCase):
    def test_topic_knowledge_is_data_driven(self):
        self.assertIn("weather", SOCIAL_TOPICS)
        self.assertIn("everyday", SOCIAL_TOPICS)
        self.assertEqual(
            social_topic_reply("Wie ist das Wetter heute?"),
            "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
        )

    def test_topic_router_normalizes_punctuation_and_case(self):
        self.assertIn("Mir geht es gut", social_topic_reply("WIE GEHT ES DIR?!"))
        self.assertIn("Nele", social_topic_reply("Wie heißt du?"))

    def test_free_conversation_uses_shared_topic_router(self):
        state = {}
        generate_free_welcome(state)
        reply, _ = generate_free_conversation_reply("Was machst du heute?", state)
        self.assertIn("Heute spreche ich mit dir", reply)

    def test_new_topic_question_beats_stale_weather_context(self):
        state = {}
        generate_free_welcome(state)
        state["free_conversation"]["last_question"] = "Ist es warm oder kalt?"
        reply, _ = generate_free_conversation_reply("Was kaufst du gern?", state)
        self.assertIn("kauf", reply.lower())
        self.assertNotIn("warm oder kalt", reply.lower())


if __name__ == "__main__":
    unittest.main()
