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


_GERMAN_NUMBER_WORDS = {
    0: "null", 1: "eins", 2: "zwei", 3: "drei", 4: "vier", 5: "fünf",
    6: "sechs", 7: "sieben", 8: "acht", 9: "neun", 10: "zehn",
    11: "elf", 12: "zwölf", 13: "dreizehn", 14: "vierzehn", 15: "fünfzehn",
    16: "sechzehn", 17: "siebzehn", 18: "achtzehn", 19: "neunzehn",
    20: "zwanzig", 30: "dreißig", 40: "vierzig", 50: "fünfzig",
    60: "sechzig", 70: "siebzig", 80: "achtzig", 90: "neunzig", 100: "hundert",
}


def _german_number_word(number):
    """Return the canonical German cardinal for the A1 range 0..100."""
    try:
        number = int(number)
    except (TypeError, ValueError):
        return None
    if number in _GERMAN_NUMBER_WORDS:
        return _GERMAN_NUMBER_WORDS[number]
    if 21 <= number <= 99:
        ones = number % 10
        tens = number - ones
        one_word = "ein" if ones == 1 else _GERMAN_NUMBER_WORDS.get(ones)
        tens_word = _GERMAN_NUMBER_WORDS.get(tens)
        if one_word and tens_word:
            return f"{one_word}und{tens_word}"
    return None


def _expand_digit_tokens(tokens):
    expanded = []
    for token in tokens:
        if re.fullmatch(r"\d{1,3}", token):
            word = _german_number_word(token)
            if word:
                expanded.append(word)
                continue
        expanded.append(token)
    return expanded


def semantic_equivalent(user_message, accepted_values, render=None):
    render = render or (lambda value: str(value or ""))
    learner_tokens = semantic_tokens(user_message)
    if len(learner_tokens) < 2:
        return False

    for value in accepted_values or []:
        target_tokens = semantic_tokens(render(value))
        # Complete natural sentences may express the same number with digits
        # or words. Keep standalone number-word drills strict by applying this
        # only inside semantic sentence comparison (which requires >=2 tokens).
        learner_compare = _expand_digit_tokens(learner_tokens)
        target_tokens = _expand_digit_tokens(target_tokens)
        learner_bag = sorted(learner_compare)
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
            and learner_compare[0] == target_tokens[0]
            and learner_compare[1] != target_tokens[1]
        ):
            continue

        if learner_bag == sorted(target_tokens):
            if target_tokens[0] in subject_pronouns and len(target_tokens) >= 3:
                if learner_compare == target_tokens:
                    return True
                model_subject = target_tokens[0]
                model_verb = target_tokens[1]
                tail = target_tokens[2:]
                if learner_compare == tail + [model_verb, model_subject]:
                    return True
                # A fronted prefix must be able to stand as a constituent.
                # Never split immediately after a word that requires its
                # complement (for example "aus" in "aus Italien").  Without
                # this guard the bag matcher accepted malformed V2 productions
                # such as "Aus komme ich Italien".
                dangling_fronting_words = {
                    "aus", "bei", "bis", "durch", "für", "gegen", "in", "mit",
                    "nach", "ohne", "seit", "über", "um", "unter", "von", "vor",
                    "zu", "an", "auf",
                }
                for split in range(1, len(tail)):
                    if tail[split - 1] in dangling_fronting_words:
                        continue
                    candidate = tail[:split] + [model_verb, model_subject] + tail[split:]
                    if learner_compare == candidate:
                        return True
                continue
            return True

        removable = [token for token in target_tokens if token in subject_pronouns]
        if len(removable) == 1:
            reduced = list(target_tokens)
            reduced.remove(removable[0])
            # Subject omission is safe only when the learner preserves the
            # remaining model order. Bag comparison here accepted malformed
            # productions such as "Komme Italien aus" for
            # "Ich komme aus Italien".
            if len(reduced) >= 2 and learner_compare == reduced:
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
