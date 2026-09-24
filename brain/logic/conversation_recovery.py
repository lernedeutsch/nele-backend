"""Conversation Recovery Engine v1.

Uses Quality Controller diagnostics to recover only high-confidence broken
normal conversation turns. Pedagogical correction/repetition/model actions are
never replaced. Recovery is deterministic and A1-safe.
"""

ENGINE_VERSION = 1

SAFE_TOPIC_QUESTIONS = {
    "work": "Was machst du bei der Arbeit?",
    "hobby": "Was machst du gern in deiner Freizeit?",
    "weather": "Wie ist das Wetter bei dir?",
    "holiday": "Was machst du gern im Urlaub?",
    "shopping": "Was möchtest du kaufen?",
    "yesterday": "Was hast du gestern gemacht?",
    "today": "Was machst du heute?",
    "place": "Wo bist du jetzt?",
}

def _meaning(response_understanding):
    data = response_understanding or {}
    return str(data.get("canonical") or data.get("meaning") or "").strip()

def _content_recovery(meaning, topic):
    low = meaning.lower()
    if not meaning or low in {"ja", "nein", "yes", "no"}:
        return None
    if topic == "work":
        if low in {"pizza", "suppe", "nudeln", "brot"}:
            return f"Ah, {meaning.capitalize()}. Kochst du das bei der Arbeit?"
        if low in {"kochen", "arbeit", "arbeiten"}:
            return "Du arbeitest heute. Was machst du bei der Arbeit?"
    if topic == "hobby":
        return f"Ah, {meaning}. Machst du das oft?"
    if topic == "weather":
        return f"Ah, {meaning}. Ist es warm oder kalt?"
    if topic == "shopping":
        return f"Ah, {meaning}. Welche Farbe möchtest du?"
    return None

def recover_reply(reply, quality, *, topic=None, action=None,
                  response_understanding=None, safe_question=None):
    issues = set((quality or {}).get("issues") or [])
    original = str(reply or "").strip()

    result = {
        "version": ENGINE_VERSION,
        "original": original,
        "reply": original,
        "recovered": False,
        "strategy": None,
        "trigger_issues": sorted(issues),
        "topic": topic,
        "action": action,
    }

    # Never override pedagogy or an already deterministic QC repair.
    if action not in {"CONTINUE", "ADVANCE"} or (quality or {}).get("changed"):
        return result

    recoverable = {"topic_alignment_warning", "response_alignment_warning"}
    if not issues.intersection(recoverable):
        return result

    meaning = _meaning(response_understanding)
    contextual = _content_recovery(meaning, topic)
    if contextual:
        result.update(reply=contextual, recovered=True, strategy="learner_meaning")
        return result

    fallback = safe_question or SAFE_TOPIC_QUESTIONS.get(topic)
    if fallback:
        result.update(reply=fallback, recovered=True, strategy="safe_topic_question")
    return result
