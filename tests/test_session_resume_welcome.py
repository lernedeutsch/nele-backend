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


if __name__ == "__main__":
    unittest.main()
