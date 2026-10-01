from brain.logic.a1_lesson2_conversation import classify, evaluate_lesson2_answer, start, handle, NUMBERS

def task(kind, expected, **kw):
    d={"kind":kind,"expected":expected,"prompt":"test"}
    d.update(kw); return d

def test_origin_errors():
    cases = [
        ("Ich kommen aus Polen.","CONJUGATION_ERROR"),
        ("Ich kommst aus Polen.","CONJUGATION_ERROR"),
        ("Ich komme Polen.","PREPOSITION_ERROR"),
        ("Ich komme aus der Polen.","ARTICLE_ERROR"),
        ("Ich komme aus Schweiz.","ARTICLE_ERROR"),
        ("Ich komme aus der Schweiz.","CORRECT_FULL"),
        ("Ich komme aus USA.","ARTICLE_ERROR"),
        ("Ich komme aus den USA.","CORRECT_FULL"),
    ]
    for text, status in cases:
        expected = "Ich komme aus Polen." if "Polen" in text else ("Ich komme aus der Schweiz." if "Schweiz" in text else "Ich komme aus den USA.")
        assert classify(text,task("origin", expected))["status"] == status

def test_number_spelling():
    cases = [
        ("zwolf","CORRECT_WITH_TYPO"),("sechszehn","CORRECT_WITH_TYPO"),
        ("siebenzehn","CORRECT_WITH_TYPO"),("sechzehn","CORRECT_FULL"),("siebzehn","CORRECT_FULL")
    ]
    for text, status in cases:
        num=12 if "zw" in text else (16 if "sech" in text else 17)
        assert classify(text,task("number",NUMBERS[num],number=num))["status"] == status

def test_short_answer_is_not_error():
    assert classify("Polen",task("origin","Ich komme aus Polen."))["status"]=="CORRECT_SHORT"

def test_conjugation_error():
    assert classify("Er kommen aus Deutschland.",task("kommen","kommt",pronoun="er",form="kommt"))["status"]=="CONJUGATION_ERROR"

def test_delayed_review_is_scheduled():
    state={}
    start("Das Verb kommen",state)
    state["a1_l2_tutor"]["task"]=task("kommen","komme",pronoun="ich",form="komme",intent="PRACTICE_KOMMEN")
    reply=handle("kommen",state)
    assert "Fast richtig" in reply
    item=state["a1_l2_tutor"]["errors"]["CONJUGATION_ERROR"]
    assert item["review_due"] >= state["a1_l2_tutor"]["turn"]+3

def test_generator_changes_prompts():
    state={}
    first=start("Zahlen 1–20",state)
    prompts=[first]
    for _ in range(6):
        current=state["a1_l2_tutor"]["task"]
        prompts.append(handle(current["expected"],state))
    assert len(set(prompts)) >= 5


def test_full_sentence_is_accepted_for_gap_task():
    t=task("kommen","kommt",pronoun="er",form="kommt")
    assert classify("Thomas kommt aus Kroatien.",t)["status"]=="CORRECT_FULL"

def test_short_number_does_not_call_word_a_full_sentence():
    state={}
    start("Zahlen 1–20",state)
    state["a1_l2_tutor"]["task"]=task("number","neun",number=9,intent="NUMBER_PRODUCTION")
    reply=handle("9",state)
    assert "Als ganzer Satz" not in reply


def test_short_meaningful_answer_gets_speaking_turn_before_next_task():
    state={}
    start("Woher kommen Sie?",state)
    state["a1_l2_tutor"]["task"]=task(
        "origin","Ich komme aus Polen.",
        intent="ASK_USER_ORIGIN",prompt="Woher kommst du?"
    )
    reply=handle("Polen",state)
    assert "Ich komme aus Polen." in reply
    assert state["course_pending_speaking_model"]=="Ich komme aus Polen."
    assert "Sag es mal" in reply
    # The next task must not be introduced before the learner says the model.
    assert state["a1_l2_tutor"]["turn"]==0

    reply2=handle("Ich komme aus Polen.",state)
    assert "Sehr gut!" in reply2
    assert state.get("course_pending_speaking_model") is None
    assert state["a1_l2_tutor"]["turn"]==1


def test_unclear_answer_uses_progressive_scaffolding_not_immediate_solution():
    state={}
    start("Woher kommen Sie?",state)
    state["a1_l2_tutor"]["task"]=task(
        "origin","Ich komme aus Polen.",
        intent="ASK_USER_ORIGIN",prompt="Woher kommst du?"
    )
    first=handle("weiß nicht",state)
    assert "Ich komme aus Polen." not in first
    assert "Versuch" in first

    second=handle("keine Ahnung",state)
    assert "Fang so an" in second
    assert "Ich komme" in second


def test_short_answer_is_accepted_before_expansion():
    state={}
    start("Woher kommen Sie?",state)
    state["a1_l2_tutor"]["task"]=task(
        "origin","Ich komme aus Polen.",
        intent="ASK_USER_ORIGIN",prompt="Woher kommst du?"
    )
    reply=handle("Polen",state)
    assert reply.startswith("Genau.")
    assert "Fast" not in reply
    assert "Richtig ist" not in reply


def test_mixed_review_requires_number_word():
    t=task("number","neun",number=9,require_word=True,intent="MIXED_REVIEW")
    assert classify("9",t)["status"]=="NUMBER_WORD_REQUIRED"
    assert classify("neun",t)["status"]=="CORRECT_FULL"


def test_incomplete_gap_sentence_is_not_accepted():
    t=task(
        "kommen","kommt",pronoun="er",form="kommt",
        full_sentence_expected="Thomas kommt aus Österreich."
    )
    assert classify("Thomas kommt aus",t)["status"]=="INCOMPLETE_ANSWER"
    assert classify("Thomas kommt aus Österreich.",t)["status"]=="CORRECT_FULL"


def test_wrong_netherlands_article_is_detected():
    t=task("origin","Max kommt aus den Niederlanden.")
    assert classify("Max kommt aus der Niederlanden",t)["status"]=="ARTICLE_ERROR"


def test_wrong_recognized_country_is_not_accepted_as_short_origin_answer():
    t=task("origin","Ich komme aus Polen.",intent="ASK_USER_ORIGIN")
    assert classify("Deutschland",t)["status"]=="ORIGIN_MISMATCH"
    assert classify("aus Deutschland",t)["status"]=="ORIGIN_MISMATCH"


def test_wrong_country_in_person_origin_task_is_not_accepted():
    t=task("origin","Paul kommt aus Österreich.",intent="ASK_PERSON_ORIGIN")
    assert classify("Schweiz",t)["status"]=="ORIGIN_MISMATCH"
    assert classify("Österreich",t)["status"]=="CORRECT_SHORT"


def test_lesson2_answers_feed_shared_course_mastery():
    state={}
    start("Zahlen 1–20",state)
    for number in (3, 7, 12):
        state["a1_l2_tutor"]["task"]=task(
            "number", NUMBERS[number], number=number, intent="NUMBER_PRODUCTION"
        )
        handle(NUMBERS[number],state)
    skill=state["learning_progress_v1"]["skills"]["course:a1:2:zahlen_1–20"]
    assert skill["status"]=="mastered"
    assert skill["successes"]==3
    assert skill["requires_independent_confirmation"] is True
    assert skill["independent_confirmations"]==3


def test_lesson2_wrong_answer_reopens_mastered_course_skill():
    state={}
    start("Zahlen 1–20",state)
    for number in (3, 7, 12):
        state["a1_l2_tutor"]["task"]=task(
            "number", NUMBERS[number], number=number, intent="NUMBER_PRODUCTION"
        )
        handle(NUMBERS[number],state)
    state["a1_l2_tutor"]["task"]=task(
        "number", NUMBERS[9], number=9, intent="NUMBER_PRODUCTION"
    )
    handle("fünf",state)
    skill=state["learning_progress_v1"]["skills"]["course:a1:2:zahlen_1–20"]
    assert skill["status"]=="needs_review"


def test_lesson2_assisted_success_is_practice_not_independent_mastery_proof():
    state={}
    start("Das Verb kommen",state)
    state["a1_l2_tutor"]["task"]=task(
        "kommen","komme",pronoun="ich",form="komme",
        intent="PRACTICE_KOMMEN",prompt="Ich ___ aus Deutschland."
    )

    # A real error activates scaffolding for this task.
    handle("kommen",state)
    skill=state["learning_progress_v1"]["skills"]["course:a1:2:das_verb_kommen"]
    assert skill["not_yet"]==1
    assert skill["independent_confirmations"]==0
    assert skill["requires_independent_confirmation"] is True

    # Correcting the same assisted task is SUCCESS evidence, but it must not
    # count as independent mastery confirmation.
    handle("komme",state)
    skill=state["learning_progress_v1"]["skills"]["course:a1:2:das_verb_kommen"]
    assert skill["successes"]==1
    assert skill["independent_confirmations"]==0
    assert skill["status"]!="mastered"

    # The next generated task starts clean; a correct answer may now confirm
    # independent production.
    current=state["a1_l2_tutor"]["task"]
    handle(current["expected"],state)
    skill=state["learning_progress_v1"]["skills"]["course:a1:2:das_verb_kommen"]
    assert skill["independent_confirmations"]==1
    assert skill["status"]!="mastered"


def test_lesson2_typo_model_does_not_count_as_independent_confirmation():
    state={}
    start("Zahlen 1–20",state)
    state["a1_l2_tutor"]["task"]=task(
        "number","zwölf",number=12,intent="NUMBER_PRODUCTION"
    )
    handle("zwolf",state)
    skill=state["learning_progress_v1"]["skills"]["course:a1:2:zahlen_1–20"]
    assert skill["successes"]==1
    assert skill["independent_confirmations"]==0
    assert skill["status"]!="mastered"


def test_lesson2_shared_evaluator_accepts_natural_origin_variant():
    t=task("origin","Ich komme aus Polen.",intent="ASK_USER_ORIGIN")
    result=evaluate_lesson2_answer("aus Polen",t)
    assert result["kind"]=="correct"
    assert result["correct"]=="Ich komme aus Polen."


def test_lesson2_shared_evaluator_preserves_error_diagnosis():
    t=task("origin","Ich komme aus Polen.",intent="ASK_USER_ORIGIN")
    result=evaluate_lesson2_answer("Ich kommst aus Polen.",t)
    assert result["kind"]=="wrong"
    assert result["status"]=="CONJUGATION_ERROR"


def test_lesson2_wrong_answer_uses_shared_teacher_engine():
    state={}
    start("Das Verb kommen",state)
    state["a1_l2_tutor"]["task"]=task(
        "kommen","komme",pronoun="ich",form="komme",
        intent="PRACTICE_KOMMEN",prompt="Ich ___ aus Deutschland."
    )
    reply=handle("kommen",state)
    assert reply
    assert state["course_teacher_action"]["action"]=="correct_and_retry"
    assert state["course_teacher_action"]["reason"]=="answer_not_yet"
    assert state["a1_l2_tutor"]["turn"]==0
    skill=state["learning_progress_v1"]["skills"]["course:a1:2:das_verb_kommen"]
    assert skill["status"]=="needs_review"


def test_nationality_yes_no_question_accepts_natural_affirmative_answer():
    t=task(
        "nationality",
        "Polin",
        country="polen",
        intent="COUNTRY_TO_NATIONALITY",
        prompt="Anna kommt aus Polen. Ist Anna Polin?",
    )
    for answer in ("ja", "Ja, genau.", "richtig"):
        result=evaluate_lesson2_answer(answer,t)
        assert result["kind"]=="correct"
        assert result["status"]=="CORRECT_SHORT"


def test_nationality_production_task_does_not_accept_bare_yes():
    t=task(
        "nationality",
        "Polin",
        country="polen",
        intent="NATIONALITY_PRODUCTION",
        prompt="Welche Nationalität hat Anna?",
    )
    result=evaluate_lesson2_answer("ja",t)
    assert result["kind"]=="wrong"
