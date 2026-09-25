"""Normalize raw dialogue definitions before they enter Nele's active knowledge."""

import re
from copy import deepcopy

from brain.logic.dialogue_knowledge import slot_names
from brain.logic.content_validation import ContentValidationError


LEARNER_ROLES = {"student", "learner", "user", "du"}
TEACHER_ROLES = {"nele", "teacher", "assistant"}


def _text(value):
    return str(value or "").strip()


def _slug(value):
    value = _text(value).casefold()
    value = value.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "dialogue"


def _intent_from_text(text, prefix):
    words = re.findall(r"[a-zäöüß0-9]+", _text(text).casefold())[:4]
    return prefix + "_" + "_".join(words or ["turn"])


def normalize_dialogue(raw, *, level="A1", lesson=None, section=None):
    """Convert a minimally structured dialogue into Nele's semantic schema.

    The importer is deliberately conservative: it fills safe structural
    defaults, but it never invents grammar/vocabulary/learning goals.
    """
    if not isinstance(raw, dict):
        raise ContentValidationError("Raw dialogue must be a dict.")

    d = deepcopy(raw)
    d["level"] = _text(d.get("level") or level).upper()
    if lesson is not None and d.get("lesson") is None:
        d["lesson"] = lesson
    if section and not d.get("section") and not d.get("sections"):
        d["section"] = section

    title = _text(d.get("title") or d.get("situation") or d.get("topic"))
    if not title:
        raise ContentValidationError("Raw dialogue needs title, situation, or topic.")
    d["title"] = title
    d["id"] = _text(d.get("id")) or _slug(title)
    d.setdefault("register", "informal")
    d.setdefault("max_turns", 8)
    d.setdefault("max_variations", 2)
    d.setdefault("slots", {})
    d.setdefault("allowed_variations", [])
    d.setdefault("forbidden_variations", ["combine_unrelated_topics"])
    d.setdefault("next_allowed_topics", [])

    turns = d.get("turns")
    if not isinstance(turns, list) or not turns:
        raise ContentValidationError(f"Dialogue {d['id']}: turns are empty.")

    normalized = []
    for index, source in enumerate(turns):
        if not isinstance(source, dict):
            raise ContentValidationError(f"Dialogue {d['id']}: turn {index} is not a dict.")
        turn = deepcopy(source)
        role = _text(turn.get("role")).casefold()
        if role in TEACHER_ROLES:
            turn["role"] = "nele"
            turn.setdefault("intent", _intent_from_text(turn.get("text"), "say"))
        elif role in LEARNER_ROLES:
            turn["role"] = "student"
            expected = _text(turn.get("expected"))
            accepted = turn.get("accepted_patterns", turn.get("accepted", []))
            if isinstance(accepted, str):
                accepted = [accepted]
            if expected and expected not in accepted:
                accepted = [expected] + list(accepted or [])
            turn["accepted_patterns"] = list(dict.fromkeys(
                _text(x) for x in accepted if _text(x)
            ))
            turn.pop("accepted", None)
            turn.setdefault(
                "expected_intent",
                _intent_from_text(expected or turn.get("prompt"), "answer"),
            )
        normalized.append(turn)

    d["turns"] = normalized
    return d


def validate_imported_slots(dialogue):
    """Reject patterns that reference slots missing from dialogue.slots."""
    slots = dialogue.get("slots") or {}
    if not isinstance(slots, dict):
        raise ContentValidationError(f"Dialogue {dialogue.get('id')}: slots must be a dict.")
    known = set(slots)
    for index, turn in enumerate(dialogue.get("turns") or []):
        for pattern in turn.get("accepted_patterns", []) or []:
            missing = slot_names(pattern) - known
            if missing:
                raise ContentValidationError(
                    f"Dialogue {dialogue.get('id')} turn {index}: undefined slots "
                    + ", ".join(sorted(missing))
                )
    return True
