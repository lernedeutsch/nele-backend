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
