"""Central Error Engine v1 for Nele.

Detects clear A1 errors, decides whether a correction should interrupt the
conversation, creates a short natural recast, and records the error in the
existing Student Memory 2.0 error memory.
"""

import re

from brain.memory.error_memory import remember_error, get_error_summary


EXACT_ERRORS = {
    "wie heißen du": ("grammar", "Wie heißt du?", "wie_heisst_du"),
    "wie heissen du": ("grammar", "Wie heißt du?", "wie_heisst_du"),
    "wie heißt sie": ("grammar", "Wie heißt du?", "wie_heisst_du"),
    "wie heisst sie": ("grammar", "Wie heißt du?", "wie_heisst_du"),
    "wie du heißt": ("grammar", "Wie heißt du?", "wie_heisst_du"),
    "wie du heisst": ("grammar", "Wie heißt du?", "wie_heisst_du"),
    "wie geht du": ("grammar", "Wie geht es dir?", "wie_geht_es_dir"),
    "wie geht dir": ("grammar", "Wie geht es dir?", "wie_geht_es_dir"),
    "wie geht es du": ("grammar", "Wie geht es dir?", "wie_geht_es_dir"),
    "wie geht ihnen": ("grammar", "Wie geht es Ihnen?", "wie_geht_es_dir"),
    "wie geht sie": ("grammar", "Wie geht es dir?", "wie_geht_es_dir"),
    "wie wetter heute": ("grammar", "Wie ist das Wetter heute?", "wie_ist_das_wetter"),
    "wie ist wetter": ("grammar", "Wie ist das Wetter heute?", "wie_ist_das_wetter"),
    "was ist das wetter": ("grammar", "Wie ist das Wetter heute?", "wie_ist_das_wetter"),
    "wie das wetter ist": ("grammar", "Wie ist das Wetter heute?", "wie_ist_das_wetter"),
    "sonn8g": ("spelling", "Es ist sonnig.", "sonnig_spelling"),
    "sonnlg": ("spelling", "Es ist sonnig.", "sonnig_spelling"),
    "sonig": ("spelling", "Es ist sonnig.", "sonnig_spelling"),
    "gute morgen": ("grammar", "Guten Morgen!", "greeting"),
    "gut morgen": ("grammar", "Guten Morgen!", "greeting"),
    "guten morg": ("spelling", "Guten Morgen!", "greeting"),
    "gute tag": ("grammar", "Guten Tag!", "greeting"),
    "gut tag": ("grammar", "Guten Tag!", "greeting"),
    "gute abend": ("grammar", "Guten Abend!", "greeting"),
    "gut abend": ("grammar", "Guten Abend!", "greeting"),
    "guten nacht": ("grammar", "Gute Nacht!", "greeting"),
    "es ist regen": ("grammar", "Es regnet.", "es_regnet"),
    "ich gut": ("grammar", "Mir geht es gut.", "wellbeing_ich"),
    "ich heißen moni": ("verb", "Ich heiße Moni.", "ich_heisse"),
}

ERROR_PATTERNS = [
    (r"^ich\s+machen\s+lesen$", "verb", "Ich lese gern.", "ich_machen_lesen"),
    (r"^ich\s+lesen\s+gern$", "verb", "Ich lese gern.", "ich_lesen"),
    (r"^ich\s+lesen$", "verb", "Ich lese.", "ich_lesen"),
    (r"^ich\s+fahren\s+rad$", "verb", "Ich fahre gern Rad.", "ich_fahren_rad"),
    (r"^ich\s+(?:horen|hören|hoere)\s+(.+)$", "verb", None, "ich_hoeren"),
    (r"^ich\s+(?:shwimmen|schwimmen|schwimen)$", "verb", "Ich schwimme gern.", "ich_schwimmen"),
    (r"^ich\s+kaufen\s+(.+)$", "verb", None, "ich_kaufen"),
    (r"^ich\s+gehen\s+(.+)$", "verb", None, "ich_gehen"),
    (r"^ich\s+arbeiten(?:\s+(.+))?$", "verb", None, "ich_arbeiten"),
    (r"^ich\s+wohnen\s+(.+)$", "verb", None, "ich_wohnen"),
    (r"^ich\\s+machen\\s+sport$", "verb", "Ich mache Sport.", "ich_mache_sport"),
    (r"^ich\\s+machen\\s+urlaub(?:\\s+(.+))?$", "verb", None, "ich_mache_urlaub"),
    (r"^ich\\s+gehen\\s+einkaufen$", "verb", "Ich gehe einkaufen.", "ich_gehe_einkaufen"),
    (r"^es\\s+ist\\s+regen$", "grammar", "Es regnet.", "es_regnet"),
    (r"^es\\s+(?:regnen|regen)$", "verb", "Es regnet.", "es_regnet"),
    (r"^es\\s+(sonnig|warm|kalt|windig|bewölkt|bewoelkt)$", "grammar", None, "wetter_es_ist"),
    (r"^ich\\s+(gut|prima|schlecht)$", "grammar", None, "wellbeing_ich"),
    (r"^mir\\s+geht\\s+(gut|prima|schlecht|super)$", "grammar", None, "wellbeing_es"),
    (r"^ich\\s+(?:heißen|heissen|heißt|heisst)\\s+(.+)$", "verb", None, "ich_heisse"),
    (r"^mein\\s+name\\s+(?:sein|sind)\\s+(.+)$", "verb", None, "mein_name_ist"),
]


def _normalize(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _build_correction(key, match):
    if key == "ich_hoeren":
        return f"Ich höre {match.group(1)}."
    if key == "ich_kaufen":
        return f"Ich kaufe {match.group(1)}."
    if key == "ich_gehen":
        return f"Ich gehe {match.group(1)}."
    if key == "ich_arbeiten":
        extra = match.group(1)
        return "Ich arbeite" + (f" {extra}." if extra else ".")
    if key == "ich_wohnen":
        return f"Ich wohne {match.group(1)}."
    if key == "ich_mache_urlaub":
        extra = match.group(1)
        return "Ich mache Urlaub" + (f" {extra}." if extra else ".")
    if key == "wetter_es_ist":
        word = match.group(1)
        return f"Es ist {'bewölkt' if word == 'bewoelkt' else word}."
    if key == "wellbeing_ich":
        return f"Mir geht es {match.group(1)}."
    if key == "wellbeing_es":
        return f"Mir geht es {match.group(1)}."
    if key == "ich_heisse":
        return f"Ich heiße {match.group(1).strip(' .')}."
    if key == "mein_name_ist":
        return f"Mein Name ist {match.group(1).strip(' .')}."
    return None


def detect_error(text):
    """Return a structured error or None. Only clear A1 errors are detected."""
    low = _normalize(text).strip(" ?!.")
    if low in EXACT_ERRORS:
        error_type, correction, key = EXACT_ERRORS[low]
        return {
            "key": key,
            "type": error_type,
            "original": str(text or "").strip(),
            "correct": correction,
            "confidence": "high",
        }

    for pattern, error_type, fixed, key in ERROR_PATTERNS:
        match = re.match(pattern, low, re.I)
        if not match:
            continue
        correction = fixed or _build_correction(key, match)
        if not correction:
            continue
        return {
            "key": key,
            "type": error_type,
            "original": str(text or "").strip(),
            "correct": correction,
            "confidence": "high",
        }
    return None


def _previous_error_count(state, error):
    if not state or not error:
        return 0
    summary = get_error_summary(state, error.get("type") or "grammar")
    if not isinstance(summary, dict):
        return 0
    return int(summary.get("count", 0) or 0)


def decide_correction(error, *, state=None, support_level=1, expected_answer=None):
    """Choose a teaching reaction while protecting conversation flow."""
    if not error:
        return {"correct": False, "style": "none", "reason": "no_clear_error"}

    if error.get("confidence") != "high":
        return {"correct": False, "style": "none", "reason": "uncertain"}

    support = int(support_level or 1)
    previous_count = _previous_error_count(state, error)

    # A repeated clear error deserves active retrieval: learner says the
    # corrected form once instead of only seeing it again.
    if previous_count >= 2:
        style = "repeat_request"
        reason = "recurring_clear_error"
    # At higher support levels, give the learner an explicit ready-to-use model.
    elif support >= 2:
        style = "explicit_model"
        reason = "learner_needs_support"
    # For a normal first occurrence, a short natural recast is enough.
    else:
        style = "natural_recast"
        reason = "first_clear_error"

    return {
        "correct": True,
        "style": style,
        "reason": reason,
        "support_level": support,
        "expected_answer": expected_answer,
        "previous_count": previous_count,
    }


def render_correction(error, decision):
    if not error or not decision.get("correct"):
        return None
    correct = error["correct"]
    style = decision.get("style")
    if style == "repeat_request":
        return f"Richtig ist: „{correct}“ Sag es bitte noch einmal."
    if style == "explicit_model":
        return f"Du kannst sagen: „{correct}“"
    if style == "natural_recast":
        return f"Ah, {correct}"
    return None

def record_error(state, error, *, context=None):
    if not error:
        return False
    return remember_error(
        state,
        error.get("type") or "grammar",
        error.get("original"),
        error.get("correct"),
        context=context,
    )


def process_error(text, state, *, support_level=1, expected_answer=None, context=None):
    """Detect, decide, remember and return one central correction decision."""
    error = detect_error(text)
    decision = decide_correction(
        error,
        state=state,
        support_level=support_level,
        expected_answer=expected_answer,
    )
    if error and decision.get("correct"):
        record_error(state, error, context=context)

    result = {
        "detected": bool(error),
        "error": error,
        "decision": decision,
        "recast": None,
    }
    if error and decision.get("correct"):
        result["recast"] = render_correction(error, decision)
    state["error_engine_v2"] = result
    state["error_engine_v1"] = result  # compatibility
    return result
