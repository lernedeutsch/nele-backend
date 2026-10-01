import importlib

from brain.logic.generic_lesson_engine import evaluate_step_answer, render_text


def _origin_step():
    lesson2 = importlib.import_module("brain.responses.A1.2")
    return lesson2.LESSON_FLOW["sections"]["Woher kommen Sie?"]["steps"][0]


def test_personal_origin_task_uses_remembered_country_instead_of_hardcoded_poland():
    state = {
        "name": "Moni",
        "origin": "Italien",
        "user_facts": {"name": "Moni", "origin": "Italien"},
    }
    step = _origin_step()

    assert evaluate_step_answer("Ich komme aus Italien", step, state)["correct"] is True
    assert evaluate_step_answer("Italien", step, state)["correct"] is True
    assert evaluate_step_answer("Ich komme aus Polen", step, state)["correct"] is False
    assert render_text(step["correct_answer"], state) == "Ich komme aus Italien."\n    assert render_text(step["retry"], state) == "Fast. Sag den ganzen Satz: „Ich komme aus Italien.“ Sprich ihn bitte nach."


def test_personal_origin_template_preserves_inflected_article_from_memory():
    state = {
        "origin": "der Schweiz",
        "user_facts": {"origin": "der Schweiz"},
    }
    step = _origin_step()

    assert evaluate_step_answer("Ich komme aus der Schweiz", step, state)["correct"] is True
    assert render_text(step["correct_answer"], state) == "Ich komme aus der Schweiz."


def test_personal_origin_template_keeps_previous_poland_fallback_without_memory():
    step = _origin_step()
    state = {}

    assert evaluate_step_answer("Ich komme aus Polen", step, state)["correct"] is True
    assert render_text(step["correct_answer"], state) == "Ich komme aus Polen."
