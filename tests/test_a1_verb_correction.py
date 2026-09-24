from brain.logic.a1_verb_correction import find_a1_verb_correction
from brain.logic.learner_feedback import prepare_message_with_feedback


def test_ich_fahren():
    result = find_a1_verb_correction("Ich fahren Fahrrad")
    assert result["corrected_message"] == "Ich fahre Fahrrad."


def test_du_fahren_irregular():
    result = find_a1_verb_correction("Du fahren Fahrrad")
    assert result["corrected_message"] == "Du fährst Fahrrad."


def test_du_essen_irregular():
    result = find_a1_verb_correction("Du essen Pizza")
    assert result["corrected_message"] == "Du isst Pizza."


def test_du_sprechen_irregular():
    result = find_a1_verb_correction("Du sprechen Deutsch")
    assert result["corrected_message"] == "Du sprichst Deutsch."


def test_sein_and_haben():
    assert find_a1_verb_correction("Ich sein müde")["corrected_message"] == "Ich bin müde."
    assert find_a1_verb_correction("Du haben Zeit")["corrected_message"] == "Du hast Zeit."


def test_correct_form_is_untouched():
    assert find_a1_verb_correction("Ich fahre Fahrrad") is None
    assert find_a1_verb_correction("Du sprichst Deutsch") is None


def test_unknown_verb_is_untouched():
    assert find_a1_verb_correction("Ich fotografieren gern") is None


def test_automatic_correction_reaches_student_memory():
    state = {}

    corrected, feedback = prepare_message_with_feedback(
        "Du essen Pizza",
        state,
    )

    assert corrected == "Du isst Pizza."
    assert "Du isst Pizza" in feedback
    assert state.get("error_memory")
