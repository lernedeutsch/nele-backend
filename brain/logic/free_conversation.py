"""Natural, adaptive free-speaking mode for Nele.

This mode deliberately lives beside Teacher Mode. It reuses the same learner
state, but does not start lessons or exercises. Difficulty grows gently with
the learner and falls back when an answer shows difficulty.
"""

import re


OPENERS = [
    "Hallo! Wie geht's dir heute?",
    "Hallo! Wie war dein Tag?",
    "Schön, dass du da bist. Was machst du gerade?",
    "Hallo! Hast du heute schon etwas Schönes gemacht?",
]

TOPIC_QUESTIONS = {
    "today": ["Was machst du heute?", "Hast du heute gearbeitet?", "Was möchtest du heute noch machen?"],
    "yesterday": ["Was hast du gestern gemacht?", "War dein Tag gestern gut?"],
    "hobby": ["Was machst du gern in deiner Freizeit?", "Was ist dein Hobby?", "Was machst du am Wochenende gern?"],
    "weather": ["Wie ist das Wetter bei dir?", "Magst du dieses Wetter?"],
    "work": ["Arbeitest du heute?", "Was machst du bei der Arbeit?", "Wann fängst du normalerweise an?"],
    "holiday": ["Machst du gern Urlaub?", "Wo machst du gern Urlaub?", "Meer oder Berge – was magst du lieber?"],
}

EASY_CHOICES = [
    "Magst du das oder eher nicht?",
    "Machst du das morgens oder abends?",
    "Lieber zu Hause oder draußen?",
]

def _words(text):
    return re.findall(r"[A-Za-zÄÖÜäöüß]+", str(text or ""))

def _difficulty_signal(text):
    value = str(text or "").strip().lower()
    words = _words(value)
    struggle = (
        len(words) <= 1
        or "weiß nicht" in value
        or "weiss nicht" in value
        or "nicht wissen" in value
        or value in {"?", "...", "keine ahnung"}
    )
    strong = len(words) >= 7
    return struggle, strong

def _topic(text):
    value = str(text or "").lower()
    if "gestern" in value: return "yesterday"
    if any(x in value for x in ("arbeit", "job", "hotel")): return "work"
    if any(x in value for x in ("hobby", "freizeit", "lesen", "sport", "musik")): return "hobby"
    if any(x in value for x in ("wetter", "sonne", "regen", "kalt", "warm")): return "weather"
    if any(x in value for x in ("urlaub", "reise", "ferien", "meer", "berge")): return "holiday"
    return "today"

def _natural_echo(text):
    value = str(text or "").strip()
    low = value.lower()
    if low in {"gut", "sehr gut", "prima", "super"}:
        return "Schön!"
    if low in {"müde", "ich bin müde"}:
        return "Oh, du bist müde."
    if low == "arbeit":
        return "Ah, du arbeitest heute."
    if len(_words(value)) <= 3:
        return "Verstehe."
    return "Das klingt interessant."

def generate_free_welcome(state, session_id=None):
    free = state.setdefault("free_conversation", {})
    turn = int(free.get("welcome_index", 0) or 0)
    free["welcome_index"] = (turn + 1) % len(OPENERS)
    free.setdefault("support_level", 1)
    free.setdefault("independent_turns", 0)
    free.setdefault("struggle_turns", 0)
    free.setdefault("recent_errors", [])
    state.setdefault("student_progress", {}).setdefault("current_level", "A1")
    return OPENERS[turn]

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
    elif strong:
        independent += 1
        struggles = max(0, struggles - 1)
        if independent >= 2:
            support = max(0, support - 1)
    else:
        independent += 1

    free["independent_turns"] = independent
    free["struggle_turns"] = struggles
    free["support_level"] = support

    topic = _topic(user_message)
    free["last_topic"] = topic
    free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1

    echo = _natural_echo(user_message)

    if struggle or support >= 3:
        question = EASY_CHOICES[free["turn_count"] % len(EASY_CHOICES)]
    else:
        pool = TOPIC_QUESTIONS.get(topic, TOPIC_QUESTIONS["today"])
        question = pool[free["turn_count"] % len(pool)]

    # Gentle 90/10 growth: at higher independence use a slightly more open
    # question, without turning the conversation into a grammar exercise.
    if independent >= 3 and not struggle:
        open_questions = {
            "today": "Was war heute besonders schön oder interessant?",
            "yesterday": "Erzähl mir ein bisschen von gestern. Was ist passiert?",
            "hobby": "Warum machst du das gern?",
            "weather": "Was machst du gern bei diesem Wetter?",
            "work": "Was gefällt dir an deiner Arbeit?",
            "holiday": "Wie sieht ein schöner Urlaub für dich aus?",
        }
        question = open_questions.get(topic, question)

    return f"{echo} {question}", {
        "conversation_mode": "free",
        "support_level": support,
        "topic": topic,
        "independent_turns": independent,
        "course_level": (state.get("student_progress") or {}).get("current_level", "A1"),
    }
