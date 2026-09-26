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

    def test_learner_question_guard_never_falls_back_to_previous_weather_topic(self):
        state = self.fresh_state()
        turn(state, "Wie ist das Wetter heute?")
        turn(state, "schön")
        reply = turn(state, "Was machst du gern am Wochenende?")
        self.assertNotIn("warm oder kalt", reply.lower())
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


    def test_free_wellbeing_uses_shared_extended_vocabulary(self):
        state = self.fresh_state()
        state["free_conversation"]["last_question"] = "Wie geht es dir heute?"
        reply = turn(state, "gestresst")
        self.assertIn("gestresst", reply.lower())
        self.assertNotIn("Wie geht es dir", reply)

    def test_free_wellbeing_uses_shared_correction_engine(self):
        state = self.fresh_state()
        state["free_conversation"]["last_question"] = "Wie geht es dir heute?"
        reply = turn(state, "mir geht gut")
        self.assertIn("Mir geht es gut", reply)

    def test_free_wellbeing_preserves_natural_bad_model(self):
        state = self.fresh_state()
        state["free_conversation"]["last_question"] = "Wie geht es dir heute?"
        reply = turn(state, "schlecht")
        self.assertIn("Mir geht es schlecht", reply)



    def test_explicit_wellbeing_update_outranks_stale_topic(self):
        state = {"student_progress": {"current_level": "A1.1"}, "conversation_mode": "free"}
        free = state.setdefault("free_conversation", {})
        free["last_question"] = "Was machst du heute?"
        free["turn_count"] = 3
        from brain.logic.free_conversation import generate_free_conversation_reply
        reply, meta = generate_free_conversation_reply("gestresst", state)
        self.assertTrue(meta.get("shared_wellbeing"))
        self.assertIn("gestresst", reply.lower())
        self.assertNotIn("Was machst du heute?", reply)

    def test_malformed_explicit_wellbeing_uses_shared_correction_after_other_topic(self):
        state = {"student_progress": {"current_level": "A1.1"}, "conversation_mode": "free"}
        free = state.setdefault("free_conversation", {})
        free["last_question"] = "Was machst du heute?"
        free["turn_count"] = 3
        from brain.logic.free_conversation import generate_free_conversation_reply
        reply, meta = generate_free_conversation_reply("mir geht gut", state)
        self.assertTrue(meta.get("shared_wellbeing"))
        self.assertIn("Mir geht es gut", reply)

    def test_learner_led_dialogue_question_can_switch_mid_conversation(self):
        state = {"student_progress": {"current_level": "A1.1"}, "conversation_mode": "free"}
        free = state.setdefault("free_conversation", {})
        free["last_question"] = "Hörst du gern Musik?"
        free["turn_count"] = 5
        from brain.logic.free_conversation import generate_free_conversation_reply
        reply, meta = generate_free_conversation_reply("Wie komme ich zum Bahnhof?", state)
        self.assertTrue(meta.get("dialogue_knowledge"))
        self.assertEqual(state.get("dialogue_id"), "a1-l15-weg-bahnhof")
        self.assertNotIn("Musik", reply)


    def test_weekend_question_does_not_auto_start_travel_dialogue(self):
        state = self.fresh_state()
        turn(state, "Wie ist das Wetter heute?")
        turn(state, "schön")
        reply = turn(state, "Was machst du gern am Wochenende?")
        self.assertNotIn("ich fahre nach berlin", reply.lower())
        self.assertFalse(state.get("dialogue_active"))

    def test_evening_question_interrupts_home_chain(self):
        state = self.fresh_state()
        turn(state, "Ich wohne in Deutschland.")
        reply = turn(state, "Was machst du heute Abend?")
        self.assertNotIn("zuhause groß oder klein", reply.lower())
        self.assertNotIn("welche zimmer", reply.lower())

    def test_full_housekeeping_answer_stays_in_work_context(self):
        state = self.fresh_state()
        turn(state, "Wann fängst du an?")
        turn(state, "um 8 Uhr")
        reply = turn(state, "Ich putze Zimmer.")
        self.assertIn("zimmer", reply.lower())
        self.assertNotIn("wie ist dein tag", reply.lower())

if __name__ == "__main__":
    unittest.main()
