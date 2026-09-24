"""Conversation Quality Controller v1.

Final deterministic guard before a free-conversation reply is returned.
It detects a small set of high-confidence quality problems and repairs only
when a safe replacement is known. It never rewrites pedagogical correction
models or invents new learner facts.
"""

import re

CONTROLLER_VERSION = 1

KNOWN_BAD = {
    "ich arbeite kochen.": "Ich koche bei der Arbeit.",
    "ich arbeite kochen": "Ich koche bei der Arbeit.",
}

def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip()

def _sentences(text):
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", str(text or "").strip()) if part.strip()]

def _dedupe_adjacent(text):
    parts = _sentences(text)
    if len(parts) < 2:
        return str(text or "").strip(), False
    kept = []
    changed = False
    for part in parts:
        if kept and _norm(part) == _norm(kept[-1]):
            changed = True
            continue
        kept.append(part)
    return " ".join(kept), changed

def _too_complex_for_a1(text):
    words = re.findall(r"[A-Za-zÄÖÜäöüß0-9'-]+", str(text or ""))
    # Conservative signal only; corrections/examples may legitimately be longer.
    return len(words) > 32

def check_reply(reply, *, topic=None, action=None, model=None):
    original = str(reply or "").strip()
    fixed = original
    issues = []
    changed = False

    bad = KNOWN_BAD.get(_norm(fixed))
    if bad:
        fixed = bad
        issues.append("known_invalid_construction")
        changed = True

    deduped, did_dedupe = _dedupe_adjacent(fixed)
    if did_dedupe:
        fixed = deduped
        issues.append("adjacent_duplicate")
        changed = True

    too_complex = _too_complex_for_a1(fixed)
    if too_complex:
        issues.append("a1_length_warning")

    return {
        "version": CONTROLLER_VERSION,
        "original": original,
        "reply": fixed,
        "changed": changed,
        "issues": issues,
        "topic": topic,
        "action": action,
        "model": model,
        "a1_length_warning": too_complex,
        "passed": not issues,
    }
