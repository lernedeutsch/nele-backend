"""Shared Knowledge Retriever v1.

Read-only retrieval facade for conversation/teaching engines.
Conversation policy stays outside this module.
"""
from brain.knowledge.active_dialogues import get_active_dialogues
from brain.logic.personal_sentences import PERSONAL_SENTENCES

VERSION = 1

ALIASES = {
    "arbeit": "work", "work": "work", "hotel": "work",
    "freizeit": "hobby", "hobby": "hobby",
    "wetter": "weather", "weather": "weather",
    "essen": "food", "food": "food",
    "urlaub": "holiday", "holiday": "holiday",
    "einkaufen": "shopping", "shopping": "shopping",
}

def canonical_topic(value):
    low = str(value or "").strip().lower()
    return ALIASES.get(low, low or None)

def _blob(item):
    if not isinstance(item, dict):
        return ""
    keys = ("id", "title", "topic", "situation", "category", "text", "reply", "practice_prompt")
    return " ".join(str(item.get(k) or "") for k in keys).lower()

def _matches(item, topic=None, query=None):
    blob = _blob(item)
    topic = canonical_topic(topic)
    words = {w for w in str(query or "").lower().split() if len(w) >= 3}
    topic_terms = {topic} if topic else set()
    topic_terms.update(alias for alias, canonical in ALIASES.items() if canonical == topic)
    topic_ok = not topic_terms or any(term in blob for term in topic_terms)
    query_ok = not words or any(word in blob for word in words)
    return topic_ok and query_ok

def retrieve_knowledge(*, level="A1", topic=None, query=None, limit=6):
    results = []
    for dialogue in get_active_dialogues(str(level or "A1").upper()):
        if _matches(dialogue, topic, query):
            results.append({
                "source": "dialogue", "id": dialogue.get("id"),
                "topic": canonical_topic(dialogue.get("topic")),
                "title": dialogue.get("title"), "situation": dialogue.get("situation"),
            })
            if len(results) >= limit:
                return results
    for item in PERSONAL_SENTENCES:
        if _matches(item, topic, query):
            results.append({
                "source": "personal_sentence", "id": item.get("id"),
                "topic": canonical_topic(item.get("category")),
                "text": item.get("text"), "reply": item.get("reply"),
            })
            if len(results) >= limit:
                break
    return results
