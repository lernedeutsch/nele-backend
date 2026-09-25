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
