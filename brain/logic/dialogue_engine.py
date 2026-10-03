"""Reusable dialogue engine for production Nele.

Lesson files may expose DIALOGUES as a list of dialogue definitions. The engine
owns HOW a dialogue is practised; lesson content owns WHAT is practised.
"""
from brain.logic.lesson_loader import load_lesson_module
from brain.knowledge.active_dialogues import get_active_dialogues
from brain.logic.matcher import normalize
import re
from brain.logic.dialogue_knowledge import accepted_patterns, infer_intent, render_pattern, slot_names
from brain.logic.dialogue_state_engine import (
    clear_semantic_state,
    initialise_dialogue_state,
    mark_intent_complete,
    record_exchange,
    within_turn_limit,
)
from brain.memory.lesson_progress import mark_section_completed, get_next_incomplete_section
from brain.logic.learning_progress_engine import update_learning_progress
from brain.logic.course_answer_evaluator import (
    answer_matches_course_definition,
    evaluate_course_answer,
)
from brain.logic.learner_model import build_learner_model
from brain.logic.curriculum_skill_graph import get_skill
from brain.logic.course_teacher_engine import (
    choose_course_teacher_action,
    render_course_teacher_action,
)
from brain.memory.user_facts import get_user_fact
from brain.memory.error_memory import remember_error
from brain.logic.speaking_support import (
    consume_course_model_exhaustion,
    handle_pending_course_model,
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


def _match_slot_pattern(user_message, pattern, slots=None, variable_slots=None):
    """Match a dialogue pattern while allowing explicitly variable semantic slots."""
    variable_slots = dict(variable_slots or {})
    names = set(slot_names(pattern))
    if not names or not (names & set(variable_slots)):
        return None

    regex = re.escape(str(pattern or ""))
    for name in names:
        token = re.escape("{" + name + "}")
        if name in variable_slots:
            regex = regex.replace(token, rf"(?P<{name}>.+?)")
        else:
            value = str((slots or {}).get(name, ""))
            regex = regex.replace(token, re.escape(value))

    match = re.fullmatch(regex + r"[ .?!„“\"']*", str(user_message or "").strip(), flags=re.IGNORECASE)
    if not match:
        return None
    captured = {
        name: str(value or "").strip(" .?!„“\"'")
        for name, value in match.groupdict().items()
        if str(value or "").strip()
    }
    for name, value in captured.items():
        allowed = {_norm(item) for item in variable_slots.get(name, []) if _norm(item)}
        if allowed and _norm(value) not in allowed:
            return None
    return captured


def _match_slot_semantic_pattern(user_message, pattern, slots=None, variable_slots=None):
    """Use the shared course evaluator after substituting declared slot values.

    This keeps natural word order / omitted-pronoun handling identical to lesson
    exercises while still limiting dialogue variations to explicitly declared
    semantic slot values.
    """
    variable_slots = dict(variable_slots or {})
    names = set(slot_names(pattern))
    changing = [name for name in names if name in variable_slots]
    if len(changing) != 1:
        return None

    name = changing[0]
    for candidate in variable_slots.get(name, []) or []:
        candidate_slots = dict(slots or {})
        candidate_slots[name] = candidate
        rendered = render_pattern(pattern, candidate_slots)
        if answer_matches_course_definition(
            user_message,
            {"accepted": [rendered]},
            render=lambda value: str(value or ""),
        ):
            return {name: str(candidate)}
    return None


def _contradicts_dialogue_context(user_message, turn, slots=None):
    """Reject answers whose polarity contradicts the active semantic slot.

    Confirmation turns may allow a negative correction with a different slot
    value (for example: "Nein, ich komme aus Polen.").  A negative answer that
    repeats the value being denied is self-contradictory and must not count as
    successful evidence.
    """
    message = _norm(user_message)
    intent = _norm((turn or {}).get("expected_intent"))
    if not message.startswith("nein") or not intent.startswith("confirm"):
        return False

    for name, value in (slots or {}).items():
        value_norm = _norm(value)
        if value_norm and value_norm in message:
            return True
    return False


def _personal_origin_equivalent(user_message, turn, slots=None):
    """Accept ordinary A1 ways of stating the learner's remembered origin."""
    if _norm((turn or {}).get("expected_intent")) != "give_origin":
        return False
    country = _norm((slots or {}).get("country"))
    message = _norm(user_message)
    if not country or not message:
        return False
    return message in {
        country,
        f"aus {country}",
        f"ich komme aus {country}",
        f"ich bin aus {country}",
    }


def answer_matches_dialogue_turn(user_message, turn, slots=None, variable_slots=None):
    message = _norm(user_message)
    if not message:
        return False
    if _contradicts_dialogue_context(user_message, turn, slots):
        return False
    if _personal_origin_equivalent(user_message, turn, slots):
        return True
    if turn.get("allow_any") is True:
        return True
    accepted = _accepted(turn, slots)
    if message in accepted:
        return True
    for pattern in accepted_patterns(turn):
        if _match_slot_pattern(user_message, pattern, slots, variable_slots) is not None:
            return True
        if _match_slot_semantic_pattern(user_message, pattern, slots, variable_slots) is not None:
            return True

    shared_definition = dict(turn)
    shared_definition["accepted"] = [
        render_pattern(pattern, slots or {})
        for pattern in accepted_patterns(turn)
        if not slot_names(pattern)
        or all(name in (slots or {}) for name in slot_names(pattern))
    ]
    return evaluate_course_answer(
        user_message,
        shared_definition,
        render=lambda value: str(value or ""),
    )["correct"]


def is_dialogue_active(state):
    return bool(state and state.get("dialogue_active"))


def _current_turn(state, dialogue):
    turns = _turns(dialogue)
    index = int(state.get("dialogue_turn", 0) or 0)
    if index < 0 or index >= len(turns):
        return None
    return turns[index]


def _advance_to_learner(turns, index, slots=None):
    spoken = []
    while index < len(turns):
        turn = turns[index]
        role = _norm(turn.get("role"))
        if role in {"student", "learner", "user", "du"}:
            return index, spoken
        line = _text(render_pattern(turn.get("text"), slots or {}))
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
    dialogue_slots = dict(dialogue.get("slots", {}) or {})

    # A newly selected dialogue is a fresh mastery attempt. Assistance from a
    # previous lesson task/dialogue must not make clean answers look guided.
    state["course_mastery_assistance_used"] = False
    state.pop("course_pending_speaking_model", None)
    state.pop("course_model_practice_exhausted", None)

    # Personal slots describe the learner, so prefer remembered learner facts
    # over a lesson's example/default value. Content can still provide a
    # fallback for anonymous practice sessions.
    personal_slot_facts = {
        "country": "origin",
        "name": "name",
        "residence": "residence",
    }
    for slot_name, fact_name in personal_slot_facts.items():
        if slot_name not in dialogue_slots:
            continue
        remembered = get_user_fact(state, fact_name)
        if str(remembered or "").strip():
            dialogue_slots[slot_name] = str(remembered).strip()

    index, spoken = _advance_to_learner(turns, requested_start, dialogue_slots)
    state["dialogue_active"] = True
    state["dialogue_level"] = str(level).upper()
    state["dialogue_lesson"] = int(lesson)
    state["dialogue_id"] = _text(dialogue.get("id") or dialogue_id)
    state["dialogue_turn"] = index
    state["last_activity"] = "dialogue"
    state["last_activity_detail"] = _text(dialogue.get("title") or dialogue_id)
    state["dialogue_slots"] = dialogue_slots
    initialise_dialogue_state(state, dialogue)

    intro = _text(dialogue.get("intro"))
    prompt = ""
    if index < len(turns):
        prompt = _text(render_pattern(turns[index].get("prompt") or turns[index].get("text"), dialogue_slots))

    return " ".join(part for part in [intro, *spoken, prompt] if part)


_ROUTER_STOPWORDS = {"ich","du","dir","mir","mich","dich","was","wie","wo","wohin","wann","welcher","welche","welches","hast","haben","hat","ist","sind","bist","kannst","kann","machst","machen","geht","gehen","fährst","fahre","fahr","fliegst","fliege","gern","gerne","am","im","in","die","der","das","dem","den","ein","eine","einen","mit","zu","zum","zur","nach","auch","sehr","bitte","und","oder","heute","morgen","sie"}


def _router_tokens(text):
    return {token for token in _norm(text).split() if len(token) >= 3 and token not in _ROUTER_STOPWORDS}


def _router_shared_tokens(left, right):
    """Match content tokens while tolerating ordinary German compounds/endings."""
    shared = set()
    for left_token in left:
        for right_token in right:
            if left_token == right_token:
                shared.add(left_token)
                break
            if min(len(left_token), len(right_token)) >= 5 and (
                left_token in right_token or right_token in left_token
            ):
                shared.add(left_token)
                break
    return shared


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
        shared_tokens = _router_shared_tokens(message_tokens, prompt_tokens)
        # One generic shared word (for example "Wochenende") is not enough
        # evidence to start a scripted dialogue with a different intent.
        if len(shared_tokens) < 2:
            continue
        overlap = len(shared_tokens) / len(prompt_tokens)
        coverage = len(shared_tokens) / max(1, len(message_tokens))
        score = (0.72 * overlap) + (0.28 * coverage)
        best = max(best, score)
        best_overlap = max(best_overlap, overlap)
    metadata = " ".join(str(dialogue.get(key) or "") for key in ("title","topic","situation"))
    meta_tokens = _router_tokens(metadata)
    meta_shared = _router_shared_tokens(message_tokens, meta_tokens)
    meta_overlap = len(meta_shared) / len(meta_tokens) if meta_tokens else 0.0
    for trigger in dialogue.get("entry_triggers", []):
        trigger_tokens = _router_tokens(trigger)
        if not trigger_tokens:
            continue
        shared = _router_shared_tokens(message_tokens, trigger_tokens)
        if len(shared) < 2:
            continue
        trigger_overlap = len(shared) / len(trigger_tokens)
        trigger_coverage = len(shared) / max(1, len(message_tokens))
        best = max(best, (0.72 * trigger_overlap) + (0.28 * trigger_coverage))
    best = max(best, 0.58 * meta_overlap)
    return best, best_overlap


def find_dialogue_for_message(message, level="A1", min_score=0.68, lesson=None):
    if not _text(message):
        return None
    message_tokens = _router_tokens(message)
    candidates = []
    requested_level = str(level or "A1").upper()
    if requested_level in {"A1-A2", "A1/A2", "A1+A2"}:
        dialogues = get_active_dialogues("A1") + get_active_dialogues("A2")
    else:
        dialogues = get_active_dialogues(requested_level)
    if lesson is not None:
        try:
            lesson = int(lesson)
        except (TypeError, ValueError):
            lesson = None
    if lesson is not None:
        dialogues = [dialogue for dialogue in dialogues if int(dialogue.get("lesson") or 0) == lesson]
    for dialogue in dialogues:
        score, overlap = _dialogue_router_score(message, dialogue)
        # A partial prompt match is not enough to select a dialogue. Require
        # at least one content-bearing token from the dialogue metadata
        # (topic/title/situation). This prevents generic questions such as
        # "Was machst du am Wochenende?" from accidentally selecting Reisen,
        # while "Welche Musik hörst du gern?" still has the anchor "musik".
        metadata = " ".join(str(dialogue.get(key) or "") for key in ("title", "topic", "situation"))
        anchor_tokens = _router_tokens(metadata)
        shared_anchors = _router_shared_tokens(message_tokens, anchor_tokens)
        has_topic_anchor = bool(shared_anchors)
        # Prefer an explicit metadata/topic word over a coincidental prompt
        # match when neighbouring dialogues share the same sentence pattern.
        # Example: "Wochenende" should beat a generic Freizeit/Samstag match.
        anchor_specificity = len(shared_anchors) / max(1, len(anchor_tokens))
        entry_turn = next(
            (
                turn for turn in _turns(dialogue)
                if _norm(turn.get("role")) in {"nele", "teacher", "assistant"}
            ),
            None,
        )
        entry_triggers = {
            _norm(value)
            for value in dialogue.get("entry_triggers", [])
            if _norm(value)
        }
        exact_prompt_match = bool(
            (
                entry_turn
                and _norm(entry_turn.get("text") or entry_turn.get("prompt")) == _norm(message)
            )
            or _norm(message) in entry_triggers
        )
        trigger_match = any(
            len(_router_shared_tokens(message_tokens, _router_tokens(trigger))) >= 2
            for trigger in dialogue.get("entry_triggers", [])
        )
        if score >= float(min_score) and (exact_prompt_match or has_topic_anchor or trigger_match):
            # Exact prompts are canonical triggers and outrank fuzzy matches.
            candidates.append((1 if exact_prompt_match else 0, anchor_specificity, score, overlap, dialogue))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1], item[2], item[3], -int(item[4].get("lesson") or 999), _norm(item[4].get("id"))), reverse=True)
    return candidates[0][4]


def auto_start_dialogue_from_message(message, state, level="A1", min_score=0.68):
    if not state or is_dialogue_active(state):
        return None
    dialogue = find_dialogue_for_message(message, level, min_score=min_score)
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

_TOPIC_CHANGE_QUESTION_STARTS = (
    "was ", "wie ", "wo ", "woher ", "wohin ", "wann ", "warum ",
    "wer ", "welcher ", "welche ", "welches ", "arbeitest ", "wohnst ",
    "isst ", "trinkst ", "magst ", "machst ", "hast ", "bist ", "kommst ",
)


def _learner_is_changing_topic(user_message, turn, slots=None):
    """Release a scripted dialogue when the learner clearly asks a new question.

    The current turn still wins when the message is a valid answer. This keeps
    short A1 answers inside the dialogue while allowing normal free-conversation
    questions to interrupt it instead of being swallowed as retry attempts.
    """
    if answer_matches_dialogue_turn(user_message, turn, slots):
        return False
    raw = _text(user_message)
    message = _norm(raw)
    if not raw or "?" not in raw:
        return False
    return message.startswith(_TOPIC_CHANGE_QUESTION_STARTS)


_DIALOGUE_EXIT_PHRASES = {
    "danke", "danke schön", "danke schoen", "vielen dank",
    "tschüss", "tschuss", "ciao", "bis bald", "bis später", "bis spaeter",
    "auf wiedersehen", "genug", "stopp", "stop",
}


def _learner_is_ending_dialogue(user_message, turn, slots=None):
    """Allow natural social closings to leave a practice dialogue.

    A phrase that is explicitly accepted by the current learner turn still
    belongs to the dialogue; otherwise common thanks/goodbyes release it.
    """
    if answer_matches_dialogue_turn(user_message, turn, slots):
        return False
    return _norm(user_message) in _DIALOGUE_EXIT_PHRASES


def _course_dialogue_skill_key(dialogue, state):
    section = _text((dialogue or {}).get("section") or state.get("lesson_teaching_section") or (dialogue or {}).get("title") or (dialogue or {}).get("id"))
    level = _text((dialogue or {}).get("level") or state.get("dialogue_level") or "A1").lower()
    lesson = (dialogue or {}).get("lesson") or state.get("dialogue_lesson")
    slug = _norm(section).replace(" ", "_")
    if not slug or not lesson:
        return None
    return f"course:{level}:{lesson}:{slug}"


def _dialogue_covers_section_mastery(dialogue):
    """Whether this dialogue alone is sufficient evidence for its whole section."""
    return _norm((dialogue or {}).get("mastery_scope") or "section") == "section"


def _dialogue_required_evidence(dialogue):
    """Stable evidence keys for every learner turn in a section-mastery dialogue."""
    turns = (dialogue or {}).get("turns") or []
    learner_roles = {"student", "learner", "user", "du"}
    return [
        f"dialogue_turn:{index}"
        for index, turn in enumerate(turns)
        if _norm((turn or {}).get("role")) in learner_roles
    ]


def _current_dialogue_evidence(dialogue, state):
    """Evidence key for the learner turn that has just been answered."""
    try:
        index = int((state or {}).get("dialogue_turn"))
    except (TypeError, ValueError):
        return ""
    turn = (((dialogue or {}).get("turns") or []) + [{}])[index] if index >= 0 else {}
    if _norm((turn or {}).get("role")) not in {"student", "learner", "user", "du"}:
        return ""
    return f"dialogue_turn:{index}"


def _record_course_dialogue_outcome(dialogue, state, success, partial=False, independent_confirmation=False):
    if str(state.get("conversation_mode") or "").strip().lower() != "course":
        return None
    skill = _course_dialogue_skill_key(dialogue, state)
    if not skill:
        return None
    covers_section = _dialogue_covers_section_mastery(dialogue)
    required_evidence = _dialogue_required_evidence(dialogue) if covers_section else []
    independent = bool(success and not partial and not state.get("course_mastery_assistance_used"))
    outcome = {
        "skill": skill,
        "expected_outcome": "course_dialogue_turn",
        "status": "PARTIAL" if partial else ("SUCCESS" if success else "NOT_YET"),
        # A section dialogue may prove mastery only after every learner turn
        # has fresh independent evidence. The final turn is merely the mastery
        # checkpoint; it cannot stand in for the earlier required productions.
        "mastery_eligible": bool(success and independent_confirmation and not partial and covers_section),
        "requires_independent_confirmation": True,
        "independent_confirmation": bool(independent and covers_section),
        "required_evidence": required_evidence,
        "evidence": _current_dialogue_evidence(dialogue, state) if independent and covers_section else "",
    }
    progress = update_learning_progress(state, outcome)
    state["last_course_learning_outcome"] = dict(outcome, progress=progress)
    return progress


def _repeat_dialogue_for_mastery(dialogue, state, progress):
    if str(state.get("conversation_mode") or "").strip().lower() != "course":
        return None
    if (progress or {}).get("status") == "mastered":
        return None
    opening = start_dialogue(
        state.get("dialogue_level") or (dialogue or {}).get("level") or "A1",
        state.get("dialogue_lesson") or (dialogue or {}).get("lesson") or 1,
        (dialogue or {}).get("id"),
        state,
    )
    if not opening:
        return None
    action = choose_course_teacher_action(
        state,
        answer_correct=True,
        mastery_status=(progress or {}).get("status"),
    )
    return render_course_teacher_action(action, prompt=opening)


def _continue_section_after_practice_dialogue(dialogue, state):
    """Continue with section teaching when a dialogue is practice, not mastery."""
    if str(state.get("conversation_mode") or "").strip().lower() != "course":
        return None
    if _dialogue_covers_section_mastery(dialogue):
        return None

    section = _text((dialogue or {}).get("section"))
    if not section:
        return None

    # Clear only dialogue state; the selected course lesson remains active.
    clear_dialogue(state)
    try:
        from brain.logic.generic_lesson_engine import start_generic_lesson_teaching
        opening = start_generic_lesson_teaching(section, state)
    except Exception:
        opening = None
    if not opening:
        return None

    return opening


def _complete_course_dialogue(dialogue, state):
    """Connect a completed lesson dialogue back to the course progression."""
    if not state or not isinstance(dialogue, dict):
        return None
    section = _text(dialogue.get("section"))
    level = _text(dialogue.get("level") or state.get("dialogue_level") or "A1").upper()
    lesson = dialogue.get("lesson") or state.get("dialogue_lesson")
    if not section or not lesson:
        return None
    # The persistence boundary is authoritative: a dialogue may route onward
    # only if this exact section was actually accepted as completed from
    # durable course mastery. Never prepare the next section after a rejected
    # completion attempt (for example stale/partial dialogue state).
    section_completed = mark_section_completed(state, level, lesson, section)
    if not section_completed:
        state["course_teaching_decision"] = {
            "decision": "continue_current",
            "skill": _course_dialogue_skill_key(dialogue, state),
            "reason": "section_not_mastered",
        }
        state["pending_new_learning"] = None
        if state.get("last_question") == "continue_new_learning":
            state["last_question"] = None
        return None

    learner_model = build_learner_model(state)
    course_learning = learner_model.get("course_learning") or {}
    next_skill = course_learning.get("next_skill")
    next_decision = course_learning.get("teaching_decision")

    # Course routing is owned by mastery + Learner Model + Course Skill Graph.
    # Legacy lesson_progress is only a compatibility fallback. In production a
    # dialogue can be entered without a populated legacy section list, so using
    # it first can falsely report that the lesson has no next section.
    next_section = None
    graph_item = get_skill(next_skill) if next_skill else None
    if (
        next_decision == "teach_next"
        and isinstance(graph_item, dict)
        and int(graph_item.get("lesson") or 0) == int(lesson)
    ):
        next_section = _text(graph_item.get("section"))
    if not next_section:
        next_section = get_next_incomplete_section(state, level, lesson)
    state["course_teaching_decision"] = {
        "decision": next_decision,
        "skill": next_skill,
        "reason": course_learning.get("next_reason"),
    }
    if next_section:
        state["pending_new_learning"] = {
            "type": "new_section",
            "level": level,
            "lesson": int(lesson),
            "section": next_section,
            "topic": next_section,
            "skill": next_skill,
            "decision": next_decision,
        }
        state["last_question"] = "continue_new_learning"
    return next_section


def get_current_dialogue_prompt(state):
    """Return the exact learner prompt for an active dialogue without advancing it."""
    if not is_dialogue_active(state):
        return None
    dialogue = get_dialogue(
        state.get("dialogue_level"),
        state.get("dialogue_lesson"),
        state.get("dialogue_id"),
    )
    if dialogue is None:
        return None
    turns = _turns(dialogue)
    turn = _current_turn(state, dialogue)
    if turn is None:
        return None
    slots = state.get("dialogue_slots") or {}
    index = int(state.get("dialogue_turn", 0) or 0)
    spoken = ""
    for previous in reversed(turns[:index]):
        if _norm(previous.get("role")) not in {"student", "learner", "user", "du"}:
            spoken = _text(render_pattern(previous.get("text"), slots))
            if spoken:
                speaker = _text(previous.get("speaker")) or "Nele"
                spoken = f"{speaker}: {spoken}"
                break
    prompt = _text(render_pattern(turn.get("prompt") or turn.get("text"), slots))
    body = " ".join(part for part in (spoken, prompt) if part)
    return f"Jetzt machen wir weiter. {body}".strip() if body else None


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

    # Dialogue turns use the same speaking-support ladder as lesson tasks.
    # Let the shared pending-model handler own guided repetition so repeated
    # failures can actually reach the bounded exhaustion state.
    pending_reply = handle_pending_course_model(user_message, state)
    if pending_reply is not None:
        return pending_reply

    exhausted = consume_course_model_exhaustion(state)
    if exhausted and str(state.get("conversation_mode") or "").strip().lower() == "course":
        state["course_mastery_assistance_used"] = True
        _record_course_dialogue_outcome(dialogue, state, False)

        # Maximal scaffolding means this turn needs later review, not another
        # immediate pass through the same support ladder. Move to the next
        # learner turn when the dialogue has one, while the failed skill stays
        # NOT_YET/needs_review in learning progress.
        failed_turn_index = int(state.get("dialogue_turn", 0) or 0)
        next_index, spoken = _advance_to_learner(
            turns,
            failed_turn_index + 1,
            state.get("dialogue_slots"),
        )
        if next_index < len(turns):
            # Keep the exact failed learner turn. The next learner turn is a
            # bounded transfer task; one successful transfer returns to this
            # deferred turn instead of silently abandoning it.
            state["dialogue_deferred_turn"] = failed_turn_index
            state["dialogue_transfer_turn"] = next_index
            state["dialogue_turn"] = next_index
            state.pop("dialogue_retry_turn", None)
            next_prompt = _text(
                render_pattern(
                    turns[next_index].get("prompt") or turns[next_index].get("text"),
                    state.get("dialogue_slots") or {},
                )
            )
            return " ".join(
                part for part in [
                    "Wir machen erst einmal weiter.",
                    *spoken,
                    next_prompt,
                ] if part
            )

        action = choose_course_teacher_action(
            state,
            answer_correct=True,
            mastery_status="needs_review",
        )
        retry_prompt = _text(render_pattern(turn.get("retry"), state.get("dialogue_slots") or {})) or "Versuch es noch einmal."
        return render_course_teacher_action(action, prompt=retry_prompt)

    # A learner may explicitly open a different validated dialogue while
    # practising. If the new message exactly matches another dialogue's
    # opening, switch cleanly instead of treating it as a wrong answer.
    course_lesson = None
    if str(state.get("conversation_mode") or "").strip().lower() == "course":
        course_lesson = state.get("selected_lesson") or state.get("lesson") or state.get("dialogue_lesson")
    candidate = find_dialogue_for_message(
        user_message,
        state.get("dialogue_level") or "A1",
        lesson=course_lesson,
    )
    # A clear new dialogue intent must pre-empt the old dialogue. Requiring an
    # exact stored prompt made natural paraphrases and topic changes look like
    # wrong answers, which caused loops and dialogue mixing.
    if (
        candidate is not None
        and _norm(candidate.get("id")) != _norm(state.get("dialogue_id"))
        and "?" in str(user_message or "")
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

    # Thanks/goodbyes are valid conversational exits, not failed repetitions.
    if _learner_is_ending_dialogue(user_message, turn, state.get("dialogue_slots")):
        closing = _norm(user_message)
        clear_dialogue(state)
        if closing in {"danke", "danke schön", "danke schoen", "vielen dank"}:
            return "Gern!"
        if closing in {"tschüss", "tschuss", "ciao", "bis bald", "bis später", "bis spaeter", "auf wiedersehen"}:
            return "Tschüss!"
        return "Gut, wir machen frei weiter."

    # A side question has different semantics in the two modes. In free mode
    # it releases the scripted dialogue. In course mode it is a temporary
    # digression: keep the exact dialogue turn in session state, let the shared
    # routers answer the side question, then resume this prompt.
    if _learner_is_changing_topic(user_message, turn, state.get("dialogue_slots")):
        if str(state.get("conversation_mode") or "").strip().lower() == "course":
            state["course_side_question_pending"] = True
            return None
        clear_dialogue(state)
        return None

    # A safety turn limit is not evidence of mastery. In strict course mode
    # the learner must still satisfy the current turn before the dialogue can
    # complete; otherwise a sequence of wrong answers could falsely mark the
    # lesson section as learned. Free mode keeps the existing bounded-dialogue
    # behaviour.
    if (
        str(state.get("conversation_mode") or "").strip().lower() != "course"
        and not within_turn_limit(state, dialogue)
    ):
        complete = _text(dialogue.get("complete")) or "Sehr gut. Wir gehen jetzt weiter."
        clear_dialogue(state)
        return complete

    variable_slots = {}
    variations = set(dialogue.get("allowed_variations", []) or [])
    slot_values = dialogue.get("slot_values", {}) or {}
    if "change_country" in variations and slot_values.get("country"):
        variable_slots["country"] = slot_values["country"]

    record_exchange(state)
    # Some correction turns deliberately tighten the task after an error.
    # A short answer may be valid on the first attempt, but when the teacher
    # explicitly asks for a full corrected sentence, the retry must actually
    # produce that sentence before the dialogue can advance.
    retry_requires_full_sentence = bool(
        turn.get("retry_requires_full_sentence")
        and state.get("dialogue_retry_turn") == int(state.get("dialogue_turn", 0) or 0)
    )
    answer_matches = answer_matches_dialogue_turn(
        user_message,
        turn,
        state.get("dialogue_slots"),
        variable_slots=variable_slots,
    )
    if retry_requires_full_sentence:
        expected_retry = render_pattern(
            turn.get("expected", ""),
            state.get("dialogue_slots") or {},
        )
        answer_matches = bool(
            expected_retry
            and _norm(user_message) == _norm(expected_retry)
        )

    if not answer_matches:
        # Preserve the shared evaluator's three-way classification. Previously
        # dialogue routing collapsed PARTIAL into False and stored NOT_YET,
        # so Learner Model lost evidence that the learner was partly correct.
        shared_definition = dict(turn)
        shared_definition["accepted"] = [
            render_pattern(pattern, state.get("dialogue_slots") or {})
            for pattern in accepted_patterns(turn)
            if not slot_names(pattern)
            or all(name in (state.get("dialogue_slots") or {}) for name in slot_names(pattern))
        ]
        evaluation = evaluate_course_answer(
            user_message,
            shared_definition,
            render=lambda value: str(value or ""),
        )
        expected = _text(render_pattern(turn.get("expected"), state.get("dialogue_slots") or {}))
        if evaluation.get("kind") == "partial":
            state["course_mastery_assistance_used"] = True
            _record_course_dialogue_outcome(dialogue, state, False, partial=True)
            action = choose_course_teacher_action(
                state,
                answer_correct=False,
                partial=evaluation.get("partial"),
                correct_answer=expected,
            )
            return render_course_teacher_action(action)

        state["course_mastery_assistance_used"] = True
        _record_course_dialogue_outcome(dialogue, state, False)

        # A wrong course-dialogue answer is also a real learner error. Keep it
        # in the shared Error Memory so "meine Fehler üben" can temporarily
        # branch into Error Practice and, after independent correction, return
        # to this exact still-active dialogue turn.
        if (
            str(state.get("conversation_mode") or "").strip().lower() == "course"
            and expected
        ):
            try:
                remember_error(
                    state,
                    "course_dialogue",
                    str(user_message or "").strip(),
                    expected,
                    context=get_current_dialogue_prompt(state) or "",
                )
            except Exception as error:
                print(f"Dialogue error memory error: {error}")

        if turn.get("retry_requires_full_sentence"):
            state["dialogue_retry_turn"] = int(state.get("dialogue_turn", 0) or 0)
        retry = _text(render_pattern(turn.get("retry"), state.get("dialogue_slots") or {}))
        action = choose_course_teacher_action(
            state,
            answer_correct=False,
            correct_answer=expected,
            retry=retry,
        )
        return render_course_teacher_action(action)

    for pattern in accepted_patterns(turn):
        captured = _match_slot_pattern(
            user_message,
            pattern,
            state.get("dialogue_slots"),
            variable_slots=variable_slots,
        )
        if not captured:
            captured = _match_slot_semantic_pattern(
                user_message,
                pattern,
                state.get("dialogue_slots"),
                variable_slots=variable_slots,
            )
        if captured:
            state.setdefault("dialogue_slots", {}).update(captured)
            break

    state.pop("dialogue_retry_turn", None)
    mark_intent_complete(state, infer_intent(turn))
    success = _text(turn.get("success"))
    next_index, spoken = _advance_to_learner(
        turns,
        int(state.get("dialogue_turn", 0)) + 1,
        state.get("dialogue_slots"),
    )
    dialogue_finishes = (
        next_index >= len(turns)
        or not any(
            _norm(item.get("role")) in {"student", "learner", "user", "du"}
            for item in turns[next_index:]
        )
    )
    independent_confirmation = bool(
        dialogue_finishes
        and not state.get("course_mastery_assistance_used")
    )
    course_progress = _record_course_dialogue_outcome(
        dialogue,
        state,
        True,
        independent_confirmation=independent_confirmation,
    )

    # A successful transfer after exhausted scaffolding must revisit the exact
    # learner turn that was deferred. The transfer is guided practice and does
    # not erase the unresolved target.
    current_turn_index = int(state.get("dialogue_turn", 0) or 0)
    deferred_turn = state.get("dialogue_deferred_turn")
    transfer_turn = state.get("dialogue_transfer_turn")
    if (
        deferred_turn is not None
        and transfer_turn is not None
        and current_turn_index == int(transfer_turn)
    ):
        deferred_index = int(deferred_turn)
        state["dialogue_turn"] = deferred_index
        state.pop("dialogue_deferred_turn", None)
        state.pop("dialogue_transfer_turn", None)
        state["course_mastery_assistance_used"] = False
        deferred = turns[deferred_index]
        deferred_prompt = _text(
            render_pattern(
                deferred.get("prompt") or deferred.get("text"),
                state.get("dialogue_slots") or {},
            )
        )
        return " ".join(
            part for part in [success, "Jetzt noch einmal:", deferred_prompt] if part
        )

    if next_index >= len(turns):
        practice_continuation = _continue_section_after_practice_dialogue(dialogue, state)
        if practice_continuation:
            complete = _text(dialogue.get("complete")) or "Sehr gut! Der Dialog ist fertig."
            return " ".join(part for part in [success, *spoken, complete, practice_continuation] if part)
        if not independent_confirmation:
            state["course_mastery_assistance_used"] = False
        repeat = _repeat_dialogue_for_mastery(dialogue, state, course_progress)
        if repeat:
            return " ".join(part for part in [success, *spoken, repeat] if part)
        complete = _text(dialogue.get("complete")) or "Sehr gut! Der Dialog ist fertig."
        next_section = _complete_course_dialogue(dialogue, state)
        clear_dialogue(state)
        if next_section:
            complete += f" Als Nächstes kommt „{next_section}“. Möchtest du weitermachen?"
        return " ".join(part for part in [success, *spoken, complete] if part)

    state["dialogue_turn"] = next_index
    # A dialogue may intentionally finish with a Nele closing line.
    if not any(
        _norm(item.get("role")) in {"student", "learner", "user", "du"}
        for item in turns[next_index:]
    ):
        practice_continuation = _continue_section_after_practice_dialogue(dialogue, state)
        if practice_continuation:
            complete = _text(dialogue.get("complete")) or "Sehr gut! Der Dialog ist fertig."
            return " ".join(part for part in [success, *spoken, complete, practice_continuation] if part)
        if not independent_confirmation:
            state["course_mastery_assistance_used"] = False
        repeat = _repeat_dialogue_for_mastery(dialogue, state, course_progress)
        if repeat:
            return " ".join(part for part in [success, *spoken, repeat] if part)
        complete = _text(dialogue.get("complete"))
        next_section = _complete_course_dialogue(dialogue, state)
        clear_dialogue(state)
        if next_section:
            complete = (complete + f" Als Nächstes kommt „{next_section}“. Möchtest du weitermachen?").strip()
        return " ".join(part for part in [success, *spoken, complete] if part)

    next_turn = turns[next_index]
    prompt = _text(next_turn.get("prompt") or next_turn.get("text"))
    return " ".join(part for part in [success, *spoken, prompt] if part)
