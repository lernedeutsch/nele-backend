import unittest

from brain.logic.free_conversation import (
    generate_free_conversation_reply,
    generate_free_welcome,
)


def _turn(state, message):
    reply, meta = generate_free_conversation_reply(message, state)
    return reply, meta


class GeneratedTests(unittest.TestCase):
    def test_beginner_work_dialog_keeps_context(self):
        state = {}
        generate_free_welcome(state)

        # Force the exact question being regression-tested.
        free = state["free_conversation"]
        free["last_question"] = "Was machst du bei der Arbeit?"

        reply, _ = _turn(state, "Kochen")

        self.assertTrue("Ich koche." in reply)
        self.assertTrue("Ich arbeite Kochen" not in reply)
        self.assertTrue("Arbeit" in reply)


    def test_beginner_work_time_dialog_understands_bis_two(self):
        state = {"free_conversation": {
        "last_question": "Bis wann arbeitest du heute?",
        "recent_questions": ["Bis wann arbeitest du heute?"],
        "conversation_facts": {},
        }}

        reply, _ = _turn(state, "Bis 2")

        self.assertTrue("Ich arbeite bis 2 Uhr" in reply)
        self.assertTrue("danach" in reply.lower())


    def test_beginner_food_dialog_understands_pizza(self):
        state = {"free_conversation": {
        "last_question": "Was isst du gern?",
        "recent_questions": ["Was isst du gern?"],
        "conversation_facts": {},
        }}

        reply, _ = _turn(state, "Pizza")

        self.assertTrue("Pizza" in reply)
        self.assertTrue("Isst du das oft?" in reply)


    def test_beginner_hobby_dialog_understands_company(self):
        state = {"free_conversation": {
        "last_question": "Machst du das lieber allein oder mit jemandem?",
        "recent_questions": ["Machst du das lieber allein oder mit jemandem?"],
        "conversation_facts": {},
        }}

        reply, _ = _turn(state, "Mit meinem Mann")

        self.assertTrue("zusammen" in reply.lower())


    def test_weather_yes_does_not_repeat_same_question(self):
        state = {"free_conversation": {
        "last_question": "Magst du das Wetter heute?",
        "recent_questions": ["Magst du das Wetter heute?"],
        "conversation_facts": {"weather": "warm"},
        }}

        reply, _ = _turn(state, "Ja")

        self.assertTrue("Magst du das Wetter heute?" not in reply)
        self.assertTrue("bei diesem Wetter" in reply)


    def test_typo_sonnig_gets_gentle_help_and_stays_weather(self):
        state = {"free_conversation": {
        "last_question": "Wie ist das Wetter bei dir?",
        "recent_questions": ["Wie ist das Wetter bei dir?"],
        "conversation_facts": {},
        }}

        reply, _ = _turn(state, "Sonn8g")

        self.assertTrue("sonnig" in reply)
        self.assertTrue("warm" in reply.lower())


    def test_free_conversation_multi_turn_regression(self):
        state = {"free_conversation": {
        "last_question": "Was machst du heute?",
        "recent_questions": ["Was machst du heute?"],
        "conversation_facts": {},
        }}

        first, _ = _turn(state, "Arbeit")
        self.assertTrue("arbeit" in first.lower())

        # Simulate a natural work follow-up explicitly; this isolates learner
        # interpretation from randomized/open fallback wording.
        state["free_conversation"]["last_question"] = "Was machst du bei der Arbeit?"
        second, _ = _turn(state, "Kochen")
        self.assertTrue("Ich koche." in second)
        self.assertTrue("Ich arbeite Kochen" not in second)

        state["free_conversation"]["last_question"] = "Was isst du gern?"
        third, _ = _turn(state, "Pizza")
        self.assertTrue("Pizza" in third)
        self.assertTrue(third != second)

    def test_real_work_sequence_does_not_restart_after_kochen_yes(self):
        state = {"free_conversation": {
        "last_question": "Was machst du gerade?",
        "recent_questions": ["Was machst du gerade?"],
        "conversation_facts": {},
        }}

        first, _ = _turn(state, "Arbeit")
        self.assertTrue("Wann fängst du an?" in first)

        second, _ = _turn(state, "8")
        self.assertTrue("Ich fange um 8 Uhr an." in second)
        self.assertTrue("Was machst du bei der Arbeit?" in second)

        third, _ = _turn(state, "kochen")
        self.assertTrue("Ich koche." in third)
        self.assertTrue("Kochst du jeden Tag bei der Arbeit?" in third)

        fourth, _ = _turn(state, "ja")
        self.assertTrue("Wann fängst du" not in fourth)
        self.assertTrue("Was machst du bei der Arbeit?" not in fourth)
        self.assertTrue("Was kochst du gern bei der Arbeit?" in fourth)

    def test_work_cooking_food_chain_keeps_context(self):
        state = {"free_conversation": {
            "last_question": "Was kochst du gern bei der Arbeit?",
            "recent_questions": ["Was kochst du gern bei der Arbeit?"],
            "conversation_facts": {"work_activity": "kochen"},
        }}

        first, _ = _turn(state, "suppe")
        self.assertTrue("Ich koche gern Suppe." in first)
        self.assertTrue("etwas anderes" in first)

        second, _ = _turn(state, "pizza")
        self.assertTrue("Ich koche auch gern Pizza." in second)
        self.assertTrue("Wann fängst du" not in second)
        self.assertTrue("Was machst du bei der Arbeit?" not in second)

