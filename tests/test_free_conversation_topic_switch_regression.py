import unittest

from brain.logic.free_conversation import generate_free_conversation_reply, generate_free_welcome


def turn(state, message):
    reply, _ = generate_free_conversation_reply(message, state)
    return reply


class FreeConversationTopicSwitchRegressionTests(unittest.TestCase):
    def fresh_state(self):
        state = {}
        generate_free_welcome(state)
        return state

    def test_direct_wellbeing_question_beats_previous_topic(self):
        state = self.fresh_state()
        state["free_conversation"]["last_question"] = "Wie ist das Wetter bei dir?"
        reply = turn(state, "Hallo Nele, wie geht es dir heute?")
        self.assertIn("Mir geht", reply)

    def test_tired_statement_beats_previous_weather_topic(self):
        state = self.fresh_state()
        state["free_conversation"]["last_question"] = "Magst du das Wetter heute?"
        reply = turn(state, "Ich bin heute müde.")
        self.assertIn("müde", reply.lower())
        self.assertNotIn("Magst du das Wetter", reply)

    def test_weekend_question_beats_previous_weather_topic(self):
        state = self.fresh_state()
        state["free_conversation"]["last_question"] = "Wie ist das Wetter bei dir?"
        reply = turn(state, "Was machst du gern am Wochenende?")
        self.assertNotIn("wetter", reply.lower())

    def test_food_question_beats_previous_weather_topic(self):
        state = self.fresh_state()
        state["free_conversation"]["last_question"] = "Ist es warm oder kalt?"
        reply = turn(state, "Und was isst du gern?")
        self.assertNotIn("warm oder kalt", reply.lower())

    def test_evening_question_beats_previous_home_topic(self):
        state = self.fresh_state()
        state["free_conversation"]["last_question"] = "Wohnst du in einem Haus oder in einer Wohnung?"
        reply = turn(state, "Was machst du heute Abend?")
        self.assertNotIn("zuhause", reply.lower())
        self.assertNotIn("zimmer", reply.lower())

    def test_existing_weather_short_answer_still_keeps_context(self):
        state = self.fresh_state()
        state["free_conversation"]["last_question"] = "Wie ist das Wetter bei dir?"
        reply = turn(state, "warm")
        self.assertIn("warm", reply.lower())

    def test_existing_work_yes_still_keeps_context(self):
        state = self.fresh_state()
        state["free_conversation"]["last_question"] = "Arbeitest du heute?"
        reply = turn(state, "ja")
        self.assertIn("Wann", reply)


if __name__ == "__main__":
    unittest.main()
