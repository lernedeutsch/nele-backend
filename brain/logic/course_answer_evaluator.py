"""Shared deterministic evaluator for Nele course answers.

Lessons and dialogues both delegate ordinary correctness decisions here so a
natural variant is judged consistently across course surfaces. Dialogue-specific
slot/context rules remain in dialogue_engine and can veto or extend this base
evaluation without duplicating semantic matching.
"""
import re

from brain.logic.matcher import normalize


_SEMANTIC_FUNCTION_WORDS = {
    "ich", "du", "er", "sie", "es", "wir", "ihr", "aus", "der", "die", "das",
    "den", "dem", "ein", "eine", "einen", "am", "im", "in", "zu", "zum", "zur",
}


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
