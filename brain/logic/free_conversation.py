"""Adaptive everyday conversation for Nele.

Frei sprechen uses the same learner state as the course, but behaves like a
friendly conversation partner. It keeps a topic for several turns, recasts a
small set of frequent A1 errors without lecturing, and changes support based
on how independently the learner answers.
"""
import re

OPENERS = [
    "Hallo! Wie geht's dir heute?",
    "Hallo! Wie war dein Tag?",
    "Schön, dass du da bist. Was machst du gerade?",
    "Hallo! Hast du heute schon etwas Schönes gemacht?",
]

TOPICS = {
    "today": {
        "easy": ["Arbeitest du heute?", "Bist du heute zu Hause?", "Hast du heute viel zu tun?"],
        "normal": ["Was machst du heute?", "Was möchtest du heute noch machen?", "Wie ist dein Tag heute?"],
        "open": ["Was war heute schön oder interessant?", "Erzähl mir ein bisschen von deinem Tag."],
    },
    "yesterday": {
        "easy": ["Warst du gestern zu Hause oder bei der Arbeit?", "War dein Tag gestern gut?"],
        "normal": ["Was hast du gestern gemacht?", "Was war gestern schön?"],
        "open": ["Erzähl mir ein bisschen von gestern. Was ist passiert?"],
    },
    "hobby": {
        "easy": ["Liest du gern?", "Hörst du gern Musik?", "Machst du gern Sport?"],
        "normal": ["Was machst du gern in deiner Freizeit?", "Was machst du am Wochenende gern?", "Was ist dein Hobby?"],
        "open": ["Warum machst du das gern?", "Was gefällt dir daran besonders?"],
    },
    "weather": {
        "easy": ["Ist es bei dir warm oder kalt?", "Regnet es bei dir?", "Magst du Sonne?"],
        "normal": ["Wie ist das Wetter bei dir?", "Was machst du bei diesem Wetter?"],
        "open": ["Welches Wetter magst du am liebsten und warum?"],
    },
    "work": {
        "easy": ["Arbeitest du heute?", "Arbeitest du morgens?", "Ist die Arbeit heute anstrengend?"],
        "normal": ["Was machst du bei der Arbeit?", "Wann fängst du normalerweise an?", "Wie war die Arbeit heute?"],
        "open": ["Was gefällt dir an deiner Arbeit?", "Was war heute bei der Arbeit interessant?"],
    },
    "holiday": {
        "easy": ["Meer oder Berge – was magst du lieber?", "Fährst du gern in den Urlaub?"],
        "normal": ["Wo machst du gern Urlaub?", "Was machst du gern im Urlaub?"],
        "open": ["Wie sieht ein schöner Urlaub für dich aus?", "Wohin möchtest du einmal reisen und warum?"],
    },
}

def _words(text):
    return re.findall(r"[A-Za-zÄÖÜäöüß]+", str(text or ""))

def _difficulty_signal(text):
    value = str(text or "").strip().lower()
    words = _words(value)
    normal_short_answers = {
        "ja", "nein", "ja ja", "nein nein", "gut", "sehr gut", "prima",
        "super", "okay", "ok", "gern", "ja gern", "nein danke",
        "müde", "arbeit", "zu hause"
    }
    struggle = (
        value not in normal_short_answers
        and (
            any(x in value for x in ("weiß nicht", "weiss nicht", "nicht wissen", "keine ahnung"))
            or value in {"?", "..."}
        )
    )
    return struggle, len(words) >= 7

def _detect_topic(text, previous="today"):
    value = str(text or "").lower()
    if "gestern" in value: return "yesterday"
    if any(x in value for x in ("arbeit", "job", "hotel", "kolleg")): return "work"
    if any(x in value for x in ("hobby", "freizeit", "lesen", "buch", "krimi", "sport", "musik")): return "hobby"
    if any(x in value for x in ("wetter", "sonne", "regen", "kalt", "warm", "wind")): return "weather"
    if any(x in value for x in ("urlaub", "reise", "ferien", "meer", "berge")): return "holiday"
    if any(x in value for x in ("heute", "jetzt", "morgen")): return "today"
    return previous if previous in TOPICS else "today"

def _recast(text):
    """Return a short natural reformulation only for very clear A1 patterns."""
    value = str(text or "").strip()
    low = value.lower()
    patterns = [
        (r"^ich\s+gehen\s+(.+)$", lambda m: f"Ah, du gehst {m.group(1)}."),
        (r"^ich\s+arbeiten\s+(.+)$", lambda m: f"Ah, du arbeitest {m.group(1)}."),
        (r"^ich\s+lesen\s+gern(?:\s+(.+))?$", lambda m: "Ah, du liest gern" + (f" {m.group(1)}." if m.group(1) else ".")),
        (r"^ich\s+wohnen\s+(.+)$", lambda m: f"Ah, du wohnst {m.group(1)}."),
    ]
    for pattern, build in patterns:
        match = re.match(pattern, low, re.I)
        if match:
            return build(match)
    if low in {"gut", "sehr gut", "prima", "super"}: return "Schön!"
    if low in {"müde", "ich bin müde"}: return "Oh, du bist müde."
    if low == "arbeit": return "Ah, du arbeitest heute."
    if len(_words(value)) <= 3: return "Verstehe."
    return "Das klingt interessant."

def _pick_question(topic, support, independent, turn, last_question=""):
    data = TOPICS[topic]
    if support >= 2:
        pool = data["easy"]
    elif independent >= 3:
        pool = data["open"]
    else:
        pool = data["normal"]
    choices = [q for q in pool if q != last_question] or pool
    return choices[turn % len(choices)]

def _context_followup(text, last_question):
    low = str(text or "").strip().lower()
    q = str(last_question or "").lower()
    yes = low in {"ja", "ja ja", "ja, gern", "ja gern"}
    no = low in {"nein", "nein nein", "nein, danke", "nein danke"}
    if not (yes or no):
        return None
    if "arbeitest du heute" in q:
        return ("Ah, du arbeitest heute. Wann fängst du an?" if yes
                else "Heute hast du also frei. Was machst du heute?")
    if "zu hause" in q:
        return ("Schön. Was machst du zu Hause?" if yes
                else "Ah, du bist unterwegs. Wo bist du gerade?")
    if "viel zu tun" in q:
        return ("Oh, du hast heute viel zu tun. Was musst du noch machen?" if yes
                else "Das ist schön. Was möchtest du heute machen?")
    if "liest du gern" in q:
        return ("Schön! Was liest du gern?" if yes else "Was machst du lieber in deiner Freizeit?")
    if "musik" in q:
        return ("Welche Musik hörst du gern?" if yes else "Was machst du lieber?")
    if "sport" in q:
        return ("Welchen Sport machst du gern?" if yes else "Was machst du gern in deiner Freizeit?")
    if "regnet" in q:
        return ("Oh, es regnet. Bleibst du heute zu Hause?" if yes else "Ist es sonnig bei dir?")
    if "urlaub" in q:
        return ("Wo machst du gern Urlaub?" if yes else "Was machst du gern in deiner Freizeit?")
    return None

def generate_free_welcome(state, session_id=None):
    free = state.setdefault("free_conversation", {})
    index = int(free.get("welcome_index", 0) or 0)
    free["welcome_index"] = (index + 1) % len(OPENERS)
    free.setdefault("support_level", 1)
    free.setdefault("independent_turns", 0)
    free.setdefault("struggle_turns", 0)
    free.setdefault("last_topic", "today")
    free.setdefault("topic_turns", 0)
    free.setdefault("recent_errors", [])
    free.setdefault("last_question", "")
    state.setdefault("student_progress", {}).setdefault("current_level", "A1.1")
    return OPENERS[index]

def generate_free_conversation_reply(user_message, state, session_id=None):
    free = state.setdefault("free_conversation", {})
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

    previous_topic = free.get("last_topic", "today")
    topic = _detect_topic(user_message, previous_topic)
    topic_turns = int(free.get("topic_turns", 0) or 0)
    topic_turns = topic_turns + 1 if topic == previous_topic else 1

    # Do not jump topics every turn. After a few exchanges, a neutral answer
    # may gently move the conversation back to everyday "today".
    if topic_turns >= 5 and topic == previous_topic and topic != "today" and not struggle:
        topic = "today"
        topic_turns = 1

    turn = int(free.get("turn_count", 0) or 0) + 1
    free.update({
        "independent_turns": independent,
        "struggle_turns": struggles,
        "support_level": support,
        "last_topic": topic,
        "topic_turns": topic_turns,
        "turn_count": turn,
        "last_user_message": str(user_message or "").strip(),
    })

    last_question = free.get("last_question", "")
    contextual = _context_followup(user_message, last_question)
    reaction = _recast(user_message)

    if contextual:
        reply = contextual
        # The follow-up itself becomes the context for the next ja/nein answer.
        question = contextual.split(". ")[-1]
    else:
        question = _pick_question(topic, support, independent, turn, last_question)
        reply = f"{reaction} {question}"
        if struggle:
            reply = f"Kein Problem. 😊 {reply}"

    free["last_question"] = question

    return reply, {
        "conversation_mode": "free",
        "support_level": support,
        "topic": topic,
        "topic_turns": topic_turns,
        "independent_turns": independent,
        "course_level": (state.get("student_progress") or {}).get("current_level", "A1.1"),
    }
