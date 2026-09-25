"""Semantic helpers for reusable Nele dialogue content.

Dialogue data describes WHAT may be practised.  This module provides the
small deterministic vocabulary needed by the global dialogue engine to reason
about intent, slots and safe variations without hard-coding lesson logic.
"""
import re
from brain.logic.matcher import normalize

LEARNER_ROLES = {"student", "learner", "user", "du"}
TEACHER_ROLES = {"nele", "teacher", "assistant"}
SLOT_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def norm(value):
    return normalize(str(value or "")).strip(" .?!„“\"'")


def role_of(turn):
    return norm((turn or {}).get("role"))


def slot_names(value):
    return set(SLOT_RE.findall(str(value or "")))


def render_pattern(pattern, slots):
    text = str(pattern or "")
    for name, value in (slots or {}).items():
        text = text.replace("{" + str(name) + "}", str(value))
    return text


def accepted_patterns(turn):
    values = turn.get("accepted_patterns", turn.get("accepted", []))
    if isinstance(values, str):
        values = [values]
    expected = turn.get("expected")
    if expected:
        values = list(values) + [expected]
    return [str(v) for v in values if str(v or "").strip()]


def infer_intent(turn):
    explicit = str(turn.get("intent") or turn.get("expected_intent") or "").strip()
    if explicit:
        return explicit
    text = norm(turn.get("prompt") or turn.get("text") or turn.get("expected"))
    if "woher" in text:
        return "origin"
    if "wohn" in text:
        return "residence"
    if "heiß" in text or "heiss" in text:
        return "name"
    return "utterance"


def compatible_topics(current, candidate, allowed):
    current, candidate = norm(current), norm(candidate)
    if not current or not candidate or current == candidate:
        return True
    return candidate in {norm(x) for x in (allowed or [])}
