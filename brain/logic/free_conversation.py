"""Natural adaptive free conversation for Nele.

The free mode follows the learner's last answer instead of running a quiz.
It keeps short conversational memory, avoids repeated questions, recasts only
clear A1 errors, and records recurring errors in shared learner state.
"""
import re

OPENERS = [
    "Hallo! Wie geht's dir heute?",
    "Hallo! Wie war dein Tag?",
    "Schön, dass du da bist. Was machst du gerade?",
    "Hallo! Was machst du heute?",
]

# Course level controls what free conversation may actively introduce.
# New lessons can be added here without creating a separate free mode.
LEVEL_ORDER = ["A1.1", "A1.2", "A1.3", "A1.4", "A2.1", "A2.2", "B1.1"]
LEVEL_SKILLS = {
    "A1.1": {"today", "place", "work", "shopping", "hobby", "weather", "holiday"},
    "A1.2": {"yesterday"},
}

FALLBACKS = {
    "today": ["Was machst du heute?", "Was möchtest du heute noch machen?", "Wie ist dein Tag heute?"],
    "work": ["Arbeitest du heute?", "Wann fängst du an?", "Was machst du bei der Arbeit?"],
    "hobby": ["Was machst du gern in deiner Freizeit?", "Hörst du gern Musik?", "Machst du gern Sport?"],
    "weather": ["Wie ist das Wetter bei dir?", "Ist es warm oder kalt?", "Magst du das Wetter heute?"],
    "holiday": ["Wo machst du gern Urlaub?", "Meer oder Berge – was magst du lieber?", "Was machst du gern im Urlaub?"],
    "yesterday": ["Was hast du gestern gemacht?", "Wie war dein Tag gestern?"],
}

YES = {"ja", "ja ja", "ja gern", "ja, gern", "klar", "genau"}
NO = {"nein", "nein nein", "nein danke", "nein, danke"}
NORMAL_SHORT = YES | NO | {
    "gut", "sehr gut", "prima", "super", "okay", "ok", "gern",
    "müde", "arbeit", "zu hause", "zuhause",
}

def _words(text):
    return re.findall(r"[A-Za-zÄÖÜäöüß]+", str(text or ""))

def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower())

def _difficulty_signal(text):
    value = _norm(text)
    explicit = any(x in value for x in (
        "weiß nicht", "weiss nicht", "keine ahnung", "ich verstehe nicht",
        "verstehe nicht",
    )) or value in {"?", "..."}
    # A short correct answer is normal in a real conversation, not failure.
    struggle = explicit and value not in NORMAL_SHORT
    return struggle, len(_words(value)) >= 7

def _allowed_skills(level):
    skills = set()
    try:
        upto = LEVEL_ORDER.index(level)
    except ValueError:
        upto = 0
    for item in LEVEL_ORDER[:upto + 1]:
        skills.update(LEVEL_SKILLS.get(item, set()))
    return skills or set(LEVEL_SKILLS["A1.1"])

def _extract_facts(text):
    """Extract only facts that are clear enough to reuse naturally."""
    value = str(text or "").strip()
    low = value.lower()
    facts = {}

    # Places: "Ich bin heute in Heidelberg", "Ich bin in Mannheim".
    m = re.search(r"\bich\s+bin(?:\s+heute)?\s+in\s+([A-ZÄÖÜ][A-Za-zÄÖÜäöüß-]+)", value)
    if m:
        facts["place"] = m.group(1)

    # Shopping and object.
    if re.search(r"\b(?:ich\s+)?(?:kaufe|kaufen|kauf)\b", low):
        facts["activity"] = "shopping"
        if "schuh" in low:
            facts["shopping_item"] = "Schuhe"
    if "sportschuh" in low:
        facts["shopping_item"] = "Sportschuhe"

    if re.search(r"\bmein\s+tag\b", low):
        facts["topic"] = "today"
        facts["day_statement"] = True

    # Simple colors useful for shopping follow-ups.
    for color in ("schwarz", "blau", "rot", "grün", "grau", "rosa", "weiß", "braun"):
        if re.search(rf"\b{color}\w*\b", low):
            facts["color"] = color.capitalize()
            break

    if any(x in low for x in ("arbeit", "job", "hotel")):
        facts["topic"] = "work"
    elif any(x in low for x in ("hobby", "freizeit", "musik", "sport", "lesen", "buch")):
        facts["topic"] = "hobby"
    elif any(x in low for x in ("wetter", "sonne", "regen", "kalt", "warm")):
        facts["topic"] = "weather"
    elif any(x in low for x in ("urlaub", "reise", "ferien", "meer", "berge")):
        facts["topic"] = "holiday"
    elif "gestern" in low:
        facts["topic"] = "yesterday"
    return facts

def _error_and_recast(text):
    """Return (natural recast, error key). Never interrupt with grammar theory."""
    value = str(text or "").strip()
    low = value.lower()
    patterns = [
        (r"^ich\s+kaufen\s+(.+)$", "ich_kaufen", lambda m: f"Ah, du kaufst {m.group(1)}."),
        (r"^ich\s+gehen\s+(.+)$", "ich_gehen", lambda m: f"Ah, du gehst {m.group(1)}."),
        (r"^ich\s+arbeiten(?:\s+(.+))?$", "ich_arbeiten", lambda m: "Ah, du arbeitest" + (f" {m.group(1)}." if m.group(1) else ".")),
        (r"^ich\s+lesen\s+gern(?:\s+(.+))?$", "ich_lesen", lambda m: "Ah, du liest gern" + (f" {m.group(1)}." if m.group(1) else ".")),
        (r"^ich\s+wohnen\s+(.+)$", "ich_wohnen", lambda m: f"Ah, du wohnst {m.group(1)}."),
    ]
    for pattern, key, build in patterns:
        match = re.match(pattern, low, re.I)
        if match:
            return build(match), key
    return None, None

def _record_error(state, free, key, original):
    if not key:
        return
    counts = free.setdefault("error_counts", {})
    counts[key] = int(counts.get(key, 0) or 0) + 1
    if counts[key] < 2:
        return

    # Shared memory: course mode can consume these recurring errors later.
    shared = state.setdefault("learner_memory", {})
    recurring = shared.setdefault("recurring_errors", [])
    existing = next((x for x in recurring if isinstance(x, dict) and x.get("key") == key), None)
    if existing:
        existing["count"] = counts[key]
        existing["last_example"] = str(original or "").strip()
    else:
        recurring.append({
            "key": key,
            "count": counts[key],
            "last_example": str(original or "").strip(),
            "source": "free_conversation",
        })
    del recurring[:-12]

def _remember_question(free, question):
    if not question:
        return
    free["last_question"] = question
    history = free.setdefault("recent_questions", [])
    if not history or history[-1] != question:
        history.append(question)
    del history[:-8]

def _not_recent(free, candidates):
    recent = set(free.get("recent_questions", [])[-5:])
    available = [q for q in candidates if q not in recent]
    return available or candidates

def _yes_no_followup(text, last_question, facts):
    low = _norm(text)
    yes, no = low in YES, low in NO
    if not (yes or no):
        return None

    q = _norm(last_question)
    if "suchst du sportschuhe" in q:
        return "Welche Farbe möchtest du?" if yes else "Welche Schuhe suchst du?"
    if "arbeitest du heute" in q:
        return "Wann fängst du an?" if yes else "Heute hast du also frei. Was machst du heute?"
    if "bist du heute zu hause" in q:
        return "Was machst du zu Hause?" if yes else "Ah, du bist unterwegs. Wo bist du gerade?"
    if "hast du heute viel zu tun" in q:
        return "Was musst du noch machen?" if yes else "Das ist schön. Was möchtest du heute machen?"
    if "hörst du gern musik" in q:
        return "Welche Musik hörst du gern?" if yes else "Was machst du lieber in deiner Freizeit?"
    if "machst du gern sport" in q:
        return "Welchen Sport machst du gern?" if yes else "Was machst du gern in deiner Freizeit?"
    if "hast du schon schöne schuhe" in q:
        if yes:
            facts["shopping_complete"] = True
            return "Super! Gefallen dir die Schuhe?"
        return "Welche Schuhe suchst du?"
    if "gefallen dir die schuhe" in q:
        facts["shopping_complete"] = True
        return "Schön! Und wie ist dein Tag heute?" if yes else "Oh, schade. Suchst du noch weiter?"
    if "magst du das wetter heute" in q:
        return "Schön! Was machst du bei diesem Wetter gern?" if yes else "Was machst du bei diesem Wetter lieber?"
    if "magst du das wetter" in q:
        return "Schön! Was machst du bei diesem Wetter gern?" if yes else "Was machst du bei diesem Wetter lieber?"
    return None

def _content_followup(text, facts, memory, free, level):
    """Choose a question from the learner's content before any generic pool."""
    low = _norm(text)
    place = facts.get("place") or memory.get("place")
    item = facts.get("shopping_item") or memory.get("shopping_item")
    color = facts.get("color") or memory.get("color")

    if facts.get("place"):
        return f"Schön! Was machst du in {facts['place']}?"

    if facts.get("activity") == "shopping" and item == "Schuhe":
        return "Suchst du Sportschuhe?"

    if facts.get("activity") == "shopping":
        return "Was möchtest du kaufen?"

    # A one-word color is meaningful after a shopping/color question.
    # Keep very short weather answers attached to the weather question.
    last_q = _norm(free.get("last_question", ""))
    if "warm oder kalt" in last_q:
        if low in {"warm", "waren", "war"}:
            memory["weather"] = "warm"
            return "Ah, es ist warm. Ist es auch sonnig?"
        if low == "kalt":
            memory["weather"] = "kalt"
            return "Oh, es ist kalt. Bleibst du heute lieber drinnen?"

    if "es regnet" in low or low == "regen":
        memory["weather"] = "Regen"
        return "Oh, es regnet. Magst du das Wetter heute?"

    if facts.get("day_statement"):
        # "schon" is a very common keyboard/ASR spelling for "schön" here.
        if re.search(r"\b(?:schon|schön)\b", low):
            return "Das freut mich! Was war heute schön?"
        if "gut" in low:
            return "Das freut mich! Was war heute gut?"
        return "Erzähl mir ein bisschen von deinem Tag."

    if color and (
        "farbe" in _norm(free.get("last_question", ""))
        or (item and not memory.get("shopping_complete"))
    ):
        if place:
            return f"{color} passt gut. Hast du schon schöne Schuhe in {place} gefunden?"
        return f"{color} passt gut. Hast du schon schöne Schuhe gefunden?"

    if "ich bin müde" in low or low == "müde":
        return "Oh, du bist müde. War dein Tag anstrengend?"

    if re.search(r"\bich\s+arbeite\b", low):
        return "Wann fängst du an?"
    if re.search(r"\bich\s+(?:höre|mag)\b.*musik", low):
        return "Welche Musik hörst du gern?"
    if re.search(r"\bich\s+lese\b", low):
        return "Was liest du gern?"

    return None

def _generic_followup(topic, free, support, independent, level):
    allowed = _allowed_skills(level)
    if topic == "yesterday" and "yesterday" not in allowed:
        topic = "today"
    pool = FALLBACKS.get(topic, FALLBACKS["today"])
    pool = _not_recent(free, pool)
    # More independent learners get the more open end of the same A1 material.
    index = -1 if independent >= 3 and support == 0 else 0
    return pool[index]

def generate_free_welcome(state, session_id=None):
    free = state.setdefault("free_conversation", {})
    index = int(free.get("welcome_index", 0) or 0)
    free["welcome_index"] = (index + 1) % len(OPENERS)
    free["last_question"] = OPENERS[index]
    free["recent_questions"] = [OPENERS[index]]
    free["turn_count"] = 0
    free["support_level"] = 1
    free["independent_turns"] = 0
    free["struggle_turns"] = 0
    free["topic_turns"] = 0
    free["conversation_facts"] = {}
    free.setdefault("error_counts", {})
    state.setdefault("student_progress", {}).setdefault("current_level", "A1.1")
    return OPENERS[index]

def generate_free_conversation_reply(user_message, state, session_id=None):
    free = state.setdefault("free_conversation", {})
    progress = state.setdefault("student_progress", {})
    level = str(progress.get("current_level", "A1.1") or "A1.1")

    struggle, strong = _difficulty_signal(user_message)
    independent = int(free.get("independent_turns", 0) or 0)
    struggles = int(free.get("struggle_turns", 0) or 0)
    support = int(free.get("support_level", 1) or 1)

    if struggle:
        struggles += 1
        independent = 0
        support = min(3, support + 1)
    else:
        independent += 1
        struggles = max(0, struggles - 1)
        if strong or independent >= 3:
            support = max(0, support - 1)

    facts = _extract_facts(user_message)
    memory = free.setdefault("conversation_facts", {})
    memory.update({k: v for k, v in facts.items() if k not in {"topic", "day_statement"}})

    # A clear new everyday topic closes the active shopping branch. Keep the
    # useful facts (place/color) in memory, but do not let them hijack replies.
    if facts.get("day_statement"):
        memory["shopping_complete"] = True

    previous_topic = free.get("last_topic", "today")
    topic = facts.get("topic", previous_topic)
    if facts.get("activity") == "shopping":
        topic = "shopping"
    elif facts.get("place"):
        topic = "place"

    last_question = free.get("last_question", "")
    recast, error_key = _error_and_recast(user_message)
    _record_error(state, free, error_key, user_message)

    # Priority: answer context -> learner content -> safe course-level fallback.
    question = _yes_no_followup(user_message, last_question, memory)
    if not question:
        question = _content_followup(user_message, facts, memory, free, level)
    if not question:
        question = _generic_followup(topic, free, support, independent, level)

    # Do not repeat the same question. If a content rule happens to return it,
    # fall back to a different everyday question.
    if question == last_question:
        question = _generic_followup("today", free, support, independent, level)
        if question == last_question:
            question = _not_recent(free, FALLBACKS["today"])[0]

    if struggle:
        reply = f"Kein Problem. {question}"
    elif recast:
        reply = f"{recast} {question}"
    elif _norm(user_message) in {"gut", "sehr gut", "prima", "super"}:
        reply = f"Schön! {question}"
    elif _norm(user_message) in YES | NO:
        reply = question
    else:
        reply = question

    turn = int(free.get("turn_count", 0) or 0) + 1
    free.update({
        "independent_turns": independent,
        "struggle_turns": struggles,
        "support_level": support,
        "last_topic": topic,
        "topic_turns": int(free.get("topic_turns", 0) or 0) + 1,
        "turn_count": turn,
        "last_user_message": str(user_message or "").strip(),
    })
    _remember_question(free, question)

    return reply, {
        "conversation_mode": "free",
        "support_level": support,
        "topic": topic,
        "independent_turns": independent,
        "course_level": level,
        "conversation_facts": dict(memory),
        "recurring_errors": list((state.get("learner_memory") or {}).get("recurring_errors", [])),
    }
