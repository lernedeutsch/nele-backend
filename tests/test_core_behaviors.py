import unittest

from brain.nele3_upgrade.activities import (
    _items_for_level,
    _looks_like_prompt_echo,
    resume_active_task,
)
from brain.nele3_upgrade.router import handle_upgrade_message
from brain.nele3_upgrade.teacher_brain import build_adaptive_recommendation
from brain.nele3_upgrade.state import mark_activity_completed, update_skill
from brain.nele3_upgrade.content import (
    DIALOGUES,
    LISTENING_TASKS,
    WRITING_TASKS,
    WORK_GERMAN,
    PRONUNCIATION_TARGETS,
)
from brain.logic.lesson_loader import (
    get_available_lesson_numbers,
)


class NeleCoreBehaviorTests(unittest.TestCase):

    def test_a1_addon_content_never_returns_a2_items(self):
        groups = [
            DIALOGUES,
            LISTENING_TASKS,
            WRITING_TASKS,
            WORK_GERMAN,
            PRONUNCIATION_TARGETS,
        ]

        for group in groups:
            selected = _items_for_level(group, "A1")
            self.assertTrue(selected)
            self.assertTrue(
                all(
                    str(item.get("level") or "A1").upper() == "A1"
                    for item in selected
                )
            )

    def test_a2_addon_content_uses_a2_when_available(self):
        for group in [
            DIALOGUES,
            LISTENING_TASKS,
            WRITING_TASKS,
            WORK_GERMAN,
            PRONUNCIATION_TARGETS,
        ]:
            selected = _items_for_level(group, "A2")
            self.assertTrue(selected)
            self.assertTrue(
                all(
                    str(item.get("level") or "").upper() == "A2"
                    for item in selected
                )
            )

    def test_writing_prompt_copy_is_detected(self):
        prompt = (
            "Schreib zwei kurze Sätze: "
            "Du kommst heute zehn Minuten später zur Arbeit."
        )

        self.assertTrue(
            _looks_like_prompt_echo(
                "Du kommst heute zehn Minuten später zur Arbeit.",
                prompt,
            )
        )

        self.assertFalse(
            _looks_like_prompt_echo(
                "Ich komme heute zehn Minuten später. Entschuldigung.",
                prompt,
            )
        )

    def test_interrupted_writing_task_can_resume(self):
        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "writing",
                    "prompt": "Schreib zwei kurze Sätze.",
                }
            }
        }

        result = resume_active_task(state)

        self.assertIsInstance(result, dict)
        self.assertIn("Schreib zwei kurze Sätze.", result["reply"])
        self.assertTrue(result["meta"]["resumed"])

    def test_interrupted_listening_task_keeps_audio_text(self):
        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "listening",
                    "prompt": "Um wie viel Uhr fährt der Zug?",
                    "speak_text": "Der Zug fährt um acht Uhr zwanzig.",
                }
            }
        }

        result = resume_active_task(state)

        self.assertEqual(
            result["speak_text"],
            "Der Zug fährt um acht Uhr zwanzig.",
        )
        self.assertEqual(
            result["meta"]["activity"],
            "listening",
        )

    def test_empty_a1_lesson_2_is_not_treated_as_ready(self):
        available = get_available_lesson_numbers("A1")
        self.assertNotIn(2, available)

    def test_wellbeing_reply_is_not_consumed_by_interrupted_addon_task(self):
        state = {
            "last_question": "wellbeing",
            "nele3_upgrade": {
                "active_task": {
                    "type": "writing",
                    "prompt": "Schreib zwei kurze Sätze.",
                    "keywords": ["komme", "später"],
                    "required": ["ich"],
                    "min_words": 6,
                    "min_sentences": 2,
                }
            }
        }

        handled, answer, meta = handle_upgrade_message(
            "Gut",
            state,
        )

        self.assertFalse(handled)
        self.assertIsNone(answer)
        self.assertEqual(meta, {})
        self.assertEqual(
            state["nele3_upgrade"]["active_task"]["type"],
            "writing",
        )

    def test_teacher_brain_does_not_repeat_just_completed_skill(self):
        state = {}

        update_skill(state, "writing", 40)
        update_skill(state, "writing", 100)
        mark_activity_completed(
            state,
            "writing",
            detail="Verspätung melden",
            score=100,
        )

        recommendation = build_adaptive_recommendation(state)

        self.assertIsInstance(recommendation, dict)
        self.assertNotEqual(
            recommendation.get("activity"),
            "writing",
        )


if __name__ == "__main__":
    unittest.main()
