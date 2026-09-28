import unittest

from brain.logic.free_conversation import (
    FALLBACKS, _generic_followup, _not_recent, _question_key,
    _remember_question, _short_answer_followup,
)


class FreeSessionMemoryTests(unittest.TestCase):
    def test_asked_keeps_questions_beyond_recent_window(self):
        free = {}
        questions = [f"Frage {i}?" for i in range(12)]
        for question in questions:
            _remember_question(free, question)
        self.assertEqual(len(free["recent_questions"]), 8)
        self.assertEqual(len(free["asked"]), 12)
        self.assertEqual(_not_recent(free, [questions[0], "Neue Frage?"]), ["Neue Frage?"])

    def test_exhausted_pool_never_reopens_used_questions(self):
        free = {"asked": [_question_key(q) for q in FALLBACKS["work"]], "conversation_facts": {}}
        self.assertEqual(_not_recent(free, FALLBACKS["work"]), [])

    def test_yes_followups_do_not_repeat_generic_schoen_reaction(self):
        from brain.logic.free_conversation import _yes_no_followup
        cases = [
            "Fährst du dort oft Rad?",
            "Schwimmst du dort im Sommer?",
            "Magst du das Wetter heute?",
        ]
        for question in cases:
            reply = _yes_no_followup("ja", question, {})
            self.assertNotIn("Schön!", reply)

    def test_work_start_creates_filled_slot(self):
        memory = {}
        reply = _short_answer_followup("8", "Wann fängst du an?", memory)
        self.assertIn("8 Uhr", reply)
        self.assertEqual(memory["filled_slots"]["work_start"], "8")

    def test_work_activity_creates_filled_slot(self):
        memory = {}
        reply = _short_answer_followup("kochen", "Was machst du bei der Arbeit?", memory)
        self.assertIn("Ich koche", reply)
        self.assertEqual(memory["filled_slots"]["work_activity"], "kochen")

    def test_filled_work_slots_are_not_asked_again(self):
        free = {
            "asked": [],
            "conversation_facts": {
                "filled_slots": {"work_start": "8", "work_activity": "kochen"}
            },
        }
        question = _generic_followup("work", free, support=1, independent=0, level="A1.1")
        self.assertNotEqual(_question_key(question), _question_key("Wann fängst du an?"))
        self.assertNotEqual(_question_key(question), _question_key("Was machst du bei der Arbeit?"))

    def test_food_fallback_stays_in_food_topic(self):
        free = {"asked": [], "conversation_facts": {}}
        question = _generic_followup("food", free, support=1, independent=0, level="A1.1")
        self.assertIn(question, FALLBACKS["food"])
        self.assertNotIn(question, FALLBACKS["today"] + FALLBACKS["work"])

    def test_food_fallback_moves_to_another_food_question_before_other_topics(self):
        free = {
            "asked": [_question_key("Was isst du gern?")],
            "conversation_facts": {},
        }
        question = _generic_followup("food", free, support=1, independent=0, level="A1.1")
        self.assertIn(question, FALLBACKS["food"])
        self.assertNotEqual(_question_key(question), _question_key("Was isst du gern?"))

    def test_old_question_outside_recent_window_stays_blocked(self):
        old = "Arbeitest du heute?"
        free = {
            "asked": [_question_key(old)],
            "recent_questions": [f"Neue Frage {i}?" for i in range(8)],
            "conversation_facts": {},
        }
        self.assertNotIn(old, _not_recent(free, FALLBACKS["work"]))

    def test_twenty_five_selections_do_not_repeat_normalized_questions(self):
        free = {"asked": [], "conversation_facts": {}}
        seen = set()
        for _ in range(25):
            question = _generic_followup("work", free, support=1, independent=0, level="A1.1")
            key = _question_key(question)
            if question != "Erzähl mir noch etwas darüber.":
                self.assertNotIn(key, seen)
                seen.add(key)
                _remember_question(free, question)


if __name__ == "__main__":
    unittest.main()
