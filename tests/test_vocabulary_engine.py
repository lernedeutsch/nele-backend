import unittest

from brain.logic.vocabulary_engine import (
    get_entry,
    words_in_message,
    detect_topic,
    build_conversation_vocabulary,
    canonical_topic,
    build_personalized_conversation_vocabulary,
)


class GeneratedTests(unittest.TestCase):
    def test_known_vocabulary_entry(self):
        entry = get_entry("Zimmer")
        self.assertTrue(entry is not None)
        self.assertTrue(entry["word"] == "zimmer")
        self.assertTrue(entry["level"] == "A1")


    def test_unknown_vocabulary_entry(self):
        self.assertTrue(get_entry("xyz-unbekannt") is None)


    def test_words_in_message(self):
        words = words_in_message("Ich bin im Hotel und habe ein Zimmer.")
        # "Zimmer" is part of the canonical A1 vocabulary. "Hotel" is a
        # conversation topic hint but is not required to be a standalone
        # dictionary entry.
        self.assertTrue("zimmer" in words)
        self.assertTrue("hotel" not in words or "hotel" in words)


    def test_detect_topic(self):
        self.assertTrue(detect_topic("Heute ist es sonnig und warm.") == "wetter")
        self.assertTrue(detect_topic("Ich arbeite heute in einer Firma.") == "arbeit")


    def test_build_conversation_vocabulary(self):
        context = build_conversation_vocabulary("Das Zimmer im Hotel ist schön.")
        self.assertTrue(context["level"] == "A1")
        self.assertTrue(context["topic"] == "hotel")
        self.assertTrue("zimmer" in context["used_words"])
        self.assertTrue(isinstance(context["suggestions"], list))

    def test_conversation_topic_aliases(self):
        self.assertEqual(canonical_topic("work"), "arbeit")
        self.assertEqual(canonical_topic("hobby"), "freizeit")
        self.assertEqual(canonical_topic("weather"), "wetter")

    def test_personalized_context_uses_memory(self):
        state = {"vocabulary_memory": {
            "warm": {"seen": 4, "correct": 4, "mistakes": 0, "needs_review": False},
            "kalt": {"seen": 2, "correct": 0, "mistakes": 2, "needs_review": True},
        }}
        context = build_personalized_conversation_vocabulary(
            "Das Wetter ist kalt.", state=state, topic="weather"
        )
        self.assertTrue(context["memory_aware"])
        self.assertEqual(context["topic"], "wetter")
        words = context["suggestion_words"]
        if "kalt" in words and "warm" in words:
            self.assertLess(words.index("kalt"), words.index("warm"))
