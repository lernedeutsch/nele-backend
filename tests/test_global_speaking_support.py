from brain.logic.speaking_support import (
    assess_course_answer,
    build_course_support_reply,
    handle_pending_course_model,
)


def _step(target, accepted=None, natural=None):
    return {
        "prompt": "Was sagst du?",
        "correct_answer": target,
        "accepted": accepted or [target],
        "natural_short_answers": natural or [],
    }


def test_unseen_vocabulary_short_answer_uses_lesson_target_not_hardcoded_map():
    state = {"lesson_teaching_level": "A1", "lesson_teaching_lesson": 20}
    step = _step("Ich spiele heute Tennis.", ["Ich spiele heute Tennis.", "Tennis"])
    result = assess_course_answer("Tennis", step, state, answer_matches=False)
    assert result["kind"] == "short_answer_expansion"
    assert result["intercept"] is True
    reply = build_course_support_reply(result, step, state)
    assert "Ich spiele heute Tennis." in reply
    assert state["course_pending_speaking_model"] == "Ich spiele heute Tennis."


def test_future_lesson_new_place_uses_same_engine():
    state = {"lesson_teaching_level": "A1", "lesson_teaching_lesson": 27}
    step = _step("Ich fahre nach Köln.", ["Ich fahre nach Köln.", "Köln"])
    result = assess_course_answer("Köln", step, state, answer_matches=False)
    assert result["intercept"] is True
    assert result["target"] == "Ich fahre nach Köln."


def test_natural_short_answer_is_not_forced_into_full_sentence():
    state = {}
    step = _step("Ja, ich habe Zeit.", ["ja"], ["ja"])
    result = assess_course_answer("ja", step, state, answer_matches=True)
    assert result["intercept"] is False
    assert result["kind"] == "natural_short_success"
    assert state.get("course_pending_speaking_model") is None


def test_help_increases_gradually_and_does_not_advance_target():
    state = {"course_pending_speaking_model": "Ich lerne heute Deutsch."}
    first = handle_pending_course_model("weiß nicht", state)
    assert "Versuch" in first
    second = handle_pending_course_model("hm", state)
    assert "Fang so an" in second
    assert "Ich lerne" in second
    assert state["course_pending_speaking_model"] == "Ich lerne heute Deutsch."


def test_successful_model_attempt_releases_same_turn_to_lesson_engine():
    state = {
        "course_pending_speaking_model": "Ich kaufe morgen Brot.",
        "course_speaking_support_level": 3,
    }
    result = handle_pending_course_model("Ich kaufe morgen Brot.", state)
    assert result is None
    assert state["course_pending_speaking_model"] is None
    assert state["course_speaking_support_level"] == 2


def test_unknown_short_word_is_not_invented_into_a_sentence():
    state = {}
    step = _step("Ich lese am Abend.")
    result = assess_course_answer("Gitarre", step, state, answer_matches=False)
    assert result["intercept"] is False
    assert result["semantic_short"] is False
