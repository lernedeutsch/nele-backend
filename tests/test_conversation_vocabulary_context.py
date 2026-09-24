import unittest

from brain.logic.conversation_vocabulary_context import (
    update_conversation_vocabulary_context,
    get_conversation_vocabulary_context,
)


class GeneratedTests(unittest.TestCase):
    def test_context_detects_and_remembers_topic(self):
        state = {}

        context = update_conversation_vocabulary_context(
        "Das Zimmer im Hotel ist schön.",
        state,
        )

        self.assertTrue(context["topic"] == "hotel")
        self.assertTrue(state["conversation_vocabulary_topic"] == "hotel")


    def test_short_answer_keeps_previous_topic():
        state = {
        "conversation_vocabulary_topic": "freizeit",
        }

        update_conversation_vocabulary_context(
        "Ja",
        state,
        )

        context = get_conversation_vocabulary_context(state)
        self.assertTrue(context["topic"] == "freizeit")
        self.assertTrue(isinstance(context["suggestions"], list))


    def test_context_does_not_generate_reply():
        state = {}

        result = update_conversation_vocabulary_context(
        "Ich esse Brot.",
        state,
        )

        self.assertTrue(isinstance(result, dict))
        self.assertTrue("topic" in result)
