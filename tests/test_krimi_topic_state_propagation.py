import unittest

from brain.logic.free_conversation import (
    SUBTOPIC_QUESTIONS,
    _content_followup,
    _extract_facts,
    _subtopic_followup,
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

    def test_reading_kind_skips_already_completed_genre_slot(self):
        memory = {"reading_kind": "Krimis"}
        free = {"recent_questions": ["Krimis? Welche Krimis liest du gern?"]}

        reply = _subtopic_followup("hobby", "reading", free, memory)

        self.assertEqual(reply, "Was gefällt dir daran?")
        self.assertEqual(memory["subtopic_slots"]["hobby/reading"], 2)

    def test_reading_subtopic_progresses_after_detail_followup(self):
        memory = {"reading_kind": "Krimis"}
        free = {"recent_questions": ["Krimis? Welche Krimis liest du gern?"]}

        first = _subtopic_followup("hobby", "reading", free, memory)
        free["recent_questions"].append(first)
        second = _subtopic_followup("hobby", "reading", free, memory)

        self.assertEqual(first, "Was gefällt dir daran?")
        self.assertEqual(second, "Liest du oft?")
        self.assertEqual(memory["subtopic_slots"]["hobby/reading"], 3)


if __name__ == "__main__":
    unittest.main()
