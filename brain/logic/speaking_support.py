"""Global Speaking Support Engine for 📚 Mit dem Kurs üben.

Lessons define WHAT is being learned. This layer decides HOW much speaking
support the learner needs. It intentionally contains no vocabulary-specific
answer map, so future LESSON_FLOW lessons inherit the same pedagogy.
"""

import re

ENGINE_VERSION = 1


def _text(value):
    return str(value or "").strip()


def _norm(value):
    return re.sub(r"\s+", " ", _text(value).lower()).strip(" .?!„“\"'")


def _words(value):
    return re.findall(r"[A-Za-zÄÖÜäöüß0-9'-]+", _text(value))


def _render_target(step, state):
    # Avoid importing generic_lesson_engine here (circular import). Generic
    # LESSON_FLOW targets are plain strings or simple {student fact} templates.
    target = _text((step or {}).get("correct_answer"))
    if not target:
        return ""
    values = {
        "name": _text((state or {}).get("name")),
        "level": _text((state or {}).get("lesson_teaching_level")),
        "lesson": _text((state or {}).get("lesson_teaching_lesson")),
        "section": _text((state or {}).get("lesson_teaching_section")),
    }
    try:
        return target.format(**values)
    except Exception:
        return target


def _is_natural_short_answer(user_message, step):
    low = _norm(user_message)
    if low in {"ja", "nein", "ja gern", "nein danke"}:
        return True
    # Lesson authors may explicitly say a short form is natural. This is
    # pedagogical metadata, not a vocabulary-specific program rule.
    natural = (step or {}).get("natural_short_answers") or []
    if isinstance(natural, str):
        natural = [natural]
    return any(low == _norm(item) for item in natural)


def _semantic_short_match(user_message, target, step):
    """Conservative generic check: does a short learner answer express a
    salient content item of the lesson's own target/accepted material?"""
    words = _words(user_message)
    if not words or len(words) > 2:
        return False

    low = _norm(user_message)
    sources = [target]
    accepted = (step or {}).get("accepted") or []
    if isinstance(accepted, str):
        accepted = [accepted]
    sources.extend(accepted)
    contains_any = (step or {}).get("contains_any") or []
    if isinstance(contains_any, str):
        contains_any = [contains_any]
    sources.extend(contains_any)

    source_tokens = set()
    for source in sources:
        source_tokens.update(_words(_norm(source)))
    learner_tokens = set(_words(low))
    return bool(learner_tokens and learner_tokens.issubset(source_tokens))


def _support_level(state):
    try:
        return max(0, min(5, int((state or {}).get("course_speaking_support_level", 0) or 0)))
    except (TypeError, ValueError):
        return 0


def _set_support(state, value):
    state["course_speaking_support_level"] = max(0, min(5, int(value)))


def assess_course_answer(user_message, step, state, *, answer_matches=False):
    target = _render_target(step, state)
    natural_short = _is_natural_short_answer(user_message, step)
    semantic_short = _semantic_short_match(user_message, target, step)

    result = {
        "version": ENGINE_VERSION,
        "answer_matches": bool(answer_matches),
        "intercept": False,
        "kind": "normal",
        "target": target,
        "natural_short": natural_short,
        "semantic_short": semantic_short,
        "support_level": _support_level(state),
    }

    # A natural conversational short answer is success and should not be
    # mechanically expanded merely because it is short.
    if answer_matches and natural_short:
        _set_support(state, max(0, _support_level(state) - 1))
        result["kind"] = "natural_short_success"
        return result

    # Meaning is present, but the learner has not yet produced the lesson's
    # target construction. Treat this as communicative success + speaking
    # opportunity, never as an error.
    if not answer_matches and semantic_short and target:
        result.update(intercept=True, kind="short_answer_expansion")
        return result

    if answer_matches:
        _set_support(state, max(0, _support_level(state) - 1))
        result["kind"] = "independent_success"
        return result

    return result


def build_course_support_reply(assessment, step, state):
    target = _text((assessment or {}).get("target"))
    if (assessment or {}).get("kind") == "short_answer_expansion" and target:
        state["course_pending_speaking_model"] = target
        # Keep the learner on the same lesson step. Advancement happens only
        # after the learner has had a turn to produce the model.
        return f"Genau. Du kannst auch sagen: „{target}“ Sag es mal."
    return None


def handle_pending_course_model(user_message, state):
    target = _text((state or {}).get("course_pending_speaking_model"))
    if not target:
        return None

    if _norm(user_message) == _norm(target):
        state["course_pending_speaking_model"] = None
        _set_support(state, max(0, _support_level(state) - 1))
        # Returning None lets the normal lesson matcher process this same
        # learner utterance and advance the lesson exactly once.
        return None

    level = min(5, _support_level(state) + 1)
    _set_support(state, level)
    if level <= 1:
        return "Fast. Versuch es noch einmal."
    if level == 2:
        starter = " ".join(_words(target)[:2])
        return f"Fang so an: „{starter} …“" if starter else "Versuch es noch einmal."
    return f"Du kannst sagen: „{target}“ Sag es mal."


def legacy_course_support(
    user_message,
    target,
    state,
    *,
    context=None,
    semantic_attempt=False,
):
    """Adapter for older course steps that predate LESSON_FLOW metadata.

    It uses only the current target and learner attempt. No vocabulary-specific
    cases are encoded here. Returns support only for a plausible partial
    production; unrelated answers remain owned by the legacy validator.
    """
    target = _text(target)
    learner = _norm(user_message)
    if not target or not learner:
        return None

    target_tokens = _words(_norm(target))
    learner_tokens = _words(learner)
    if not learner_tokens:
        return None

    # A one/two-token fragment that is literally part of the target is evidence
    # that the learner knows what they mean but may lack the construction.
    if len(learner_tokens) <= 2 and set(learner_tokens).issubset(set(target_tokens)):
        state["course_pending_speaking_model"] = target
        return f"Genau. Du kannst sagen: „{target}“ Sag es mal."

    # For a malformed attempt that shares meaningful material with the target,
    # begin with a small cue instead of immediately exposing the whole answer.
    shared = set(learner_tokens) & set(target_tokens)
    if shared or semantic_attempt:
        level = min(5, _support_level(state) + 1)
        _set_support(state, level)
        if level <= 1:
            return "Fast. Versuch es noch einmal."
        if level == 2:
            starter = " ".join(target_tokens[:2])
            return f"Fang so an: „{starter} …“"
        state["course_pending_speaking_model"] = target
        return f"Du kannst sagen: „{target}“ Sag es mal."

    return None
