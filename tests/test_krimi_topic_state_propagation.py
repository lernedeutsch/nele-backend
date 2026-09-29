import unittest
import inspect

from brain.logic import free_conversation


class KrimiTopicStatePropagationTests(unittest.TestCase):
    def test_krimi_is_a_hobby_topic_keyword(self):
        source = inspect.getsource(free_conversation.generate_free_conversation_reply)
        self.assertIn('"buch", "krimi"', source)

    def test_krimi_content_sets_reading_activity(self):
        source = inspect.getsource(free_conversation.generate_free_conversation_reply)
        self.assertIn('memory.setdefault("activity", "reading")', source)

    def test_krimi_content_still_precedes_generic_subtopic_fallback(self):
        source = inspect.getsource(free_conversation.generate_free_conversation_reply)
        content_pos = source.index("explicit_content_followup = _content_followup")
        fallback_pos = source.index("subtopic_followup = None")
        self.assertLess(content_pos, fallback_pos)

    def test_generic_reading_subtopic_exists_for_following_unexpected_turn(self):
        self.assertIn(
            ("hobby", "reading"),
            free_conversation.SUBTOPIC_QUESTIONS,
        )


if __name__ == "__main__":
    unittest.main()
