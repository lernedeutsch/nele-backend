from brain.nele3_upgrade.activities import start_activity, answer_active_task
from brain.nele3_upgrade.dashboard import dashboard_text
from brain.nele3_upgrade.reports import daily_report, weekly_report, report_text
from brain.nele3_upgrade.state import (
    ensure_upgrade_state,
    get_active_task,
    set_active_task,
    register_turn,
    record_event,
    get_pending_recommendation,
    set_pending_recommendation,
    clear_pending_recommendation,
)
from brain.nele3_upgrade.teacher_brain import (
    DISABLED_UPGRADE_ACTIVITIES,
    select_next_action,
    build_adaptive_recommendation,
)


def _n(text):
    return " ".join(str(text or "").strip().lower().split())


def _contains_any(text, needles):
    return any(n in text for n in needles)


def handle_upgrade_message(user_message, state, session_id="default", transcript=None, input_mode=None):
    """Handle only explicit Nele-3 features and active tasks.

    Normal conversation remains in Nele 1's original router.
    """
    upgrade = ensure_upgrade_state(state)
    register_turn(state)

    message = str(user_message or "").strip()
    norm = _n(message)

    # 📚 Mit dem Kurs üben is a closed curriculum path. Nele-3 addon
    # activities (Alltagsdialog, Arbeitsdeutsch, Aussprache, Sprechen) must
    # never interrupt or extend an A1 lesson. Clear stale addon state left by
    # older deployments and hand the turn back to the normal course router.
    if str(state.get("conversation_mode") or "").strip().lower() == "course":
        if get_pending_recommendation(state):
            clear_pending_recommendation(state)
        if get_active_task(state):
            set_active_task(state, None)
        return False, None, {"course_only": True}

    # Po ponownym otwarciu strony Nele najpierw pyta
    # "Wie geht es dir?". Odpowiedź na to pytanie nie może
    # zostać potraktowana jako odpowiedź do zachowanego
    # Schreibübung / Hörübung / Dialogu / Aussprache.
    #
    # Główny router obsłuży wellbeing, a następnie
    # response_engine wznowi dokładnie aktywne ćwiczenie.
    if state.get("last_question") == "wellbeing":
        return False, None, {}

    pending = get_pending_recommendation(state)

    # Hören und Schreiben werden außerhalb von Nele trainiert.
    # Alte, bereits gespeicherte Empfehlungen dürfen nach einem Deploy
    # nicht wieder als aktive Nele-Aufgabe erscheinen.
    if (
        isinstance(pending, dict)
        and str(pending.get("activity") or "").strip().lower()
        in DISABLED_UPGRADE_ACTIVITIES
    ):
        clear_pending_recommendation(state)
        pending = None

    if pending:
        yes_answers = {
            "ja", "ja gern", "ja gerne", "gern", "gerne",
            "okay", "ok", "klar", "natürlich", "ja bitte",
            "machen wir", "ja machen wir", "tak",
        }
        no_answers = {
            "nein", "nein danke", "nicht jetzt", "später",
            "lieber nicht", "jetzt nicht", "nie", "nie teraz",
        }

        if norm in yes_answers:
            activity = pending.get("activity")
            clear_pending_recommendation(state)
            started = start_activity(state, activity)
            return True, started.get("reply", ""), {
                **started.get("meta", {}),
                "adaptive_recommendation": True,
                **(
                    {"speak_text": started.get("speak_text")}
                    if started.get("speak_text")
                    else {}
                ),
            }

        if norm in no_answers:
            clear_pending_recommendation(state)
            return True, "Okay, kein Problem. Wir machen später weiter.", {
                "adaptive_recommendation_declined": True,
                "recommendation_chain_stopped": True,
            }

    active = get_active_task(state)

    # Ebenso verwerfen wir alte aktive Hören-/Schreiben-Aufgaben aus
    # gespeicherter Student Memory. Die eigentlichen Implementierungen
    # bleiben im Projekt erhalten und können später reaktiviert werden.
    if (
        isinstance(active, dict)
        and str(active.get("type") or "").strip().lower()
        in DISABLED_UPGRADE_ACTIVITIES
    ):
        set_active_task(state, None)
        active = None

    if active:
        if norm in {"nein", "nein danke", "nicht jetzt", "lieber nicht", "jetzt nicht"}:
            set_active_task(state, None)
            record_event(state, "activity_cancelled", detail=active.get("type"))
            return True, "Okay, kein Problem. Wir machen später weiter.", {
                "activity_cancelled": True,
                "activity": active.get("type"),
            }

        if norm in {"stop", "stopp", "abbrechen", "übung beenden", "ubung beenden"}:
            set_active_task(state, None)
            record_event(state, "activity_cancelled", detail=active.get("type"))
            return True, "Okay. Wir beenden diese Übung.", {"activity_cancelled": True}

        repeat_requests = {
            "bitte wiederholen",
            "wiederholen bitte",
            "wiederhol bitte",
            "wiederhole bitte",
            "noch einmal",
            "noch einmal bitte",
            "nochmal",
            "nochmal bitte",
            "kannst du das bitte wiederholen",
            "kannst du das noch einmal sagen",
            "powtórz",
            "powtorz",
            "powtórz proszę",
            "powtorz prosze",
            "jeszcze raz",
            "jeszcze raz proszę",
            "jeszcze raz prosze",
        }

        if norm in repeat_requests:
            activity_type = active.get("type", "")
            prompt = str(active.get("prompt") or "").strip()
            speak_text = str(active.get("speak_text") or "").strip()

            if activity_type == "listening":
                return True, (
                    "Hör noch einmal gut zu.\n\n" + prompt
                ).strip(), {
                    "activity": "listening",
                    "speak_text": speak_text,
                    "repeat": True,
                }

            if activity_type == "pronunciation":
                return True, (
                    prompt or
                    f"Sprich bitte nach: „{active.get('target', '')}“"
                ), {
                    "activity": "pronunciation",
                    "speak_text": speak_text or str(active.get("target") or "").strip(),
                    "repeat": True,
                }

            if prompt:
                return True, prompt, {
                    "activity": activity_type,
                    "repeat": True,
                }

        result = answer_active_task(state, message, transcript=transcript, input_mode=input_mode)
        if result:
            return True, result.get("reply", ""), result.get("meta", {}) | {
                "score": result.get("score"),
                "completed": result.get("completed", False),
            }

    continue_requests = {
        "weiter",
        "weiter bitte",
        "bitte weiter",
        "machen wir weiter",
        "wir machen weiter",
        "noch eine",
        "noch eine bitte",
        "następne",
        "nastepne",
        "dalej",
    }

    if norm in continue_requests:
        session = upgrade.get("session") or {}
        last_action = str(session.get("last_action") or "").strip()

        repeatable_activities = {
            "dialogue",
            "work_german",
            "pronunciation",
            "speaking",
        }

        if last_action in repeatable_activities:
            started = start_activity(state, last_action)
            return True, started.get("reply", ""), {
                **started.get("meta", {}),
                "continued_activity": last_action,
                **(
                    {"speak_text": started.get("speak_text")}
                    if started.get("speak_text")
                    else {}
                ),
            }

    # Jeżeli uczeń zamiast "ja/nein" wybiera własną komendę,
    # stara propozycja nie może pozostać aktywna.
    if pending:
        clear_pending_recommendation(state)

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
        return True, (
            "Hören übst du auf deiner Deutschsprechen-Seite."
        ), {
            "activity_disabled": "listening",
        }

    if _contains_any(norm, {"schreibübung", "schreibuebung", "schreiben üben", "schreiben uben"}):
        return True, (
            "Schreiben übst du auf deiner Deutschsprechen-Seite."
        ), {
            "activity_disabled": "writing",
        }

    if _contains_any(norm, {"arbeitsdeutsch", "housekeeping üben", "housekeeping uben", "hotel deutsch", "deutsch für die arbeit", "deutsch fur die arbeit"}):
        started = start_activity(state, "work_german")
        return True, started["reply"], started.get("meta", {})

    if _contains_any(norm, {"aussprache üben", "aussprache uben", "aussprachetraining", "aussprache training"}):
        started = start_activity(state, "pronunciation")
        return True, started["reply"], {**started.get("meta", {}), "speak_text": started.get("speak_text")}

    return False, None, {}
