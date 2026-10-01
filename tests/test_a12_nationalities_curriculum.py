import importlib

from brain.logic.curriculum_skill_graph import A1_COURSE_SKILL_GRAPH, get_prerequisites


def test_a12_curriculum_keeps_nationalities_between_origin_and_kommen():
    origin = "course:a1:2:woher_kommen_sie"
    nationalities = "course:a1:2:lander_und_nationalitaten"
    kommen = "course:a1:2:das_verb_kommen"

    # Use graph metadata rather than spelling assumptions for the umlauted key.
    nationality_skill = next(
        key for key, item in A1_COURSE_SKILL_GRAPH.items()
        if item.get("lesson") == 2 and item.get("section") == "Länder und Nationalitäten"
    )
    assert nationality_skill
    assert get_prerequisites(nationality_skill) == [origin]
    assert get_prerequisites(kommen) == [nationality_skill]


def test_a12_nationalities_section_has_real_teaching_steps():
    lesson2 = importlib.import_module("brain.responses.A1.2")
    section = lesson2.LESSON_FLOW["sections"]["Länder und Nationalitäten"]
    assert len(section["steps"]) >= 3
    assert section["steps"][0]["correct_answer"] == "Anna ist Polin."
