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
    # Completion bridges ask for a different semantic slot than their broad
    # domain wording suggests. Resolve these specific shapes before the generic
    # music/sport/food/reading/birthday rules below, otherwise sync state
    # overwrites the bridge slot immediately after it was activated.
    if ("musik" in q or "hörst du" in q or "hoerst du" in q) and any(x in q for x in ("zu hause", "unterwegs")):
        return "music_place"
    if any(x in q for x in ("sport", "machst du diesen sport")) and any(x in q for x in ("draußen", "draussen", "drinnen")):
        return "sport_environment"
    if any(x in q for x in ("isst du", "essen")) and any(x in q for x in ("zu hause", "restaurant")):
        return "food_place"
    if any(x in q for x in ("liest du", "lesen")) and any(x in q for x in ("zu hause", "unterwegs")):
        return "reading_place"
    if "geburtstag" in q and q.startswith(("magst ", "magst du ")):
        return "birthday_preference"
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
        if "mit wem" in q:
            return "birthday_company"
        if any(x in q for x in ("was machst", "wie feierst", "feierst du")):
            return "birthday_activity"
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

def learner_question_context(text):
    """Return stable semantic context for common learner-led questions."""
    q = re.sub(r"^(?:(?:und|aber|also)\s+)+", "", _norm(text))
    if not q:
        return None
    if re.search(r"^was machst du(?: normalerweise)?(?: gern)? am wochenende$", q):
        return {"slot": "activity", "context": "weekend", "topic": "hobby"}
    if re.search(r"^was machst du(?: normalerweise)?(?: gern)? (?:in )?deiner freizeit$", q):
        return {"slot": "activity", "context": "free_time", "topic": "hobby"}
    if re.search(r"^was machst du(?: normalerweise)?(?: gern)? heute abend$", q):
        return {"slot": "activity", "context": "evening", "topic": "today"}
    return None

def semantic_statement_context(text):
    low = _norm(text)
    patterns = (
        (r"^ich\s+lese(?:\s+gern)?\s+(.+)$", "reading_genre", "hobby", "reading"),
        (r"^ich\s+(?:höre|hoere|hore)\s+(?:gern\s+)?(.+)$", "music_genre", "hobby", "music"),
        (r"^ich\s+(?:spiele|mache)\s+(?:gern\s+)?(.+)$", "sport_kind", "hobby", "sport"),
        (r"^ich\s+(?:esse|mag)\s+(?:gern\s+)?(.+)$", "food", "food", "essen"),
    )
    for pattern, slot, topic, subtopic in patterns:
        match = re.match(pattern, low, re.I)
        if match:
            content = match.group(1).strip(" .?!")
            if content not in {"", "gern", "gerne"} and not (slot == "sport_kind" and content in {"das", "es", "etwas"}):
                return {"slot": slot, "topic": topic, "subtopic": subtopic, "content": content}
    return None


def analyze_learner_turn(text, *, last_question=None):
    raw = str(text or "").strip()
    low = _norm(raw)
    words = re.findall(r"[A-Za-zÄÖÜäöüß0-9'-]+", low)
    slot = question_slot(last_question)
    semantic_statement = semantic_statement_context(raw)
    if is_learner_question(raw):
        intent = "question_to_nele"
        slot = question_slot(raw)
    elif semantic_statement:
        intent = "semantic_statement"
        slot = semantic_statement["slot"]
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
        "content": (semantic_statement or {}).get("content") or raw.strip(" .?!"),
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
    activity_context = learner_question_context(text)
    if activity_context:
        if activity_context["context"] == "weekend":
            return "Am Wochenende höre ich gern Musik und lese. Und du, was machst du gern am Wochenende?"
        if activity_context["context"] == "free_time":
            return "Ich lese gern und höre gern Musik. Und du, was machst du gern in deiner Freizeit?"
        if activity_context["context"] == "evening":
            return "Heute Abend lese ich ein bisschen. Und du, was machst du heute Abend?"
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
