from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

UPGRADE_KEY = "nele3_upgrade"
MAX_EVENTS = 600

SKILLS = (
    "speaking",
    "listening",
    "writing",
    "vocabulary",
    "grammar",
    "pronunciation",
    "dialogue",
    "work_german",
)


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_skill() -> Dict[str, Any]:
    return {
        "attempts": 0,
        "correct": 0,
        "score_avg": 0.0,
        "last_score": None,
        "last_practiced": None,
    }


def create_upgrade_state() -> Dict[str, Any]:
    return {
        "version": "3.0-compat-1",
        "created_at": utcnow_iso(),
        "session": {
            "started_at": None,
            "turns": 0,
            "completed_activities": 0,
            "last_action": None,
        },
        "skills": {skill: _empty_skill() for skill in SKILLS},
        "events": [],
        "active_task": None,
        "activity_cursor": {},
        "course": {"A1": 0, "A2": 0},
        "preferences": {
            "teacher_autopilot": True,
            "short_feedback": True,
        },
    }


def ensure_upgrade_state(state: Optional[dict]) -> Dict[str, Any]:
    if not isinstance(state, dict):
        return create_upgrade_state()

    upgrade = state.get(UPGRADE_KEY)
    if not isinstance(upgrade, dict):
        upgrade = create_upgrade_state()
        state[UPGRADE_KEY] = upgrade

    defaults = create_upgrade_state()
    for key, value in defaults.items():
        if key not in upgrade:
            upgrade[key] = value

    if not isinstance(upgrade.get("skills"), dict):
        upgrade["skills"] = {}
    for skill in SKILLS:
        item = upgrade["skills"].get(skill)
        if not isinstance(item, dict):
            item = _empty_skill()
            upgrade["skills"][skill] = item
        for key, value in _empty_skill().items():
            item.setdefault(key, value)

    if not isinstance(upgrade.get("events"), list):
        upgrade["events"] = []
    if not isinstance(upgrade.get("activity_cursor"), dict):
        upgrade["activity_cursor"] = {}
    if not isinstance(upgrade.get("course"), dict):
        upgrade["course"] = {"A1": 0, "A2": 0}
    if not isinstance(upgrade.get("session"), dict):
        upgrade["session"] = dict(defaults["session"])
    if not isinstance(upgrade.get("preferences"), dict):
        upgrade["preferences"] = dict(defaults["preferences"])

    for key, value in defaults["session"].items():
        upgrade["session"].setdefault(key, value)

    return upgrade


def start_upgrade_session(state: dict) -> Dict[str, Any]:
    upgrade = ensure_upgrade_state(state)
    session = upgrade["session"]
    session["started_at"] = utcnow_iso()
    session["turns"] = 0
    session["completed_activities"] = 0
    session["last_action"] = None
    record_event(state, "session_start")
    return session


def register_turn(state: dict) -> None:
    upgrade = ensure_upgrade_state(state)
    session = upgrade["session"]
    try:
        turns = int(session.get("turns", 0))
    except (TypeError, ValueError):
        turns = 0
    session["turns"] = turns + 1


def set_last_action(state: dict, action: Any) -> None:
    ensure_upgrade_state(state)["session"]["last_action"] = action


def get_active_task(state: dict) -> Optional[dict]:
    task = ensure_upgrade_state(state).get("active_task")
    return task if isinstance(task, dict) else None


def set_active_task(state: dict, task: Optional[dict]) -> None:
    ensure_upgrade_state(state)["active_task"] = task if isinstance(task, dict) else None


def next_cursor(state: dict, key: str, size: int) -> int:
    upgrade = ensure_upgrade_state(state)
    cursor = upgrade["activity_cursor"]
    try:
        index = int(cursor.get(key, 0))
    except (TypeError, ValueError):
        index = 0
    if size <= 0:
        return 0
    selected = index % size
    cursor[key] = (selected + 1) % size
    return selected


def update_skill(state: dict, skill: str, score: float, correct: Optional[bool] = None) -> dict:
    upgrade = ensure_upgrade_state(state)
    if skill not in upgrade["skills"]:
        upgrade["skills"][skill] = _empty_skill()

    item = upgrade["skills"][skill]
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0
    score = max(0.0, min(100.0, score))

    try:
        attempts = int(item.get("attempts", 0))
    except (TypeError, ValueError):
        attempts = 0
    try:
        current_avg = float(item.get("score_avg", 0.0))
    except (TypeError, ValueError):
        current_avg = 0.0

    item["attempts"] = attempts + 1
    item["score_avg"] = round(((current_avg * attempts) + score) / (attempts + 1), 2)
    item["last_score"] = round(score, 2)
    item["last_practiced"] = utcnow_iso()

    if correct is None:
        correct = score >= 70
    if correct:
        try:
            item["correct"] = int(item.get("correct", 0)) + 1
        except (TypeError, ValueError):
            item["correct"] = 1

    return item


def record_event(
    state: dict,
    event_type: str,
    detail: Any = None,
    result: Any = None,
) -> dict:
    upgrade = ensure_upgrade_state(state)
    item = {
        "type": str(event_type or "event"),
        "at": utcnow_iso(),
    }
    if detail is not None:
        item["detail"] = detail
    if result is not None:
        item["result"] = result
    events = upgrade["events"]
    events.append(item)
    if len(events) > MAX_EVENTS:
        del events[:-MAX_EVENTS]
    return item


def mark_activity_completed(
    state: dict,
    activity_type: str,
    detail: Any = None,
    score: float = 0,
) -> None:
    upgrade = ensure_upgrade_state(state)
    session = upgrade["session"]
    try:
        count = int(session.get("completed_activities", 0))
    except (TypeError, ValueError):
        count = 0
    session["completed_activities"] = count + 1
    session["last_action"] = activity_type
    record_event(
        state,
        "activity_completed",
        detail={"activity_type": activity_type, "detail": detail},
        result={"score": round(float(score), 2)},
    )


def get_skills(state: dict) -> Dict[str, dict]:
    return ensure_upgrade_state(state)["skills"]
