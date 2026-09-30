import unittest
from unittest.mock import patch

from brain.logic.dialogue_engine import (
    answer_matches_dialogue_turn,
    handle_dialogue,
    start_dialogue,
    get_current_dialogue_prompt,
    start_dialogue_for_section,
)


SAMPLE = {
    "id": "street",
    "title": "Auf der Straße",
    "intro": "Wir spielen einen kurzen Dialog.",
    "turns": [
        {"role": "nele", "speaker": "Mia", "text": "Hallo! Woher kommst du?"},
        {
            "role": "student",
            "prompt": "Du bist dran.",
            "expected": "Ich komme aus Polen.",
            "accepted": ["Ich komme aus Polen", "aus Polen"],
            "retry": "Sag: „Ich komme aus Polen.“",
        },
        {"role": "nele", "speaker": "Mia", "text": "Kommst du aus Polen?"},
        {
            "role": "student",
            "expected": "Ja, ich komme aus Polen.",
            "accepted": ["ja ich komme aus Polen", "ja"],
        },
    ],
    "complete": "Sehr gut! Der Dialog ist fertig.",
}


class DialogueEngineTests(unittest.TestCase):
    def test_accepts_natural_variant(self):
        self.assertTrue(
            answer_matches_dialogue_turn(
                "aus Polen",
                SAMPLE["turns"][1],
            )
        )


    def test_dialogue_uses_same_semantic_word_order_rule_as_course_step(self):
        turn = {
            "expected": "Du kommst aus Frankreich.",
            "accepted": ["Du kommst aus Frankreich."],
        }
        self.assertTrue(
            answer_matches_dialogue_turn("Aus Frankreich kommst du.", turn)
        )

    def test_dialogue_shared_semantics_still_reject_wrong_conjugation(self):
        turn = {
            "expected": "Ich komme aus Spanien.",
            "accepted": ["Ich komme aus Spanien."],
        }
        self.assertTrue(answer_matches_dialogue_turn("Komme aus Spanien.", turn))
        self.assertFalse(answer_matches_dialogue_turn("Ich kommen aus Spanien.", turn))
        self.assertFalse(answer_matches_dialogue_turn("Wir wohnen in Spanien.", turn))

    @patch("brain.logic.dialogue_engine.get_dialogue", return_value=SAMPLE)
    def test_dialogue_advances_and_finishes(self, _):
        state = {}
        opening = start_dialogue("A1", 2, "street", state)
        self.assertIn("Woher kommst du", opening)
        self.assertTrue(state["dialogue_active"])

        reply = handle_dialogue("Ich komme aus Polen", state)
        self.assertIn("Kommst du aus Polen", reply)
        self.assertEqual(state["dialogue_turn"], 3)

        reply = handle_dialogue("ja", state)
        self.assertIn("Dialog ist fertig", reply)
        self.assertFalse(state["dialogue_active"])

    def test_real_a12_dialogue_is_selected_from_section(self):
        state = {}
        opening = start_dialogue_for_section("A1", 2, "Woher kommen Sie?", state)
        self.assertIn("Woher kommst du", opening)
        self.assertEqual(state["dialogue_id"], "woher-kommst-du")

    def test_real_a12_dialogue_accepts_declared_country_variation(self):
        state = {}
        opening = start_dialogue("A1", 2, "woher-kommst-du", state)
        self.assertIn("Woher kommst du", opening)

        reply = handle_dialogue("Ich komme aus Deutschland.", state)

        self.assertIn("Kommst du aus Deutschland", reply)
        self.assertEqual(state["dialogue_slots"]["country"], "Deutschland")
        self.assertEqual(state["dialogue_turn"], 3)

    def test_real_a12_dialogue_accepts_semantic_country_variation(self):
        state = {}
        opening = start_dialogue("A1", 2, "woher-kommst-du", state)
        self.assertIn("Woher kommst du", opening)

        reply = handle_dialogue("Komme aus Spanien.", state)

        self.assertIn("Kommst du aus Spanien", reply)
        self.assertEqual(state["dialogue_slots"]["country"], "Spanien")
        self.assertEqual(state["dialogue_turn"], 3)

    def test_real_a12_dialogue_accepts_negative_country_correction(self):
        state = {}
        start_dialogue("A1", 2, "woher-kommst-du", state)
        first = handle_dialogue("Ich komme aus Deutschland.", state)
        self.assertIn("Kommst du aus Deutschland", first)

        reply = handle_dialogue("Nein, ich komme aus Polen.", state)

        self.assertIn("Anna kommt aus Österreich", reply)
        self.assertEqual(state["dialogue_slots"]["country"], "Polen")
        self.assertEqual(state["dialogue_turn"], 5)

    def test_real_a12_dialogue_rejects_self_contradictory_negative_confirmation(self):
        state = {}
        start_dialogue("A1", 2, "woher-kommst-du", state)
        first = handle_dialogue("Ich komme aus Frankreich.", state)
        self.assertIn("Kommst du aus Frankreich", first)

        reply = handle_dialogue("Nein, ich komme aus Frankreich.", state)

        self.assertIn("Ja", reply)
        self.assertIn("Nein", reply)
        self.assertEqual(state["dialogue_slots"]["country"], "Frankreich")
        self.assertEqual(state["dialogue_turn"], 3)

    def test_real_a12_dialogue_runs_end_to_end(self):
        state = {}
        opening = start_dialogue("A1", 2, "woher-kommst-du", state)
        self.assertIn("Woher kommst du", opening)
        reply = handle_dialogue("Ich komme aus Polen", state)
        self.assertIn("Kommst du aus Polen", reply)
        reply = handle_dialogue("Ja", state)
        self.assertIn("Anna kommt aus Österreich", reply)
        reply = handle_dialogue("Anna kommt aus Österreich", state)
        self.assertIn("Herkunftsdialog geschafft", reply)
        self.assertFalse(state["dialogue_active"])

    @patch("brain.logic.dialogue_engine.get_dialogue", return_value=SAMPLE)
    def test_new_question_releases_active_dialogue(self, _):
        state = {}
        start_dialogue("A1", 2, "street", state)
        reply = handle_dialogue("Was isst du gern?", state)
        self.assertIsNone(reply)
        self.assertFalse(state["dialogue_active"])

    @patch("brain.logic.dialogue_engine.get_dialogue", return_value=SAMPLE)
    def test_wrong_statement_stays_in_active_dialogue(self, _):
        state = {}
        start_dialogue("A1", 2, "street", state)
        reply = handle_dialogue("Berlin", state)
        self.assertIn("Ich komme aus Polen", reply)
        self.assertTrue(state["dialogue_active"])

    @patch("brain.logic.dialogue_engine.get_dialogue", return_value=SAMPLE)
    def test_wrong_answer_does_not_advance(self, _):
        state = {}
        start_dialogue("A1", 2, "street", state)
        reply = handle_dialogue("Berlin", state)
        self.assertIn("Ich komme aus Polen", reply)
        self.assertEqual(state["dialogue_turn"], 1)


if __name__ == "__main__":
    unittest.main()


def test_course_dialogue_side_question_keeps_exact_turn_for_resume():
    state = {"conversation_mode": "course"}
    start_dialogue("A1", 2, "woher-kommst-du", state)
    handle_dialogue("Aus Deutschland.", state)

    turn_before = state["dialogue_turn"]
    reply = handle_dialogue("Wie ist das Wetter?", state)

    assert reply is None
    assert state["dialogue_active"] is True
    assert state["dialogue_turn"] == turn_before
    assert state["course_side_question_pending"] is True
    resumed = get_current_dialogue_prompt(state)
    assert "Kommst du aus Deutschland?" in resumed
    assert "Antworte Mia." in resumed


def test_course_turn_limit_never_counts_wrong_answer_as_mastery():
    state = {"conversation_mode": "course"}
    opening = start_dialogue("A1", 2, "woher-kommst-du", state)
    assert "Woher kommst du" in opening

    handle_dialogue("ich komme aus Polen", state)
    handle_dialogue("ja", state)
    assert state["dialogue_turn"] == 5

    # Exhaust the dialogue's ordinary safety budget with wrong answers.
    for wrong in ("Berlin", "zwölf", "20", "polnisch", "nein"):
        reply = handle_dialogue(wrong, state)
        assert "Herkunftsdialog geschafft" not in reply
        assert state["dialogue_active"] is True
        assert state["dialogue_turn"] == 5

    reply = handle_dialogue("Anna kommt aus Österreich", state)
    assert "Herkunftsdialog geschafft" not in reply
    assert "festigen" in reply
    assert state["dialogue_active"] is True
    skill = state["learning_progress_v1"]["skills"]["course:a1:2:woher_kommen_sie"]
    assert skill["status"] != "mastered"


def test_course_dialogue_wrong_answer_records_shared_teacher_action():
    state = {"conversation_mode": "course"}
    start_dialogue("A1", 2, "woher-kommst-du", state)

    reply = handle_dialogue("Berlin", state)

    assert state["course_teacher_action"]["action"] == "correct_and_retry"
    assert state["course_teacher_action"]["reason"] == "answer_not_yet"
    assert state["dialogue_active"] is True
    assert state["dialogue_turn"] == 1
    assert reply


def test_course_dialogue_completes_only_after_shared_mastery():
    state = {"conversation_mode": "course"}
    start_dialogue("A1", 2, "woher-kommst-du", state)
    handle_dialogue("Ich komme aus Polen", state)
    handle_dialogue("Ja", state)
    reply = handle_dialogue("Anna kommt aus Österreich", state)

    skill = state["learning_progress_v1"]["skills"]["course:a1:2:woher_kommen_sie"]
    assert skill["status"] == "mastered"
    assert "Herkunftsdialog geschafft" in reply
    assert state["dialogue_active"] is False
    assert state["learner_model_v2"]["version"] == 2
    assert state["course_teaching_decision"] == {
        "decision": "teach_next",
        "skill": "course:a1:2:das_verb_kommen",
        "reason": "course_prerequisites_met",
    }
    assert state["pending_new_learning"]["skill"] == "course:a1:2:das_verb_kommen"
