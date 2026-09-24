"""Response Understanding Engine v1.

Interprets short/noisy beginner responses using the actual conversation
question. It never replaces the learner's original text for Error Engine.
"""

import re

ENGINE_VERSION = 1

YES = {"ja", "ja gern", "ja, gern", "klar", "genau", "jap"}
NO = {"nein", "nein danke", "nein, danke", "nee"}
WEATHER_NOISE = {"sonn8g": "sonnig", "sonnlg": "sonnig", "sonig": "sonnig"}

def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip(" ?!.")

def _intent_from_question(question):
    q = _norm(question)
    if q.startswith(("wann ", "bis wann ")):
        return "time"
    if q.startswith(("wo ", "woher ")):
        return "place"
    if q.startswith(("was ", "welche ", "welchen ")):
        return "content"
    if q.startswith(("arbeitest ", "bist ", "hast ", "hörst ", "hoerst ", "machst ",
                     "fährst ", "faehrst ", "schwimmst ", "spielst ", "kochst ",
                     "magst ", "ist ", "gehst ")):
        return "yes_no"
    return "open"

def understand_response(text, *, conversation_state=None):
    conversation_state = conversation_state or {}
    raw = str(text or "").strip()
    low = _norm(raw)
    question = conversation_state.get("last_question") or ""
    expected = conversation_state.get("expected_answer") or _intent_from_question(question)
    topic = conversation_state.get("topic")
    subtopic = conversation_state.get("subtopic")

    result = {
        "version": ENGINE_VERSION,
        "original": raw,
        "normalized": low,
        "understood": bool(low),
        "confidence": "low" if not low else "medium",
        "intent": expected or "open",
        "meaning": None,
        "canonical": None,
        "topic": topic,
        "subtopic": subtopic,
        "preserve_for_error_engine": raw,
    }

    if low in YES:
        result.update(confidence="high", intent="yes_no", meaning="yes", canonical="ja")
        return result
    if low in NO:
        result.update(confidence="high", intent="yes_no", meaning="no", canonical="nein")
        return result

    if low in WEATHER_NOISE:
        result.update(confidence="high", intent="weather", meaning="sunny", canonical=WEATHER_NOISE[low])
        return result

    # Beginner time answers: "8", "bis 2", "um 8".
    if re.fullmatch(r"\d{1,2}(?::\d{2})?", low):
        result.update(confidence="high", intent="time", meaning="time", canonical=low)
        return result
    if re.fullmatch(r"(?:bis|um)\s+\d{1,2}(?::\d{2})?(?:\s*uhr)?", low):
        result.update(confidence="high", intent="time", meaning="time", canonical=low)
        return result

    # One-word content is valid evidence of understanding at A1.
    if len(re.findall(r"[A-Za-zÄÖÜäöüß0-9-]+", low)) == 1:
        result.update(
            confidence="high" if expected in {"open", "place", "time"} else "medium",
            intent="short_content",
            meaning=low,
            canonical=low,
        )
        return result

    if low:
        result.update(confidence="high", meaning=low, canonical=low)
    return result
