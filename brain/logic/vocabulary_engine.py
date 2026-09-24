# ==========================================
# NELE – VOCABULARY ENGINE v1
# Central access layer for conversation-aware vocabulary.
# Existing vocabulary data remains the single source of truth.
# ==========================================

import re

from brain.knowledge.A1.vocabulary import VOCABULARY


TOPIC_HINTS = {
    "wetter": {"wetter", "sonnig", "warm", "kalt", "regen", "regnen", "wind", "windig"},
    "arbeit": {"arbeit", "arbeiten", "job", "pause", "kollege", "kollegin", "firma"},
    "freizeit": {"freizeit", "hobby", "spazieren", "rad", "fahrrad", "lesen", "sport"},
    "essen": {"essen", "trinken", "brot", "wasser", "kaffee", "tee", "kochen"},
    "hotel": {"hotel", "zimmer", "gast", "rezeption", "reservierung", "buchung", "handtuch"},
    "alltag": {"heute", "gestern", "morgen", "einkaufen", "haus", "wohnung"},
}


def normalize_text(value):
    text = str(value or "").lower().strip()
    text = re.sub(r"[^a-zäöüß0-9\- ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def get_entry(word):
    """Return a vocabulary entry without exposing mutable source data."""
    key = normalize_text(word)
    entry = VOCABULARY.get(key)
    if not entry:
        return None
    result = dict(entry)
    result["word"] = key
    result.setdefault("level", "A1")
    return result


def words_in_message(message):
    """Find known vocabulary items used in a learner message."""
    text = normalize_text(message)
    if not text:
        return []

    padded = f" {text} "
    found = []
    for word in VOCABULARY:
        normalized_word = normalize_text(word)
        if normalized_word and f" {normalized_word} " in padded:
            found.append(normalized_word)

    return sorted(set(found), key=lambda item: (-len(item), item))


def detect_topic(message):
    """Detect a broad conversation topic from explicit A1 vocabulary hints."""
    tokens = set(normalize_text(message).split())
    if not tokens:
        return None

    best_topic = None
    best_score = 0
    for topic, hints in TOPIC_HINTS.items():
        score = len(tokens.intersection(hints))
        if score > best_score:
            best_topic = topic
            best_score = score

    return best_topic


def vocabulary_for_topic(topic, limit=8):
    """Return known vocabulary suitable for a conversation topic."""
    topic = normalize_text(topic)
    hints = TOPIC_HINTS.get(topic, set())
    if not hints:
        return []

    results = []
    for hint in hints:
        entry = get_entry(hint)
        if entry:
            results.append(entry)

    results.sort(key=lambda item: item["word"])
    return results[:max(0, int(limit))]


def build_conversation_vocabulary(message, topic=None, limit=8):
    """Create compact vocabulary context for Conversation Engine."""
    detected_topic = normalize_text(topic) if topic else detect_topic(message)
    used_words = words_in_message(message)
    suggestions = vocabulary_for_topic(detected_topic, limit=limit) if detected_topic else []

    return {
        "level": "A1",
        "topic": detected_topic or None,
        "used_words": used_words,
        "suggestions": suggestions,
    }
