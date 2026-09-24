import unittest

from brain.logic.vocabulary_engine import (
    get_entry,
    words_in_message,
    detect_topic,
    build_conversation_vocabulary,
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
        self.assertTrue("hotel" in words)
        self.assertTrue("zimmer" in words)


    def test_detect_topic(self):
        self.assertTrue(detect_topic("Heute ist es sonnig und warm.") == "wetter")
        self.assertTrue(detect_topic("Ich arbeite heute in einer Firma.") == "arbeit")


    def test_build_conversation_vocabulary(self):
        context = build_conversation_vocabulary("Das Zimmer im Hotel ist schön.")
        self.assertTrue(context["level"] == "A1")
        self.assertTrue(context["topic"] == "hotel")
        self.assertTrue("zimmer" in context["used_words"])
        self.assertTrue(isinstance(context["suggestions"], list))
