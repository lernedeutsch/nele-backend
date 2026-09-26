import unittest

from brain.logic.free_conversation import (
    FALLBACKS,
    LEVEL_SKILLS,
    _generic_followup,
    generate_free_conversation_reply,
)
from brain.logic.topic_manager import canonical_topic

NEW_TOPICS = [
    "family", "friends", "housing", "weekend", "transport", "technology", "health",
]


class NewEverydayTopicsTests(unittest.TestCase):
    def test_every_new_topic_has_a_fallback_pool(self):
        for topic in NEW_TOPICS + ["food"]:
            self.assertIn(topic, FALLBACKS)
            self.assertGreaterEqual(len(FALLBACKS[topic]), 2)

    def test_every_new_topic_has_a_topic_alias(self):
        for topic in NEW_TOPICS + ["food"]:
            self.assertEqual(canonical_topic(topic), topic)

    def test_every_new_topic_is_listed_in_level_skills(self):
        all_skills = set()
        for skills in LEVEL_SKILLS.values():
            all_skills |= skills
        for topic in NEW_TOPICS + ["food"]:
            self.assertIn(topic, all_skills)

    def _first_turn(self, message, level="A2.1"):
        state = {
            "student_progress": {"current_level": level},
            "free_conversation": {
                "last_question": "Wie ist dein Tag heute?",
                "recent_questions": ["Wie ist dein Tag heute?"],
                "conversation_facts": {},
            },
        }
        reply, _ = generate_free_conversation_reply(message, state)
        return reply, state.get("topic_manager_v2", {}).get("topic")

    def test_family_topic_is_reachable(self):
        _, topic = self._first_turn("Ich habe eine Schwester.", level="A1.2")
        self.assertEqual(topic, "family")

    def test_friends_topic_is_reachable(self):
        reply, topic = self._first_turn("Ich treffe meine Freunde oft.", level="A1.2")
        self.assertEqual(topic, "friends")
        self.assertNotIn(reply, FALLBACKS["today"])

    def test_housing_topic_is_reachable(self):
        _, topic = self._first_turn("Ich wohne in einer Wohnung.", level="A1.3")
        self.assertEqual(topic, "housing")

    def test_weekend_topic_is_reachable(self):
        reply, topic = self._first_turn("Am Wochenende schlafe ich lange.", level="A1.3")
        self.assertEqual(topic, "weekend")
        self.assertNotIn(reply, FALLBACKS["today"])

    def test_transport_topic_is_reachable(self):
        reply, topic = self._first_turn("Ich fahre gern mit dem Fahrrad.")
        self.assertEqual(topic, "transport")
        self.assertNotIn(reply, FALLBACKS["today"])

    def test_technology_topic_is_reachable(self):
        reply, topic = self._first_turn("Ich nutze oft Instagram.")
        self.assertEqual(topic, "technology")
        self.assertNotIn(reply, FALLBACKS["today"])

    def test_health_topic_is_reachable(self):
        reply, topic = self._first_turn("Ich gehe zum Arzt.")
        self.assertEqual(topic, "health")
        self.assertNotIn(reply, FALLBACKS["today"])

    def test_food_topic_no_longer_falls_back_to_today(self):
        free = {"recent_questions": [], "conversation_facts": {}}
        question = _generic_followup("food", free, support=0, independent=0, level="A1.2")
        self.assertIn(question, FALLBACKS["food"])
        self.assertNotIn(question, FALLBACKS["today"])

    def test_levels_really_expand_topic_access(self):
        self.assertNotIn("family", LEVEL_SKILLS["A1.1"])
        self.assertIn("family", LEVEL_SKILLS["A1.2"])
        self.assertIn("housing", LEVEL_SKILLS["A1.3"])
        self.assertIn("transport", LEVEL_SKILLS["A2.1"])


if __name__ == "__main__":
    unittest.main()
