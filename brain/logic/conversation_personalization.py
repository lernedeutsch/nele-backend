"""Conversation Memory & Personalization Engine v1.

Promotes clear conversational facts into reusable learner-profile facts and
offers occasional topic-relevant follow-ups. State is part of the learner
session and therefore follows the backend's existing persistence mechanism.
"""

ENGINE_VERSION = 1
REUSABLE_KEYS = {
    "place", "activity", "music_genre", "reading_genre", "shopping_item", "color",
}

def remember_conversation_facts(state, facts, *, topic=None):
    store = state.setdefault("conversation_personalization_v1", {
        "version": ENGINE_VERSION,
        "facts": {},
        "used_prompts": [],
    })
    saved = store.setdefault("facts", {})
    for key, value in (facts or {}).items():
        if key not in REUSABLE_KEYS or value in (None, "", False):
            continue
        old = saved.get(key) or {}
        same = old.get("value") == value
        saved[key] = {
            "value": value,
            "topic": topic,
            "confirmations": int(old.get("confirmations", 0) or 0) + 1 if same else 1,
        }
    return dict(store)

def _prompt_candidates(facts, topic):
    candidates = []
    activity = (facts.get("activity") or {}).get("value")
    place = (facts.get("place") or {}).get("value")
    genre = (facts.get("music_genre") or {}).get("value")
    reading_genre = (facts.get("reading_genre") or {}).get("value")
    item = (facts.get("shopping_item") or {}).get("value")
    color = (facts.get("color") or {}).get("value")

    if topic == "hobby" and activity == "cycling":
        candidates.append("Du fährst gern Rad. Wo fährst du am liebsten?")
    if topic == "hobby" and activity == "swimming":
        candidates.append("Du schwimmst gern. Wo schwimmst du am liebsten?")
    if topic == "hobby" and activity == "reading":
        if reading_genre:
            candidates.append(f"Du liest gern {reading_genre}. Liest du gerade ein Buch?")
        else:
            candidates.append("Du liest gern. Was liest du am liebsten?")
    if topic == "hobby" and genre:
        candidates.append(f"Du hörst gern {genre}. Wann hörst du Musik?")
    if topic == "place" and place:
        candidates.append(f"Du bist oft in {place}. Was machst du dort gern?")
    if topic == "shopping" and item:
        if color:
            candidates.append(f"Du magst {color.lower()}e {item}. Suchst du heute auch {item}?")
        else:
            candidates.append(f"Du suchst gern {item}. Suchst du heute auch {item}?")
    return candidates

def choose_personalized_followup(state, *, topic, recent_questions=None, turn_count=0):
    store = state.get("conversation_personalization_v1") or {}
    facts = store.get("facts") or {}
    used = set(store.get("used_prompts") or [])
    recent = set(recent_questions or [])

    # Personalization should feel occasional, not like Nele is repeating a
    # dossier back to the learner. Do not use it in the first few turns.
    if int(turn_count or 0) < 3:
        return None

    for prompt in _prompt_candidates(facts, topic):
        if prompt not in used and prompt not in recent:
            history = store.setdefault("used_prompts", [])
            history.append(prompt)
            del history[:-20]
            return {
                "version": ENGINE_VERSION,
                "question": prompt,
                "topic": topic,
                "personalized": True,
            }
    return None

def get_personalization_summary(state):
    store = state.get("conversation_personalization_v1") or {}
    return {
        "version": ENGINE_VERSION,
        "facts": dict(store.get("facts") or {}),
        "used_prompt_count": len(store.get("used_prompts") or []),
    }
