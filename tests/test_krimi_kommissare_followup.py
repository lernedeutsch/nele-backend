import unittest

from brain.logic.free_conversation import _content_followup


class KrimiKommissareFollowupTests(unittest.TestCase):
    def test_kommissare_uses_existing_krimi_memory(self):
        memory = {"reading_kind": "Krimis"}
        free = {"last_question": "Welche Krimis liest du gern?"}

        reply = _content_followup("Kommissare", {}, memory, free, "A2")

        self.assertEqual(reply, "Liest du solche Krimis oft?")
        self.assertEqual(memory["reading_detail"], "Kommissare")

    def test_kommissare_does_not_require_krimi_in_same_message(self):
        memory = {"reading_kind": "Krimis"}
        free = {"last_question": "Welche Krimis liest du gern?"}

        reply = _content_followup("Kommissare", {}, memory, free, "A1")

        self.assertNotIn("Freizeit", reply)
        self.assertNotIn("Was machst du heute", reply)
        self.assertEqual(reply, "Liest du solche Krimis oft?")


if __name__ == "__main__":
    unittest.main()
