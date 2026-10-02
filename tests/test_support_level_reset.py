import unittest

from brain.logic.speaking_support import (
    consume_course_model_exhaustion,
    progressive_course_support,
    _support_level,
    _set_support,
)


class SupportLevelResetsAfterExhaustionTests(unittest.TestCase):
    def test_level_resets_to_zero_after_exhaustion(self):
        state = {}
        _set_support(state, 5)
        state["course_model_practice_exhausted"] = "Guten Morgen"
        consume_course_model_exhaustion(state)
        self.assertEqual(_support_level(state), 0)

    def test_next_hint_after_exhaustion_starts_from_the_beginning(self):
        state = {}
        _set_support(state, 5)
        state["course_model_practice_exhausted"] = "Guten Morgen"
        consume_course_model_exhaustion(state)
        reply = progressive_course_support(
            "Guten Morgen",
            state,
            first_hint="Fast. Denk an die Begrüßung.",
        )
        self.assertEqual(reply, "Fast. Denk an die Begrüßung.")


if __name__ == "__main__":
    unittest.main()
