import unittest

from brain.logic.dialogue_engine import answer_matches_dialogue_turn, clear_dialogue
from brain.logic.dialogue_knowledge import compatible_topics, render_pattern
from brain.logic.dialogue_state_engine import (
    allow_variation,
    initialise_dialogue_state,
    mark_intent_complete,
    within_turn_limit,
)


class GoldenDialogueSystemTests(unittest.TestCase):
    def test_slot_pattern_accepts_safe_variant(self):
        turn = {
            "expected_intent": "give_origin",
            "accepted_patterns": ["Ich komme aus {country}.", "Aus {country}."],
        }
        self.assertTrue(answer_matches_dialogue_turn(
            "Aus Italien", turn, {"country": "Italien"}
        ))
        self.assertFalse(answer_matches_dialogue_turn(
            "Ich wohne in Berlin", turn, {"country": "Italien"}
        ))

    def test_render_pattern(self):
        self.assertEqual(
            render_pattern("Ich komme aus {country}.", {"country": "Polen"}),
            "Ich komme aus Polen.",
        )

    def test_topic_mixing_is_denied_by_default(self):
        self.assertTrue(compatible_topics("Herkunft", "Herkunft", []))
        self.assertFalse(compatible_topics("Herkunft", "Einkaufen", []))
        self.assertTrue(compatible_topics("Herkunft", "Wohnort", ["Wohnort"]))

    def test_state_tracks_intents_and_has_hard_turn_limit(self):
        state = {}
        dialogue = {"topic": "Herkunft", "max_turns": 2}
        initialise_dialogue_state(state, dialogue)
        self.assertTrue(within_turn_limit(state, dialogue))
        state["dialogue_exchange_count"] = 2
        self.assertFalse(within_turn_limit(state, dialogue))
        mark_intent_complete(state, "give_origin")
        mark_intent_complete(state, "give_origin")
        self.assertEqual(state["dialogue_completed_intents"], ["give_origin"])

    def test_variation_limit_prevents_endless_country_drill(self):
        state = {}
        dialogue = {"max_variations": 2}
        initialise_dialogue_state(state, dialogue)
        self.assertTrue(allow_variation(state, "country", dialogue))
        self.assertTrue(allow_variation(state, "country", dialogue))
        self.assertFalse(allow_variation(state, "country", dialogue))

    def test_clear_removes_semantic_dialogue_state(self):
        state = {"dialogue_active": True}
        initialise_dialogue_state(state, {"topic": "Herkunft"})
        clear_dialogue(state)
        self.assertFalse(state["dialogue_active"])
        self.assertNotIn("dialogue_topic", state)


if __name__ == "__main__":
    unittest.main()


    def test_active_registry_is_consumed_by_same_engine(self):
        from unittest.mock import patch
        from brain.logic.dialogue_engine import load_dialogues, get_dialogue
        active = [{
            "id": "hotel-greeting-001",
            "level": "A1",
            "lesson": 4,
            "knowledge_status": "active",
            "title": "Im Hotel",
            "turns": [
                {"role": "nele", "text": "Guten Morgen!", "intent": "greet"},
                {"role": "student", "expected": "Guten Morgen!", "expected_intent": "greet_back"},
            ],
        }]
        with patch("brain.logic.dialogue_engine.get_active_dialogues", return_value=active):
            loaded = load_dialogues("A1", 4)
            self.assertEqual(loaded[0]["id"], "hotel-greeting-001")
            self.assertEqual(get_dialogue("A1", 4, "hotel-greeting-001")["knowledge_status"], "active")




    def test_real_a12_origin_dialogue_completes_without_topic_mixing(self):
        from brain.logic.dialogue_engine import start_dialogue, handle_dialogue
        state = {}
        opening = start_dialogue("A1", 2, "woher-kommst-du", state)
        self.assertIn("Woher kommst du?", opening)

        # Correct meaning but unrelated topic must not advance.
        reply = handle_dialogue("Ich kaufe Brot.", state)
        self.assertIn("Ich komme aus Polen", reply)
        self.assertEqual(state["dialogue_turn"], 1)

        reply = handle_dialogue("Polen", state)
        self.assertIn("Kommst du aus Polen?", reply)
        self.assertIn("give_origin", state["dialogue_completed_intents"])

        reply = handle_dialogue("Ja", state)
        self.assertIn("Woher kommt Anna?", reply)

        reply = handle_dialogue("Anna kommt aus Österreich.", state)
        self.assertFalse(state["dialogue_active"])
        self.assertIn("geschafft", reply)


