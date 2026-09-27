import unittest
from unittest.mock import patch

from brain.logic.personal_sentences import should_offer_personal_sentence_practice
from brain.logic.lesson_teaching import handle_lesson_teaching


class DialoguePersonalSentencePriorityTests(unittest.TestCase):
    def test_personal_sentence_offer_is_blocked_during_active_dialogue(self):
        state = {
            "dialogue_active": True,
            "lesson_teaching_active": False,
            "personal_sentences": {
                "items": {},
                "recent_ids": [],
                "scheduler": {"turns_since_practice": 9},
            },
        }
        self.assertFalse(
            should_offer_personal_sentence_practice(
                state,
                normal_turns=9,
                learner_needs_support=False,
                has_active_error=False,
            )
        )

    def test_active_dialogue_clears_stale_personal_drill_and_owns_turn(self):
        state = {
            "dialogue_active": True,
            "personal_sentence_practice": {
                "id": "arbeitest_du_am_sonntag",
                "attempts": 0,
            },
        }
        with patch("brain.logic.lesson_teaching.is_dialogue_active", return_value=True), patch(
            "brain.logic.lesson_teaching.handle_dialogue",
            return_value="Mia: Kommst du aus Polen? Antworte Mia.",
        ) as dialogue:
            reply = handle_lesson_teaching("ich komme aus Polen", state)

        self.assertEqual(reply, "Mia: Kommst du aus Polen? Antworte Mia.")
        self.assertNotIn("personal_sentence_practice", state)
        dialogue.assert_called_once_with("ich komme aus Polen", state)


if __name__ == "__main__":
    unittest.main()
