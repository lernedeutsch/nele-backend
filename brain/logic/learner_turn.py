"""Shared learner-turn analysis for free conversation.

This module separates what the learner is doing now from what Nele expected
from the previous turn. It intentionally stays small and deterministic so
Teacher Policy and routers can consume the same signal.
"""
import re

VERSION = 1

def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip(" ?!.")

def question_slot(question):
    q = _norm(question)
    if not q:
        return None
    if any(x in q for x in ("isst du", "essen", "kochst du", "gericht", "frühstück", "fruehstueck")):
        return "food"
    if any(x in q for x in ("film", "kino", "serie")):
        return "film_genre"
    if any(x in q for x in ("buch", "bücher", "buecher", "liest du", "lesen")):
        return "reading"
    if q.startswith(("wann ", "um wie viel", "bis wann")):
        return "time"
    if q.startswith(("wo ", "woher ", "wohin ")):
        return "place"
    if "mit wem" in q or "mit jemandem" in q:
        return "person"
    if any(x in q for x in ("freizeit", "hobby", "machst du gern")):
        return "activity"
    if any(x in q for x in ("arbeit", "job")):
        return "work"
    return "content"

def is_learner_question(text):
    raw = str(text or "").strip()
    if "?" not in raw:
        return False
    q = re.sub(r"^(?:(?:und|aber|also)\s+)+", "", _norm(raw))
    return q.startswith((
        "was ", "wie ", "wo ", "woher ", "wohin ", "wann ", "warum ", "wer ",
        "welcher ", "welche ", "welches ", "arbeitest ", "wohnst ", "isst ",
        "trinkst ", "magst ", "machst ", "hast ", "bist ", "kommst ", "liest ",
        "siehst ", "gehst ", "fährst ", "faehrst ",
    ))

def analyze_learner_turn(text, *, last_question=None):
    raw = str(text or "").strip()
    low = _norm(raw)
    words = re.findall(r"[A-Za-zÄÖÜäöüß0-9'-]+", low)
    slot = question_slot(last_question)
    if is_learner_question(raw):
        intent = "question_to_nele"
        slot = question_slot(raw)
    elif len(words) <= 5 and last_question:
        intent = "short_answer"
    elif last_question:
        intent = "answer_to_nele_question"
    else:
        intent = "statement"
    return {
        "version": VERSION,
        "intent": intent,
        "slot": slot,
        "content": raw.strip(" .?!"),
        "last_question": str(last_question or "").strip() or None,
    }

def direct_nele_answer(text):
    """Answer common learner-led A1/A2 questions before asking a follow-up."""
    q = _norm(text)
    q = re.sub(r"^(?:(?:und|aber|also)\s+)+", "", q)
    if re.search(r"^was machst du heute abend$", q):
        return "Heute Abend lese ich ein bisschen. Und du, was machst du heute Abend?"
    if re.search(r"^was machst du heute$", q):
        return "Heute übe ich Deutsch mit dir. Und du, was machst du heute?"
    if re.search(r"^was machst du gern(?: in deiner freizeit)?$", q):
        return "Ich lese gern und höre gern Musik. Und du, was machst du gern?"
    if re.search(r"^was (?:liest|liest du)\b", q) or q == "was liest du gern":
        return "Ich lese gern Krimis. Und du, was liest du gern?"
    if re.search(r"^was isst du gern$", q):
        return "Ich mag gern Pizza. Und du, was isst du gern?"
    return None
