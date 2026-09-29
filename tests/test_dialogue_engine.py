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

    def test_real_a12_dialogue_accepts_negative_country_correction(self):
        state = {}
        start_dialogue("A1", 2, "woher-kommst-du", state)
        first = handle_dialogue("Ich komme aus Deutschland.", state)
        self.assertIn("Kommst du aus Deutschland", first)

        reply = handle_dialogue("Nein, ich komme aus Polen.", state)

        self.assertIn("Anna kommt aus Österreich", reply)
        self.assertEqual(state["dialogue_slots"]["country"], "Polen")
        self.assertEqual(state["dialogue_turn"], 5)

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
