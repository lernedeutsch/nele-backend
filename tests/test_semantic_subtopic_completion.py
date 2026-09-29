import unittest
from brain.logic.free_conversation import generate_free_conversation_reply

def turn(state, message):
    return generate_free_conversation_reply(message, state)

class SemanticSubtopicCompletionTests(unittest.TestCase):
    def test_music_completion_stays_related(self):
        state = {}
        turn(state, "Welche Musik hörst du gern?")
        turn(state, "Pop")
        turn(state, "Die Sängerin ist gut")
        reply, meta = turn(state, "Oft am Abend")
        self.assertEqual(meta["topic_manager"]["subtopic"], "music")
        self.assertNotEqual(reply, "Was machst du gern in deiner Freizeit?")
        self.assertIn("Musik", reply)

    def test_sport_completion_stays_related(self):
        state = {}
        turn(state, "Welchen Sport machst du gern?")
        turn(state, "Fußball")
        turn(state, "Mit Freunden")
        reply, meta = turn(state, "Am Wochenende")
        self.assertEqual(meta["topic_manager"]["subtopic"], "sport")
        self.assertNotEqual(reply, "Was machst du gern in deiner Freizeit?")
        self.assertIn("Sport", reply)

    def test_food_completion_stays_related(self):
        state = {}
        turn(state, "Was isst du gern?")
        turn(state, "Pizza")
        turn(state, "Mit Käse")
        reply, meta = turn(state, "Am Wochenende")
        self.assertEqual(meta["topic_manager"]["subtopic"], "essen")
        self.assertNotEqual(reply, "Was isst du heute?")
        self.assertTrue("Restaurant" in reply or "zu Hause" in reply)

    def test_music_bridge_answer_is_committed_and_completes_subtopic(self):
        state = {}
        turn(state, "Welche Musik hörst du gern?")
        turn(state, "Pop")
        turn(state, "Die Sängerin ist gut")
        turn(state, "Oft am Abend")
        turn(state, "Zu Hause")
        semantic = state.get("conversation_state_v2") or {}
        self.assertEqual((semantic.get("semantic_slots") or {}).get("music_place"), "zu hause")
        self.assertEqual(semantic.get("subtopic_status"), "completed")
        self.assertIsNone(semantic.get("active_slot"))

    def test_sport_bridge_answer_is_committed_and_completes_subtopic(self):
        state = {}
        turn(state, "Welchen Sport machst du gern?")
        turn(state, "Fußball")
        turn(state, "Mit Freunden")
        turn(state, "Am Wochenende")
        turn(state, "Draußen")
        semantic = state.get("conversation_state_v2") or {}
        self.assertEqual((semantic.get("semantic_slots") or {}).get("sport_environment"), "draußen")
        self.assertEqual(semantic.get("subtopic_status"), "completed")
        self.assertIsNone(semantic.get("active_slot"))

    def test_food_bridge_answer_is_committed_and_completes_subtopic(self):
        state = {}
        turn(state, "Was isst du gern?")
        turn(state, "Pizza")
        turn(state, "Mit Käse")
        turn(state, "Am Wochenende")
        turn(state, "Zu Hause")
        semantic = state.get("conversation_state_v2") or {}
        self.assertEqual((semantic.get("semantic_slots") or {}).get("food_place"), "zu hause")
        self.assertEqual(semantic.get("subtopic_status"), "completed")
        self.assertIsNone(semantic.get("active_slot"))

    def test_reading_bridge_answer_is_committed_and_completes_subtopic(self):
        state = {}
        transcript = []
        for message in ("Was liest du gern?", "Krimis", "Die Spannung", "Oft am Abend", "Oft", "Unterwegs"):
            reply, meta = turn(state, message)
            semantic_now = state.get("conversation_state_v2") or {}
            transcript.append({
                "user": message,
                "reply": reply,
                "active_slot": semantic_now.get("active_slot"),
                "subtopic": semantic_now.get("subtopic"),
                "status": semantic_now.get("subtopic_status"),
                "slots": dict(semantic_now.get("semantic_slots") or {}),
                "meta_topic": (meta or {}).get("topic"),
            })
        semantic = state.get("conversation_state_v2") or {}
        self.assertEqual(
            (semantic.get("semantic_slots") or {}).get("reading_place"),
            "unterwegs",
            msg=f"reading transcript: {transcript!r}",
        )
        self.assertEqual(semantic.get("subtopic_status"), "completed")

    def test_birthday_bridge_answer_is_committed_and_completes_subtopic(self):
        state = {}
        turn(state, "Wann hast du Geburtstag?")
        turn(state, "Am vierzehnten Februar")
        turn(state, "Mit meiner Familie")
        turn(state, "Wir essen Kuchen")
        turn(state, "Ja")
        semantic = state.get("conversation_state_v2") or {}
        self.assertEqual((semantic.get("semantic_slots") or {}).get("birthday_preference"), "ja")
        self.assertEqual(semantic.get("subtopic_status"), "completed")

    def test_bare_gut_does_not_steal_music_question_as_wellbeing(self):
        state = {}
        turn(state, "Welche Musik hörst du gern?")
        reply, meta = turn(state, "gut")
        self.assertNotEqual(meta.get("topic"), "today")
        self.assertNotIn("mir geht es gut", reply.lower())
        self.assertNotIn("was machst du heute", reply.lower())

    def test_birthday_date_stays_birthday(self):
        state = {}
        turn(state, "Wann hast du Geburtstag?")
        reply, meta = turn(state, "Am vierzehnten Februar")
        self.assertEqual(meta["topic"], "personal")
        self.assertEqual(meta["topic_manager"]["subtopic"], "birthday")
        self.assertNotIn("heute", reply.lower())
        self.assertIn("Geburtstag", reply)

if __name__ == "__main__":
    unittest.main()
