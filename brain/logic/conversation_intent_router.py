"""Shared intent routing for Nele conversation modes.

This module does not generate replies. It only decides what kind of learner
turn arrived so existing engines can run in the right order.
"""
import re
from brain.logic.wellbeing_feedback import analyze_wellbeing_response

QUESTION_STARTS = (
    "was ", "wie ", "wo ", "woher ", "wohin ", "wann ", "warum ", "wer ",
    "welcher ", "welche ", "welches ", "arbeitest ", "wohnst ", "isst ",
    "trinkst ", "magst ", "machst ", "hast ", "bist ", "kommst ", "kannst ",
    "kochst ", "gehst ", "fährst ", "faehrst ", "hörst ", "hoerst ",
)

def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip(" .?!")

def classify_conversation_intent(message, *, last_question="", dialogue_active=False):
    raw = str(message or "").strip()
    low = _norm(raw)
    wellbeing = analyze_wellbeing_response(raw)
    last = _norm(last_question)
    wellbeing_context = any(x in last for x in (
        "wie geht es dir", "wie geht's dir", "wie geht es ihnen", "wie geht's ihnen"
    ))
    explicit_wellbeing = wellbeing.get("type") in {"stressed", "sad", "sick"} or bool(wellbeing.get("feedback"))
    if wellbeing.get("recognized") and (wellbeing_context or explicit_wellbeing):
        return {"intent": "wellbeing", "wellbeing": wellbeing}

    learner_question = low.startswith(QUESTION_STARTS)
    if learner_question:
        return {"intent": "learner_question", "wellbeing": wellbeing}

    # An active scripted dialogue only owns the turn when its prompt is also
    # the question the learner is currently answering. Free-conversation
    # questions must not leave a hidden dialogue state that later captures
    # short answers such as "Pizza" or "Zimmer".
    if dialogue_active and last_question:
        return {"intent": "dialogue_answer", "wellbeing": wellbeing}

    if last_question:
        return {"intent": "contextual_answer", "wellbeing": wellbeing}

    return {"intent": "open_statement", "wellbeing": wellbeing}
