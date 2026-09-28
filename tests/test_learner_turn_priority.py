import unittest

from brain.logic.learner_turn import analyze_learner_turn, question_slot
from brain.logic.response_understanding import understand_response
from brain.logic.free_conversation import generate_free_conversation_reply


class LearnerTurnPriorityTests(unittest.TestCase):
    def test_krimi_is_contextual_short_answer_not_new_question(self):
        turn = analyze_learner_turn("Krimi", last_question="Was für Filme magst du?")
        self.assertEqual(turn["intent"], "short_answer")
        self.assertEqual(turn["slot"], "film_genre")
        self.assertEqual(turn["content"], "Krimi")

    def test_common_short_answers_share_one_mechanism(self):
        cases = [
            ("um 8 Uhr", "Wann fängst du an?", "time"),
            ("im Hotel", "Wo arbeitest du?", "place"),
            ("mit meiner Familie", "Mit wem gehst du spazieren?", "person"),
            ("spazieren", "Was machst du gern in deiner Freizeit?", "activity"),
        ]
        for answer, question, slot in cases:
            with self.subTest(answer=answer):
                turn = analyze_learner_turn(answer, last_question=question)
                self.assertEqual(turn["intent"], "short_answer")
                self.assertEqual(turn["slot"], slot)

    def test_response_understanding_exposes_turn_contract(self):
        result = understand_response(
            "Krimi",
            conversation_state={"last_question": "Was für Filme magst du?", "topic": "hobby"},
        )
        self.assertEqual(result["turn_intent"], "short_answer")
        self.assertEqual(result["slot"], "film_genre")
        self.assertEqual(result["content"], "Krimi")

    def test_learner_question_outranks_stale_food_context(self):
        state = {
            "free_conversation": {
                "last_question": "Was kochst du gern?",
                "last_topic": "food",
                "turn_count": 4,
                "conversation_facts": {},
            },
            "student_progress": {"current_level": "A1.1"},
        }
        reply, meta = generate_free_conversation_reply("Was machst du heute Abend?", state)
        self.assertTrue(meta.get("answered_learner_question"))
        self.assertIn("Heute Abend", reply)
        self.assertNotEqual(reply, "Wie ist dein Tag heute?")
        self.assertEqual(meta["learner_turn"]["intent"], "question_to_nele")
        self.assertEqual(meta["topic_manager"]["topic"], "today")

    def test_last_question_context_is_structured(self):
        state = {
            "free_conversation": {
                "last_question": "Was kochst du gern?",
                "last_topic": "food",
                "turn_count": 2,
                "conversation_facts": {},
            },
            "student_progress": {"current_level": "A1.1"},
        }
        generate_free_conversation_reply("Was machst du heute Abend?", state)
        ctx = state["free_conversation"].get("last_question_context") or {}
        self.assertEqual(ctx.get("slot"), "content")
        self.assertEqual(ctx.get("topic"), "today")


if __name__ == "__main__":
    unittest.main()
