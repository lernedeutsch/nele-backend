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
        if "oft" in q or "wie oft" in q:
            return "food_frequency"
        if any(x in q for x in ("womit", "mit was", "dazu", "darauf")):
            return "food_detail"
        return "food"
    if any(x in q for x in ("film", "kino", "serie")):
        return "film_genre"
    if any(x in q for x in ("buch", "bücher", "buecher", "liest du", "lesen")):
        if "oft" in q:
            return "reading_frequency"
        return "reading_genre"
    # Specific semantic domains must outrank broad interrogative words.
    if "geburtstag" in q:
        return "birthday"
    if q.startswith(("wann ", "um wie viel", "bis wann")):
        return "time"
    if any(x in q for x in ("musik", "hörst du", "hoerst du", "sänger", "saenger", "band", "künstler", "kuenstler")):
        if "oft" in q:
            return "music_frequency"
        if any(x in q for x in ("sänger", "saenger", "band", "künstler", "kuenstler")):
            return "music_artist"
        return "music_genre"
    if "mit wem" in q or "mit jemandem" in q:
        if any(x in q for x in ("sport", "spiel", "fußball", "fussball", "schwimm")):
            return "sport_companion"
        return "person"
    if q.startswith(("wo ", "woher ", "wohin ")):
        return "place"
    if any(x in q for x in ("sport", "schwimmen", "fußball", "fussball", "spielst du")):
        if "oft" in q or "wie oft" in q:
            return "sport_frequency"
        return "sport_kind"
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
        "welcher ", "welche ", "welchen ", "welchem ", "welches ", "arbeitest ", "wohnst ", "isst ",
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
    if re.search(r"^wann hast du geburtstag$", q):
        return "Ich habe keinen Geburtstag wie ein Mensch. Wann hast du Geburtstag?"
    if re.search(r"^welche musik hörst du gern$", q) or re.search(r"^welche musik hoerst du gern$", q):
        return "Ich höre nicht wirklich Musik, aber ich spreche gern darüber. Welche Musik hörst du gern?"
    if re.search(r"^welchen sport machst du gern$", q):
        return "Ich mache nicht wirklich Sport, aber ich spreche gern darüber. Welchen Sport machst du gern?"
    return None
