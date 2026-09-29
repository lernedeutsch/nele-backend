import unittest
from unittest.mock import patch

from brain.logic.dialogue_engine import (
    answer_matches_dialogue_turn,
    clear_dialogue,
    get_dialogue,
    handle_dialogue,
    load_dialogues,
    find_dialogue_for_message,
    start_dialogue,
)
from brain.logic.dialogue_knowledge import compatible_topics, render_pattern
from brain.logic.dialogue_importer import activate_dialogue_candidates, validate_imported_slots
from brain.logic.dialogue_state_engine import (
    allow_variation,
    initialise_dialogue_state,
    mark_intent_complete,
    within_turn_limit,
)
from brain.knowledge.active_dialogues import ACTIVE_DIALOGUES


EXPECTED_ACTIVE_DIALOGUES = 23


class GoldenDialogueSystemTests(unittest.TestCase):
    def test_slot_pattern_accepts_safe_variant(self):
        turn = {
            "expected_intent": "give_origin",
            "accepted_patterns": ["Ich komme aus {country}.", "Aus {country}."],
        }
        self.assertTrue(answer_matches_dialogue_turn(
            "Aus Italien", turn, {"country": "Italien"}
        ))
        self.assertFalse(answer_matches_dialogue_turn(
            "Ich wohne in Berlin", turn, {"country": "Italien"}
        ))

    def test_render_pattern(self):
        self.assertEqual(
            render_pattern("Ich komme aus {country}.", {"country": "Polen"}),
            "Ich komme aus Polen.",
        )

    def test_topic_mixing_is_denied_by_default(self):
        self.assertTrue(compatible_topics("Herkunft", "Herkunft", []))
        self.assertFalse(compatible_topics("Herkunft", "Einkaufen", []))
        self.assertTrue(compatible_topics("Herkunft", "Wohnort", ["Wohnort"]))

    def test_state_tracks_intents_and_has_hard_turn_limit(self):
        state = {}
        dialogue = {"topic": "Herkunft", "max_turns": 2}
        initialise_dialogue_state(state, dialogue)
        self.assertTrue(within_turn_limit(state, dialogue))
        state["dialogue_exchange_count"] = 2
        self.assertFalse(within_turn_limit(state, dialogue))
        mark_intent_complete(state, "give_origin")
        mark_intent_complete(state, "give_origin")
        self.assertEqual(state["dialogue_completed_intents"], ["give_origin"])

    def test_variation_limit_prevents_endless_country_drill(self):
        state = {}
        dialogue = {"max_variations": 2}
        initialise_dialogue_state(state, dialogue)
        self.assertTrue(allow_variation(state, "country", dialogue))
        self.assertTrue(allow_variation(state, "country", dialogue))
        self.assertFalse(allow_variation(state, "country", dialogue))

    def test_clear_removes_semantic_dialogue_state(self):
        state = {"dialogue_active": True}
        initialise_dialogue_state(state, {"topic": "Herkunft"})
        clear_dialogue(state)
        self.assertFalse(state["dialogue_active"])
        self.assertNotIn("dialogue_topic", state)

    def test_active_registry_contains_expected_promoted_dialogues(self):
        self.assertEqual(len(ACTIVE_DIALOGUES), EXPECTED_ACTIVE_DIALOGUES)
        ids = [d["id"] for d in ACTIVE_DIALOGUES]
        self.assertEqual(len(ids), len(set(ids)))
        for dialogue in ACTIVE_DIALOGUES:
            self.assertEqual(dialogue["knowledge_status"], "active")
            self.assertIn(dialogue["level"], ("A1", "A2"))
            self.assertIn(dialogue["lesson"], [11, 12, 13, 14, 15, 16])
            self.assertGreaterEqual(len(dialogue["turns"]), 2)
            self.assertIn("combine_unrelated_topics", dialogue["forbidden_variations"])
            validate_imported_slots(dialogue)

    def test_every_promoted_dialogue_passes_candidate_to_active_gate(self):
        candidates = []
        for source in ACTIVE_DIALOGUES:
            item = dict(source)
            item["knowledge_status"] = "candidate"
            candidates.append(item)
        report = {
            "accepted": candidates,
            "rejected": [],
            "accepted_count": len(candidates),
            "rejected_count": 0,
            "ok": True,
            "stage": "candidate",
            "activation_ready": True,
        }
        active = activate_dialogue_candidates(report)
        self.assertEqual(len(active), EXPECTED_ACTIVE_DIALOGUES)
        self.assertTrue(all(d["knowledge_status"] == "active" for d in active))

    def test_each_promoted_dialogue_rejects_unrelated_first_answer(self):
        for dialogue in ACTIVE_DIALOGUES:
            state = {}
            opening = start_dialogue(dialogue["level"], dialogue["lesson"], dialogue["id"], state)
            self.assertTrue(opening)
            before = state.get("dialogue_turn", 0)
            response = handle_dialogue("Ich kaufe Brot.", state)
            self.assertTrue(response)
            self.assertEqual(
                state.get("dialogue_turn", 0),
                before,
                msg=f"Unrelated answer advanced {dialogue['id']}",
            )

    def test_each_promoted_dialogue_can_follow_its_canonical_answers(self):
        for dialogue in ACTIVE_DIALOGUES:
            state = {}
            opening = start_dialogue(dialogue["level"], dialogue["lesson"], dialogue["id"], state)
            self.assertTrue(opening, msg=f"Dialogue did not start: {dialogue['id']}")
            for turn in dialogue["turns"]:
                if turn.get("role") != "student":
                    continue
                expected = turn.get("expected")
                if not expected:
                    continue
                handle_dialogue(expected, state)
            self.assertFalse(
                state.get("dialogue_active", False),
                msg=f"Dialogue did not complete: {dialogue['id']}",
            )

    def test_global_router_finds_each_requested_topic(self):
        cases = [
            ("Wann hast du Geburtstag?", "a1-l11-geburtstag"),
            ("Was machst du am Samstag?", "a1-l11-wochenende"),
            ("Was machst du gern in deiner Freizeit?", "a1-l12-hobbys"),
            ("Kannst du schwimmen?", "a1-l13-faehigkeiten"),
            ("Welche Musik hörst du gern?", "a1-l14-musik"),
            ("Hast du Lust, ins Kino zu gehen?", "a1-l14-kino"),
            ("Wie fährst du nach Berlin?", "a1-l15-verkehrsmittel"),
            ("Wie komme ich zum Bahnhof?", "a1-l15-weg-bahnhof"),
            ("Fährt von hier ein Zug nach Zürich?", "a1-l15-bahnhof"),
            ("Wie fahre ich am besten in die Schweiz?", "a1-l15-schweiz"),
        ]
        for message, expected_id in cases:
            dialogue = find_dialogue_for_message(message, "A1")
            self.assertIsNotNone(dialogue, message)
            self.assertEqual(dialogue["id"], expected_id, message)

    def test_router_finds_daily_dialogues_from_natural_slot_variants(self):
        cases = [
            ("Ich möchte einen Brief nach Italien schicken.", "a1-daily-post"),
            ("Ich brauche eine Fahrkarte zum Hauptbahnhof.", "a1-daily-bus-ticket"),
            ("Mein Nachbar hat mein Paket angenommen.", "a2-daily-nachbar-paket"),
        ]
        for message, expected_id in cases:
            dialogue = find_dialogue_for_message(message, "A1-A2")
            self.assertIsNotNone(dialogue, message)
            self.assertEqual(dialogue["id"], expected_id, message)

    def test_free_conversation_can_retrieve_a2_daily_dialogue(self):
        from brain.logic.free_conversation import generate_free_conversation_reply

        state = {
            "student_progress": {"current_level": "A1.1"},
            "conversation_mode": "free",
        }
        reply, meta = generate_free_conversation_reply(
            "Mein Nachbar hat mein Paket angenommen.",
            state,
        )
        self.assertTrue(meta.get("dialogue_knowledge"))
        self.assertEqual(state.get("dialogue_id"), "a2-daily-nachbar-paket")
        self.assertTrue(state.get("dialogue_active"))
        self.assertIn("Paket", reply)

    def test_free_conversation_starts_and_keeps_selected_dialogue(self):
        from brain.logic.free_conversation import generate_free_conversation_reply

        state = {
            "student_progress": {"current_level": "A1.1"},
            "conversation_mode": "free",
        }
        reply, meta = generate_free_conversation_reply(
            "Wann hast du Geburtstag?",
            state,
        )
        self.assertTrue(meta.get("dialogue_knowledge"))
        self.assertEqual(state.get("dialogue_id"), "a1-l11-geburtstag")
        self.assertTrue(state.get("dialogue_active"))
        self.assertIn("Geburtstag", reply)

        reply, meta = generate_free_conversation_reply(
            "Am vierzehnten Februar.",
            state,
        )
        self.assertTrue(meta.get("dialogue_knowledge"))
        self.assertTrue(state.get("dialogue_active"))
        self.assertIn("Und du?", reply)

    def test_active_dialogue_switches_cleanly_to_explicit_new_topic(self):
        state = {}
        start_dialogue("A1", 11, "a1-l11-geburtstag", state)
        reply = handle_dialogue("Was machst du am Samstag?", state)
        self.assertEqual(state.get("dialogue_id"), "a1-l11-wochenende")
        self.assertIn("Was machst du am Samstag?", reply)
        self.assertNotIn("Sag bitte", reply)

    def test_active_dialogue_switches_on_natural_new_dialogue_question(self):
        state = {}
        start_dialogue("A1", 11, "a1-l11-geburtstag", state)
        reply = handle_dialogue("Welche Musik hörst du gern?", state)
        self.assertEqual(state.get("dialogue_id"), "a1-l14-musik")
        self.assertIn("Musik", reply)
        self.assertNotIn("vierzehnten Februar", reply)

    def test_active_dialogue_allows_natural_thanks_exit(self):
        state = {}
        start_dialogue("A1", 15, "a1-l15-weg-bahnhof", state)
        reply = handle_dialogue("Danke.", state)
        self.assertEqual(reply, "Gern!")
        self.assertFalse(state.get("dialogue_active"))

    def test_active_dialogue_allows_goodbye_exit(self):
        state = {}
        start_dialogue("A1", 15, "a1-l15-weg-bahnhof", state)
        reply = handle_dialogue("Tschüss!", state)
        self.assertEqual(reply, "Tschüss!")
        self.assertFalse(state.get("dialogue_active"))

    def test_global_router_ignores_unrelated_message(self):
        self.assertIsNone(
            find_dialogue_for_message("Ich brauche heute Milch und Äpfel.", "A1")
        )

    def test_active_registry_is_consumed_by_same_engine(self):
        active = [{
            "id": "hotel-greeting-001",
            "level": "A1",
            "lesson": 4,
            "knowledge_status": "active",
            "title": "Im Hotel",
            "turns": [
                {"role": "nele", "text": "Guten Morgen!", "intent": "greet"},
                {"role": "student", "expected": "Guten Morgen!", "expected_intent": "greet_back"},
            ],
        }]
        with patch("brain.logic.dialogue_engine.get_active_dialogues", return_value=active):
            loaded = load_dialogues("A1", 4)
            self.assertEqual(loaded[0]["id"], "hotel-greeting-001")
            self.assertEqual(
                get_dialogue("A1", 4, "hotel-greeting-001")["knowledge_status"],
                "active",
            )

    def test_real_a12_origin_dialogue_completes_without_topic_mixing(self):
        state = {}
        opening = start_dialogue("A1", 2, "woher-kommst-du", state)
        self.assertIn("Woher kommst du?", opening)

        reply = handle_dialogue("Ich kaufe Brot.", state)
        self.assertIn("Ich komme aus Polen", reply)
        self.assertEqual(state["dialogue_turn"], 1)

        reply = handle_dialogue("Polen", state)
        self.assertIn("Kommst du aus Polen?", reply)
        self.assertIn("give_origin", state["dialogue_completed_intents"])

        reply = handle_dialogue("Ja", state)
        self.assertIn("woher kommt Anna?", reply)

        reply = handle_dialogue("Anna kommt aus Österreich.", state)
        self.assertFalse(state["dialogue_active"])
        self.assertIn("geschafft", reply)

    def test_free_conversation_keeps_ownership_for_ordinary_dialogue_topics(self):
        from brain.logic.free_conversation import generate_free_conversation_reply

        cases = [
            "Welche Musik hörst du gern?",
            "Welchen Sport machst du gern?",
            "Was machst du gern in deiner Freizeit?",
        ]
        for message in cases:
            with self.subTest(message=message):
                state = {
                    "student_progress": {"current_level": "A1.1"},
                    "conversation_mode": "free",
                }
                generate_free_conversation_reply("Hallo Nele!", state)
                generate_free_conversation_reply("gut", state)

                reply, meta = generate_free_conversation_reply(message, state)

                self.assertTrue(reply)
                self.assertFalse(state.get("dialogue_active", False))
                self.assertIsNone(state.get("dialogue_id"))
                self.assertFalse(meta.get("dialogue_knowledge", False))

    def test_free_conversation_still_activates_situational_dialogue(self):
        from brain.logic.free_conversation import generate_free_conversation_reply

        state = {
            "student_progress": {"current_level": "A1.1"},
            "conversation_mode": "free",
        }
        reply, meta = generate_free_conversation_reply(
            "Wie komme ich zum Bahnhof?",
            state,
        )

        self.assertTrue(meta.get("dialogue_knowledge"))
        self.assertEqual(state.get("dialogue_id"), "a1-l15-weg-bahnhof")
        self.assertTrue(state.get("dialogue_active"))
        self.assertIn("Bahnhof", reply)


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
