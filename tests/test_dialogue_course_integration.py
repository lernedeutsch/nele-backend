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
        self.assertFalse(state["dialogue_active"])


    def test_completed_course_dialogue_offers_next_section_and_und_jetzt_continues(self):
        from brain.logic.dialogue_engine import start_dialogue
        from brain.memory.lesson_progress import set_lesson_sections

        state = {}
        set_lesson_sections(
            state,
            "A1",
            2,
            ["Woher kommen Sie?", "Das Verb kommen", "Zahlen 1–20"],
        )
        start_dialogue("A1", 2, "woher-kommst-du", state)
        handle_dialogue("Polen", state)
        handle_dialogue("Ja", state)
        reply = handle_dialogue("Anna kommt aus Österreich", state)

        self.assertIn("Herkunftsdialog geschafft", reply)
        self.assertIn("Das Verb kommen", reply)
        self.assertEqual(state["last_question"], "continue_new_learning")
        self.assertEqual(
            state["pending_new_learning"]["section"],
            "Das Verb kommen",
        )

        # A social thank-you must not destroy the pending course continuation.
        self.assertIsNone(handle_new_learning_resume("danke", state))
        self.assertEqual(
            state["pending_new_learning"]["section"],
            "Das Verb kommen",
        )

        with patch(
            "brain.logic.new_learning_resume.start_new_learning",
            return_value="NEXT_SECTION_STARTED",
        ) as start_next:
            continued = handle_new_learning_resume("und jetzt", state)

        self.assertEqual(continued, "NEXT_SECTION_STARTED")
        start_next.assert_called_once()


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



def test_real_course_dialogue_offers_graph_next_section_without_legacy_sections():
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
    assert "Das Verb kommen" in reply
    assert state["last_question"] == "continue_new_learning"
    assert state["pending_new_learning"]["section"] == "Das Verb kommen"
    assert state["pending_new_learning"]["skill"] == "course:a1:2:das_verb_kommen"


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


def test_dialogue_turn_successes_alone_do_not_count_as_mastery_proof():
    from brain.logic.dialogue_engine import _record_course_dialogue_outcome
    dialogue = {"level": "A1", "lesson": 15, "section": "Reisen"}
    state = {"conversation_mode": "course"}

    for _ in range(4):
        progress = _record_course_dialogue_outcome(dialogue, state, True)

    assert progress["successes"] == 4
    assert progress["independent_confirmations"] == 0
    assert progress["status"] != "mastered"


def test_clean_dialogue_completion_can_confirm_mastery_after_practice():
    from brain.logic.dialogue_engine import _record_course_dialogue_outcome
    dialogue = {"level": "A1", "lesson": 15, "section": "Reisen"}
    state = {"conversation_mode": "course"}

    _record_course_dialogue_outcome(dialogue, state, True)
    _record_course_dialogue_outcome(dialogue, state, True)
    progress = _record_course_dialogue_outcome(
        dialogue, state, True, independent_confirmation=True
    )

    assert progress["successes"] == 3
    assert progress["independent_confirmations"] == 1
    assert progress["status"] == "mastered"
