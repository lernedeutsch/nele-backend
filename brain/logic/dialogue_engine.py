"""Reusable dialogue engine for production Nele.

Lesson files may expose DIALOGUES as a list of dialogue definitions. The engine
owns HOW a dialogue is practised; lesson content owns WHAT is practised.
"""
from brain.logic.lesson_loader import load_lesson_module
from brain.knowledge.active_dialogues import get_active_dialogues
from brain.logic.matcher import normalize
from brain.logic.dialogue_knowledge import accepted_patterns, infer_intent, render_pattern
from brain.logic.dialogue_state_engine import (
    clear_semantic_state,
    initialise_dialogue_state,
    mark_intent_complete,
    record_exchange,
    within_turn_limit,
)


def _text(value):
    return str(value or "").strip()


def _norm(value):
    return normalize(_text(value)).strip(" .?!„“\"'")


def load_dialogues(level="A1", lesson=1):
    module = load_lesson_module(str(level or "A1").upper(), lesson)
    data = getattr(module, "LESSON_DIALOGUES", []) if module is not None else []
    local = data if isinstance(data, list) else []
    # Active reusable knowledge remains addressable even when no lesson module exists.
    active = get_active_dialogues(str(level or "A1").upper(), int(lesson))
    # Local lesson content remains first; promoted reusable knowledge is added
    # through the same engine and never gets a second conversation controller.
    seen = {_norm(item.get("id")) for item in local if isinstance(item, dict)}
    return local + [
        item for item in active
        if _norm(item.get("id")) not in seen
    ]


def get_dialogue_for_section(level, lesson, section):
    wanted = _norm(section)
    if not wanted:
        return None
    for dialogue in load_dialogues(level, lesson):
        if not isinstance(dialogue, dict):
            continue
        sections = dialogue.get("sections", dialogue.get("section", []))
        if isinstance(sections, str):
            sections = [sections]
        if any(_norm(value) == wanted for value in sections if value):
            return dialogue
    return None


def start_dialogue_for_section(level, lesson, section, state):
    dialogue = get_dialogue_for_section(level, lesson, section)
    if dialogue is None:
        return None
    return start_dialogue(level, lesson, dialogue.get("id"), state)


def get_dialogue(level, lesson, dialogue_id):
    wanted = _norm(dialogue_id)
    for dialogue in load_dialogues(level, lesson):
        if not isinstance(dialogue, dict):
            continue
        candidates = [
            dialogue.get("id"),
            dialogue.get("title"),
            *dialogue.get("aliases", []),
        ]
        if any(_norm(value) == wanted for value in candidates if value):
            return dialogue
    return None


def _turns(dialogue):
    turns = dialogue.get("turns", []) if isinstance(dialogue, dict) else []
    return [turn for turn in turns if isinstance(turn, dict)]


def _accepted(turn, slots=None):
    return {
        _norm(render_pattern(value, slots or {}))
        for value in accepted_patterns(turn)
        if _norm(render_pattern(value, slots or {}))
    }


def answer_matches_dialogue_turn(user_message, turn, slots=None):
    message = _norm(user_message)
    if not message:
        return False
    if turn.get("allow_any") is True:
        return True
    accepted = _accepted(turn, slots)
    if message in accepted:
        return True
    contains_all = turn.get("contains_all", [])
    if isinstance(contains_all, str):
        contains_all = [contains_all]
    return bool(contains_all) and all(_norm(x) in message for x in contains_all)


def is_dialogue_active(state):
    return bool(state and state.get("dialogue_active"))


def _current_turn(state, dialogue):
    turns = _turns(dialogue)
    index = int(state.get("dialogue_turn", 0) or 0)
    if index < 0 or index >= len(turns):
        return None
    return turns[index]


def _advance_to_learner(turns, index):
    spoken = []
    while index < len(turns):
        turn = turns[index]
        role = _norm(turn.get("role"))
        if role in {"student", "learner", "user", "du"}:
            return index, spoken
        line = _text(turn.get("text"))
        if line:
            speaker = _text(turn.get("speaker")) or "Nele"
            spoken.append(f"{speaker}: {line}")
        index += 1
    return index, spoken


def start_dialogue(level, lesson, dialogue_id, state):
    dialogue = get_dialogue(level, lesson, dialogue_id)
    if dialogue is None or state is None:
        return None

    turns = _turns(dialogue)
    if not turns:
        return None

    index, spoken = _advance_to_learner(turns, 0)
    state["dialogue_active"] = True
    state["dialogue_level"] = str(level).upper()
    state["dialogue_lesson"] = int(lesson)
    state["dialogue_id"] = _text(dialogue.get("id") or dialogue_id)
    state["dialogue_turn"] = index
    state["last_activity"] = "dialogue"
    state["last_activity_detail"] = _text(dialogue.get("title") or dialogue_id)
    state["dialogue_slots"] = dict(dialogue.get("slots", {}) or {})
    initialise_dialogue_state(state, dialogue)

    intro = _text(dialogue.get("intro"))
    prompt = ""
    if index < len(turns):
        prompt = _text(turns[index].get("prompt") or turns[index].get("text"))

    return " ".join(part for part in [intro, *spoken, prompt] if part)


def clear_dialogue(state):
    for key, value in {
        "dialogue_active": False,
        "dialogue_level": None,
        "dialogue_lesson": None,
        "dialogue_id": None,
        "dialogue_turn": 0,
        "dialogue_slots": {},
    }.items():
        state[key] = value
    clear_semantic_state(state)


def handle_dialogue(user_message, state):
    if not is_dialogue_active(state):
        return None

    dialogue = get_dialogue(
        state.get("dialogue_level"),
        state.get("dialogue_lesson"),
        state.get("dialogue_id"),
    )
    if dialogue is None:
        clear_dialogue(state)
        return None

    turns = _turns(dialogue)
    turn = _current_turn(state, dialogue)
    if turn is None:
        clear_dialogue(state)
        return _text(dialogue.get("complete")) or "Sehr gut! Der Dialog ist fertig."

    if not within_turn_limit(state, dialogue):
        complete = _text(dialogue.get("complete")) or "Sehr gut. Wir gehen jetzt weiter."
        clear_dialogue(state)
        return complete

    record_exchange(state)
    if not answer_matches_dialogue_turn(user_message, turn, state.get("dialogue_slots")):
        expected = _text(turn.get("expected"))
        retry = _text(turn.get("retry"))
        if retry:
            return retry
        if expected:
            return f"Fast. Sag bitte: „{expected}“"
        return "Fast. Versuch es bitte noch einmal."

    mark_intent_complete(state, infer_intent(turn))
    success = _text(turn.get("success"))
    next_index, spoken = _advance_to_learner(turns, int(state.get("dialogue_turn", 0)) + 1)

    if next_index >= len(turns):
        complete = _text(dialogue.get("complete")) or "Sehr gut! Der Dialog ist fertig."
        clear_dialogue(state)
        return " ".join(part for part in [success, *spoken, complete] if part)

    state["dialogue_turn"] = next_index
    # A dialogue may intentionally finish with a Nele closing line.
    if not any(
        _norm(item.get("role")) in {"student", "learner", "user", "du"}
        for item in turns[next_index:]
    ):
        complete = _text(dialogue.get("complete"))
        clear_dialogue(state)
        return " ".join(part for part in [success, *spoken, complete] if part)

    next_turn = turns[next_index]
    prompt = _text(next_turn.get("prompt") or next_turn.get("text"))
    return " ".join(part for part in [success, *spoken, prompt] if part)
