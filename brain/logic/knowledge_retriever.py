"""Shared deterministic knowledge retrieval for Nele.

This first version is intentionally read-only: it normalizes existing lesson,
dialogue and Meine Sätze content behind one interface without changing routing.
"""
from dataclasses import dataclass, field
from typing import Iterable

from brain.knowledge.active_dialogues import ACTIVE_DIALOGUES
from brain.logic.lesson_loader import load_lesson
from brain.logic.personal_sentences import PERSONAL_SENTENCES


@dataclass(frozen=True)
class KnowledgeItem:
    source: str
    text: str
    topic: str = ""
    level: str = ""
    tags: tuple = field(default_factory=tuple)
    score: float = 0.0
    item_id: str = ""


def _norm(value):
    return str(value or "").strip().casefold()


def _lesson_items(level, lesson):
    if not lesson:
        return []
    result = []
    for index, entry in enumerate(load_lesson(level=level, lesson=lesson) or []):
        if isinstance(entry, str):
            text, topic, tags = entry, "", ()
        elif isinstance(entry, dict):
            text = entry.get("text") or entry.get("response") or entry.get("reply") or ""
            topic = entry.get("topic") or entry.get("section") or ""
            tags = tuple(entry.get("tags") or ())
        else:
            continue
        if str(text).strip():
            result.append(KnowledgeItem("lesson", str(text).strip(), str(topic), level, tags, item_id=f"{level}-{lesson}-{index}"))
    return result


def _dialogue_items(level):
    result = []
    for dialogue in ACTIVE_DIALOGUES:
        item_level = str(dialogue.get("level") or "")
        if level and item_level.upper() != str(level).upper():
            continue
        topic = str(dialogue.get("topic") or dialogue.get("title") or "")
        tags = tuple(filter(None, [dialogue.get("section"), dialogue.get("situation")]))
        for index, turn in enumerate(dialogue.get("turns") or []):
            text = turn.get("text") or turn.get("expected") or ""
            if str(text).strip():
                result.append(KnowledgeItem("dialogue", str(text).strip(), topic, item_level, tags, item_id=f"{dialogue.get('id','dialogue')}-{index}"))
    return result


def _personal_items(level):
    return [
        KnowledgeItem(
            "meine_saetze",
            str(item.get("text") or "").strip(),
            str(item.get("category") or ""),
            str(level or ""),
            tuple(filter(None, [item.get("category")])),
            item_id=str(item.get("id") or ""),
        )
        for item in PERSONAL_SENTENCES if str(item.get("text") or "").strip()
    ]


def retrieve(query="", topic="", level="A1", intent="", lesson=None, sources=None, limit=8):
    """Return ranked KnowledgeItems from existing Nele knowledge sources."""
    allowed = set(sources or ("lesson", "dialogue", "meine_saetze"))
    items = []
    if "lesson" in allowed:
        items.extend(_lesson_items(level, lesson))
    if "dialogue" in allowed:
        items.extend(_dialogue_items(level))
    if "meine_saetze" in allowed:
        items.extend(_personal_items(level))

    q, wanted_topic, wanted_intent = _norm(query), _norm(topic), _norm(intent)
    ranked = []
    for item in items:
        haystack = " ".join([item.text, item.topic, *item.tags]).casefold()
        score = 0.0
        if wanted_topic and wanted_topic in haystack:
            score += 5.0
        if q and q in haystack:
            score += 4.0
        elif q:
            score += sum(0.5 for token in q.split() if token and token in haystack)
        if level and _norm(item.level) == _norm(level):
            score += 2.0
        if wanted_intent and wanted_intent in haystack:
            score += 1.0
        if item.source == "meine_saetze":
            score += 0.25
        ranked.append(KnowledgeItem(item.source, item.text, item.topic, item.level, item.tags, score, item.item_id))

    ranked.sort(key=lambda x: (-x.score, x.source, x.item_id, x.text))
    return ranked[:max(0, int(limit))]
