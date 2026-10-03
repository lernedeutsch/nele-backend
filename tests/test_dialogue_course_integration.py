import unittest
from unittest.mock import patch

from brain.logic.dialogue_engine import handle_dialogue
from brain.logic.conversation import _release_wellbeing_for_course_dialogue_intent
from brain.logic.new_learning_resume import handle_new_learning_resume


class DialogueCourseIntegrationTests(unittest.TestCase):
    @patch("brain.logic.new_learning_resume.remember_learning_topic")
    @patch("brain.logic.new_learning_resume.set_current_section")
    @patch("brain.logic.new_learning_resume.set_current_lesson")
    @patch("brain.logic.new_learning_resume.set_current_level")
    def test_course_offer_starts_real_a12_dialogue_and_completes_it(
        self,
        _set_level,
        _set_lesson,
        _set_section,
        _remember_topic,
    ):
        state = {
            "conversation_mode": "course",
            "student_progress": {"current_level": "A1", "current_lesson": 2},
            "pending_new_learning": {
                "type": "new_section",
                "level": "A1",
                "lesson": 2,
                "section": "Woher kommen Sie?",
                "topic": "Woher kommen Sie?",
            },
            "last_question": "continue_new_learning",
        }

        opening = handle_new_learning_resume("ja", state)
        self.assertIn("Woher kommst du", opening)
        self.assertTrue(state["dialogue_active"])
        self.assertEqual(state["dialogue_id"], "woher-kommst-du")
        self.assertIsNone(state["pending_new_learning"])

        # Natural short answer is semantically accepted.
        reply = handle_dialogue("Polen", state)
        self.assertIn("Kommst du aus Polen", reply)
        self.assertIn("give_origin", state["dialogue_completed_intents"])

        reply = handle_dialogue("Ja", state)
        self.assertIn("Anna kommt aus Österreich", reply)

        reply = handle_dialogue("Anna kommt aus Österreich", state)
        self.assertIn("Herkunftsdialog geschafft", reply)
        self.assertIn("Jetzt sprechen wir über Länder", reply)
        self.assertFalse(state["dialogue_active"])
        self.assertTrue(state["lesson_teaching_active"])
        self.assertEqual(state["lesson_teaching_section"], "Woher kommen Sie?")


    def test_practice_dialogue_continues_same_section_before_next_section(self):
        from brain.logic.dialogue_engine import start_dialogue
        from brain.memory.student_progress import set_current_level, set_current_lesson

        state = {"conversation_mode": "course"}
        set_current_level(state, "A1")
        set_current_lesson(state, 2)
        start_dialogue("A1", 2, "woher-kommst-du", state)
        handle_dialogue("Polen", state)
        handle_dialogue("Ja", state)
        reply = handle_dialogue("Anna kommt aus Österreich", state)

        self.assertIn("Herkunftsdialog geschafft", reply)
        self.assertIn("Jetzt sprechen wir über Länder", reply)
        self.assertTrue(state["lesson_teaching_active"])
        self.assertEqual(state["lesson_teaching_section"], "Woher kommen Sie?")
        self.assertFalse(state.get("pending_new_learning"))
        skill = state["learning_progress_v1"]["skills"]["course:a1:2:woher_kommen_sie"]
        self.assertNotEqual(skill["status"], "mastered")


    def test_explicit_course_dialogue_intent_releases_returning_wellbeing_prompt(self):
        state = {
            "conversation_mode": "course",
            "last_question": "wellbeing",
        }

        released = _release_wellbeing_for_course_dialogue_intent(
            "Woher kommst du?",
            state,
            "A1",
        )

        self.assertTrue(released)
        self.assertIsNone(state["last_question"])

    def test_unrelated_answer_still_belongs_to_returning_wellbeing_prompt(self):
        state = {
            "conversation_mode": "course",
            "last_question": "wellbeing",
        }

        released = _release_wellbeing_for_course_dialogue_intent(
            "Müde",
            state,
            "A1",
        )

        self.assertFalse(released)
        self.assertEqual(state["last_question"], "wellbeing")

    def test_unrelated_answer_does_not_advance_origin_dialogue(self):
        from brain.logic.dialogue_engine import start_dialogue
        state = {}
        start_dialogue("A1", 2, "woher-kommst-du", state)
        reply = handle_dialogue("Ich kaufe Brot", state)
        self.assertIn("Ich komme aus Polen", reply)
        self.assertEqual(state["dialogue_turn"], 1)
        self.assertNotIn("give_origin", state["dialogue_completed_intents"])

    def test_origin_dialogue_has_semantic_contract(self):
        from brain.logic.dialogue_engine import get_dialogue
        dialogue = get_dialogue("A1", 2, "woher-kommst-du")
        self.assertEqual(dialogue["topic"], "Herkunft")
        self.assertEqual(dialogue["register"], "informal")
        self.assertEqual(dialogue["max_variations"], 2)
        self.assertIn("combine_unrelated_topics", dialogue["forbidden_variations"])


if __name__ == "__main__":
    unittest.main()



    def test_conversation_routes_yes_to_pending_course_section_after_dialogue(self):
        from brain.logic.new_learning_resume import set_new_learning_offer
        from brain.logic.conversation import handle_message

        state = {
            "conversation_mode": "course",
            "pending_new_learning": {
                "type": "new_section",
                "level": "A1",
                "lesson": 2,
                "section": "Das Verb kommen",
                "topic": "Das Verb kommen",
            },
            "last_question": "continue_new_learning",
        }
        set_new_learning_offer(state, state["pending_new_learning"])
        with patch(
            "brain.logic.conversation.get_conversation_state",
            return_value=state,
        ), patch(
            "brain.logic.new_learning_resume.start_new_learning",
            return_value="NEXT_SECTION_STARTED",
        ):
            reply = handle_message("ja", "A1", 2, session_id="test-course-handoff")

        self.assertIn("NEXT_SECTION_STARTED", str(reply))



def test_real_course_practice_dialogue_does_not_skip_remaining_section_work():
    from brain.logic.dialogue_engine import start_dialogue

    state = {
        "conversation_mode": "course",
        "student_progress": {"current_level": "A1", "current_lesson": 2},
    }
    start_dialogue("A1", 2, "woher-kommst-du", state)
    handle_dialogue("Polen", state)
    handle_dialogue("Ja", state)
    reply = handle_dialogue("Anna kommt aus Österreich", state)

    assert "Herkunftsdialog geschafft" in reply
    assert "Jetzt sprechen wir über Länder" in reply
    assert "Das Verb kommen" not in reply
    assert state["lesson_teaching_active"] is True
    assert state["lesson_teaching_section"] == "Woher kommen Sie?"
    skill = state["learning_progress_v1"]["skills"]["course:a1:2:woher_kommen_sie"]
    assert skill["status"] != "mastered"


def test_partial_course_dialogue_answer_is_preserved_in_learning_progress():
    from brain.logic.dialogue_engine import start_dialogue, handle_dialogue

    state = {"conversation_mode": "course"}
    opening = start_dialogue("A1", 15, "a1-l15-verkehrsmittel", state)
    assert "Berlin" in opening

    reply = handle_dialogue("Ich fahre mit", state)

    skill = "course:a1:15:reisen"
    progress = state["learning_progress_v1"]["skills"][skill]
    assert progress["partials"] == 1
    assert progress["not_yet"] == 0
    assert progress["last_result"] == "PARTIAL"
    assert state["dialogue_turn"] == 1
    assert "3 von 5" in reply


def test_wrong_course_dialogue_answer_remains_not_yet_after_partial_support_fix():
    from brain.logic.dialogue_engine import start_dialogue, handle_dialogue

    state = {"conversation_mode": "course"}
    start_dialogue("A1", 15, "a1-l15-verkehrsmittel", state)
    handle_dialogue("Ich esse Pizza", state)

    skill = "course:a1:15:reisen"
    progress = state["learning_progress_v1"]["skills"][skill]
    assert progress["partials"] == 0
    assert progress["not_yet"] == 1
    assert progress["last_result"] == "NOT_YET"
    assert state["dialogue_turn"] == 1


def test_wrong_course_dialogue_answer_is_available_to_error_practice_and_dialogue_stays_active():
    from brain.logic.dialogue_engine import start_dialogue, handle_dialogue
    from brain.logic.error_practice import start_error_practice
    from brain.memory.error_memory import get_error_summary

    state = {"conversation_mode": "course"}
    start_dialogue("A1", 2, "woher-kommst-du", state)

    reply = handle_dialogue("Ich esse Pizza", state)

    summary = get_error_summary(state, "course_dialogue")
    assert summary["last_wrong"] == "Ich esse Pizza"
    assert summary["last_correct"]
    assert state["dialogue_active"] is True
    assert start_error_practice(state, "course_dialogue") is not None
    assert state["dialogue_active"] is True
    assert "Ich esse Pizza" not in reply or reply


def test_dialogue_turn_successes_alone_do_not_count_as_mastery_proof():
    from brain.logic.dialogue_engine import _record_course_dialogue_outcome
    dialogue = {"level": "A1", "lesson": 15, "section": "Reisen"}
    state = {"conversation_mode": "course"}

    for _ in range(4):
        progress = _record_course_dialogue_outcome(dialogue, state, True)

    assert progress["successes"] == 4
    assert progress["independent_confirmations"] == 0
    assert progress["status"] != "mastered"


def test_final_dialogue_turn_alone_cannot_confirm_section_mastery():
    from brain.logic.dialogue_engine import _record_course_dialogue_outcome
    dialogue = {
        "level": "A1",
        "lesson": 15,
        "section": "Reisen",
        "turns": [
            {"role": "student"},
            {"role": "nele"},
            {"role": "student"},
            {"role": "nele"},
            {"role": "student"},
        ],
    }
    state = {"conversation_mode": "course", "dialogue_turn": 4}

    progress = _record_course_dialogue_outcome(
        dialogue, state, True, independent_confirmation=True
    )

    assert progress["status"] != "mastered"
    assert progress["required_evidence"] == [
        "dialogue_turn:0", "dialogue_turn:2", "dialogue_turn:4"
    ]
    assert progress["independent_evidence"] == ["dialogue_turn:4"]


def test_clean_dialogue_coverage_can_confirm_section_mastery():
    from brain.logic.dialogue_engine import _record_course_dialogue_outcome
    dialogue = {
        "level": "A1",
        "lesson": 15,
        "section": "Reisen",
        "turns": [
            {"role": "student"},
            {"role": "nele"},
            {"role": "student"},
            {"role": "nele"},
            {"role": "student"},
        ],
    }
    state = {"conversation_mode": "course"}

    for turn in (0, 2):
        state["dialogue_turn"] = turn
        _record_course_dialogue_outcome(dialogue, state, True)

    state["dialogue_turn"] = 4
    progress = _record_course_dialogue_outcome(
        dialogue, state, True, independent_confirmation=True
    )

    assert progress["successes"] == 3
    assert progress["independent_confirmations"] == 3
    assert progress["status"] == "mastered"
    assert set(progress["independent_evidence"]) == set(progress["required_evidence"])


def test_course_dialogue_exhausted_support_becomes_review_instead_of_model_loop():
    from brain.logic.dialogue_engine import start_dialogue, handle_dialogue

    state = {"conversation_mode": "course"}
    start_dialogue("A1", 2, "woher-kommst-du", state)

    replies = [handle_dialogue("falsch", state) for _ in range(6)]

    assert any("Das ist okay" in reply for reply in replies)
    assert "Wir machen erst einmal weiter" in replies[-1]
    assert "Kommst du aus Polen" in replies[-1]
    assert state["dialogue_turn"] > 1
    assert "course_pending_speaking_model" not in state or not state["course_pending_speaking_model"]
    assert "course_model_practice_exhausted" not in state
    progress = state["learning_progress_v1"]["skills"]["course:a1:2:woher_kommen_sie"]
    assert progress["last_result"] == "NOT_YET"
    assert progress["status"] != "mastered"


def test_explicit_lesson_review_request_preempts_active_course_exercise():
    from brain.logic.conversation import handle_message

    state = {
        "conversation_mode": "course",
        "onboarding_completed": True,
        "selected_level": "A1",
        "selected_lesson": 1,
        "lesson_teaching_active": True,
        "lesson_teaching_level": "A1",
        "lesson_teaching_lesson": 1,
        "lesson_teaching_section": "Wir begrüßen uns",
        "lesson_teaching_step": 1,
    }
    with patch(
        "brain.logic.conversation.get_conversation_state",
        return_value=state,
    ):
        reply = handle_message(
            "Ich möchte Lektion 1 wiederholen.",
            "A1",
            1,
            session_id="test-explicit-review-intent",
        )

    assert "Wiederholung von A1, Lektion 1" in str(reply)
    assert state["lesson_review_training_active"] is True
    assert state["lesson_review_training_step"] == 1


def test_origin_dialogue_uses_remembered_origin_and_accepts_natural_variant():
    from brain.logic.dialogue_engine import start_dialogue, handle_dialogue
    state = {"conversation_mode": "course", "user_facts": {"origin": "Italien", "name": "Moni"}}
    opening = start_dialogue("A1", 2, "woher-kommst-du", state)
    assert "Woher kommst du" in opening
    assert state["dialogue_slots"]["country"] == "Italien"
    reply = handle_dialogue("Ich bin aus Italien.", state)
    assert "Kommst du aus Italien" in reply
    assert state["dialogue_turn"] > 1
    assert "give_origin" in state["dialogue_completed_intents"]

def test_origin_dialogue_retry_renders_remembered_origin():
    from brain.logic.dialogue_engine import start_dialogue, handle_dialogue

    state = {
        "conversation_mode": "course",
        "user_facts": {"origin": "Italien", "name": "Moni"},
    }
    start_dialogue("A1", 2, "woher-kommst-du", state)

    reply = handle_dialogue("xyz", state)

    assert "Ich komme aus Italien" in reply
    assert "Ich komme aus Polen" not in reply


def test_origin_dialogue_keeps_default_without_remembered_origin():
    from brain.logic.dialogue_engine import start_dialogue
    state = {"conversation_mode": "course"}
    start_dialogue("A1", 2, "woher-kommst-du", state)
    assert state["dialogue_slots"]["country"] == "Polen"


def test_dialogue_cannot_prepare_next_section_when_completion_gate_rejects_current():
    from brain.logic.dialogue_engine import _complete_course_dialogue

    dialogue = {
        "id": "synthetic-section-dialogue",
        "level": "A1",
        "lesson": 2,
        "section": "Woher kommen Sie?",
    }
    state = {
        "conversation_mode": "course",
        "pending_new_learning": {
            "type": "new_section",
            "level": "A1",
            "lesson": 2,
            "section": "Das Verb kommen",
        },
        "last_question": "continue_new_learning",
    }

    with patch(
        "brain.logic.dialogue_engine.mark_section_completed",
        return_value=False,
    ), patch(
        "brain.logic.dialogue_engine.build_learner_model",
    ) as learner_model:
        next_section = _complete_course_dialogue(dialogue, state)

    assert next_section is None
    assert state["pending_new_learning"] is None
    assert state["last_question"] is None
    assert state["course_teaching_decision"]["decision"] == "continue_current"
    assert state["course_teaching_decision"]["reason"] == "section_not_mastered"
    learner_model.assert_not_called()


def test_fresh_dialogue_does_not_inherit_stale_assistance_from_previous_task():
    from brain.logic.dialogue_engine import start_dialogue, handle_dialogue

    state = {
        "conversation_mode": "course",
        "course_mastery_assistance_used": True,
        "course_pending_speaking_model": "Stale model.",
        "course_model_practice_exhausted": "Stale model.",
    }
    opening = start_dialogue("A1", 15, "a1-l15-verkehrsmittel", state)

    assert "Berlin" in opening
    assert state["course_mastery_assistance_used"] is False
    assert "course_pending_speaking_model" not in state
    assert "course_model_practice_exhausted" not in state

    handle_dialogue("Ich fahre mit dem Zug.", state)
    handle_dialogue("Ja, sehr gern.", state)
    handle_dialogue("Ich fahre lieber mit dem Auto.", state)
    reply = handle_dialogue("Ja, manchmal fliege ich mit dem Flugzeug.", state)

    progress = state["learning_progress_v1"]["skills"]["course:a1:15:reisen"]
    assert progress["independent_confirmations"] == 1
    assert progress["status"] == "mastered"
    assert "festigen" not in reply.lower()


def test_course_dialogue_exhausted_support_revisits_exact_failed_turn_after_transfer_success():
    from brain.logic.dialogue_engine import start_dialogue, handle_dialogue

    state = {"conversation_mode": "course"}
    opening = start_dialogue("A1", 2, "woher-kommst-du", state)
    assert "Woher kommst du" in opening
    failed_turn = state["dialogue_turn"]

    replies = [handle_dialogue("ich weiß nicht", state) for _ in range(6)]
    assert "Wir machen erst einmal weiter" in replies[-1]
    transfer_turn = state["dialogue_turn"]
    assert transfer_turn != failed_turn
    assert state["dialogue_deferred_turn"] == failed_turn
    assert state["dialogue_transfer_turn"] == transfer_turn

    reply = handle_dialogue("Ich komme aus Polen.", state)

    assert state["dialogue_turn"] == failed_turn
    assert "Okay, noch einmal: Woher kommst du?" in reply
    assert "Mia:" not in reply
    assert "Mia fragt" not in reply
    assert "Jetzt noch einmal: Du bist dran." not in reply
    assert "dialogue_deferred_turn" not in state
    assert "dialogue_transfer_turn" not in state
    assert state.get("course_mastery_assistance_used") is False


def test_course_dialogue_renders_as_direct_nele_conversation_without_roleplay_ui():
    from brain.logic.dialogue_engine import start_dialogue, handle_dialogue

    state = {"conversation_mode": "course"}
    opening = start_dialogue("A1", 2, "woher-kommst-du", state)

    assert "Woher kommst du?" in opening
    assert "Mia:" not in opening
    assert "Du bist dran." not in opening

    reply = handle_dialogue("Ich komme aus Polen.", state)

    assert "Kommst du aus Polen?" in reply
    assert "Mia:" not in reply
    assert "Antworte Mia." not in reply


def test_course_dialogue_exhausted_transfer_hides_roleplay_prompt():
    from brain.logic.dialogue_engine import start_dialogue, handle_dialogue

    state = {"conversation_mode": "course"}
    start_dialogue("A1", 2, "woher-kommst-du", state)

    for _ in range(5):
        handle_dialogue("ich weiß nicht", state)
    reply = handle_dialogue("okay", state)

    assert "Kommst du aus Polen?" in reply
    assert "Mia:" not in reply
    assert "Antworte Mia." not in reply


def test_free_dialogue_keeps_explicit_roleplay_speaker_and_prompt():
    from brain.logic.dialogue_engine import start_dialogue

    state = {"conversation_mode": "free"}
    opening = start_dialogue("A1", 2, "woher-kommst-du", state)

    assert "Mia: Hallo! Woher kommst du?" in opening
    assert "Du bist dran." in opening
