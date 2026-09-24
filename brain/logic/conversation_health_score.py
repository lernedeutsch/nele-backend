"""Conversation Health Score v1.

Diagnostic aggregation for one turn and for long conversation simulations.
It never changes the learner reply or Teacher Policy.
"""

HEALTH_SCORE_VERSION = 1

def score_turn(*, compliance=None, orchestration=None, quality=None,
               topic_transition=None, turn_plan=None):
    compliance = dict(compliance or {})
    orchestration = dict(orchestration or {})
    quality = dict(quality or {})
    transition = dict(topic_transition or {})
    plan = dict(turn_plan or {})
    deductions = []
    score = 100

    if compliance and not compliance.get("compliant", True):
        count = max(1, len(compliance.get("violations") or []))
        points = min(40, 20 * count)
        score -= points
        deductions.append({"signal": "turn_plan_compliance", "points": points})

    conflicts = list(orchestration.get("conflicts") or [])
    if conflicts:
        points = min(30, 15 * len(conflicts))
        score -= points
        deductions.append({"signal": "orchestrator_conflict", "points": points})

    issues = list(quality.get("issues") or [])
    high_confidence = {"known_invalid_construction", "adjacent_duplicate"}
    serious = [issue for issue in issues if issue in high_confidence]
    warnings = [issue for issue in issues if issue not in high_confidence]
    if serious:
        points = min(30, 15 * len(serious))
        score -= points
        deductions.append({"signal": "quality_defect", "points": points})
    if warnings:
        points = min(10, 2 * len(warnings))
        score -= points
        deductions.append({"signal": "quality_warning", "points": points})

    if transition.get("transition") and plan and not plan.get("allow_topic_transition", True):
        score -= 20
        deductions.append({"signal": "forbidden_topic_transition", "points": 20})

    score = max(0, min(100, score))
    return {
        "version": HEALTH_SCORE_VERSION,
        "score": score,
        "healthy": score >= 80,
        "deductions": deductions,
    }

def score_conversation(turns):
    turns = list(turns or [])
    if not turns:
        return {
            "version": HEALTH_SCORE_VERSION,
            "score": 100,
            "healthy": True,
            "turn_count": 0,
            "average_turn_score": 100.0,
            "unhealthy_turns": [],
            "signals": {},
        }

    scores = []
    unhealthy = []
    signals = {}
    for index, turn in enumerate(turns):
        meta = dict((turn or {}).get("meta") or {})
        result = score_turn(
            compliance=meta.get("turn_plan_compliance"),
            orchestration=meta.get("conversation_orchestrator"),
            quality=meta.get("conversation_quality"),
            topic_transition=meta.get("topic_transition"),
            turn_plan=meta.get("turn_plan"),
        )
        scores.append(result["score"])
        if not result["healthy"]:
            unhealthy.append(index)
        for deduction in result["deductions"]:
            signal = deduction["signal"]
            signals[signal] = signals.get(signal, 0) + 1

    average = round(sum(scores) / len(scores), 1)
    return {
        "version": HEALTH_SCORE_VERSION,
        "score": round(average),
        "healthy": average >= 80 and not unhealthy,
        "turn_count": len(turns),
        "average_turn_score": average,
        "min_turn_score": min(scores),
        "unhealthy_turns": unhealthy,
        "signals": signals,
    }

def record_conversation_health(state, result):
    state["conversation_health_score_v1"] = dict(result or {})
    return state["conversation_health_score_v1"]
