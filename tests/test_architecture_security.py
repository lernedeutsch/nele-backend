import os
import unittest
from unittest.mock import patch

import brain.logic.memory as memory_module
from brain.logic.session_state import prepare_new_conversation
from brain.nele3_upgrade.state import get_active_task
from server.app import app


class NeleArchitectureSecurityTests(unittest.TestCase):

    def test_new_conversation_clears_all_transient_engines_but_keeps_learning_memory(self):
        state = {
            "name": "Moni",
            "user_facts": {"name": "Moni"},
            "student_progress": {"current_level": "A1", "completed_exercises": 12},
            "lesson_progress": {"lessons": {"A1-1": {"current_section": "Alphabet"}}},
            "vocabulary_memory": {"hotel": {"seen": 3}},
            "error_memory": {"article": {"count": 2}},
            "daily_learning": {"date": "2026-09-19"},
            "last_activity": "lesson",
            "last_activity_detail": "Das deutsche Alphabet",
            "current_topic": "temporary",
            "current_comparison": "temporary",
            "current_expression": "temporary",
            "personalization_exercise": {"type": "temporary"},
            "vocabulary_practice_active": True,
            "vocabulary_practice_word": "Hotel",
            "vocabulary_practice_type": "meaning",
            "error_practice_active": True,
            "error_practice_type": "article",
            "error_practice_step": 2,
            "lesson_review_training_active": True,
            "lesson_review_training_step": 2,
            "lesson_teaching_active": True,
            "lesson_teaching_section": "Das deutsche Alphabet",
            "lesson_teaching_step": 4,
            "pending_new_learning": {"type": "new_section"},
            "pending_error_review": "vocabulary",
            "last_question": "some_old_question",
            "nele3_upgrade": {
                "active_task": {
                    "type": "listening",
                    "prompt": "Um wie viel Uhr fährt der Zug?",
                },
                "pending_recommendation": {
                    "activity": "writing",
                },
                "skills": {
                    "listening": {
                        "attempts": 3,
                        "correct": 2,
                        "score_avg": 80.0,
                    }
                },
            },
        }

        prepare_new_conversation(state)

        self.assertIsNone(get_active_task(state))
        self.assertFalse(state["lesson_teaching_active"])
        self.assertIsNone(state["lesson_teaching_section"])
        self.assertEqual(state["lesson_teaching_step"], 0)
        self.assertFalse(state["lesson_review_training_active"])
        self.assertFalse(state["vocabulary_practice_active"])
        self.assertFalse(state["error_practice_active"])
        self.assertIsNone(state["pending_new_learning"])
        self.assertIsNone(state["pending_error_review"])
        self.assertIsNone(state["current_topic"])
        self.assertIsNone(state["last_question"])

        self.assertEqual(state["name"], "Moni")
        self.assertEqual(state["user_facts"]["name"], "Moni")
        self.assertEqual(state["student_progress"]["completed_exercises"], 12)
        self.assertEqual(
            state["lesson_progress"]["lessons"]["A1-1"]["current_section"],
            "Alphabet",
        )
        self.assertEqual(state["vocabulary_memory"]["hotel"]["seen"], 3)
        self.assertEqual(state["error_memory"]["article"]["count"], 2)
        self.assertEqual(state["last_activity_detail"], "Das deutsche Alphabet")
        self.assertEqual(
            state["nele3_upgrade"]["skills"]["listening"]["attempts"],
            3,
        )


    def test_welcome_new_conversation_clears_legacy_and_nele3_active_state(self):
        state = {
            "onboarding_completed": True,
            "user_facts": {"name": "Moni"},
            "student_progress": {
                "current_level": "A1",
                "completed_exercises": 7,
            },
            "lesson_progress": {
                "lessons": {
                    "A1-1": {
                        "current_section": "Das deutsche Alphabet",
                    }
                }
            },
            "lesson_teaching_active": True,
            "lesson_teaching_section": "Das deutsche Alphabet",
            "lesson_teaching_step": 4,
            "nele3_upgrade": {
                "active_task": {
                    "type": "listening",
                    "prompt": "Um wie viel Uhr fährt der Zug?",
                }
            },
        }

        client = app.test_client()

        with patch(
            "server.app.acquire_session_lock",
            return_value=None,
        ), patch(
            "server.app.refresh_conversation_state"
        ), patch(
            "brain.logic.session_service.get_conversation_state",
            return_value=state,
        ), patch(
            "brain.logic.session_service.save_conversation_state"
        ), patch(
            "brain.logic.welcome.get_conversation_state",
            return_value=state,
        ), patch(
            "brain.logic.welcome.save_conversation_state"
        ):
            response = client.post(
                "/welcome",
                json={
                    "session_id": "stable-moni-id",
                    "new_conversation": True,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["session_id"],
            "stable-moni-id",
        )
        self.assertIsNone(get_active_task(state))
        self.assertFalse(state["lesson_teaching_active"])
        self.assertIsNone(state["lesson_teaching_section"])
        self.assertEqual(state["lesson_teaching_step"], 0)

        # Durable learning memory is still present.
        self.assertEqual(
            state["student_progress"]["completed_exercises"],
            7,
        )
        self.assertEqual(
            state["lesson_progress"]["lessons"]["A1-1"]["current_section"],
            "Das deutsche Alphabet",
        )

    def test_cors_allows_canonical_frontend_and_rejects_unknown_origin(self):
        client = app.test_client()

        with patch.dict(
            os.environ,
            {"CORS_ORIGINS": "https://lernedeutsch.github.io"},
        ):
            allowed = client.get(
                "/health",
                headers={"Origin": "https://lernedeutsch.github.io"},
            )
            blocked = client.get(
                "/health",
                headers={"Origin": "https://example.invalid"},
            )

        self.assertEqual(
            allowed.headers.get("Access-Control-Allow-Origin"),
            "https://lernedeutsch.github.io",
        )
        self.assertIsNone(
            blocked.headers.get("Access-Control-Allow-Origin")
        )

    def test_destructive_reset_is_disabled_by_default(self):
        client = app.test_client()

        with patch.dict(
            os.environ,
            {
                "NELE_ENABLE_DESTRUCTIVE_RESET": "false",
                "NELE_RESET_SECRET": "",
            },
        ), patch(
            "server.app.reset_conversation_state"
        ) as reset_mock:
            response = client.post(
                "/reset",
                json={"session_id": "test-user"},
            )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.get_json()["error"],
            "destructive_reset_disabled",
        )
        reset_mock.assert_not_called()

    def test_destructive_reset_requires_secret_even_when_enabled(self):
        client = app.test_client()

        with patch.dict(
            os.environ,
            {
                "NELE_ENABLE_DESTRUCTIVE_RESET": "true",
                "NELE_RESET_SECRET": "secret-value",
            },
        ), patch(
            "server.app.reset_conversation_state"
        ) as reset_mock:
            response = client.post(
                "/api/reset/test-user",
                headers={"X-Nele-Reset-Token": "wrong-value"},
            )

        self.assertEqual(response.status_code, 403)
        reset_mock.assert_not_called()

    def test_public_endpoints_reject_missing_or_reserved_default_id(self):
        client = app.test_client()

        missing = client.post(
            "/welcome",
            json={},
        )
        reserved = client.post(
            "/chat",
            json={
                "session_id": "default",
                "message": "Hallo",
            },
        )
        activity_missing = client.post(
            "/api/activity/start",
            json={"type": "pronunciation"},
        )

        self.assertEqual(missing.status_code, 400)
        self.assertEqual(
            missing.get_json()["error"],
            "session_id_required",
        )
        self.assertEqual(reserved.status_code, 400)
        self.assertEqual(
            reserved.get_json()["error"],
            "session_id_required",
        )
        self.assertEqual(activity_missing.status_code, 400)

    def test_compatibility_session_start_uses_canonical_service(self):
        client = app.test_client()

        with patch(
            "server.app.acquire_session_lock",
            return_value=None,
        ), patch(
            "server.app.refresh_conversation_state"
        ), patch(
            "brain.nele3_upgrade.api.start_conversation_session",
            return_value="Hallo Moni!",
        ) as start_mock:
            response = client.post(
                "/api/session/start",
                json={
                    "session_id": "stable-moni-id",
                    "new_conversation": True,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["reply"],
            "Hallo Moni!",
        )
        start_mock.assert_called_once_with(
            "stable-moni-id",
            new_conversation=True,
        )

    def test_persistent_memory_returns_true_after_successful_init(self):
        original = memory_module.persistent_memory_initialized
        memory_module.persistent_memory_initialized = True

        try:
            self.assertTrue(
                memory_module.ensure_persistent_memory()
            )
        finally:
            memory_module.persistent_memory_initialized = original

    def test_gunicorn_defaults_to_one_worker(self):
        import gunicorn_conf

        self.assertEqual(gunicorn_conf.workers, 1)
        self.assertEqual(gunicorn_conf.worker_class, "gthread")
        self.assertGreaterEqual(gunicorn_conf.threads, 2)

    def test_persistent_memory_is_not_marked_initialized_after_failed_init(self):
        original = memory_module.persistent_memory_initialized
        memory_module.persistent_memory_initialized = False

        try:
            with patch(
                "brain.logic.memory.initialize_persistent_memory",
                return_value=False,
            ):
                result = memory_module.ensure_persistent_memory()

            self.assertFalse(result)
            self.assertFalse(
                memory_module.persistent_memory_initialized
            )
        finally:
            memory_module.persistent_memory_initialized = original


if __name__ == "__main__":
    unittest.main()
