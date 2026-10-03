import unittest

from test_nele_live import _assert_course_reply_contract


class CourseLiveContractTests(unittest.TestCase):
    def test_accepts_direct_a1_teacher_reply(self):
        _assert_course_reply_contract("Okay, noch einmal: Woher kommst du?", level="A1")

    def test_rejects_old_roleplay_teacher_cues(self):
        for reply in (
            "Mia: Hallo! Woher kommst du?",
            "Kommst du aus Polen? Antworte Mia.",
            "Du bist dran.",
        ):
            with self.assertRaises(RuntimeError):
                _assert_course_reply_contract(reply, level="A1")

    def test_rejects_empty_a1_reply(self):
        with self.assertRaises(RuntimeError):
            _assert_course_reply_contract("", level="A1")

    def test_does_not_apply_a1_contract_to_higher_level(self):
        _assert_course_reply_contract("Mia: Rollenspiel", level="B2")


if __name__ == "__main__":
    unittest.main()
