"""Session-level state and safety policy for Nele dialogues."""
from brain.logic.dialogue_knowledge import compatible_topics


DEFAULT_MAX_TURNS = 8
DEFAULT_MAX_VARIATIONS = 2


def initialise_dialogue_state(state, dialogue):
    state["dialogue_topic"] = dialogue.get("topic") or dialogue.get("title")
    state["dialogue_situation"] = dialogue.get("situation")
    state["dialogue_register"] = dialogue.get("register")
    state["dialogue_completed_intents"] = []
    state["dialogue_variations"] = {}
    state["dialogue_exchange_count"] = 0


def mark_intent_complete(state, intent):
    if not intent:
        return
    done = state.setdefault("dialogue_completed_intents", [])
    if intent not in done:
        done.append(intent)


def record_exchange(state):
    state["dialogue_exchange_count"] = int(state.get("dialogue_exchange_count", 0) or 0) + 1


def within_turn_limit(state, dialogue):
    limit = int(dialogue.get("max_turns", DEFAULT_MAX_TURNS) or DEFAULT_MAX_TURNS)
    return int(state.get("dialogue_exchange_count", 0) or 0) < limit


def allow_variation(state, key, dialogue):
    limit = int(dialogue.get("max_variations", DEFAULT_MAX_VARIATIONS) or DEFAULT_MAX_VARIATIONS)
    used = state.setdefault("dialogue_variations", {})
    count = int(used.get(key, 0) or 0)
    if count >= limit:
        return False
    used[key] = count + 1
    return True


def transition_allowed(state, next_topic, dialogue):
    return compatible_topics(
        state.get("dialogue_topic"),
        next_topic,
        dialogue.get("next_allowed_topics", []),
    )


def clear_semantic_state(state):
    for key in (
        "dialogue_topic", "dialogue_situation", "dialogue_register",
        "dialogue_completed_intents", "dialogue_variations",
        "dialogue_exchange_count",
    ):
        state.pop(key, None)
