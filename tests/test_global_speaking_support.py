from brain.logic.speaking_support import (
    assess_course_answer,
    build_course_support_reply,
    handle_pending_course_model,
    legacy_course_support,
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
    assert first == "Fast. Noch einmal."
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


def test_legacy_lesson_and_future_lesson_share_pending_model_contract():
    legacy_state = {}
    legacy_reply = legacy_course_support(
        "heiße",
        "Ich heiße Lena.",
        legacy_state,
        context="name",
    )
    assert legacy_reply is not None
    assert legacy_state["course_pending_speaking_model"] == "Ich heiße Lena."

    future_state = {"lesson_teaching_level": "A1", "lesson_teaching_lesson": 30}
    future_step = _step("Ich schwimme am Samstag.", ["Ich schwimme am Samstag.", "Samstag"])
    result = assess_course_answer("Samstag", future_step, future_state, answer_matches=False)
    build_course_support_reply(result, future_step, future_state)
    assert future_state["course_pending_speaking_model"] == "Ich schwimme am Samstag."


def test_shared_pending_model_reduces_help_after_success():
    state = {
        "course_pending_speaking_model": "Wie heißt du?",
        "course_speaking_support_level": 2,
    }
    assert handle_pending_course_model("Wie heißt du?", state) is None
    assert state.get("course_pending_speaking_model") is None
    assert state["course_speaking_support_level"] == 1


def test_review_style_wrong_attempt_keeps_shared_target_until_spoken():
    state = {}
    reply = legacy_course_support(
        "Wie heißen du?",
        "Wie heißt du?",
        state,
        context="review",
    )
    assert reply is not None
    assert state.get("course_pending_speaking_model") == "Wie heißt du?"
    # Hesitation gets help and does not clear the target.
    retry = handle_pending_course_model("weiß nicht", state)
    assert retry is not None
    assert state.get("course_pending_speaking_model") == "Wie heißt du?"
    # Only producing the target releases the learner back to review flow.
    assert handle_pending_course_model("Wie heißt du?", state) is None
    assert state.get("course_pending_speaking_model") is None


def test_15_turn_support_cycle_reduces_after_successes_and_reuses_same_policy():
    state = {}
    targets = [
        "Ich lerne heute Deutsch.",
        "Ich spiele morgen Fußball.",
        "Ich fahre am Montag nach Bonn.",
        "Ich lese am Abend ein Buch.",
        "Ich kaufe zwei Äpfel.",
    ]
    fragments = ["Deutsch", "Fußball", "Bonn", "Buch", "Äpfel"]

    completed = 0
    for target, fragment in zip(targets, fragments):
        step = _step(target, [target, fragment])
        assessment = assess_course_answer(fragment, step, state, answer_matches=False)
        assert assessment["intercept"] is True
        reply = build_course_support_reply(assessment, step, state)
        assert target in reply
        # one hesitant turn
        assert handle_pending_course_model("hm", state) is not None
        # then learner produces the sentence
        assert handle_pending_course_model(target, state) is None
        completed += 1

    assert completed == 5
    assert state.get("course_pending_speaking_model") is None
    # Successful production must counteract escalation; help must not grow
    # without bound across a long session.
    assert state.get("course_speaking_support_level", 0) <= 1


def test_repeated_independent_success_does_not_create_unwanted_model():
    state = {"course_speaking_support_level": 3}
    for target in (
        "Ich trinke morgens Tee.",
        "Ich wohne in Mainz.",
        "Ich gehe heute einkaufen.",
        "Ich habe einen Bruder.",
        "Ich möchte Wasser.",
    ):
        step = _step(target)
        result = assess_course_answer(target, step, state, answer_matches=True)
        assert result["kind"] == "independent_success"
        assert result["intercept"] is False
        assert state.get("course_pending_speaking_model") is None

    assert state["course_speaking_support_level"] == 0

def test_pending_spelling_accepts_equivalent_letter_separators_without_weakening_sentences():
    for learner in ("m o n i k a", "M-O-N-I-K-A", "M – O – N – I – K – A"):
        state = {
            "course_pending_speaking_model": "M – O – N – I – K – A",
            "course_speaking_support_level": 3,
        }
        assert handle_pending_course_model(learner, state) is None
        assert state["course_pending_speaking_model"] is None
        assert state["course_speaking_support_level"] == 2

    state = {
        "course_pending_speaking_model": "Ich heiße Monika.",
        "course_speaking_support_level": 2,
    }
    assert handle_pending_course_model("ich-heiße-monika", state) is not None
    assert state["course_pending_speaking_model"] == "Ich heiße Monika."

def test_accepted_semantic_fragment_is_real_course_success():
    state = {}
    step = _step(
        "Ich komme aus Polen.",
        ["Ich komme aus Polen.", "Polen"],
    )
    result = assess_course_answer("Polen", step, state, answer_matches=True)
    assert result["answer_matches"] is True
    assert result["intercept"] is False
    assert result["kind"] == "independent_success"
    assert state.get("course_pending_speaking_model") is None


def test_natural_short_answer_is_not_forced_into_full_sentence():
    state = {"course_speaking_support_level": 2}
    step = _step("Ja, ich arbeite heute.", ["Ja", "Ja, ich arbeite heute."])
    result = assess_course_answer("ja", step, state, answer_matches=True)
    assert result["intercept"] is False
    assert result["kind"] == "natural_short_success"



def test_course_support_replies_stay_short_and_everyday():
    state = {}
    step = _step(
        "Ich trinke morgens Kaffee.",
        ["Ich trinke morgens Kaffee.", "Kaffee"],
    )
    assessment = assess_course_answer(
        "Kaffee",
        step,
        state,
        answer_matches=True,
    )
    reply = build_course_support_reply(assessment, step, state)
    assert reply == "Genau. Sag: „Ich trinke morgens Kaffee.“"
    assert len(reply.split()) <= 7

    retry_state = {
        "course_pending_speaking_model": "Ich trinke morgens Kaffee.",
        "course_speaking_support_level": 0,
    }
    assert handle_pending_course_model("hm", retry_state) == "Fast. Noch einmal."


def test_render_target_uses_name_from_user_fact_memory():
    state = {
        "user_facts": {"name": "Moni"},
        "course_speaking_support_level": 0,
    }
    step = {
        "correct_answer": "Ich heiße {name}.",
        "accepted": ["Moni"],
    }

    assessment = assess_course_answer(
        "Moni",
        step,
        state,
        answer_matches=True,
    )

    assert assessment["target"] == "Ich heiße Moni."
    assert assessment["intercept"] is True
    assert assessment["kind"] == "short_answer_expansion"


def test_exhausted_model_is_consumable_once():
    from brain.logic.speaking_support import consume_course_model_exhaustion
    state = {
        "course_pending_speaking_model": "Guten Morgen",
        "course_speaking_support_level": 4,
    }
    reply = handle_pending_course_model("falsch", state)
    assert "später noch einmal" in reply
    evidence = consume_course_model_exhaustion(state)
    assert evidence == {"target": "Guten Morgen", "assistance_exhausted": True}
    assert consume_course_model_exhaustion(state) is None


def test_generic_course_consumes_exhaustion_into_review_instead_of_loop():
    from brain.logic.generic_lesson_engine import start_generic_lesson_teaching, handle_generic_lesson_teaching
    state = {
        "conversation_mode": "course",
        "student_progress": {"current_level": "A1", "current_lesson": 2},
    }
    opening = start_generic_lesson_teaching("A1", 2, "Das Verb kommen", state)
    assert "Ich" in opening
    state["course_pending_speaking_model"] = "Ich komme aus Spanien."
    state["course_speaking_support_level"] = 4
    exhausted_reply = handle_generic_lesson_teaching("falsch", state)
    assert "später noch einmal" in exhausted_reply
    follow_up = handle_generic_lesson_teaching("noch falsch", state)
    assert "festigen" in follow_up
    skill = state["learning_progress_v1"]["skills"]["course:a1:2:das_verb_kommen"]
    assert skill["status"] == "needs_review"
    assert state["lesson_teaching_step"] == 1
    assert state.get("course_model_practice_exhausted") is None


def test_teacher_engine_wrong_answers_reach_shared_bounded_exhaustion():
    from brain.logic.course_teacher_engine import (
        choose_course_teacher_action,
        render_course_teacher_action,
    )
    state = {"conversation_mode": "course"}

    replies = []
    for _ in range(3):
        action = choose_course_teacher_action(
            state,
            answer_correct=False,
            correct_answer="Wie alt sind Sie?",
            retry="Formell mit „Sie“: „Wie alt sind Sie?“",
        )
        replies.append(render_course_teacher_action(action))

    assert state["course_pending_speaking_model"] == "Wie alt sind Sie?"
    assert state["course_speaking_support_level"] == 3

    fourth = handle_pending_course_model("xyz", state)
    assert "langsam" in fourth.lower()
    fifth = handle_pending_course_model("xyz", state)
    assert "später noch einmal" in fifth
    assert state.get("course_pending_speaking_model") is None
    assert state["course_model_practice_exhausted"] == "Wie alt sind Sie?"


def test_generic_course_exhaustion_temporarily_varies_task_without_weakening_mastery():
    from brain.logic.generic_lesson_engine import (
        start_generic_lesson_teaching,
        handle_generic_lesson_teaching,
    )

    state = {
        "conversation_mode": "course",
        "student_progress": {"current_level": "A1", "current_lesson": 3},
    }
    opening = start_generic_lesson_teaching("Zahlen 11–100", state)
    assert "11 bis 15" in opening

    state["course_pending_speaking_model"] = (
        "elf, zwölf, dreizehn, vierzehn, fünfzehn"
    )
    state["course_speaking_support_level"] = 4

    exhausted_reply = handle_generic_lesson_teaching("falsch", state)
    assert "später noch einmal" in exhausted_reply

    follow_up = handle_generic_lesson_teaching("noch falsch", state)

    assert "wechseln kurz die Aufgabe" in follow_up
    assert "16 bis 20" in follow_up
    assert state["lesson_teaching_step"] == 2

    skill = state["learning_progress_v1"]["skills"]["course:a1:3:zahlen_11–100"]
    assert skill["status"] == "needs_review"
    assert "step:1" not in set(skill.get("independent_evidence") or [])
