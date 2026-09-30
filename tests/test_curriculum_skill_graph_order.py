import unittest

from brain.logic.lesson_progress_router import handle_lesson_progress
from brain.memory.lesson_progress import (
    mark_section_completed,
    is_section_completed,
    get_next_incomplete_section,
    is_lesson_fully_completed,
)
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


def test_persistent_course_memory_does_not_activate_course_graph_in_free_mode():
    state = {
        "conversation_mode": "free",
        "student_progress": {"current_level": "A1", "current_lesson": 2},
        "learning_progress_v1": {"skills": {
            "course:a1:1:wir_begrüßen_uns": {"status": "mastered"},
        }},
    }
    curriculum = get_curriculum_state(state)
    assert curriculum["course_ready"] == []


def test_selected_lesson_is_course_routing_entry_point():
    state = {
        "conversation_mode": "course",
        "student_progress": {"current_level": "A1", "current_lesson": 2},
        "learning_progress_v1": {
            "version": 1,
            "skills": {
                "course:a1:2:woher_kommen_sie": {"status": "mastered"},
            },
        },
    }
    choice = choose_next_curriculum_skill(state)
    assert choice == {
        "skill": "course:a1:2:das_verb_kommen",
        "reason": "course_prerequisites_met",
    }



def test_shared_progress_boundary_rejects_course_completion_without_mastery():
    state = {
        "conversation_mode": "course",
        "learning_progress_v1": {"skills": {
            "course:a1:2:woher_kommen_sie": {"status": "practicing"},
        }},
        "lesson_progress": {"lessons": {
            "A1:2": {
                "level": "A1", "lesson": 2,
                "sections": ["Woher kommen Sie?", "Das Verb kommen"],
                "completed_sections": [],
                "current_section": "Woher kommen Sie?",
                "completed": False,
            },
        }},
    }
    assert mark_section_completed(state, "A1", 2, "Woher kommen Sie?") is False
    assert not is_section_completed(state, "A1", 2, "Woher kommen Sie?")
    assert get_next_incomplete_section(state, "A1", 2) == "Woher kommen Sie?"


def test_stale_legacy_completion_cannot_override_course_mastery():
    state = {
        "conversation_mode": "course",
        "learning_progress_v1": {"skills": {
            "course:a1:2:woher_kommen_sie": {"status": "practicing"},
        }},
        "lesson_progress": {"lessons": {
            "A1:2": {
                "level": "A1", "lesson": 2,
                "sections": ["Woher kommen Sie?"],
                "completed_sections": ["Woher kommen Sie?"],
                "current_section": None,
                "completed": True,
            },
        }},
    }
    assert not is_section_completed(state, "A1", 2, "Woher kommen Sie?")
    assert not is_lesson_fully_completed(state, "A1", 2)
    assert get_next_incomplete_section(state, "A1", 2) == "Woher kommen Sie?"


def test_mastery_authorizes_course_completion_and_advances_section():
    state = {
        "conversation_mode": "course",
        "learning_progress_v1": {"skills": {
            "course:a1:2:woher_kommen_sie": {"status": "mastered"},
        }},
        "lesson_progress": {"lessons": {
            "A1:2": {
                "level": "A1", "lesson": 2,
                "sections": ["Woher kommen Sie?", "Das Verb kommen"],
                "completed_sections": [],
                "current_section": "Woher kommen Sie?",
                "completed": False,
            },
        }},
    }
    assert mark_section_completed(state, "A1", 2, "Woher kommen Sie?") is True
    assert is_section_completed(state, "A1", 2, "Woher kommen Sie?")
    assert get_next_incomplete_section(state, "A1", 2) == "Das Verb kommen"
