from brain.nele3_upgrade.activities import start_activity, answer_active_task
from brain.nele3_upgrade.dashboard import dashboard_text
from brain.nele3_upgrade.reports import daily_report, weekly_report, report_text
from brain.nele3_upgrade.state import (
    ensure_upgrade_state,
    get_active_task,
    set_active_task,
    register_turn,
    record_event,
)
from brain.nele3_upgrade.teacher_brain import select_next_action


def _n(text):
    return " ".join(str(text or "").strip().lower().split())


def _contains_any(text, needles):
    return any(n in text for n in needles)


def handle_upgrade_message(user_message, state, session_id="default", transcript=None):
    """Handle only explicit Nele-3 features and active tasks.

    Normal conversation remains in Nele 1's original router.
    """
    ensure_upgrade_state(state)
    register_turn(state)

    message = str(user_message or "").strip()
    norm = _n(message)

    active = get_active_task(state)
    if active:
        if norm in {"stop", "stopp", "abbrechen", "übung beenden", "ubung beenden"}:
            set_active_task(state, None)
            record_event(state, "activity_cancelled", detail=active.get("type"))
            return True, "Okay. Wir beenden diese Übung.", {"activity_cancelled": True}

        result = answer_active_task(state, message, transcript=transcript)
        if result:
            return True, result.get("reply", ""), result.get("meta", {}) | {
                "score": result.get("score"),
                "completed": result.get("completed", False),
            }

    if _contains_any(norm, {"wochenbericht", "wochen bericht", "bericht der woche"}):
        report = weekly_report(state)
        return True, report_text(report), {"report": report}

    if _contains_any(norm, {"tagesbericht", "heutiger bericht", "bericht heute"}):
        report = daily_report(state)
        return True, report_text(report), {"report": report}

    if _contains_any(norm, {"mein fortschritt", "lernfortschritt", "dashboard", "wie weit bin ich"}):
        return True, dashboard_text(state), {"dashboard": True}

    if _contains_any(norm, {"was soll ich lernen", "nächster schritt", "naechster schritt", "weiterlernen", "weiter lernen"}):
        action = select_next_action(state)
        if action.get("type") == "existing_teacher_plan":
            return True, action.get("message") or "Wir machen mit deiner nächsten Wiederholung weiter.", {"teacher_action": action}
        started = start_activity(state, action.get("activity"), action.get("level"))
        reply = "\n\n".join(x for x in [action.get("message"), started.get("reply")] if x)
        return True, reply, {"teacher_action": action, **started.get("meta", {})}

    if _contains_any(norm, {"rollenspiel", "rollenspiel machen", "dialog üben", "dialog uben", "alltagsdialog"}):
        started = start_activity(state, "dialogue")
        return True, started["reply"], started.get("meta", {})

    if _contains_any(norm, {"hörübung", "hoeruebung", "hörtraining", "hoertraining", "hören üben", "horen uben"}):
        started = start_activity(state, "listening")
        return True, started["reply"], {**started.get("meta", {}), "speak_text": started.get("speak_text")}

    if _contains_any(norm, {"schreibübung", "schreibuebung", "schreiben üben", "schreiben uben"}):
        started = start_activity(state, "writing")
        return True, started["reply"], started.get("meta", {})

    if _contains_any(norm, {"arbeitsdeutsch", "housekeeping üben", "housekeeping uben", "hotel deutsch", "deutsch für die arbeit", "deutsch fur die arbeit"}):
        started = start_activity(state, "work_german")
        return True, started["reply"], started.get("meta", {})

    if _contains_any(norm, {"aussprache üben", "aussprache uben", "aussprachetraining", "aussprache training"}):
        started = start_activity(state, "pronunciation")
        return True, started["reply"], {**started.get("meta", {}), "speak_text": started.get("speak_text")}

    return False, None, {}
