# ==========================================
# NELE – A1 VERB CORRECTION ENGINE
# Lightweight deterministic correction for common present-tense learner errors.
# ==========================================

import re

from brain.logic.matcher import normalize


A1_VERBS = {
    "machen": {
        "ich": "mache", "du": "machst", "er": "macht", "sie": "macht",
        "es": "macht", "wir": "machen", "ihr": "macht", "sie_pl": "machen",
    },
    "gehen": {
        "ich": "gehe", "du": "gehst", "er": "geht", "sie": "geht",
        "es": "geht", "wir": "gehen", "ihr": "geht", "sie_pl": "gehen",
    },
    "fahren": {
        "ich": "fahre", "du": "fährst", "er": "fährt", "sie": "fährt",
        "es": "fährt", "wir": "fahren", "ihr": "fahrt", "sie_pl": "fahren",
    },
    "arbeiten": {
        "ich": "arbeite", "du": "arbeitest", "er": "arbeitet", "sie": "arbeitet",
        "es": "arbeitet", "wir": "arbeiten", "ihr": "arbeitet", "sie_pl": "arbeiten",
    },
    "kochen": {
        "ich": "koche", "du": "kochst", "er": "kocht", "sie": "kocht",
        "es": "kocht", "wir": "kochen", "ihr": "kocht", "sie_pl": "kochen",
    },
    "essen": {
        "ich": "esse", "du": "isst", "er": "isst", "sie": "isst",
        "es": "isst", "wir": "essen", "ihr": "esst", "sie_pl": "essen",
    },
    "trinken": {
        "ich": "trinke", "du": "trinkst", "er": "trinkt", "sie": "trinkt",
        "es": "trinkt", "wir": "trinken", "ihr": "trinkt", "sie_pl": "trinken",
    },
    "wohnen": {
        "ich": "wohne", "du": "wohnst", "er": "wohnt", "sie": "wohnt",
        "es": "wohnt", "wir": "wohnen", "ihr": "wohnt", "sie_pl": "wohnen",
    },
    "lernen": {
        "ich": "lerne", "du": "lernst", "er": "lernt", "sie": "lernt",
        "es": "lernt", "wir": "lernen", "ihr": "lernt", "sie_pl": "lernen",
    },
    "sprechen": {
        "ich": "spreche", "du": "sprichst", "er": "spricht", "sie": "spricht",
        "es": "spricht", "wir": "sprechen", "ihr": "sprecht", "sie_pl": "sprechen",
    },
    "haben": {
        "ich": "habe", "du": "hast", "er": "hat", "sie": "hat",
        "es": "hat", "wir": "haben", "ihr": "habt", "sie_pl": "haben",
    },
    "sein": {
        "ich": "bin", "du": "bist", "er": "ist", "sie": "ist",
        "es": "ist", "wir": "sind", "ihr": "seid", "sie_pl": "sind",
    },
}


SUBJECTS = ("ich", "du", "er", "sie", "es", "wir", "ihr")


def _capitalized_sentence(text):
    text = str(text or "").strip()
    if not text:
        return text
    text = text[:1].upper() + text[1:]
    if text[-1] not in ".?!":
        text += "."
    return text


def find_a1_verb_correction(user_message):
    """
    Correct a common pattern such as:
      Ich fahren Fahrrad. -> Ich fahre Fahrrad.
      Du fahren Rad.      -> Du fährst Rad.

    The engine is conservative: it only changes a token when that token is a
    known infinitive placed directly after a known subject.
    """
    original = str(user_message or "").strip()
    normalized = normalize(original).strip(" .?!„“\"'")

    if not normalized:
        return None

    tokens = normalized.split()
    if len(tokens) < 2:
        return None

    subject = tokens[0]
    infinitive = tokens[1]

    if subject not in SUBJECTS:
        return None

    forms = A1_VERBS.get(infinitive)
    if not forms:
        return None

    correct_form = forms.get(subject)
    if not correct_form or correct_form == infinitive:
        return None

    corrected_tokens = original.rstrip(".?!").split()
    if len(corrected_tokens) < 2:
        return None

    corrected_tokens[1] = correct_form
    corrected = _capitalized_sentence(" ".join(corrected_tokens))

    return {
        "original_message": original,
        "corrected_message": corrected,
        "feedback": (
            "Fast richtig 😊 Du kannst sagen: "
            f"„{corrected}“"
        ),
        "error_type": "verb_conjugation",
        "verb": infinitive,
        "subject": subject,
        "correct_form": correct_form,
    }
