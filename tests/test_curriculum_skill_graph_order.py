import unittest

from brain.logic.lesson_progress_router import handle_lesson_progress
from brain.logic.curriculum_skill_graph import (
    choose_next_curriculum_skill,
    get_curriculum_state,
)


class CurriculumSkillGraphOrderTests(unittest.TestCase):
    def test_ready_skills_follow_graph_order_not_alphabetical_order(self):
        state = {"conversation_mode": "course", "learning_progress_v1": {"skills": {
            "conversation:supported_answer": {"status": "mastered"},
        }}}

        self.assertEqual(
            choose_next_curriculum_skill(state),
            {
                "skill": "conversation:full_sentence",
                "reason": "prerequisites_met",
            },
        )

    def test_review_priority_also_follows_graph_order(self):
        state = {"conversation_mode": "course", "learning_progress_v1": {"skills": {
            "conversation:supported_answer": {"status": "mastered"},
            "conversation:full_sentence": {"status": "needs_review"},
            "conversation:continue_after_correction": {"status": "needs_review"},
        }}}

        self.assertEqual(
            choose_next_curriculum_skill(state),
            {
                "skill": "conversation:full_sentence",
                "reason": "curriculum_review",
            },
        )


    def test_active_course_mastery_is_routed_before_unrelated_generic_skill(self):
        state = {"conversation_mode": "course", "learning_progress_v1": {"skills": {
            "course:a1:2:zahlen_1–20": {"status": "improving"},
        }}}
        self.assertEqual(
            choose_next_curriculum_skill(state),
            {"skill": "course:a1:2:zahlen_1–20", "reason": "course_mastery_in_progress"},
        )

    def test_course_review_has_priority_in_course_mode(self):
        state = {"conversation_mode": "course", "learning_progress_v1": {"skills": {
            "course:a1:2:zahlen_1–20": {"status": "needs_review"},
            "conversation:supported_answer": {"status": "needs_review"},
        }}}
        self.assertEqual(
            choose_next_curriculum_skill(state),
            {"skill": "course:a1:2:zahlen_1–20", "reason": "course_review"},
        )


if __name__ == "__main__":
    unittest.main()


def test_manual_fertig_cannot_bypass_course_mastery():
    state = {
        "conversation_mode": "course",
        "student_progress": {"current_level": "A1", "current_lesson": 2},
        "learning_progress_v1": {"skills": {
            "course:a1:2:woher_kommen_sie": {"status": "practicing"},
        }},
    }
    reply = handle_lesson_progress("Teil 1 ist fertig.", state)
    assert "noch nicht als gelernt bestätigt" in reply
    assert "completed_sections" not in str(state)


def test_manual_fertig_is_allowed_after_real_course_mastery():
    state = {
        "conversation_mode": "course",
        "student_progress": {"current_level": "A1", "current_lesson": 2},
        "learning_progress_v1": {"skills": {
            "course:a1:2:woher_kommen_sie": {"status": "mastered"},
        }},
    }
    reply = handle_lesson_progress("Teil 1 ist fertig.", state)
    assert "noch nicht als gelernt bestätigt" not in reply
    assert "abgeschlossen" in reply


def test_course_graph_follows_real_a1_section_order():
    state = {
        "conversation_mode": "course",
        "student_progress": {"current_level": "A1", "current_lesson": 1},
        "learning_progress_v1": {"skills": {
            "course:a1:1:wir_begrüßen_uns": {"status": "mastered"},
        }},
    }
    assert choose_next_curriculum_skill(state) == {
        "skill": "course:a1:1:ich_stelle_mich_vor",
        "reason": "course_prerequisites_met",
    }


def test_course_graph_blocks_later_skill_until_prerequisite_is_mastered():
    state = {
        "conversation_mode": "course",
        "student_progress": {"current_level": "A1", "current_lesson": 2},
        "learning_progress_v1": {"skills": {
            "course:a1:2:das_verb_kommen": {"status": "mastered"},
        }},
    }
    curriculum = get_curriculum_state(state)
    assert "course:a1:2:zahlen_1–20" in curriculum["course_blocked"]
    assert choose_next_curriculum_skill(state)["skill"] != "course:a1:2:zahlen_1–20"


def test_course_review_uses_curriculum_order_not_alphabetical_order():
    state = {"conversation_mode": "course", "learning_progress_v1": {"skills": {
        "course:a1:1:das_deutsche_alphabet": {"status": "needs_review"},
        "course:a1:1:ich_stelle_mich_vor": {"status": "needs_review"},
    }}}
    assert choose_next_curriculum_skill(state) == {
        "skill": "course:a1:1:ich_stelle_mich_vor",
        "reason": "course_review",
    }


def test_course_in_progress_uses_curriculum_order_not_alphabetical_order():
    state = {"conversation_mode": "course", "learning_progress_v1": {"skills": {
        "course:a1:2:zahlen_1–20": {"status": "practicing"},
        "course:a1:2:das_verb_kommen": {"status": "practicing"},
    }}}
    assert choose_next_curriculum_skill(state) == {
        "skill": "course:a1:2:das_verb_kommen",
        "reason": "course_mastery_in_progress",
    }
