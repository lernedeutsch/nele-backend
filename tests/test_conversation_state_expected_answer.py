import unittest

from brain.logic.conversation_state import infer_expected_answer


class ConversationStateExpectedAnswerTests(unittest.TestCase):
    def test_clock_time_questions_are_classified_as_time(self):
        for question in (
            "Wann lernst du Deutsch?",
            "Bis wann arbeitest du heute?",
            "Um wie viel Uhr lernst du Deutsch?",
            "Um wieviel Uhr fängst du an?",
        ):
            with self.subTest(question=question):
                self.assertEqual(infer_expected_answer(question), "time")

    def test_how_question_remains_open(self):
        self.assertEqual(infer_expected_answer("Wie lernst du Deutsch?"), "open")


if __name__ == "__main__":
    unittest.main()
