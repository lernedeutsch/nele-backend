import unittest

from brain.logic.new_learning_resume import handle_new_learning_resume
from brain.memory.next_learning_step import get_next_new_learning_step


class CourseHandoffRegressionTests(unittest.TestCase):
    def test_unrelated_reply_keeps_pending_course_section_active(self):
        state = {
            "conversation_mode": "course",
            "pending_new_learning": {
                "type": "new_section",
                "level": "A1",
                "lesson": 2,
                "section": "Länder und Nationalitäten",
                "topic": "Länder und Nationalitäten",
            },
            "last_question": "continue_new_learning",
        }

        reply = handle_new_learning_resume("Ich komme aus Italien", state)

        self.assertIn("Länder und Nationalitäten", reply)
        self.assertIn("ja", reply)
        self.assertIn("nein", reply)
        self.assertIsNotNone(state["pending_new_learning"])
        self.assertEqual(state["last_question"], "continue_new_learning")


if __name__ == "__main__":
    unittest.main()


def _course_state(lesson, statuses):
    return {
        "conversation_mode": "course",
        "student_progress": {"current_level": "A1", "current_lesson": lesson},
        "learning_progress_v1": {"skills": {
            skill: {"status": status} for skill, status in statuses.items()
        }},
    }


def test_lesson_one_cannot_offer_lesson_two_until_every_section_is_mastered():
    state = _course_state(1, {
        "course:a1:1:wir_begrüßen_uns": "mastered",
        "course:a1:1:ich_stelle_mich_vor": "mastered",
        "course:a1:1:das_deutsche_alphabet": "practicing",
    })
    plan = get_next_new_learning_step(state)
    assert plan["type"] == "new_section"
    assert plan["lesson"] == 1
    assert plan["section"] == "Das deutsche Alphabet"


def test_lesson_one_mastery_offers_real_lesson_two_first_section():
    state = _course_state(1, {
        "course:a1:1:wir_begrüßen_uns": "mastered",
        "course:a1:1:ich_stelle_mich_vor": "mastered",
        "course:a1:1:das_deutsche_alphabet": "mastered",
    })
    plan = get_next_new_learning_step(state)
    assert plan["type"] == "new_lesson"
    assert plan["lesson"] == 2
    assert plan["section"] == "Woher kommen Sie?"


def test_lesson_two_cannot_finish_while_last_section_is_not_mastered():
    state = _course_state(2, {
        "course:a1:2:woher_kommen_sie": "mastered",
        "course:a1:2:länder_und_nationalitäten": "mastered",
        "course:a1:2:das_verb_kommen": "mastered",
        "course:a1:2:zahlen_1–20": "practicing",
    })
    plan = get_next_new_learning_step(state)
    assert plan["type"] == "new_section"
    assert plan["lesson"] == 2
    assert plan["section"] == "Zahlen 1–20"


def test_lesson_two_mastery_offers_real_lesson_three_first_section():
    state = _course_state(2, {
        "course:a1:2:woher_kommen_sie": "mastered",
        "course:a1:2:länder_und_nationalitäten": "mastered",
        "course:a1:2:das_verb_kommen": "mastered",
        "course:a1:2:zahlen_1–20": "mastered",
    })
    plan = get_next_new_learning_step(state)
    assert plan["type"] == "new_lesson"
    assert plan["lesson"] == 3
    assert plan["section"] == "Wie alt sind Sie?"


def test_lesson_three_reopen_keeps_first_unmastered_section():
    state = _course_state(3, {
        "course:a1:3:wie_alt_sind_sie": "mastered",
        "course:a1:3:zahlen_11–100": "mastered",
        "course:a1:3:das_verb_sein": "practicing",
    })
    plan = get_next_new_learning_step(state)
    assert plan["type"] == "new_section"
    assert plan["lesson"] == 3
    assert plan["section"] == "Das Verb sein"


def test_repeated_unrelated_replies_do_not_loop_forever_at_course_handoff():
    state = {
        "conversation_mode": "course",
        "pending_new_learning": {
            "type": "new_section",
            "level": "A1",
            "lesson": 3,
            "section": "Zahlen 11–100",
            "topic": "Zahlen 11–100",
        },
        "last_question": "continue_new_learning",
    }

    first = handle_new_learning_resume("xyz", state)
    assert "Sag einfach „ja“ oder „nein“" in first
    assert state["pending_new_learning"] is not None
    assert state["new_learning_invalid_attempts"] == 1

    second = handle_new_learning_resume("xyz", state)
    assert "Sag die Zahlen 11 bis 15 auf Deutsch." in second
    assert state["pending_new_learning"] is None
    assert state["last_question"] is None
    assert state["new_learning_invalid_attempts"] == 0
