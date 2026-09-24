"""Central Conversation State v2 for Nele free conversation.

This module is intentionally backward compatible. Existing free_conversation
fields remain available while conversation_state_v2 becomes the canonical,
structured snapshot other engines can consume.
"""

STATE_VERSION = 2


def _free(state):
    return state.setdefault("free_conversation", {})


def _facts(free):
    return free.setdefault("conversation_facts", {})


def infer_expected_answer(question):
    q = str(question or "").strip().lower()
    if not q:
        return None
    yes_no_starts = (
        "arbeitest ", "bist ", "hast ", "hörst ", "hoerst ", "machst ",
        "fährst ", "faehrst ", "schwimmst ", "spielst ", "kochst ",
        "magst ", "ist ", "gehst ",
    )
    if q.startswith(yes_no_starts):
        return "yes_no"
    if q.startswith(("wann ", "bis wann ")):
        return "time"
    if q.startswith(("wo ", "woher ")):
        return "place"
    if q.startswith(("wer ", "mit wem ")):
        return "person"
    if q.startswith(("was ", "welche ", "welchen ", "wie ")):
        return "open"
    return "open"


def infer_subtopic(topic, facts, question=""):
    topic = str(topic or "today")
    q = str(question or "").lower()
    activity = str((facts or {}).get("work_activity") or (facts or {}).get("activity") or "").lower()
    if topic == "work" and (activity == "kochen" or "koch" in q):
        return "kochen"
    if topic == "weather":
        return "wetter"
    if topic == "hobby":
        return activity or "freizeit"
    if topic == "food":
        return "essen"
    return None


def infer_goal(topic, subtopic=None):
    goals = {
        "work": "über Arbeit sprechen",
        "hobby": "über Freizeit sprechen",
        "weather": "über Wetter sprechen",
        "food": "über Essen sprechen",
        "holiday": "über Urlaub sprechen",
        "yesterday": "über gestern sprechen",
        "today": "über den Tag sprechen",
        "shopping": "über Einkaufen sprechen",
        "place": "über Orte sprechen",
    }
    if topic == "work" and subtopic == "kochen":
        return "über Arbeit und Kochen sprechen"
    return goals.get(topic, "ein einfaches A1-Gespräch führen")


def sync_conversation_state(state, *, topic=None, last_question=None, level=None):
    free = _free(state)
    facts = _facts(free)
    current_topic = topic or free.get("last_topic") or "today"
    question = last_question if last_question is not None else free.get("last_question", "")
    subtopic = infer_subtopic(current_topic, facts, question)
    current_level = str(level or (state.get("student_progress") or {}).get("current_level") or "A1.1")

    snapshot = state.setdefault("conversation_state_v2", {})
    snapshot.update({
        "version": STATE_VERSION,
        "mode": "free",
        "topic": current_topic,
        "subtopic": subtopic,
        "last_question": question,
        "expected_answer": infer_expected_answer(question),
        "activity": facts.get("work_activity") or facts.get("activity"),
        "food": facts.get("favorite_cooked_food") or facts.get("other_cooked_food") or facts.get("cooked_food") or facts.get("food"),
        "conversation_goal": infer_goal(current_topic, subtopic),
        "support_level": current_level.split(".")[0],
        "adaptive_support": int(free.get("support_level", 1) or 1),
        "turn_number": int(free.get("turn_count", 0) or 0),
    })
    return snapshot


def reset_conversation_state(state, *, opener="", level=None):
    state["conversation_state_v2"] = {}
    return sync_conversation_state(state, topic="today", last_question=opener, level=level)


def get_conversation_state(state):
    return dict(state.get("conversation_state_v2") or {})
