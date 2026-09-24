"""Conversation Quality Controller v2.

Final deterministic guard before a free-conversation reply is returned.
Repairs only high-confidence defects. Context, A1 complexity, topic drift and
memory contradictions are diagnostics unless a safe replacement is known.
"""

import re

CONTROLLER_VERSION = 2

KNOWN_BAD = {
    "ich arbeite kochen.": "Ich koche bei der Arbeit.",
    "ich arbeite kochen": "Ich koche bei der Arbeit.",
}

TOPIC_TERMS = {
    "work": {"arbeit", "arbeitest", "arbeiten", "hotel", "koch", "kochst", "pause", "fängst", "faengst"},
    "hobby": {"hobby", "freizeit", "musik", "sport", "rad", "schwimm", "lesen"},
    "weather": {"wetter", "warm", "kalt", "sonn", "regen", "wind", "schnee"},
    "holiday": {"urlaub", "ferien", "reise", "meer", "berge"},
    "shopping": {"kauf", "einkauf", "schuhe", "farbe"},
    "yesterday": {"gestern"},
}

def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip()

def _sentences(text):
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", str(text or "").strip()) if part.strip()]

def _dedupe_adjacent(text):
    parts = _sentences(text)
    if len(parts) < 2:
        return str(text or "").strip(), False
    kept, changed = [], False
    for part in parts:
        if kept and _norm(part) == _norm(kept[-1]):
            changed = True
            continue
        kept.append(part)
    return " ".join(kept), changed

def _a1_complexity(text):
    words = re.findall(r"[A-Za-zÄÖÜäöüß0-9'-]+", str(text or ""))
    sentences = _sentences(text)
    max_sentence_words = max(
        (len(re.findall(r"[A-Za-zÄÖÜäöüß0-9'-]+", s)) for s in sentences),
        default=0,
    )
    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "max_sentence_words": max_sentence_words,
        "warning": len(words) > 32 or max_sentence_words > 18,
    }

def _topic_alignment(text, topic):
    terms = TOPIC_TERMS.get(str(topic or ""), set())
    if not terms:
        return None
    low = _norm(text)
    return any(term in low for term in terms)

def _response_alignment(reply, user_message, response_understanding):
    meaning = _norm((response_understanding or {}).get("canonical") or (response_understanding or {}).get("meaning"))
    user = _norm(user_message)
    low = _norm(reply)
    if not meaning and not user:
        return None
    tokens = {t for t in re.findall(r"[a-zäöüß0-9'-]+", meaning or user) if len(t) >= 3}
    if not tokens:
        return None
    return any(token in low for token in tokens)

def _memory_contradictions(reply, personalization_facts):
    low = _norm(reply)
    contradictions = []
    facts = personalization_facts or {}
    # v2 only flags explicit negation of a confirmed remembered preference/fact.
    for key in ("activity", "music_genre", "shopping_item", "color", "place"):
        record = facts.get(key) or {}
        value = _norm(record.get("value"))
        if not value or int(record.get("confirmations", 0) or 0) < 2:
            continue
        if value in low and re.search(r"\b(?:nicht|kein|keine)\b", low):
            contradictions.append(key)
    return contradictions

def check_reply(reply, *, topic=None, action=None, model=None, user_message=None,
                response_understanding=None, personalization_facts=None):
    original = str(reply or "").strip()
    fixed = original
    issues = []
    changed = False

    bad = KNOWN_BAD.get(_norm(fixed))
    if bad:
        fixed = bad
        issues.append("known_invalid_construction")
        changed = True

    deduped, did_dedupe = _dedupe_adjacent(fixed)
    if did_dedupe:
        fixed = deduped
        issues.append("adjacent_duplicate")
        changed = True

    complexity = _a1_complexity(fixed)
    if complexity["warning"]:
        issues.append("a1_complexity_warning")

    topic_alignment = _topic_alignment(fixed, topic)
    if topic_alignment is False and action in {"CONTINUE", "ADVANCE"}:
        issues.append("topic_alignment_warning")

    response_alignment = _response_alignment(fixed, user_message, response_understanding)
    if response_alignment is False and action in {"CONTINUE", "ADVANCE"}:
        issues.append("response_alignment_warning")

    contradictions = _memory_contradictions(fixed, personalization_facts)
    if contradictions:
        issues.append("memory_contradiction_warning")

    return {
        "version": CONTROLLER_VERSION,
        "original": original,
        "reply": fixed,
        "changed": changed,
        "issues": issues,
        "topic": topic,
        "action": action,
        "model": model,
        "a1_length_warning": complexity["warning"],
        "a1_complexity": complexity,
        "topic_alignment": topic_alignment,
        "response_alignment": response_alignment,
        "memory_contradictions": contradictions,
        "passed": not issues,
    }
