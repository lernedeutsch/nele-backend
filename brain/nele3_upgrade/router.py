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

