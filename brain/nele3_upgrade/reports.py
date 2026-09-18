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
    completed = 0

    for event in events:
        typ = str(event.get("type", "unknown"))
        activities[typ] = activities.get(typ, 0) + 1

        if typ != "activity_completed":
            continue

        completed += 1
        result = event.get("result")

        if (
            isinstance(result, dict)
            and isinstance(result.get("score"), (int, float))
        ):
            scored.append(float(result["score"]))

    average = (
        round(sum(scored) / len(scored), 1)
        if scored
        else None
    )

    return activities, average, completed


def daily_report(state):
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    events = _events_since(state, start)
    activities, average, completed_addon = _summarize_events(events)
    dash = build_dashboard(state)
    today = dash.get("today", {})
    completed_exercises = int(today.get("completed_exercises", 0) or 0)
    return {
        "ok": True,
        "period": "today",
        "events": len(events),
        "completed_exercises": completed_exercises,
        "completed_addon_exercises": completed_addon,
        "activities": activities,
        "average_score": average,
        "today": today,
        "skills": dash.get("skills", {}),
        "teacher_plan": dash.get("teacher_plan", {}),
    }


def weekly_report(state):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    events = _events_since(state, start)
    activities, average, completed_addon = _summarize_events(events)
    dash = build_dashboard(state)
    return {
        "ok": True,
        "period": "last_7_days",
        "events": len(events),
        "completed_addon_exercises": completed_addon,
        "activities": activities,
        "average_score": average,
        "progress": dash.get("progress", {}),
        "skills": dash.get("skills", {}),
        "teacher_plan": dash.get("teacher_plan", {}),
    }


def report_text(report):
    period = report.get("period")
    average = report.get("average_score")

    if period == "today":
        completed = int(
            report.get("completed_exercises", 0)
            or 0
        )
        intro = (
            f"Heute hast du {completed} Übungen abgeschlossen."
        )
    else:
        completed = int(
            report.get("completed_addon_exercises", 0)
            or 0
        )
        intro = (
            "In den letzten sieben Tagen habe ich "
            f"{completed} abgeschlossene Zusatzübungen gespeichert."
        )

    if average is not None:
        intro += (
            " Dein Durchschnitt bei bewerteten Zusatzübungen "
            f"liegt bei {average} von 100."
        )

    return intro
