from brain.logic.free_conversation import _short_answer_followup


def test_bis_two_answers_work_time_question():
    memory = {}
    reply = _short_answer_followup(
        "Bis 2",
        "Bis wann arbeitest du heute?",
        memory,
    )
    assert "Ich arbeite bis 2 Uhr" in reply
    assert memory["work_until"] == "2"


def test_kochen_answers_work_activity_question():
    memory = {}
    reply = _short_answer_followup(
        "Kochen",
        "Was machst du bei der Arbeit?",
        memory,
    )
    assert "Ich koche." in reply
    assert "Ich arbeite Kochen" not in reply


def test_pizza_answers_food_question():
    memory = {}
    reply = _short_answer_followup(
        "Pizza",
        "Was isst du gern?",
        memory,
    )
    assert "Pizza" in reply
    assert memory["food"] == "Pizza"


def test_company_answer_stays_in_activity_context():
    memory = {}
    reply = _short_answer_followup(
        "Mit meinem Mann",
        "Machst du das lieber allein oder mit jemandem?",
        memory,
    )
    assert "zusammen" in reply
    assert memory["activity_company"] == "Mit meinem Mann"


def test_short_answer_without_matching_question_is_not_guessed():
    assert _short_answer_followup("Pizza", "Wie ist das Wetter?", {}) is None
