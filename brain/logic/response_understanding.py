"""Response Understanding Engine v2.

Context-aware interpretation of short/noisy beginner and ASR responses.
Candidate correction is constrained by the active question/topic/vocabulary.
The learner's original text always remains available to Error Engine.
"""

import re
from difflib import SequenceMatcher

from brain.logic.learner_turn import analyze_learner_turn

ENGINE_VERSION = 2

YES = {"ja", "ja gern", "ja, gern", "klar", "genau", "jap", "yah", "ya"}
NO = {"nein", "nein danke", "nein, danke", "nee", "nai", "neyn"}

ASR_NORMALIZATION = {
    "sonn8g": "sonnig", "sonnlg": "sonnig", "sonig": "sonnig",
    "arbait": "arbeit", "arbyte": "arbeit",
    "kochn": "kochen", "koch'n": "kochen",
    "shwimmen": "schwimmen", "schwimen": "schwimmen",
    "fraitzeit": "freizeit",
}

TOPIC_CANDIDATES = {
    "weather": {"sonnig", "warm", "kalt", "windig", "regen", "schnee", "bewölkt"},
    "work": {"arbeit", "arbeiten", "kochen", "pause", "hotel", "kollege"},
    "hobby": {"lesen", "musik", "sport", "radfahren", "schwimmen", "spazieren"},
    "food": {"pizza", "suppe", "nudeln", "brot", "wasser", "kaffee", "tee", "kochen"},
    "holiday": {"urlaub", "meer", "berge", "reisen"},
    "shopping": {"einkaufen", "schuhe", "sportschuhe"},
}

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

def _candidate_words(topic, subtopic, vocabulary_context):
    words = set(TOPIC_CANDIDATES.get(str(topic or ""), set()))
    if subtopic == "kochen":
        words.update(TOPIC_CANDIDATES["food"])
    for item in (vocabulary_context or {}).get("suggestion_words", []) or []:
        value = _norm(item)
        if value and " " not in value:
            words.add(value)
    return words

def _contextual_asr_match(low, candidates):
    if not low or " " in low or len(low) < 4:
        return None
    if low in ASR_NORMALIZATION:
        canonical = ASR_NORMALIZATION[low]
        if not candidates or canonical in candidates:
            return canonical, 1.0, "known_asr_variant"
    scored = []
    for candidate in candidates:
        ratio = SequenceMatcher(None, low, candidate).ratio()
        if ratio >= 0.82:
            scored.append((ratio, candidate))
    scored.sort(reverse=True)
    if not scored:
        return None
    best_ratio, best = scored[0]
    # Avoid guessing when two context words are almost equally plausible.
    if len(scored) > 1 and best_ratio - scored[1][0] < 0.08:
        return None
    return best, best_ratio, "context_similarity"

def understand_response(text, *, conversation_state=None, vocabulary_context=None):
    conversation_state = conversation_state or {}
    raw = str(text or "").strip()
    low = _norm(raw)
    question = conversation_state.get("last_question") or ""
    expected = conversation_state.get("expected_answer") or _intent_from_question(question)
    topic = conversation_state.get("topic")
    subtopic = conversation_state.get("subtopic")
    candidates = _candidate_words(topic, subtopic, vocabulary_context)

    turn = analyze_learner_turn(raw, last_question=question)

    result = {
        "version": ENGINE_VERSION,
        "turn_intent": turn["intent"],
        "slot": turn["slot"],
        "content": turn["content"],
        "original": raw,
        "normalized": low,
        "understood": bool(low),
        "confidence": "low" if not low else "medium",
        "intent": expected or "open",
        "meaning": None,
        "canonical": None,
        "topic": topic,
        "subtopic": subtopic,
        "asr_tolerant": False,
        "asr_strategy": None,
        "similarity": None,
        "preserve_for_error_engine": raw,
    }

    if low in YES:
        result.update(confidence="high", intent="yes_no", meaning="yes", canonical="ja")
        return result
    if low in NO:
        result.update(confidence="high", intent="yes_no", meaning="no", canonical="nein")
        return result

    if re.fullmatch(r"\d{1,2}(?::\d{2})?", low):
        result.update(confidence="high", intent="time", meaning="time", canonical=low)
        return result
    if re.fullmatch(r"(?:bis|um)\s+\d{1,2}(?::\d{2})?(?:\s*uhr)?", low):
        result.update(confidence="high", intent="time", meaning="time", canonical=low)
        return result

    words = re.findall(r"[A-Za-zÄÖÜäöüß0-9'-]+", low)
    if len(words) == 1:
        match = _contextual_asr_match(low, candidates)
        if match:
            canonical, similarity, strategy = match
            result.update(
                confidence="high" if similarity >= 0.9 else "medium",
                intent="short_content",
                meaning=canonical,
                canonical=canonical,
                asr_tolerant=True,
                asr_strategy=strategy,
                similarity=round(similarity, 3),
            )
            return result
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
