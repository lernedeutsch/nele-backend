import unittest

from brain.logic.free_conversation import _short_answer_followup


class GeneratedTests(unittest.TestCase):
    def test_bis_two_answers_work_time_question(self):
        memory = {}
        reply = _short_answer_followup(
        "Bis 2",
        "Bis wann arbeitest du heute?",
        memory,
        )
        self.assertTrue("Ich arbeite bis 2 Uhr" in reply)
        self.assertTrue(memory["work_until"] == "2")


    def test_kochen_answers_work_activity_question(self):
        memory = {}
        reply = _short_answer_followup(
        "Kochen",
        "Was machst du bei der Arbeit?",
        memory,
        )
        self.assertTrue("Ich koche." in reply)
        self.assertTrue("Ich arbeite Kochen" not in reply)


    def test_pizza_answers_food_question(self):
        memory = {}
        reply = _short_answer_followup(
        "Pizza",
        "Was isst du gern?",
        memory,
        )
        self.assertTrue("Pizza" in reply)
        self.assertTrue(memory["food"] == "Pizza")


    def test_company_answer_stays_in_activity_context(self):
        memory = {}
        reply = _short_answer_followup(
        "Mit meinem Mann",
        "Machst du das lieber allein oder mit jemandem?",
        memory,
        )
        self.assertTrue("zusammen" in reply)
        self.assertTrue(memory["activity_company"] == "Mit meinem Mann")


    def test_short_answer_without_matching_question_is_not_guessed(self):
        self.assertTrue(_short_answer_followup("Pizza", "Wie ist das Wetter?", {}) is None)


    def test_walking_frequency_stays_in_local_activity_context(self):
        memory = {"activity_company": "Mit meinem Mann"}
        reply = _short_answer_followup("oft", "Macht ihr das oft zusammen?", memory)
        self.assertNotIn("was machst du gern in deiner freizeit", reply.lower())
        self.assertIn("zusammen", reply.lower())
        self.assertEqual(memory["activity_frequency"], "oft")
