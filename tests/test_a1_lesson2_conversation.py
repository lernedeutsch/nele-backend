import pytest
from brain.logic.a1_lesson2_conversation import classify, start, handle, NUMBERS

def task(kind, expected, **kw):
    d={"kind":kind,"expected":expected,"prompt":"test"}
    d.update(kw); return d

@pytest.mark.parametrize("text,status",[
 ("Ich kommen aus Polen.","CONJUGATION_ERROR"),
 ("Ich kommst aus Polen.","CONJUGATION_ERROR"),
 ("Ich komme Polen.","PREPOSITION_ERROR"),
 ("Ich komme aus der Polen.","ARTICLE_ERROR"),
 ("Ich komme aus Schweiz.","ARTICLE_ERROR"),
 ("Ich komme aus der Schweiz.","CORRECT_FULL"),
 ("Ich komme aus USA.","ARTICLE_ERROR"),
 ("Ich komme aus den USA.","CORRECT_FULL"),
])
def test_origin_errors(text,status):
    assert classify(text,task("origin","Ich komme aus Polen." if "Polen" in text else ("Ich komme aus der Schweiz." if "Schweiz" in text else "Ich komme aus den USA.")))["status"]==status

@pytest.mark.parametrize("text,status",[
 ("zwolf","CORRECT_WITH_TYPO"),("sechszehn","CORRECT_WITH_TYPO"),
 ("siebenzehn","CORRECT_WITH_TYPO"),("sechzehn","CORRECT_FULL"),("siebzehn","CORRECT_FULL")
])
def test_number_spelling(text,status):
    num=12 if "zw" in text else (16 if "sech" in text else 17)
    assert classify(text,task("number",NUMBERS[num],number=num))["status"]==status

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
