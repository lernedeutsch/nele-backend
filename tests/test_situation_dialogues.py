import unittest

from brain.logic.dialogue_engine import (
    answer_matches_dialogue_turn,
    find_dialogue_for_message,
    get_dialogue,
    handle_dialogue,
    start_dialogue,
)


class SituationDialogueTests(unittest.TestCase):
    def test_situation_dialogues_are_available_to_shared_engine(self):
        self.assertIsNotNone(get_dialogue("A1", 1, "a1-situation-begruessung"))
        self.assertIsNotNone(get_dialogue("A2", 1, "a2-situation-baeckerei"))
        self.assertIsNotNone(get_dialogue("A2", 1, "a2-situation-bahnhof"))

    def test_arbitrary_long_text_is_not_accepted(self):
        dialogue = get_dialogue("A2", 1, "a2-situation-baeckerei")
        learner_turn = dialogue["turns"][1]
        self.assertFalse(answer_matches_dialogue_turn(
            "Heute scheint die Sonne und ich fahre später nach Hause.",
            learner_turn,
        ))

    def test_natural_bakery_variants_are_accepted(self):
        dialogue = get_dialogue("A2", 1, "a2-situation-baeckerei")
        learner_turn = dialogue["turns"][1]
        self.assertTrue(answer_matches_dialogue_turn("Ein Brötchen, bitte.", learner_turn))
        self.assertTrue(answer_matches_dialogue_turn("Ich möchte ein Brot, bitte.", learner_turn))

    def test_wrong_answer_does_not_advance_dialogue(self):
        state = {}
        start_dialogue("A2", 1, "a2-situation-baeckerei", state)
        before = state["dialogue_turn"]
        reply = handle_dialogue("Heute fahre ich mit dem Zug.", state)
        self.assertEqual(before, state["dialogue_turn"])
        self.assertTrue(reply)

    def test_station_trigger_can_find_situation(self):
        found = find_dialogue_for_message("Ich brauche eine Fahrkarte nach Frankfurt.", "A2")
        self.assertIsNotNone(found)
        self.assertEqual("a2-situation-bahnhof", found["id"])


if __name__ == "__main__":
    unittest.main()
