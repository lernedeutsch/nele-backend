"""Active semantic dialogue registry.

This registry is the single runtime extension point for dialogues promoted by
the candidate gate. Lesson modules remain the source for lesson-local content;
promoted reusable dialogues live here and are consumed by the same Dialogue
Engine. No dialogue-specific control flow belongs in this registry.
"""

ACTIVE_DIALOGUES = []


def get_active_dialogues(level=None, lesson=None):
    level = str(level or "").upper()
    result = []
    for dialogue in ACTIVE_DIALOGUES:
        if not isinstance(dialogue, dict):
            continue
        if level and str(dialogue.get("level") or "").upper() != level:
            continue
        if lesson is not None and dialogue.get("lesson") not in (None, lesson):
            continue
        if dialogue.get("knowledge_status", "active") != "active":
            continue
        result.append(dialogue)
    return result
