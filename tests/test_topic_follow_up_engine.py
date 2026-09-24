import unittest

from brain.logic.topic_follow_up_engine import (
    next_topic_follow_up,
    reset_topic_questions,
)


class GeneratedTests(unittest.TestCase):
    def test_follow_ups_do_not_repeat(self):
        state = {"conversation_vocabulary_topic": "freizeit"}

        first = next_topic_follow_up(state)
        second = next_topic_follow_up(state)

        self.assertTrue(first)
        self.assertTrue(second)
        self.assertTrue(first != second)


    def test_topic_has_finite_sequence(self):
        state = {"conversation_vocabulary_topic": "wetter"}

        answers = [
        next_topic_follow_up(state)
        for _ in range(5)
        ]

        self.assertTrue(len([item for item in answers if item]) == 4)
        self.assertTrue(answers[-1] is None)


    def test_topics_keep_separate_history(self):
        state = {}

        freizeit = next_topic_follow_up(state, "freizeit")
        wetter = next_topic_follow_up(state, "wetter")

        self.assertTrue(freizeit)
        self.assertTrue(wetter)
        self.assertTrue(freizeit != wetter)


    def test_reset_topic_questions(self):
        state = {"conversation_vocabulary_topic": "essen"}

        first = next_topic_follow_up(state)
        next_topic_follow_up(state)

        reset_topic_questions(state, "essen")

        self.assertTrue(next_topic_follow_up(state) == first)
