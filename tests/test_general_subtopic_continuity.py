import unittest

from brain.logic.free_conversation import _subtopic_followup


class GeneralSubtopicContinuityTests(unittest.TestCase):
    def test_reading_author_keeps_reading_subtopic(self):
        free = {"recent_questions": ["Welche Krimis liest du gern?"]}
        memory = {}
        reply = _subtopic_followup("hobby", "reading", free, memory)
        self.assertIsNotNone(reply)
        self.assertNotIn("Musik", reply)
        self.assertNotIn("Sport", reply)

    def test_music_singer_keeps_music_subtopic(self):
        free = {"recent_questions": ["Welche Musik hörst du gern?"]}
        memory = {}
        reply = _subtopic_followup("hobby", "music", free, memory)
        self.assertIn(reply, {"Wer ist dein Lieblingssänger?", "Hörst du oft Musik?"})

    def test_sport_verein_keeps_sport_subtopic(self):
        free = {"recent_questions": ["Welchen Sport machst du gern?"]}
        memory = {}
        reply = _subtopic_followup("hobby", "sport", free, memory)
        self.assertIn(reply, {"Mit wem machst du Sport?", "Wie oft machst du das?"})

    def test_subtopic_followup_does_not_repeat_recent_question(self):
        free = {"recent_questions": ["Was liest du gern?"]}
        memory = {}
        reply = _subtopic_followup("hobby", "reading", free, memory)
        self.assertNotEqual(reply, "Was liest du gern?")


if __name__ == "__main__":
    unittest.main()
