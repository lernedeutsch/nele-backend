"""Conversation Coherence Engine v1.

Guards local conversational continuity. It does not generate pedagogy or
correct language; it scores/repairs candidate questions using recent turns,
active topic and learner facts.
"""

import re

ENGINE_VERSION = 2

TOPIC_TERMS = {
    "work": {"arbeit", "arbeitest", "arbeiten", "job", "hotel", "koch", "kochst", "pause", "fängst", "faengst"},
    "hobby": {"hobby", "freizeit", "musik", "sport", "rad", "schwimm", "lesen"},
    "weather": {"wetter", "warm", "kalt", "sonn", "regen", "wind", "schnee"},
    "holiday": {"urlaub", "ferien", "reise", "meer", "berge"},
    "shopping": {"kauf", "einkauf", "schuhe", "farbe"},
    "today": {"heute", "tag", "machst"},
    "yesterday": {"gestern"},
    "place": {"wo ", "zu hause", "zuhause"},
}

def _norm(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower()).strip(" ?!.")

def _question_signature(question):
    """Collapse near-duplicate A1 prompts to a semantic intent signature."""
    q = _norm(question)
    groups = (
        ("activity_more", ("was machst du sonst noch gern", "was machst du sonst gern", "was machst du noch gern")),
        ("reading_preference", ("was liest du am liebsten", "was liest du gern")),
        ("weather_temperature", ("ist es warm oder kalt", "wie ist das wetter bei dir")),
    )
    for name, variants in groups:
        if any(v in q for v in variants):
            return name
    return q

def _topic_match(question, topic):
    q = _norm(question)
    terms = TOPIC_TERMS.get(str(topic or ""), set())
    return any(term in q for term in terms)

def assess_candidate_question(question, *, topic=None, recent_questions=None, previous_question=None):
    q = _norm(question)
    recent = [_norm(x) for x in (recent_questions or []) if x]
    recent_signatures = [_question_signature(x) for x in (recent_questions or []) if x]
    signature = _question_signature(question)
    repeated = bool(q and (q in recent[-8:] or signature in recent_signatures[-8:]))
    immediate_repeat = bool(q and signature == _question_signature(previous_question))
    topic_match = _topic_match(question, topic)
    return {
        "version": ENGINE_VERSION,
        "question": question,
        "repeated": repeated,
        "immediate_repeat": immediate_repeat,
        "topic_match": topic_match,
        "coherent": bool(q) and not repeated,
        "reason": "repeat" if repeated else "topic_continuation" if topic_match else "neutral",
    }

def choose_coherent_question(candidate, *, topic=None, recent_questions=None,
                             previous_question=None, alternatives=None):
    assessment = assess_candidate_question(
        candidate,
        topic=topic,
        recent_questions=recent_questions,
        previous_question=previous_question,
    )
    if assessment["coherent"]:
        return {**assessment, "selected": candidate, "changed": False}

    for alternative in alternatives or []:
        alt = assess_candidate_question(
            alternative,
            topic=topic,
            recent_questions=recent_questions,
            previous_question=previous_question,
        )
        if alt["coherent"] and (alt["topic_match"] or not assessment["topic_match"]):
            return {
                **alt,
                "selected": alternative,
                "changed": True,
                "original": candidate,
                "reason": "avoid_repeat_keep_topic",
            }

    return {**assessment, "selected": candidate, "changed": False}

def update_coherence_state(state, *, user_message, topic, question, facts=None, decision=None):
    store = state.setdefault("conversation_coherence_v1", {
        "version": ENGINE_VERSION,
        "turns": [],
    })
    turns = store.setdefault("turns", [])
    turns.append({
        "user": str(user_message or "").strip(),
        "topic": topic,
        "question": str(question or "").strip(),
        "facts": dict(facts or {}),
    })
    del turns[:-8]
    store["active_topic"] = topic
    store["last_question"] = str(question or "").strip()
    store["last_decision"] = dict(decision or {})
    store["recent_topics"] = [item.get("topic") for item in turns[-5:] if item.get("topic")]
    return dict(store)
