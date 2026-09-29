import unittest

from brain.logic.free_conversation import (
    SUBTOPIC_QUESTIONS,
    _content_followup,
    _extract_facts,
)


class KrimiTopicStatePropagationTests(unittest.TestCase):
    def test_krimi_extracts_hobby_topic(self):
        facts = _extract_facts("Krimi")
        self.assertEqual(facts.get("topic"), "hobby")

    def test_krimi_content_records_reading_kind(self):
        memory = {}
        reply = _content_followup(
            "Krimi", {}, memory, {"last_question": "Was liest du gern?"}, "A1"
        )
        self.assertEqual(memory.get("reading_kind"), "Krimis")
        self.assertIn("Krimi", reply)

    def test_generic_reading_subtopic_is_available(self):
        self.assertIn(("hobby", "reading"), SUBTOPIC_QUESTIONS)

    def test_reading_safety_net_has_more_than_one_followup(self):
        self.assertGreaterEqual(len(SUBTOPIC_QUESTIONS[("hobby", "reading")]), 2)


if __name__ == "__main__":
    unittest.main()
