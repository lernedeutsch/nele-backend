from brain.logic.course_teacher_engine import (
    choose_course_teacher_action,
    render_course_teacher_action,
)


def test_wrong_answer_uses_shared_course_teacher():
    state = {"conversation_mode": "course"}
    action = choose_course_teacher_action(
        state,
        answer_correct=False,
        correct_answer="Ich komme aus Polen.",
    )
    assert action["action"] == "correct_and_retry"
    assert "Ich komme aus Polen." in render_course_teacher_action(action)
    assert state["course_teacher_action"]["reason"] == "answer_not_yet"


def test_partial_answer_gets_shared_scaffold():
    state = {"conversation_mode": "course"}
    action = choose_course_teacher_action(
        state,
        answer_correct=False,
        partial={"matched": 2, "total": 3},
        correct_answer="eins, zwei, drei",
    )
    assert action["action"] == "scaffold_partial"
    reply = render_course_teacher_action(action)
    assert "2 von 3" in reply
    assert "eins, zwei, drei" in reply


def test_not_mastered_skill_is_reinforced():
    state = {"conversation_mode": "course"}
    action = choose_course_teacher_action(
        state,
        answer_correct=True,
        mastery_status="practicing",
    )
    assert action["action"] == "reinforce"
    reply = render_course_teacher_action(action, prompt="Versuch es noch einmal.")
    assert "festigen" in reply
    assert "Versuch es noch einmal." in reply
