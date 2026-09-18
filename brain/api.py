from flask import Blueprint, jsonify, request

from brain.logic.memory import (
    get_conversation_state,
    save_conversation_state,
)
from brain.logic.welcome import generate_welcome_reply
from brain.nele3_upgrade import UPGRADE_VERSION
from brain.nele3_upgrade.activities import start_activity, answer_active_task
from brain.nele3_upgrade.dashboard import build_dashboard
from brain.nele3_upgrade.pronunciation import evaluate_pronunciation
from brain.nele3_upgrade.reports import daily_report, weekly_report
from brain.nele3_upgrade.state import (
    ensure_upgrade_state,
    start_upgrade_session,
    set_active_task,
)
from brain.nele3_upgrade.teacher_brain import select_next_action


nele3_api = Blueprint("nele3_api", __name__)


def _session_id(data=None):
    data = data or {}
    value = data.get("session_id") or data.get("student_id") or "default"
    value = str(value).strip() or "default"
    return value[:100]


@nele3_api.get("/api/nele3/status")
def nele3_status():
    return jsonify({
        "ok": True,
        "service": "Nele 1 + Nele 3 feature layer",
        "version": UPGRADE_VERSION,
        "teacher_brain": True,
        "persistent_memory": True,
        "daily_memory": True,
        "session_memory": True,
        "adaptive_review": True,
        "vocabulary_memory": True,
        "error_memory": True,
        "pronunciation_memory": True,
        "listening": True,
        "writing": True,
        "dialogues": True,
        "work_german": True,
        "dashboard": True,
        "weekly_reports": True,
        "paid_api_required": False,
    })


@nele3_api.post("/api/session/start")
def api_session_start():
    data = request.get_json(silent=True) or {}
    sid = _session_id(data)
    state = get_conversation_state(sid)
    ensure_upgrade_state(state)
    set_active_task(state, None)
    start_upgrade_session(state)
    reply = generate_welcome_reply(sid)
    save_conversation_state(sid)
    return jsonify({
        "ok": True,
        "student_id": sid,
        "session_id": sid,
        "reply": reply,
        "finished": False,
        "meta": {"new_session": True, "upgrade": UPGRADE_VERSION},
    })


@nele3_api.get("/api/dashboard/<session_id>")
def api_dashboard(session_id):
    state = get_conversation_state(session_id)
    return jsonify(build_dashboard(state))


@nele3_api.get("/api/daily/<session_id>")
def api_daily(session_id):
    state = get_conversation_state(session_id)
    return jsonify(daily_report(state))


@nele3_api.get("/api/weekly/<session_id>")
def api_weekly(session_id):
    state = get_conversation_state(session_id)
    return jsonify(weekly_report(state))


@nele3_api.get("/api/next/<session_id>")
def api_next(session_id):
    state = get_conversation_state(session_id)
    action = select_next_action(state)
    save_conversation_state(session_id)
    return jsonify({"ok": True, "action": action})


@nele3_api.post("/api/activity/start")
def api_activity_start():
    data = request.get_json(silent=True) or {}
    sid = _session_id(data)
    state = get_conversation_state(sid)
    result = start_activity(state, data.get("type") or data.get("activity"), data.get("level"))
    save_conversation_state(sid)
    return jsonify({"ok": True, "session_id": sid, **result})


@nele3_api.post("/api/activity/answer")
def api_activity_answer():
    data = request.get_json(silent=True) or {}
    sid = _session_id(data)
    state = get_conversation_state(sid)
    result = answer_active_task(state, data.get("message"), transcript=data.get("transcript"))
    save_conversation_state(sid)
    if not result:
        return jsonify({"ok": False, "error": "no_active_task", "session_id": sid}), 409
    return jsonify({"ok": True, "session_id": sid, **result})


@nele3_api.post("/api/pronunciation/evaluate")
def api_pronunciation_evaluate():
    data = request.get_json(silent=True) or {}
    sid = _session_id(data)
    target = str(data.get("target") or "").strip()
    transcript = str(data.get("transcript") or "").strip()
    if not target or not transcript:
        return jsonify({"ok": False, "error": "target_and_transcript_required"}), 400
    state = get_conversation_state(sid)
    result = evaluate_pronunciation(state, target, transcript)
    save_conversation_state(sid)
    return jsonify({"ok": True, "session_id": sid, **result})
