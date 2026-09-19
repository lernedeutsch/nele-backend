from flask import Blueprint, jsonify, request

from brain.logic.learner_identity import normalize_learner_id
from brain.logic.memory import (
    get_conversation_state,
    save_conversation_state,
)
from brain.logic.session_service import start_conversation_session
from brain.nele3_upgrade import UPGRADE_VERSION
from brain.nele3_upgrade.activities import (
    start_activity,
    answer_active_task,
)
from brain.nele3_upgrade.dashboard import build_dashboard
from brain.nele3_upgrade.pronunciation import evaluate_pronunciation
from brain.nele3_upgrade.reports import daily_report, weekly_report
from brain.nele3_upgrade.teacher_brain import select_next_action


nele3_api = Blueprint("nele3_api", __name__)


def _session_id(data=None, explicit=None):
    data = data or {}
    value = (
        explicit
        or data.get("session_id")
        or data.get("student_id")
    )
    return normalize_learner_id(value)


def _session_required():
    return jsonify({
        "ok": False,
        "error": "session_id_required",
        "message": "Eine gültige session_id ist erforderlich.",
    }), 400


@nele3_api.get("/api/nele3/status")
def nele3_status():
    return jsonify({
        "ok": True,
        "service": "Nele production feature layer",
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
    """Compatibility endpoint routed through the canonical session service."""

    data = request.get_json(silent=True) or {}
    sid = _session_id(data)

    if not sid:
        return _session_required()

    new_conversation = bool(
        data.get("new_conversation", False)
    )

    reply = start_conversation_session(
        sid,
        new_conversation=new_conversation,
    )

    return jsonify({
        "ok": True,
        "student_id": sid,
        "session_id": sid,
        "reply": reply,
        "finished": False,
        "meta": {
            "new_session": True,
            "new_conversation": new_conversation,
            "upgrade": UPGRADE_VERSION,
            "canonical_session_flow": True,
        },
    })


@nele3_api.get("/api/dashboard/<session_id>")
def api_dashboard(session_id):
    sid = _session_id(explicit=session_id)
    if not sid:
        return _session_required()
    state = get_conversation_state(sid)
    return jsonify(build_dashboard(state))


@nele3_api.get("/api/daily/<session_id>")
def api_daily(session_id):
    sid = _session_id(explicit=session_id)
    if not sid:
        return _session_required()
    state = get_conversation_state(sid)
    return jsonify(daily_report(state))


@nele3_api.get("/api/weekly/<session_id>")
def api_weekly(session_id):
    sid = _session_id(explicit=session_id)
    if not sid:
        return _session_required()
    state = get_conversation_state(sid)
    return jsonify(weekly_report(state))


@nele3_api.get("/api/next/<session_id>")
def api_next(session_id):
    sid = _session_id(explicit=session_id)
    if not sid:
        return _session_required()
    state = get_conversation_state(sid)
    action = select_next_action(state)
    save_conversation_state(sid)
    return jsonify({
        "ok": True,
        "session_id": sid,
        "action": action,
    })


@nele3_api.post("/api/activity/start")
def api_activity_start():
    data = request.get_json(silent=True) or {}
    sid = _session_id(data)

    if not sid:
        return _session_required()

    activity_type = data.get("type") or data.get("activity")
    if not str(activity_type or "").strip():
        return jsonify({
            "ok": False,
            "error": "activity_required",
        }), 400

    state = get_conversation_state(sid)
    result = start_activity(
        state,
        activity_type,
        data.get("level"),
    )
    save_conversation_state(sid)
    return jsonify({
        "ok": True,
        "session_id": sid,
        **result,
    })


@nele3_api.post("/api/activity/answer")
def api_activity_answer():
    data = request.get_json(silent=True) or {}
    sid = _session_id(data)

    if not sid:
        return _session_required()

    state = get_conversation_state(sid)
    result = answer_active_task(
        state,
        data.get("message"),
        transcript=data.get("transcript"),
        input_mode=data.get("input_mode"),
    )
    save_conversation_state(sid)

    if not result:
        return jsonify({
            "ok": False,
            "error": "no_active_task",
            "session_id": sid,
        }), 409

    return jsonify({
        "ok": True,
        "session_id": sid,
        **result,
    })


@nele3_api.post("/api/pronunciation/evaluate")
def api_pronunciation_evaluate():
    data = request.get_json(silent=True) or {}
    sid = _session_id(data)

    if not sid:
        return _session_required()

    target = str(
        data.get("target")
        or ""
    ).strip()
    transcript = str(
        data.get("transcript")
        or ""
    ).strip()

    if not target or not transcript:
        return jsonify({
            "ok": False,
            "error": "target_and_transcript_required",
        }), 400

    state = get_conversation_state(sid)
    result = evaluate_pronunciation(
        state,
        target,
        transcript,
    )
    save_conversation_state(sid)

    return jsonify({
        "ok": True,
        "session_id": sid,
        **result,
    })
