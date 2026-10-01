from unittest.mock import patch

from server.app import create_nele_reply


def test_course_reply_uses_selected_lesson_from_student_progress():
    state = {
        "student_progress": {
            "current_level": "A1",
            "current_lesson": 2,
        }
    }

    with (
        patch("server.app.get_conversation_state", return_value=state),
        patch("server.app.ensure_upgrade_state"),
        patch("server.app.handle_personal_sentence", return_value=None),
        patch("server.app.handle_upgrade_message", return_value=(False, None, None)),
        patch("server.app.generate_conversation_reply", return_value="lesson-2-answer") as generate,
        patch("server.app.record_event"),
        patch("server.app.save_conversation_state"),
    ):
        answer, meta = create_nele_reply(
            "kommen konjugation",
            session_id="course-selected-lesson-test",
            input_mode="keyboard",
            conversation_mode="course",
        )

    assert answer == "lesson-2-answer"
    generate.assert_called_once_with(
        "kommen konjugation",
        level="A1",
        lesson=2,
        session_id="course-selected-lesson-test",
    )
    assert meta["level"] == "A1"
    assert meta["lesson"] == 2


def test_course_reply_keeps_a1_lesson1_as_safe_default():
    state = {"student_progress": {}}

    with (
        patch("server.app.get_conversation_state", return_value=state),
        patch("server.app.ensure_upgrade_state"),
        patch("server.app.handle_personal_sentence", return_value=None),
        patch("server.app.handle_upgrade_message", return_value=(False, None, None)),
        patch("server.app.generate_conversation_reply", return_value="default-answer") as generate,
        patch("server.app.record_event"),
        patch("server.app.save_conversation_state"),
    ):
        answer, _ = create_nele_reply(
            "hallo",
            session_id="course-default-lesson-test",
            conversation_mode="course",
        )

    assert answer == "default-answer"
    generate.assert_called_once_with(
        "hallo",
        level="A1",
        lesson=1,
        session_id="course-default-lesson-test",
    )


def test_course_exact_meine_saetze_text_stays_with_selected_lesson():
    state = {
        "student_progress": {"current_level": "A1", "current_lesson": 2},
    }

    with (
        patch("server.app.get_conversation_state", return_value=state),
        patch("server.app.ensure_upgrade_state"),
        patch("server.app.handle_personal_sentence") as global_sentence,
        patch("server.app.handle_upgrade_message", return_value=(False, None, None)),
        patch("server.app.generate_conversation_reply", return_value="lesson-keeps-turn") as generate,
        patch("server.app.record_event"),
        patch("server.app.save_conversation_state"),
    ):
        answer, _ = create_nele_reply(
            "Arbeitest du am Sonntag?",
            session_id="course-global-sentence-collision-test",
            conversation_mode="course",
        )

    assert answer == "lesson-keeps-turn"
    global_sentence.assert_not_called()
    generate.assert_called_once_with(
        "Arbeitest du am Sonntag?",
        level="A1",
        lesson=2,
        session_id="course-global-sentence-collision-test",
    )


def test_course_clears_stale_personal_sentence_practice_before_routing():
    state = {
        "student_progress": {"current_level": "A1", "current_lesson": 2},
        "personal_sentence_practice": {"id": "arbeitest_du_am_sonntag", "attempts": 0},
    }

    with (
        patch("server.app.get_conversation_state", return_value=state),
        patch("server.app.ensure_upgrade_state"),
        patch("server.app.handle_personal_sentence") as global_sentence,
        patch("server.app.handle_upgrade_message", return_value=(False, None, None)),
        patch("server.app.generate_conversation_reply", return_value="lesson-resumed") as generate,
        patch("server.app.record_event"),
        patch("server.app.save_conversation_state"),
    ):
        answer, _ = create_nele_reply(
            "ja",
            session_id="course-stale-personal-practice-test",
            conversation_mode="course",
        )

    assert answer == "lesson-resumed"
    assert "personal_sentence_practice" not in state
    global_sentence.assert_not_called()
    generate.assert_called_once()


def test_course_selection_accepts_only_a1_1_and_a1_2():
    from server.app import app

    app.config["TESTING"] = True
    cases = [
        ({"level": "A1", "lesson": 1}, 200),
        ({"level": "A1", "lesson": 2}, 200),
        ({"level": "A1", "lesson": 3}, 400),
        ({"level": "A1", "lesson": 14}, 400),
        ({"level": "A2", "lesson": 1}, 400),
    ]
    state = {"student_progress": {}}
    with (
        patch("server.app.get_conversation_state", return_value=state),
        patch("server.app.ensure_upgrade_state"),
        patch("server.app.save_conversation_state"),
    ):
        with app.test_client() as client:
            for payload, expected_status in cases:
                response = client.post("/api/students", json=payload)
                assert response.status_code == expected_status, payload
                if expected_status == 400:
                    assert response.get_json()["error"] == "course_scope_limited_to_a1_1_a1_2"
