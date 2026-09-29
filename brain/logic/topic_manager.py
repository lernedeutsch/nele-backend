"""Topic Manager v2 for Nele free conversation.

Uses Conversation State v2 to keep a coherent topic/subtopic until the learner
clearly changes it. It does not generate replies; it decides conversational
continuity and exposes a small decision object for the Conversation Engine.
"""

TOPIC_ALIASES = {
    "arbeit": "work", "work": "work", "hotel": "work",
    "freizeit": "hobby", "hobby": "hobby",
    "wetter": "weather", "weather": "weather",
    "essen": "food", "food": "food",
    "urlaub": "holiday", "holiday": "holiday",
    "gestern": "yesterday", "yesterday": "yesterday",
    "alltag": "today", "today": "today",
    "shopping": "shopping", "place": "place",
    "personal": "personal", "birthday": "personal",
}

CONTEXTUAL_SUBTOPICS = {
    ("work", "kochen"),
}


def canonical_topic(topic):
    return TOPIC_ALIASES.get(str(topic or "").strip().lower())


def choose_topic(state, *, explicit_topic=None, vocabulary_topic=None):
    """Choose the active topic without letting weak vocabulary hints hijack it."""
    current = canonical_topic((state.get("conversation_state_v2") or {}).get("topic"))
    explicit = canonical_topic(explicit_topic)
    vocabulary = canonical_topic(vocabulary_topic)

    if explicit:
        return explicit, "explicit"

    # Keep an active subtopic (for example work/kochen) for short contextual
    # answers such as Suppe, ja, Pizza, Nudeln.
    snapshot = state.get("conversation_state_v2") or {}
    if current and (current, snapshot.get("subtopic")) in CONTEXTUAL_SUBTOPICS:
        return current, "context"

    if vocabulary:
        return vocabulary, "vocabulary"
    return current or "today", "context"


def update_topic_manager(state, *, topic, source="context", subtopic=None):
    manager = state.setdefault("topic_manager_v2", {})
    previous = manager.get("topic")
    changed = bool(previous and previous != topic)
    if changed:
        manager["previous_topic"] = previous
        manager["topic_turns"] = 0
    manager["topic"] = topic
    manager["subtopic"] = subtopic
    manager["source"] = source
    manager["topic_changed"] = changed
    manager["topic_turns"] = int(manager.get("topic_turns", 0) or 0) + 1
    return dict(manager)


def get_topic_manager(state):
    return dict(state.get("topic_manager_v2") or {})
