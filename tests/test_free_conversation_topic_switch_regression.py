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

    def test_weather_question_stays_in_natural_tutor_conversation(self):
        state = self.fresh_state()
        reply = turn(state, "Wie ist das Wetter heute?")
        self.assertEqual("Ich bin gespannt. Wie ist das Wetter bei dir?", reply)
        self.assertNotIn("kein echtes Wetter", reply)

    def test_deutsch_lernen_does_not_repeat_already_answered_question(self):
        state = self.fresh_state()
        turn(state, "Was machst du heute Abend?")
        reply = turn(state, "Deutsch lernen")
        self.assertIn("Ich lerne gerade Deutsch.", reply)
        self.assertIn("Lernst du jeden Tag?", reply)
        self.assertNotIn("Was lernst du gerade?", reply)

    def test_daily_german_yes_keeps_learning_subthread(self):
        state = self.fresh_state()
        turn(state, "Was machst du heute Abend?")
        turn(state, "Deutsch lernen")
        reply = turn(state, "ja")
        self.assertIn("Wie lange lernst du jeden Tag Deutsch?", reply)
        self.assertNotIn("Was machst du heute?", reply)

    def test_daily_german_duration_keeps_learning_subthread(self):
        state = self.fresh_state()
        turn(state, "Was machst du heute Abend?")
        turn(state, "Deutsch lernen")
        turn(state, "ja")
        reply = turn(state, "30 Minuten")
        self.assertIn("30 Minuten jeden Tag", reply)
        self.assertIn("Was übst du am liebsten", reply)
        self.assertNotIn("Was machst du heute?", reply)

    def test_german_practice_choice_keeps_learning_subthread(self):
        state = self.fresh_state()
        turn(state, "Was machst du heute Abend?")
        turn(state, "Deutsch lernen")
        turn(state, "ja")
        turn(state, "30 Minuten")
        reply = turn(state, "Sprechen")
        self.assertIn("Sprechen ist wichtig", reply)
        self.assertIn("Mit wem sprichst du gern Deutsch?", reply)
        self.assertNotIn("Was machst du heute?", reply)

    def test_german_speaking_partner_keeps_learning_subthread(self):
        state = self.fresh_state()
        turn(state, "Was machst du heute Abend?")
        turn(state, "Deutsch lernen")
        turn(state, "ja")
        turn(state, "30 Minuten")
        turn(state, "Sprechen")
        reply = turn(state, "Mit dir")
        self.assertIn("Mit mir? Sehr gern!", reply)
        self.assertIn("Worüber sprichst du gern auf Deutsch?", reply)
        self.assertNotIn("Was machst du heute?", reply)

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


    def test_weekend_question_updates_topic_away_from_weather(self):
        state = self.fresh_state()
        turn(state, "Wie ist das Wetter heute?")
        turn(state, "schön")
        turn(state, "Was machst du gern am Wochenende?")
        self.assertEqual(state["free_conversation"].get("last_topic"), "hobby")

    def test_food_question_updates_topic_away_from_weather(self):
        state = self.fresh_state()
        turn(state, "Wie ist das Wetter heute?")
        turn(state, "schön")
        reply = turn(state, "Und was isst du gern?")
        self.assertNotIn("warm oder kalt", reply.lower())
        self.assertEqual(state["free_conversation"].get("last_topic"), "food")

    def test_evening_question_does_not_rotate_to_yesterday(self):
        state = self.fresh_state()
        turn(state, "Ich wohne in Deutschland.")
        reply = turn(state, "Was machst du heute Abend?")
        self.assertNotIn("gestern", reply.lower())
        self.assertEqual(state["free_conversation"].get("last_topic"), "today")


    def test_weekend_question_keeps_spazieren_in_the_same_activity_thread(self):
        state = self.fresh_state()
        reply = turn(state, "Was machst du gern am Wochenende?")
        self.assertIn("was machst du gern am wochenende", reply.lower())
        self.assertEqual(state["free_conversation"].get("last_topic"), "hobby")

        reply = turn(state, "spazieren")
        self.assertIn("spazieren", reply.lower())
        self.assertIn("allein oder mit jemandem", reply.lower())
        self.assertNotIn("sport", reply.lower())

    def test_weekend_activity_question_variants_share_semantic_context(self):
        variants = (
            "Was machst du gern am Wochenende?",
            "Und was machst du gern am Wochenende?",
            "Was machst du am Wochenende?",
            "Was machst du normalerweise am Wochenende?",
        )
        for question in variants:
            state = self.fresh_state()
            reply = turn(state, question)
            pending = state["free_conversation"].get("pending_learner_question") or {}
            self.assertEqual(pending.get("slot"), "activity", question)
            self.assertEqual(pending.get("context"), "weekend", question)
            self.assertEqual(pending.get("topic"), "hobby", question)
            self.assertIn("wochenende", reply.lower(), question)

    def test_weekend_activity_question_variants_own_topic_manager_state(self):
        variants = (
            "Was machst du gern am Wochenende?",
            "Und was machst du gern am Wochenende?",
            "Was machst du am Wochenende?",
            "Was machst du normalerweise am Wochenende?",
        )
        for question in variants:
            state = self.fresh_state()
            reply = turn(state, question)
            self.assertIn("wochenende", reply.lower(), question)
            self.assertEqual(state["free_conversation"].get("last_topic"), "hobby", question)
            manager = state.get("topic_manager_v2") or {}
            self.assertEqual(manager.get("topic"), "hobby", question)
            self.assertEqual(manager.get("subtopic"), "freizeit", question)

    def test_weekend_activity_answers_do_not_collapse_into_sport(self):
        cases = (
            ("spazieren", "spazieren"),
            ("lesen", "liest"),
            ("Musik hören", "musik"),
            ("schwimmen", "schwimm"),
        )
        for answer, expected in cases:
            state = self.fresh_state()
            turn(state, "Was machst du gern am Wochenende?")
            reply = turn(state, answer)
            self.assertIn(expected, reply.lower(), answer)
            if answer != "schwimmen":
                self.assertNotIn("machst du gern sport", reply.lower(), answer)

    def test_weekend_walking_company_continues_walking_thread(self):
        state = self.fresh_state()
        turn(state, "Was machst du gern am Wochenende?")
        turn(state, "spazieren")
        reply = turn(state, "Mit meinem Mann")
        self.assertIn("oft", reply.lower())
        self.assertNotIn("machst du gern sport", reply.lower())

    def test_explicit_weather_switch_beats_pending_weekend_activity(self):
        state = self.fresh_state()
        turn(state, "Was machst du gern am Wochenende?")
        turn(state, "spazieren")
        reply = turn(state, "Heute regnet es")
        self.assertEqual(state["free_conversation"].get("last_topic"), "weather")
        self.assertIn("regnet", reply.lower())

    def test_food_intent_with_discourse_particle_overrides_hobby(self):
        state = self.fresh_state()
        turn(state, "Was machst du gern am Wochenende?")
        turn(state, "spazieren")
        reply = turn(state, "Und was isst du gern?")
        self.assertEqual(state["free_conversation"].get("last_topic"), "food")
        self.assertNotIn("sport", reply.lower())
        self.assertNotIn("musik", reply.lower())

    def test_food_intent_accepts_natural_discourse_variants(self):
        variants = (
            "Und was isst du gern?",
            "Aber was isst du gern?",
            "Also was isst du gern?",
            "Und was frühstückst du gern?",
        )
        for question in variants:
            state = self.fresh_state()
            turn(state, "Was machst du gern am Wochenende?")
            turn(state, "spazieren")
            reply = turn(state, question)
            self.assertEqual(state["free_conversation"].get("last_topic"), "food", question)
            self.assertNotIn("sport", reply.lower(), question)
            self.assertNotIn("musik", reply.lower(), question)

    def test_food_intent_variants_share_one_classifier(self):
        for question in ("Was isst du gern?", "Und was isst du gern?", "Aber was isst du gern?"):
            state = self.fresh_state()
            turn(state, "Was machst du gern am Wochenende?")
            turn(state, "spazieren")
            turn(state, question)
            self.assertEqual(state["free_conversation"].get("last_topic"), "food", question)


    def test_explicit_wellbeing_switch_commits_canonical_state_and_clears_reading_slot(self):
        state = self.fresh_state()
        turn(state, "Was liest du gern?")
        turn(state, "Krimis")
        self.assertEqual((state.get("conversation_state_v2") or {}).get("active_slot"), "reading_detail")

        reply, meta = generate_free_conversation_reply("Mir geht es schlecht", state)

        self.assertIn("tut mir leid", reply.lower())
        self.assertEqual(meta.get("topic"), "today")
        self.assertEqual((meta.get("conversation_state") or {}).get("subtopic"), "wellbeing")
        self.assertIsNone((state.get("conversation_state_v2") or {}).get("active_slot"))
        self.assertEqual((state.get("conversation_state_v2") or {}).get("subtopic"), "wellbeing")
        self.assertEqual((state.get("topic_manager_v2") or {}).get("topic"), "today")
        self.assertEqual((state.get("topic_manager_v2") or {}).get("subtopic"), "wellbeing")
        self.assertEqual((state.get("topic_manager_v2") or {}).get("source"), "wellbeing")

    def test_wellbeing_followup_stays_canonical_then_explicit_reading_question_switches_back(self):
        state = self.fresh_state()
        turn(state, "Was liest du gern?")
        turn(state, "Krimis")
        turn(state, "Mir geht es schlecht")

        reply, meta = generate_free_conversation_reply("Ich bin müde", state)
        self.assertIn("müde", reply.lower())
        self.assertEqual((meta.get("conversation_state") or {}).get("subtopic"), "wellbeing")
        self.assertEqual((state.get("topic_manager_v2") or {}).get("subtopic"), "wellbeing")
        self.assertIsNone((state.get("conversation_state_v2") or {}).get("active_slot"))

        reply, meta = generate_free_conversation_reply("Und was liest du gern?", state)
        self.assertIn("krimis", reply.lower())
        self.assertEqual(meta.get("topic"), "hobby")
        self.assertEqual((state.get("topic_manager_v2") or {}).get("subtopic"), "reading")

    def test_bare_gut_in_reading_still_does_not_become_wellbeing(self):
        state = self.fresh_state()
        turn(state, "Was liest du gern?")
        turn(state, "Krimis")
        reply, meta = generate_free_conversation_reply("Gut", state)
        self.assertNotIn("mir geht es gut", reply.lower())
        self.assertEqual(meta.get("topic"), "hobby")
        self.assertEqual((state.get("topic_manager_v2") or {}).get("subtopic"), "reading")


    def test_work_statement_with_today_and_end_time_does_not_ask_if_learner_works_today(self):
        state = self.fresh_state()
        turn(state, "Was isst du gern?")
        turn(state, "Pizza")
        reply = turn(state, "Ich arbeite heute bis 15 Uhr")
        self.assertNotEqual(reply, "Arbeitest du heute?")
        self.assertIn("fängst du", reply)
        facts = state.get("a1_everyday_facts") or {}
        self.assertTrue(facts.get("works_today"))
        self.assertEqual(facts.get("work_end"), "15")

    def test_contextual_company_echo_preserves_internal_capitalization(self):
        for answer, expected in (("Mit meinem Mann", "Mit meinem Mann"), ("Mit meiner Familie", "Mit meiner Familie")):
            state = self.fresh_state()
            turn(state, "Was machst du gern am Wochenende?")
            turn(state, "spazieren")
            reply = turn(state, answer)
            self.assertIn(expected, reply)


    def test_full_sentence_semantic_statements_fill_domain_slots(self):
        cases = (
            ("Ich lese Krimis", "reading_genre", "krimis", "hobby", "reading"),
            ("Ich höre gern Popmusik", "music_genre", "popmusik", "hobby", "music"),
            ("Ich spiele Fußball", "sport_kind", "fußball", "hobby", "sport"),
            ("Ich esse gern Pizza", "food", "pizza", "food", "essen"),
        )
        for statement, slot, value, topic, subtopic in cases:
            state = self.fresh_state()
            turn(state, "Was machst du heute?")
            reply = turn(state, statement)
            snap = state.get("conversation_state_v2") or {}
            self.assertEqual(snap.get("semantic_slots", {}).get(slot), value, statement)
            self.assertEqual(snap.get("topic"), topic, statement)
            self.assertEqual(snap.get("subtopic"), subtopic, statement)
            if slot == "reading_genre":
                self.assertNotIn("was liest du gern", reply.lower(), statement)
            elif slot == "music_genre":
                self.assertNotIn("welche musik hörst du gern", reply.lower(), statement)
            elif slot == "sport_kind":
                self.assertNotIn("was machst du gern in deiner freizeit", reply.lower(), statement)
            elif slot == "food_item":
                self.assertNotIn("was machst du sonst noch gern", reply.lower(), statement)

    def test_full_sentence_sport_keeps_companion_answer_in_sport(self):
        state = self.fresh_state()
        turn(state, "Was machst du gern?")
        reply = turn(state, "Ich spiele Fußball")
        self.assertIn("mit wem", reply.lower())
        reply = turn(state, "Mit Freunden")
        self.assertIn("oft", reply.lower())
        self.assertNotIn("musik", reply.lower())


    def test_und_du_answers_the_delivered_housing_question(self):
        state = self.fresh_state()
        turn(state, "Ich wohne in Heidelberg")
        reply = turn(state, "Und du?")
        self.assertIn("haus", reply.lower())
        self.assertIn("wohnung", reply.lower())
        self.assertNotIn("was machst du gern", reply.lower())

    def test_reciprocal_question_reuses_reading_and_food_meaning(self):
        cases = (
            ("Was liest du gern?", "Und du?", "krimis"),
            ("Was isst du gern?", "Und bei dir?", "essen"),
        )
        for question, reciprocal, expected in cases:
            state = self.fresh_state()
            turn(state, question)
            reply = turn(state, reciprocal)
            self.assertIn(expected, reply.lower(), question)


    def test_und_du_answers_exact_active_semantic_question(self):
        cases = (
            ("Was liest du gern?", "Ich lese Krimis", "spannung", "freizeit"),
            ("Welchen Sport machst du gern?", "Ich spiele Fußball", "sportpartner", "freizeit"),
        )
        for opener, answer, expected, forbidden in cases:
            state = self.fresh_state()
            turn(state, opener)
            turn(state, answer)
            reply = turn(state, "Und du?")
            self.assertIn(expected, reply.lower(), opener)
            self.assertNotIn(forbidden, reply.lower(), opener)

    def test_food_item_gets_natural_preference_followup(self):
        state = self.fresh_state()
        turn(state, "Und was isst du gern?")
        reply = turn(state, "Pizza")
        self.assertIn("wie magst du das am liebsten", reply.lower())
        self.assertNotIn("wie isst du das gern", reply.lower())

    def test_full_cycling_gern_statement_reaches_cycling_followup(self):
        state = self.fresh_state()
        reply = turn(state, "Ich fahre gern Rad")
        self.assertIn("wo fährst du gern rad", reply.lower())
        self.assertNotIn("was machst du sonst noch gern", reply.lower())
        reply = turn(state, "Im Park")
        self.assertIn("fährst du dort oft rad", reply.lower())

    def test_full_swimming_gern_statement_keeps_context_after_place(self):
        state = self.fresh_state()
        reply = turn(state, "Ich schwimme gern")
        self.assertIn("wo schwimmst du gern", reply.lower())
        reply = turn(state, "Draußen")
        self.assertIn("schwimmst du oft", reply.lower())
        reply = turn(state, "oft")
        self.assertNotIn("musik", reply.lower())
        self.assertIn("freizeit", reply.lower())

    def test_swimming_activity_keeps_context_after_place(self):
        state = self.fresh_state()
        turn(state, "Was machst du gern am Wochenende?")
        self.assertIn("schwimm", turn(state, "schwimmen").lower())
        reply = turn(state, "Draußen")
        self.assertIn("schwimmst du oft", reply.lower())
        reply = turn(state, "oft")
        self.assertNotIn("musik", reply.lower())
        self.assertIn("freizeit", reply.lower())

if __name__ == "__main__":
    unittest.main()


class FreeConversationControlPriorityTests(unittest.TestCase):
    def _state(self, last_question, status="active"):
        state = {"student_progress": {"current_level": "A1.1"}, "conversation_mode": "free"}
        state["free_conversation"] = {
            "last_question": last_question,
            "last_topic": "hobby",
            "turn_count": 8,
            "conversation_facts": {},
        }
        state["conversation_state_v2"] = {
            "topic": "hobby",
            "subtopic": "sport",
            "subtopic_status": status,
            "active_slot": "sport_environment" if status == "active" else None,
            "semantic_slots": {},
        }
        return state

    def test_pause_outranks_active_sport_subtopic(self):
        state = self._state("Machst du diesen Sport lieber draußen oder drinnen?")
        reply, meta = generate_free_conversation_reply("Pause", state)
        self.assertEqual(reply, "Klar, machen wir eine Pause.")
        self.assertIn(meta["global_conversation_guard"]["reason"], {"conversation_control", "contextual_short_answer"})

    def test_nichts_closes_broad_freizeit_question_before_subtopic_reopens_it(self):
        state = self._state("Das klingt gut. Und was machst du sonst gern in deiner Freizeit?", status="completed")
        reply, meta = generate_free_conversation_reply("nichts", state)
        self.assertNotIn("was machst du sonst gern in deiner freizeit", reply.lower())
        self.assertIn("wechseln wir das thema", reply.lower())
        self.assertEqual(meta["global_conversation_guard"]["reason"], "conversation_control")
