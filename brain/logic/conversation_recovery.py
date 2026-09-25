"""Conversation Recovery Engine v2.

Classifies why a free conversation needs recovery before choosing a response:
learner did not understand, Nele is uncertain, answer mismatch, or explicit
learner topic change. Pedagogical correction/repetition/model actions remain
authoritative and are never replaced.
"""

ENGINE_VERSION = 2

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

STRUGGLE_PHRASES = {
    "ich verstehe nicht", "verstehe nicht", "ich weiß nicht", "ich weiss nicht",
    "keine ahnung", "was", "wie bitte", "bitte",
}

def _meaning(response_understanding):
    data = response_understanding or {}
    return str(data.get("canonical") or data.get("meaning") or "").strip()

def _norm(value):
    return " ".join(str(value or "").strip().lower().split()).strip(" ?!.")

def classify_recovery(quality, *, user_message=None, response_understanding=None,
                      explicit_topic=None, current_topic=None):
    issues = set((quality or {}).get("issues") or [])
    understood = response_understanding or {}
    low = _norm(user_message)

    if explicit_topic and explicit_topic != current_topic:
        return "learner_topic_change"
    if low in STRUGGLE_PHRASES or any(p in low for p in ("verstehe nicht", "weiß nicht", "weiss nicht")):
        return "learner_did_not_understand"
    if understood.get("understood") is False or understood.get("confidence") == "low":
        return "nele_uncertain"
    # A short, meaningful beginner answer must not be treated as a
    # conversation failure merely because the generated reply does not repeat
    # the learner's exact word. Response alignment is a lexical diagnostic,
    # while Response Understanding is the authoritative semantic signal.
    #
    # Examples: "gut", "müde", "Pizza", "Polen", "8 Uhr", "ja", "nein".
    # If these are understood with medium/high confidence, Recovery must not
    # override a valid conversational continuation.
    meaning = _meaning(understood)
    confident_meaning = (
        bool(meaning)
        and understood.get("understood") is not False
        and understood.get("confidence") in {"medium", "high"}
    )
    if "topic_alignment_warning" in issues:
        return "topic_drift"
    if "response_alignment_warning" in issues:
        if confident_meaning:
            return None
        return "answer_mismatch"
    return None

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
                  response_understanding=None, safe_question=None,
                  user_message=None, explicit_topic=None):
    issues = set((quality or {}).get("issues") or [])
    original = str(reply or "").strip()
    reason = classify_recovery(
        quality,
        user_message=user_message,
        response_understanding=response_understanding,
        explicit_topic=explicit_topic,
        current_topic=topic,
    )
    result = {
        "version": ENGINE_VERSION,
        "original": original,
        "reply": original,
        "recovered": False,
        "strategy": None,
        "recovery_reason": reason,
        "trigger_issues": sorted(issues),
        "topic": topic,
        "action": action,
    }

    if action not in {"CONTINUE", "ADVANCE"} or (quality or {}).get("changed"):
        return result

    # A learner-led topic change is not an error. The normal Topic Manager /
    # generated question should stand; Recovery must not pull them backwards.
    if reason == "learner_topic_change":
        result["strategy"] = "accept_topic_change"
        return result

    if reason == "learner_did_not_understand":
        fallback = safe_question or SAFE_TOPIC_QUESTIONS.get(topic)
        if fallback:
            result.update(
                reply=f"Kein Problem. Ich frage einfacher. {fallback}",
                recovered=True,
                strategy="simplify_for_learner",
            )
        return result

    if reason == "nele_uncertain":
        meaning = _meaning(response_understanding)
        if meaning:
            result.update(
                reply=f"Meinst du „{meaning}“?",
                recovered=True,
                strategy="clarify_meaning",
            )
        else:
            result.update(
                reply="Ich habe dich nicht ganz verstanden. Kannst du das noch einmal sagen?",
                recovered=True,
                strategy="ask_again",
            )
        return result

    if reason not in {"answer_mismatch", "topic_drift"}:
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
