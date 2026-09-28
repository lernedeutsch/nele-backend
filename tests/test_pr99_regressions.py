import unittest

from brain.logic.error_practice import is_equivalent_correct_answer
from brain.logic.free_conversation import FALLBACKS, LEVEL_SKILLS


class PR99RegressionTests(unittest.TestCase):
    def test_vocabulary_target_is_accepted_inside_natural_sentence(self):
        self.assertTrue(
            is_equivalent_correct_answer(
                "Ich fahre mit dem Zug.",
                "Zug",
                error_type="vocabulary",
            )
        )

    def test_new_everyday_topics_are_registered_for_expected_levels(self):
        self.assertTrue({"family", "friends", "food"} <= LEVEL_SKILLS["A1.2"])
        self.assertTrue({"housing", "weekend"} <= LEVEL_SKILLS["A1.3"])
        self.assertTrue({"transport", "technology", "health"} <= LEVEL_SKILLS["A2.1"])
        for topic in (
            "family", "friends", "food", "housing", "weekend",
            "transport", "technology", "health",
        ):
            self.assertIn(topic, FALLBACKS)
            self.assertTrue(FALLBACKS[topic])


if __name__ == "__main__":
    unittest.main()
