"""Shared learner-turn analysis for free conversation.

This module separates what the learner is doing now from what Nele expected
from the previous turn. It intentionally stays small and deterministic so
Teacher Policy and routers can consume the same signal.
"""
import re

VERSION = 1

ELLIPTICAL_TOPIC_QUESTIONS = {
    "sport": {"slot": "sport_kind", "topic": "hobby", "subtopic": "sport"},
    "musik": {"slot": "music_genre", "topic": "hobby", "subtopic": "music"},
    "lesen": {"slot": "reading_genre", "topic": "hobby", "subtopic": "reading"},
    "bücher": {"slot": "reading_genre", "topic": "hobby", "subtopic": "reading"},
    "buecher": {"slot": "reading_genre", "topic": "hobby", "subtopic": "reading"},
    "essen": {"slot": "food", "topic": "food", "subtopic": "essen"},
    "arbeit": {"slot": "work_activity", "topic": "work", "subtopic": "work"},
}

def elliptical_topic_question(text):
    """Understand natural hand-off questions such as 'Und Sport?'."""
    raw = str(text or "").strip()
    if "?" not in raw:
        return None
    q = _norm(raw)
    q = re.sub(r"^(?:(?:und|aber|also)\s+)+", "", q)
    return ELLIPTICAL_TOPIC_QUESTIONS.get(q)

def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip(" ?!.")

def question_slot(question):
    q = _norm(question)
    if not q:
        return None
    # The broad work activity question owns a semantic work slot. More generic
    # shapes such as Wo/Mit wem/Bis wann keep their generic lexical slot here;
    # Response Understanding refines them from the canonical active_slot.
    if ("arbeit" in q or "job" in q) and any(x in q for x in ("was machst", "was arbeitest", "beruf")):
        return "work_activity"
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
    if elliptical_topic_question(raw):
        return True
    q = re.sub(r"^(?:(?:und|aber|also)\s+)+", "", _norm(raw))
    return q.startswith((
        "was ", "wie ", "wo ", "woher ", "wohin ", "wann ", "warum ", "wer ",
        "welcher ", "welche ", "welchen ", "welchem ", "welches ", "arbeitest ", "wohnst ", "isst ",
        "trinkst ", "magst ", "machst ", "hast ", "bist ", "kommst ", "liest ",
        "siehst ", "gehst ", "fährst ", "faehrst ",
    ))

def is_reciprocal_question(text):
    return _norm(text) in {"und du", "du", "und bei dir", "bei dir"}

def reciprocal_nele_answer(text, last_question):
    if not is_reciprocal_question(text): return None
    q = _norm(last_question)
    if not q: return None
    if ("haus" in q and "wohnung" in q) or "wohnst du allein" in q: return "Ich wohne nicht wirklich in einem Haus oder in einer Wohnung."
    if q.startswith(("wo wohnst du", "wo lebst du")): return "Ich wohne nicht wirklich an einem Ort."
    if "woher kommst du" in q: return "Ich komme nicht wirklich aus einem Land. Ich bin deine Deutschtrainerin."
    if "was gefällt dir daran" in q or "was gefaellt dir daran" in q: return "Mir gefällt zum Beispiel die Spannung."
    if "liest du oft" in q: return "Ja, ich lese oft."
    if any(x in q for x in ("was liest du", "liest du gern")): return "Ich lese gern Krimis."
    if any(x in q for x in ("welche musik", "hörst du gern", "hoerst du gern")): return "Ich höre nicht wirklich Musik, aber ich spreche gern darüber."
    if "mit wem machst du sport" in q: return "Ich mache nicht wirklich Sport, also habe ich auch keinen Sportpartner."
    if "wie oft machst du das" in q: return "Ich mache das nicht wirklich, aber wir können gern darüber sprechen."
    if any(x in q for x in ("welchen sport", "machst du sport", "spielst du")): return "Ich mache nicht wirklich Sport, aber ich spreche gern darüber."
    if any(x in q for x in ("was isst du", "isst du gern")): return "Ich esse nicht wirklich, aber ich spreche gern über Essen."
    if "was machst du heute" in q: return "Heute übe ich Deutsch mit dir."
    if any(x in q for x in ("freizeit", "was machst du gern")): return "Ich lese gern und höre gern Musik."
    return None

def learner_question_context(text):
    """Return stable semantic context for common learner-led questions."""
    elliptical = elliptical_topic_question(text)
    if elliptical:
        return dict(elliptical)
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
        elliptical = elliptical_topic_question(raw)
        slot = (elliptical or {}).get("slot") or question_slot(raw)
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
    elliptical = elliptical_topic_question(text)
    if elliptical:
        replies = {
            "sport": "Sport? Ich mache nicht wirklich Sport, aber ich spreche gern darüber. Welchen Sport machst du gern?",
            "music": "Musik? Ich höre nicht wirklich Musik, aber ich spreche gern darüber. Welche Musik hörst du gern?",
            "reading": "Lesen? Ich lese gern Krimis. Was liest du gern?",
            "essen": "Essen? Ich esse nicht wirklich, aber ich spreche gern darüber. Was isst du gern?",
            "work": "Arbeit? Ich bin deine Deutschtrainerin. Was machst du bei der Arbeit?",
        }
        return replies.get(elliptical.get("subtopic"))
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
