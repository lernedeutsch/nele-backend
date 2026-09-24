"""Conversation Health Dashboard v1.

Builds a compact diagnostic report from conversation turns and Health Score.
Observational only: it never changes Nele's reply or teaching decisions.
"""
from collections import Counter
from brain.logic.conversation_health_score import score_conversation

DASHBOARD_VERSION = 1

def build_health_dashboard(turns):
    turns = list(turns or [])
    health = score_conversation(turns)
    compliance = []
    conflicts = []
    quality_issues = Counter()
    topic_transitions = []
    actions = Counter()

    for index, turn in enumerate(turns):
        meta = dict((turn or {}).get("meta") or {})
        plan = dict(meta.get("turn_plan") or {})
        if plan.get("action"):
            actions[plan["action"]] += 1

        check = dict(meta.get("turn_plan_compliance") or {})
        if check and not check.get("compliant", True):
            compliance.append({
                "turn": index,
                "violations": list(check.get("violations") or []),
            })

        orchestration = dict(meta.get("conversation_orchestrator") or {})
        if orchestration.get("conflicts"):
            conflicts.append({
                "turn": index,
                "conflicts": list(orchestration.get("conflicts") or []),
            })

        quality = dict(meta.get("conversation_quality") or {})
        for issue in quality.get("issues") or []:
            quality_issues[issue] += 1

        transition = dict(meta.get("topic_transition") or {})
        if transition.get("transition"):
            topic_transitions.append({
                "turn": index,
                "from": transition.get("topic"),
                "to": transition.get("next_topic"),
            })

    alerts = []
    if compliance:
        alerts.append("turn_plan_compliance")
    if conflicts:
        alerts.append("orchestrator_conflicts")
    if health.get("unhealthy_turns"):
        alerts.append("unhealthy_turns")
    if quality_issues.get("known_invalid_construction"):
        alerts.append("invalid_german")
    if quality_issues.get("adjacent_duplicate"):
        alerts.append("reply_repetition")

    return {
        "version": DASHBOARD_VERSION,
        "health": health,
        "summary": {
            "turn_count": len(turns),
            "health_score": health.get("score", 100),
            "average_turn_score": health.get("average_turn_score", 100.0),
            "min_turn_score": health.get("min_turn_score", 100),
            "healthy": health.get("healthy", True),
            "compliance_violation_count": len(compliance),
            "orchestrator_conflict_count": len(conflicts),
            "topic_transition_count": len(topic_transitions),
            "quality_issue_count": sum(quality_issues.values()),
        },
        "actions": dict(actions),
        "quality_issues": dict(quality_issues),
        "compliance_violations": compliance,
        "orchestrator_conflicts": conflicts,
        "topic_transitions": topic_transitions,
        "alerts": alerts,
    }

def record_health_dashboard(state, dashboard):
    state["conversation_health_dashboard_v1"] = dict(dashboard or {})
    return state["conversation_health_dashboard_v1"]
