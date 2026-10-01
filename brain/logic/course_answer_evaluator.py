"""Shared deterministic evaluator for Nele course answers.

Lessons and dialogues both delegate ordinary correctness decisions here so a
natural variant is judged consistently across course surfaces. Dialogue-specific
slot/context rules remain in dialogue_engine and can veto or extend this base
evaluation without duplicating semantic matching.
"""
import re

from brain.logic.matcher import normalize


# Course grammar words are learning evidence, not semantic noise.  Dropping
# prepositions/articles here made malformed productions such as
# "Ich komme Polen" compare equal to "Ich komme aus Polen".  Keep every token
# for semantic bag matching; the explicit subject-pronoun fallback below may
# still remove one subject where that omission is intentionally safe.
_SEMANTIC_FUNCTION_WORDS = set()


def _norm(value):
    return normalize(str(value or "").strip()).strip(" .?!„“\"'")


def semantic_tokens(value):
    return [
        token
        for token in _norm(value).split()
        if token and token not in _SEMANTIC_FUNCTION_WORDS
    ]


def semantic_equivalent(user_message, accepted_values, render=None):
    render = render or (lambda value: str(value or ""))
    learner_tokens = semantic_tokens(user_message)
    if len(learner_tokens) < 2:
        return False

    learner_bag = sorted(learner_tokens)
    for value in accepted_values or []:
        target_tokens = semantic_tokens(render(value))
        if len(target_tokens) < 2:
            continue

        # Preserve natural German fronting (for example
        # "Aus Frankreich kommst du"), but do not let bag matching bless a
        # broken subject-first clause such as "Ich aus Italien komme".
        # When both forms start with the same subject pronoun, the finite verb
        # that directly follows it in the accepted model must remain there.
        subject_pronouns = {"ich", "du", "er", "sie", "es", "wir", "ihr"}
        if (
            len(target_tokens) >= 2
            and len(learner_tokens) >= 2
            and target_tokens[0] in subject_pronouns
            and learner_tokens[0] == target_tokens[0]
            and learner_tokens[1] != target_tokens[1]
        ):
            continue

        if learner_bag == sorted(target_tokens):
            return True

        subject_pronouns = {"ich", "du", "er", "sie", "es", "wir", "ihr"}
        removable = [token for token in target_tokens if token in subject_pronouns]
        if len(removable) == 1:
            reduced = list(target_tokens)
            reduced.remove(removable[0])
            if len(reduced) >= 2 and learner_bag == sorted(reduced):
                return True
    return False


def sequence_partial_progress(user_message, accepted_values, state=None, render=None):
    render = render or (lambda value: str(value or ""))
    learner_tokens = _norm(user_message).replace(",", " ").split()
    if not learner_tokens:
        return None

    for value in accepted_values or []:
        rendered = render(value)
        target_tokens = _norm(rendered).replace(",", " ").split()
        if len(target_tokens) < 3 or len(learner_tokens) >= len(target_tokens):
            continue
        if learner_tokens == target_tokens[:len(learner_tokens)]:
            return {
                "matched": len(learner_tokens),
                "total": len(target_tokens),
                "target": rendered,
            }
    return None


def _gap_fill_fragment(definition, render=None):
    """Return the exact missing fragment for a simple quoted gap-fill prompt."""
    if not isinstance(definition, dict):
        return None
    render = render or (lambda value: str(value or ""))
    prompt = render(definition.get("prompt", ""))
    correct = render(definition.get("correct_answer", ""))
    if not prompt or not correct:
        return None

    quoted = re.findall(r'[„"]([^„“"]*(?:…|___+)[^„“"]*)[“"]', prompt)
    for template in quoted:
        parts = re.split(r'(?:…|___+)', template, maxsplit=1)
        if len(parts) != 2:
            continue
        prefix = _norm(parts[0])
        suffix = _norm(parts[1])
        target = _norm(correct)
        if prefix and not target.startswith(prefix):
            continue
        if suffix and not target.endswith(suffix):
            continue

        start = len(prefix)
        end = len(target) - len(suffix) if suffix else len(target)
        missing = target[start:end].strip()
        if missing:
            return missing
    return None


def answer_matches_course_definition(user_message, definition, render=None, validator=None):
    if not isinstance(definition, dict):
        return False

    render = render or (lambda value: str(value or ""))
    message = _norm(user_message)
    if not message:
        return False

    if definition.get("allow_any") is True:
        return True

    named_validator = definition.get("validator")
    if named_validator:
        return bool(validator and validator(named_validator, user_message))

    accepted = definition.get("accepted", [])
    if isinstance(accepted, str):
        accepted = [accepted]
    if not isinstance(accepted, list):
        accepted = []

    rendered_accepted = [render(value) for value in accepted]
    if any(message == _norm(value) for value in rendered_accepted):
        return True
    if semantic_equivalent(user_message, accepted, render=render):
        return True

    # In a real gap-fill task, the learner may naturally say only the missing
    # word/form. Infer that fragment from the prompt + correct answer instead
    # of forcing every lesson to duplicate it in `accepted`.
    gap_fragment = _gap_fill_fragment(definition, render=render)
    if gap_fragment and message == gap_fragment:
        return True

    regex_patterns = definition.get("regex", [])
    if isinstance(regex_patterns, str):
        regex_patterns = [regex_patterns]
    if isinstance(regex_patterns, list):
        for pattern in regex_patterns:
            try:
                if re.fullmatch(str(pattern), str(user_message or "").strip(), flags=re.IGNORECASE):
                    return True
            except re.error:
                continue

    contains_all = definition.get("contains_all", [])
    if isinstance(contains_all, str):
        contains_all = [contains_all]
    if isinstance(contains_all, list) and contains_all:
        if all(_norm(render(value)) in message for value in contains_all):
            return True

    contains_any = definition.get("contains_any", [])
    if isinstance(contains_any, str):
        contains_any = [contains_any]
    if isinstance(contains_any, list) and contains_any:
        if any(_norm(render(value)) in message for value in contains_any):
            return True

    return False


def evaluate_course_answer(user_message, definition, *, render=None, validator=None):
    """Classify a course answer once for all course surfaces.

    Returns:
      {"kind": "correct", "correct": True, "partial": None}
      {"kind": "partial", "correct": False, "partial": {...}}
      {"kind": "wrong", "correct": False, "partial": None}
    """
    if answer_matches_course_definition(
        user_message,
        definition,
        render=render,
        validator=validator,
    ):
        return {"kind": "correct", "correct": True, "partial": None}

    accepted = (definition or {}).get("accepted", []) if isinstance(definition, dict) else []
    if isinstance(accepted, str):
        accepted = [accepted]
    if not isinstance(accepted, list):
        accepted = []

    partial = sequence_partial_progress(
        user_message,
        accepted,
        render=render,
    )
    if partial:
        return {"kind": "partial", "correct": False, "partial": partial}

    return {"kind": "wrong", "correct": False, "partial": None}
