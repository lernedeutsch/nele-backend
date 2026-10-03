import unittest
from unittest.mock import patch

from brain.logic.session_service import start_conversation_session


class SessionResumeWelcomeTests(unittest.TestCase):
    @patch("brain.logic.session_service.generate_welcome_reply")
    @patch("brain.logic.session_service.resume_current_training")
    @patch("brain.logic.session_service.start_upgrade_session")
    @patch("brain.logic.session_service.ensure_upgrade_state")
    @patch("brain.logic.session_service.save_conversation_state")
    @patch("brain.logic.session_service.get_conversation_state")
    def test_page_reopen_returns_active_course_prompt(
        self, get_state, save_state, ensure_state, start_session, resume, welcome
    ):
        state = {"dialogue_active": True}
        get_state.return_value = state
        resume.return_value = "Mia: Kommst du aus Polen? Antworte Mia."

        reply = start_conversation_session("test-user", new_conversation=False)

        self.assertEqual(reply, "Mia: Kommst du aus Polen? Antworte Mia.")
        resume.assert_called_once_with(state)
        welcome.assert_not_called()
        save_state.assert_called_once_with("test-user")

    @patch("brain.logic.session_service.generate_welcome_reply", return_value="Hallo Moni!")
    @patch("brain.logic.session_service.resume_current_training")
    @patch("brain.logic.session_service.prepare_new_conversation")
    @patch("brain.logic.session_service.start_upgrade_session")
    @patch("brain.logic.session_service.ensure_upgrade_state")
    @patch("brain.logic.session_service.save_conversation_state")
    @patch("brain.logic.session_service.get_conversation_state", return_value={})
    def test_new_conversation_does_not_resume_old_prompt(
        self, get_state, save_state, ensure_state, start_session, prepare_new, resume, welcome
    ):
        reply = start_conversation_session("test-user", new_conversation=True)

        self.assertEqual(reply, "Hallo Moni!")
        prepare_new.assert_called_once()
        resume.assert_not_called()


    def test_new_conversation_clears_transient_course_state_but_keeps_progress(self):
        from brain.logic.session_state import prepare_new_conversation

        progress = {"skills": {"A1:3:sein": {"status": "needs_review"}}}
        state = {
            "learning_progress_v1": progress,
            "lesson_teaching_active": True,
            "lesson_teaching_level": "A1",
            "lesson_teaching_lesson": 3,
            "lesson_teaching_section": "sein",
            "lesson_teaching_step": 2,
            "generic_lesson_review_active": True,
            "generic_lesson_review_sections": ["Alter", "sein"],
            "generic_lesson_review_index": 1,
            "generic_lesson_review_level": "A1",
            "generic_lesson_review_lesson": 3,
            "course_mastery_assistance_used": True,
            "course_generic_assisted_step": 2,
            "course_pending_speaking_model": "bin",
            "course_model_practice_exhausted": {"step": 2},
            "course_teaching_decision": {"decision": "continue_current"},
        }

        prepare_new_conversation(state)

        self.assertFalse(state["lesson_teaching_active"])
        self.assertIsNone(state["lesson_teaching_level"])
        self.assertIsNone(state["lesson_teaching_lesson"])
        self.assertIsNone(state["lesson_teaching_section"])
        self.assertEqual(state["lesson_teaching_step"], 0)
        self.assertFalse(state["generic_lesson_review_active"])
        self.assertEqual(state["generic_lesson_review_sections"], [])
        self.assertEqual(state["generic_lesson_review_index"], 0)
        self.assertIsNone(state["generic_lesson_review_level"])
        self.assertIsNone(state["generic_lesson_review_lesson"])
        self.assertFalse(state["course_mastery_assistance_used"])
        self.assertNotIn("course_generic_assisted_step", state)
        self.assertNotIn("course_pending_speaking_model", state)
        self.assertNotIn("course_model_practice_exhausted", state)
        self.assertNotIn("course_teaching_decision", state)
        self.assertIs(state["learning_progress_v1"], progress)


if __name__ == "__main__":
    unittest.main()
