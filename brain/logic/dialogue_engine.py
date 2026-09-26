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


def _matching_nele_turn_index(message, dialogue):
    message_norm = _norm(message)
    for index, turn in enumerate(_turns(dialogue)):
        if _norm(turn.get("role")) in {"nele", "teacher", "assistant"}:
            prompt = _norm(turn.get("text") or turn.get("prompt"))
            if prompt and prompt == message_norm:
                return index
    return 0


def start_dialogue(level, lesson, dialogue_id, state, start_turn=0):
    dialogue = get_dialogue(level, lesson, dialogue_id)
    if dialogue is None or state is None:
        return None

    turns = _turns(dialogue)
    if not turns:
        return None

    try:
        requested_start = max(0, int(start_turn or 0))
    except (TypeError, ValueError):
        requested_start = 0
    requested_start = min(requested_start, len(turns) - 1)
    index, spoken = _advance_to_learner(turns, requested_start)
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


_ROUTER_STOPWORDS = {"ich","du","dir","mir","mich","dich","was","wie","wo","wohin","wann","welcher","welche","welches","hast","haben","hat","ist","sind","bist","kannst","kann","machst","machen","geht","gehen","fährst","fahre","fahr","fliegst","fliege","gern","gerne","am","im","in","die","der","das","dem","den","ein","eine","einen","mit","zu","zum","zur","nach","auch","sehr","bitte","und","oder","heute","morgen","sie"}


def _router_tokens(text):
    return {token for token in _norm(text).split() if len(token) >= 3 and token not in _ROUTER_STOPWORDS}


def _dialogue_router_score(message, dialogue):
    message_norm = _norm(message)
    if not message_norm or not isinstance(dialogue, dict):
        return 0.0, 0.0
    best = 0.0
    best_overlap = 0.0
    message_tokens = _router_tokens(message_norm)
    for turn in _turns(dialogue):
        if _norm(turn.get("role")) not in {"nele", "teacher", "assistant"}:
            continue
        prompt = _norm(turn.get("text") or turn.get("prompt"))
        if not prompt:
            continue
        if message_norm == prompt:
            return 1.0, 1.0
        prompt_tokens = _router_tokens(prompt)
        if not prompt_tokens:
            continue
        overlap = len(message_tokens & prompt_tokens) / len(prompt_tokens)
        coverage = len(message_tokens & prompt_tokens) / max(1, len(message_tokens))
        score = (0.72 * overlap) + (0.28 * coverage)
        best = max(best, score)
        best_overlap = max(best_overlap, overlap)
    metadata = " ".join(str(dialogue.get(key) or "") for key in ("title","topic","situation"))
    meta_tokens = _router_tokens(metadata)
    meta_overlap = len(message_tokens & meta_tokens) / len(meta_tokens) if meta_tokens else 0.0
    best = max(best, 0.58 * meta_overlap)
    return best, best_overlap


def find_dialogue_for_message(message, level="A1"):
    if not _text(message):
        return None
    candidates = []
    for dialogue in get_active_dialogues(str(level or "A1").upper()):
        score, overlap = _dialogue_router_score(message, dialogue)
        if score >= 0.68:
            candidates.append((score, overlap, dialogue))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1], -int(item[2].get("lesson") or 999), _norm(item[2].get("id"))), reverse=True)
    return candidates[0][2]


def auto_start_dialogue_from_message(message, state, level="A1"):
    if not state or is_dialogue_active(state):
        return None
    dialogue = find_dialogue_for_message(message, level)
    if dialogue is None:
        return None
    start_turn = _matching_nele_turn_index(message, dialogue)
    reply = start_dialogue(
        dialogue.get("level") or level,
        dialogue.get("lesson") or 1,
        dialogue.get("id"),
        state,
        start_turn=start_turn,
    )
    if not reply:
        return None
    title = _text(dialogue.get("title") or dialogue.get("topic"))
    prefix = f"Gerne! Wir sprechen kurz über {title.lower()}. " if title else "Gerne! "
    return prefix + reply

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

    # A learner may explicitly open a different validated dialogue while
    # practising. If the new message exactly matches another dialogue's
    # opening, switch cleanly instead of treating it as a wrong answer.
    candidate = find_dialogue_for_message(
        user_message,
        state.get("dialogue_level") or "A1",
    )
    if (
        candidate is not None
        and _norm(candidate.get("id")) != _norm(state.get("dialogue_id"))
        and "?" in str(user_message or "")
        and _norm(user_message) == _norm(
            next(
                (
                    turn.get("text") or turn.get("prompt")
                    for turn in _turns(candidate)
                    if _norm(turn.get("role")) in {"nele", "teacher", "assistant"}
                    and _norm(turn.get("text") or turn.get("prompt")) == _norm(user_message)
                ),
                "",
            )
        )
    ):
        switched = start_dialogue(
            candidate.get("level") or state.get("dialogue_level") or "A1",
            candidate.get("lesson") or state.get("dialogue_lesson") or 1,
            candidate.get("id"),
            state,
            start_turn=_matching_nele_turn_index(user_message, candidate),
        )
        if switched:
            title = _text(candidate.get("title") or candidate.get("topic"))
            prefix = f"Gerne! Wir sprechen kurz über {title.lower()}. " if title else "Gerne! "
            return prefix + switched

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
