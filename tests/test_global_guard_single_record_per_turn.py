import unittest

from brain.logic.free_conversation import generate_free_conversation_reply


def _well_formed_state():
    return {"free_conversation": {
        "last_question": "Wie ist dein Tag heute?",
        "recent_questions": ["Wie ist dein Tag heute?"],
        "conversation_facts": {},
    }}


class GlobalGuardSingleRecordPerTurnTests(unittest.TestCase):
    """A free-conversation turn may record at most one actually selected question."""

    def _run_turns(self, messages):
        state = _well_formed_state()
        recent_lengths = []
        for message in messages:
            generate_free_conversation_reply(message, state)
            guard_store = state.get("global_conversation_guard_v1", {})
            recent_lengths.append(len(guard_store.get("recent", [])))
        return recent_lengths

    def test_recent_memory_never_grows_by_more_than_one_per_turn(self):
        messages = [
            "gut", "Arbeit", "Kochen", "ja", "Pizza", "Musik",
            "Fussball", "warm", "sonnig", "Urlaub", "Meer", "ja",
            "schlecht", "müde", "traurig",
        ]
        lengths = self._run_turns(messages)
        deltas = [lengths[0]] + [b - a for a, b in zip(lengths, lengths[1:])]
        for turn_index, delta in enumerate(deltas, start=1):
            self.assertLessEqual(
                delta, 1,
                f"turn {turn_index}: guard recent memory grew by {delta} in one turn",
            )

    def test_recent_memory_length_never_exceeds_turn_count_or_cap(self):
        messages = [
            "gut", "Arbeit", "Kochen", "ja", "Pizza", "Musik",
            "Fussball", "warm", "sonnig", "Urlaub", "Meer", "ja",
            "schlecht", "müde", "traurig",
        ]
        lengths = self._run_turns(messages)
        for turn_number, length in enumerate(lengths, start=1):
            self.assertLessEqual(length, min(turn_number, 12))


if __name__ == "__main__":
    unittest.main()
