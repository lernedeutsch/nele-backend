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


    def test_spazieren_advances_hobby_thread_instead_of_repeating_question(self):
        state = {
            "free_conversation": {
                "last_question": "Was machst du gern in deiner Freizeit?",
                "last_topic": "hobby",
                "turn_count": 2,
                "conversation_facts": {},
            },
            "student_progress": {"current_level": "A1.1"},
        }
        reply, meta = generate_free_conversation_reply("spazieren", state)
        self.assertNotEqual(reply, "Was machst du gern in deiner Freizeit?")
        self.assertIn("spazieren", reply.lower())
        self.assertEqual(meta["topic_manager"]["topic"], "hobby")

    def test_origin_statement_expires_stale_food_topic(self):
        state = {
            "free_conversation": {
                "last_question": "Isst du das oft?",
                "last_topic": "food",
                "turn_count": 5,
                "conversation_facts": {},
            },
            "student_progress": {"current_level": "A1.1"},
        }
        reply, meta = generate_free_conversation_reply("Ich komme aus Polen.", state)
        self.assertEqual(meta["topic_manager"]["topic"], "place")
        self.assertNotEqual(meta["topic"], "food")

    def test_origin_question_expires_stale_food_topic(self):
        state = {
            "free_conversation": {
                "last_question": "Isst du das oft?",
                "last_topic": "food",
                "turn_count": 5,
                "conversation_facts": {},
            },
            "student_progress": {"current_level": "A1.1"},
        }
        reply, meta = generate_free_conversation_reply("Woher kommst du?", state)
        self.assertEqual(meta["topic_manager"]["topic"], "place")


    def test_elliptical_topic_questions_use_shared_learner_turn_mechanism(self):
        cases = [
            ("Und Sport?", "sport_kind", "hobby"),
            ("Und Musik?", "music_genre", "hobby"),
            ("Und Essen?", "food", "food"),
            ("Und Arbeit?", "work_activity", "work"),
        ]
        for message, slot, topic in cases:
            with self.subTest(message=message):
                turn = analyze_learner_turn(message, last_question="Hörst du oft Musik?")
                self.assertEqual(turn["intent"], "question_to_nele")
                self.assertEqual(turn["slot"], slot)

                state = {
                    "free_conversation": {
                        "last_question": "Hörst du oft Musik?",
                        "last_topic": "hobby",
                        "turn_count": 4,
                        "conversation_facts": {},
                    },
                    "student_progress": {"current_level": "A1.1"},
                }
                reply, meta = generate_free_conversation_reply(message, state)
                self.assertTrue(meta.get("answered_learner_question"))
                self.assertEqual(meta["topic_manager"]["topic"], topic)
                self.assertNotEqual(reply, "Was machst du gern in deiner Freizeit?")

    def test_elliptical_sport_switch_keeps_three_turn_sport_context(self):
        state = {
            "free_conversation": {
                "last_question": "Hörst du oft Musik?",
                "last_topic": "hobby",
                "turn_count": 4,
                "conversation_facts": {},
            },
            "student_progress": {"current_level": "A1.1"},
        }
        reply, meta = generate_free_conversation_reply("Und Sport?", state)
        self.assertIn("Welchen Sport", reply)
        reply, meta = generate_free_conversation_reply("Badminton", state)
        self.assertEqual(meta["topic_manager"]["subtopic"], "sport")
        self.assertNotIn("Musik", reply)

    def test_elliptical_work_switch_keeps_semantic_context_for_unexpected_answers(self):
        state = {
            "free_conversation": {
                "last_question": "Hörst du oft Musik?",
                "last_topic": "hobby",
                "turn_count": 4,
                "conversation_facts": {},
            },
            "student_progress": {"current_level": "A1.1"},
        }
        reply, meta = generate_free_conversation_reply("Und Arbeit?", state)
        self.assertIn("Was machst du bei der Arbeit", reply)
        self.assertEqual(meta["conversation_state"]["subtopic"], "work")

        reply, meta = generate_free_conversation_reply("Gästezimmer vorbereiten", state)
        self.assertEqual(meta["topic_manager"]["subtopic"], "work")
        self.assertIn("Wo arbeitest du", reply)

        reply, meta = generate_free_conversation_reply("In einer Pension", state)
        self.assertEqual(meta["topic_manager"]["subtopic"], "work")
        self.assertIn("Mit wem arbeitest du", reply)

        reply, meta = generate_free_conversation_reply("Mit meinem Team", state)
        self.assertEqual(meta["topic_manager"]["subtopic"], "work")
        self.assertIn("Bis wann arbeitest du", reply)

    def test_valid_work_sentence_is_not_repeated_as_a_correction(self):
        state = {
            "free_conversation": {
                "last_question": "Was machst du bei der Arbeit?",
                "last_topic": "work",
                "turn_count": 3,
                "conversation_facts": {},
            },
            "student_progress": {"current_level": "A1.1"},
        }
        reply, meta = generate_free_conversation_reply("Ich putze Zimmer.", state)
        self.assertNotIn("Du kannst sagen: „Ich putze Zimmer.“", reply)
        self.assertIn("Wie viele Zimmer", reply)


if __name__ == "__main__":
    unittest.main()
