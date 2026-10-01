"""Global Speaking Support Engine for 📚 Mit dem Kurs üben.

Lessons define WHAT is being learned. This layer decides HOW much speaking
support the learner needs. It intentionally contains no vocabulary-specific
answer map, so future LESSON_FLOW lessons inherit the same pedagogy.
"""

import re

from brain.memory.user_facts import get_user_fact

ENGINE_VERSION = 1


def _text(value):
    return str(value or "").strip()


def _norm(value):
    return re.sub(r"\s+", " ", _text(value).lower()).strip(" .?!„“\"'")


def _words(value):
    return re.findall(r"[A-Za-zÄÖÜäöüß0-9'-]+", _text(value))


def _spelling_sequence(value):
    """Return a canonical letter sequence only for explicit spelling forms."""
    text = _text(value).lower()
    tokens = re.findall(r"[a-zäöüß]", text)
    if len(tokens) < 2:
        return None

    # Treat the input as spelling only when every lexical chunk is one letter.
    # This accepts separators such as spaces, hyphens and en dashes without
    # weakening normal sentence matching.
    chunks = re.findall(r"[A-Za-zÄÖÜäöüß]+", text)
    if not chunks or any(len(chunk) != 1 for chunk in chunks):
        return None
    return "".join(tokens)


def _same_course_production(user_message, target):
    if _norm(user_message) == _norm(target):
        return True

    learner_spelling = _spelling_sequence(user_message)
    target_spelling = _spelling_sequence(target)
    return bool(
        learner_spelling
        and target_spelling
        and learner_spelling == target_spelling
    )


def _render_target(step, state):
    # Avoid importing generic_lesson_engine here (circular import). Generic
    # LESSON_FLOW targets are plain strings or simple {student fact} templates.
    target = _text((step or {}).get("correct_answer"))
    if not target:
        return ""
    values = {
        "name": _text(get_user_fact(state or {}, "name") or (state or {}).get("name")),
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

    # Lesson-owned accepted variants are real success. The shared support
    # layer must not override the lesson validator and force an exact full
    # model after the author has explicitly declared a shorter/natural form
    # correct. Steps that require full production simply omit that short form
    # from their accepted variants.
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
        return f"Genau. Sag: „{target}“"
    return None



def progressive_course_support(target, state, *, first_hint=None, prefix=""):
    """Return the next global support rung for a known course target.

    Lesson modules may supply a pedagogical first hint (WHAT is being learned),
    while this shared engine owns escalation (HOW much help is revealed).
    """
    target = _text(target)
    state["course_mastery_assistance_used"] = True
    level = min(5, _support_level(state) + 1)
    _set_support(state, level)

    if level <= 1:
        reply = _text(first_hint) or "Noch einmal."
        return (prefix + reply).strip()
    if level == 2:
        starter = " ".join(_words(target)[:2])
        reply = f"Fang so an: „{starter} …“" if starter else "Noch einmal."
        return (prefix + reply).strip()

    state["course_pending_speaking_model"] = target
    reply = f"Sag: „{target}“"
    return (prefix + reply).strip()


def register_course_success(state):
    """Fade global speaking support after an independent/accepted success."""
    _set_support(state, max(0, _support_level(state) - 1))


def consume_course_model_exhaustion(state):
    """Consume one exhausted support target and turn it into durable review evidence.

    This is deliberately lesson-agnostic.  The support layer only reports that
    the learner could not produce the current target after maximal scaffolding.
    The active course engine decides which skill owns that evidence.
    """
    target = _text((state or {}).pop("course_model_practice_exhausted", None))
    if not target:
        return None
    return {
        "target": target,
        "assistance_exhausted": True,
    }


def handle_pending_course_model(user_message, state):
    target = _text((state or {}).get("course_pending_speaking_model"))
    if not target:
        return None

    # Repeating a model that Nele has already exposed is guided practice,
    # never independent mastery evidence.
    state["course_mastery_assistance_used"] = True

    if _same_course_production(user_message, target):
        state["course_pending_speaking_model"] = None
        _set_support(state, max(0, _support_level(state) - 1))
        # Returning None lets the normal lesson matcher process this same
        # learner utterance and advance the lesson exactly once.
        return None

    level = min(5, _support_level(state) + 1)
    _set_support(state, level)
    if level <= 1:
        return "Fast. Noch einmal."
    if level == 2:
        starter = " ".join(_words(target)[:2])
        return f"Fang so an: „{starter} …“" if starter else "Noch einmal."
    if level == 3:
        # First full model: hear/read the complete form once.
        return f"Hör zu: „{target}“ Jetzt du."
    if level == 4:
        # Do not repeat the exact same instruction forever. For a single
        # difficult word, split it into readable chunks; for a sentence,
        # keep one clear model.
        words = _words(target)
        if len(words) == 1 and len(target) >= 6:
            mid = max(2, len(target) // 2)
            return f"Langsam: „{target[:mid]}-{target[mid:]}“. Jetzt zusammen: „{target}“"
        return f"Noch einmal langsam: „{target}“"
    # After several failed repetitions, do not trap an A1 learner in an
    # endless ASR/pronunciation loop. Accept the practice attempt and let the
    # lesson continue on the next turn.
    state["course_pending_speaking_model"] = None
    state["course_model_practice_exhausted"] = target
    _set_support(state, 2)
    return f"Das ist okay. Wir üben „{target}“ später noch einmal."


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
        state["course_mastery_assistance_used"] = True
        state["course_pending_speaking_model"] = target
        return f"Genau. Sag: „{target}“"

    # For a malformed attempt that shares meaningful material with the target,
    # begin with a small cue instead of immediately exposing the whole answer.
    shared = set(learner_tokens) & set(target_tokens)
    if shared or semantic_attempt:
        state["course_mastery_assistance_used"] = True
        level = min(5, _support_level(state) + 1)
        _set_support(state, level)

        # If the lesson has already recognized the learner's intended meaning,
        # do not answer with an empty "try again". Give the smallest useful
        # construction cue. The lesson still owns WHAT the target means; this
        # engine owns HOW much of that target to reveal.
        if semantic_attempt and level <= 1:
            starter = target_tokens[0] if target_tokens else ""
            return (
                f"Fast. Fang so an: „{starter} …“"
                if starter
                else "Fast. Noch einmal."
            )

        if level <= 1:
            return "Fast. Noch einmal."
        if level == 2:
            starter = " ".join(target_tokens[:2])
            return f"Fang so an: „{starter} …“"
        state["course_pending_speaking_model"] = target
        return f"Sag: „{target}“"

    return None
