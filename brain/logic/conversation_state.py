"""Central Conversation State v2 for Nele free conversation.

This module is intentionally backward compatible. Existing free_conversation
fields remain available while conversation_state_v2 becomes the canonical,
structured snapshot other engines can consume.
"""

import re

STATE_VERSION = 2

SLOT_CONTEXT = {
    "music_genre": ("hobby", "music"),
    "music_artist": ("hobby", "music"),
    "music_frequency": ("hobby", "music"),
    "music_place": ("hobby", "music"),
    "sport_kind": ("hobby", "sport"),
    "sport_companion": ("hobby", "sport"),
    "sport_frequency": ("hobby", "sport"),
    "sport_environment": ("hobby", "sport"),
    "reading_genre": ("hobby", "reading"),
    "reading_detail": ("hobby", "reading"),
    "reading_frequency": ("hobby", "reading"),
    "reading_place": ("hobby", "reading"),
    "food": ("food", "essen"),
    "food_item": ("food", "essen"),
    "food_detail": ("food", "essen"),
    "food_frequency": ("food", "essen"),
    "food_place": ("food", "essen"),
    "birthday": ("personal", "birthday"),
    "birthday_company": ("personal", "birthday"),
    "birthday_activity": ("personal", "birthday"),
    "birthday_preference": ("personal", "birthday"),
}

QUESTION_SLOT_CONTEXT = {
    "music_genre": ("hobby", "music"),
    "sport_kind": ("hobby", "sport"),
    "reading_genre": ("hobby", "reading"),
    "food": ("food", "essen"),
    "birthday": ("personal", "birthday"),
}


def _slot_value_is_compatible(slot, content):
    value = str(content or "").strip().lower()
    if not value:
        return False
    if slot.endswith("_frequency"):
        return bool(
            any(x in value for x in ("oft", "manchmal", "selten", "immer", "nie", "jeden", "jede ", "am wochenende", "am abend", "abends", "morgens", "pro woche", "pro tag"))
            or re.search(r"\b\d+\s*(?:mal|x)\b", value)
        )
    if slot == "sport_companion":
        return value.startswith("mit ") or any(x in value for x in ("freund", "famil", "allein", "kolleg"))
    return True


def apply_response_to_conversation_state(state, response):
    """Merge one understood learner turn into canonical working memory."""
    snapshot = state.setdefault("conversation_state_v2", {})
    slots = snapshot.setdefault("semantic_slots", {})
    response = response or {}
    slot = response.get("slot")
    content = response.get("canonical") or response.get("content")
    value = str(content or "").strip().lower()

    # Learners often elaborate instead of answering the exact requested shape.
    # Rebind only when the utterance itself gives strong evidence; otherwise
    # carry the previous state over unchanged rather than writing a false slot.
    active_subtopic = snapshot.get("subtopic")
    if active_subtopic == "sport" and value.startswith("mit "):
        slot = "sport_companion"
    elif active_subtopic == "essen" and value.startswith("mit ") and any(k in slots for k in ("food", "food_item")):
        slot = "food_detail"

    if slot in SLOT_CONTEXT and content and response.get("understood", True) and _slot_value_is_compatible(slot, content):
        topic, subtopic = SLOT_CONTEXT[slot]
        slots[slot] = content
        snapshot["topic"] = topic
        snapshot["subtopic"] = subtopic
        snapshot["active_slot"] = None
        if snapshot.get("subtopic_status") == "bridging":
            snapshot["subtopic_status"] = "completed"
    return snapshot


def set_active_slot_from_question(state, slot):
    snapshot = state.setdefault("conversation_state_v2", {})
    if slot in SLOT_CONTEXT:
        topic, subtopic = SLOT_CONTEXT[slot]
        snapshot["topic"] = topic
        snapshot["subtopic"] = subtopic
        snapshot["active_slot"] = slot
    return snapshot



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
    if q.startswith(("wann ", "bis wann ", "um wie viel uhr", "um wieviel uhr")):
        return "time"
    if q.startswith(("wo ", "woher ")):
        return "place"
    if q.startswith(("wer ", "mit wem ")):
        return "person"
    if q.startswith(("was ", "welche ", "welchen ", "wie ")):
        return "open"
    return "open"


def infer_subtopic(topic, facts, question="", snapshot=None):
    topic = str(topic or "today")
    q = str(question or "").lower()
    snapshot = snapshot or {}
    active = snapshot.get("subtopic")
    activity = str((facts or {}).get("work_activity") or (facts or {}).get("activity") or "").lower()
    if topic == "work" and (activity == "kochen" or "koch" in q):
        return "kochen"
    if topic == "weather":
        return "wetter"
    if topic == "hobby":
        # The delivered question is the strongest subtopic signal when the
        # learner explicitly moves back from another context. This updates
        # ownership without reopening an already-completed semantic slot.
        if any(x in q for x in ("liest", "lesen", "buch", "bücher", "buecher", "krimi")):
            return "reading"
        if any(x in q for x in ("musik", "hörst", "hoerst", "sänger", "saenger")):
            return "music"
        if any(x in q for x in ("sport", "fußball", "fussball", "schwimmen")):
            return "sport"
        if active in {"reading", "music", "sport"}:
            return active
        if activity in {"reading", "music", "sport"}:
            return activity
        return "freizeit"
    if topic == "food":
        return "essen"
    if topic == "personal" and active == "birthday":
        return "birthday"
    return active if snapshot.get("topic") == topic else None


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
    snapshot = state.setdefault("conversation_state_v2", {})
    subtopic = infer_subtopic(current_topic, facts, question, snapshot=snapshot)
    current_level = str(level or (state.get("student_progress") or {}).get("current_level") or "A1.1")

    snapshot.setdefault("semantic_slots", {})
    snapshot.setdefault("active_slot", None)
    snapshot.setdefault("subtopic_status", "active")
    # The delivered question defines how a short next answer should be read.
    try:
        from brain.logic.learner_turn import question_slot
        next_slot = question_slot(question)
    except Exception:
        next_slot = None
    if next_slot in SLOT_CONTEXT:
        slot_topic, slot_subtopic = SLOT_CONTEXT[next_slot]
        # An explicitly activated semantic slot is authoritative. It is set by
        # the semantic follow-up planner for the question Nele is about to ask.
        # sync() may infer a slot from question text only when no explicit slot
        # is already waiting; otherwise stale/legacy wording can rewind the
        # canonical thread (for example reading_detail -> reading_genre).
        explicit_active_slot = snapshot.get("active_slot")
        completed_same_subtopic = (
            snapshot.get("subtopic_status") == "completed"
            and snapshot.get("subtopic") == slot_subtopic
            and explicit_active_slot is None
        )
        already_filled = next_slot in snapshot.get("semantic_slots", {})
        if (
            explicit_active_slot is None
            and slot_topic == current_topic
            and not completed_same_subtopic
            and not already_filled
        ):
            snapshot["active_slot"] = next_slot
            subtopic = slot_subtopic

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
