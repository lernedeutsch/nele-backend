from datetime import datetime, timedelta, timezone

from brain.nele3_upgrade.dashboard import build_dashboard
from brain.nele3_upgrade.state import ensure_upgrade_state


def _parse_ts(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _events_since(state, since):
    upgrade = ensure_upgrade_state(state)
    result = []
    for event in upgrade.get("events", []):
        if not isinstance(event, dict):
            continue
        dt = _parse_ts(event.get("at"))
        if dt and dt >= since:
            result.append(event)
    return result


def _summarize_events(events):
    activities = {}
    scored = []
    for event in events:
        typ = str(event.get("type", "unknown"))
        activities[typ] = activities.get(typ, 0) + 1
        result = event.get("result")
        if isinstance(result, dict) and isinstance(result.get("score"), (int, float)):
            scored.append(float(result["score"]))
    average = round(sum(scored) / len(scored), 1) if scored else None
    return activities, average


def daily_report(state):
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    events = _events_since(state, start)
    activities, average = _summarize_events(events)
    dash = build_dashboard(state)
    return {
        "ok": True,
        "period": "today",
        "events": len(events),
        "activities": activities,
        "average_score": average,
        "today": dash.get("today", {}),
        "skills": dash.get("skills", {}),
        "teacher_plan": dash.get("teacher_plan", {}),
    }


def weekly_report(state):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    events = _events_since(state, start)
    activities, average = _summarize_events(events)
    dash = build_dashboard(state)
    return {
        "ok": True,
        "period": "last_7_days",
        "events": len(events),
        "activities": activities,
        "average_score": average,
        "progress": dash.get("progress", {}),
        "skills": dash.get("skills", {}),
        "teacher_plan": dash.get("teacher_plan", {}),
    }


def report_text(report):
    period = report.get("period")
    events = report.get("events", 0)
    average = report.get("average_score")
    if period == "today":
        intro = f"Heute habe ich {events} Lernaktivitäten gespeichert."
    else:
        intro = f"In den letzten sieben Tagen habe ich {events} Lernaktivitäten gespeichert."
    if average is not None:
        intro += f" Dein Durchschnitt bei bewerteten Übungen liegt bei {average} von 100."
    return intro
