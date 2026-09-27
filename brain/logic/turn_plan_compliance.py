"""Turn Plan Compliance Monitor v1.

Observes whether the executed turn respected the Orchestrator v2 Turn Plan.
It is diagnostic only: it never changes Teacher Policy or the learner reply.
"""

COMPLIANCE_VERSION = 1

def evaluate_turn_plan_compliance(turn_plan, *, learning_action=None,
                                  topic_transition=None, personalized_followup=None,
                                  question_support=None, recovery=None,
                                  orchestration=None):
    plan = dict(turn_plan or {})
    action = dict(learning_action or {})
    transition = dict(topic_transition or {})
    recovery = dict(recovery or {})
    orchestration = dict(orchestration or {})
    violations = []
    checks = {}

    planned_action = plan.get("action") or "CONTINUE"
    executed_action = action.get("action")
    checks["action_match"] = executed_action in {None, planned_action}
    if not checks["action_match"]:
        violations.append("action_mismatch")

    expected = plan.get("expected_outcome")
    actual_expected = action.get("expects_outcome")
    # The executor's outcome vocabulary is action-specific. Compare against
    # the canonical outcome for the executed action, rather than treating a
    # valid executor contract as a mismatch with a stale/generic plan label.
    canonical_expected = {
        "REPEAT_ERROR": "repeat_correct_form",
        "CORRECT_ERROR": "continue_after_correction",
        "MODEL_SENTENCE": "use_full_sentence",
        "SIMPLIFY": "answer_with_support",
        "REVIEW_WORD": "recall_target_word",
        "INTRODUCE_WORD": "notice_new_word",
        "ADVANCE": "independent_answer",
        "CONTINUE": "continue_conversation",
    }.get(executed_action, expected)
    checks["expected_outcome_match"] = actual_expected in {None, canonical_expected}
    if not checks["expected_outcome_match"]:
        violations.append("expected_outcome_mismatch")

    checks["topic_transition_respected"] = not (
        transition.get("transition") and not plan.get("allow_topic_transition", True)
    )
    if not checks["topic_transition_respected"]:
        violations.append("forbidden_topic_transition")

    checks["personalization_respected"] = not (
        personalized_followup and not plan.get("allow_personalization", True)
    )
    if not checks["personalization_respected"]:
        violations.append("forbidden_personalization")

    checks["question_simplifier_respected"] = not (
        question_support and not plan.get("allow_question_simplifier", False)
    )
    if not checks["question_simplifier_respected"]:
        violations.append("forbidden_question_simplifier")

    checks["recovery_respected"] = not (
        recovery.get("recovered") and not plan.get("allow_recovery_override", True)
    )
    if not checks["recovery_respected"]:
        violations.append("forbidden_recovery_override")

    orchestrator_conflicts = list(orchestration.get("conflicts") or [])
    checks["orchestrator_conflict_free"] = not orchestrator_conflicts
    for conflict in orchestrator_conflicts:
        marker = f"orchestrator:{conflict}"
        if marker not in violations:
            violations.append(marker)

    status = "COMPLIANT" if not violations else "VIOLATION"
    return {
        "version": COMPLIANCE_VERSION,
        "status": status,
        "compliant": not violations,
        "planned_action": planned_action,
        "executed_action": executed_action,
        "expected_outcome": expected,
        "executor_expected_outcome": actual_expected,
        "checks": checks,
        "violations": violations,
    }

def record_turn_plan_compliance(state, result):
    state["turn_plan_compliance_v1"] = dict(result or {})
    history = state.setdefault("turn_plan_compliance_history", [])
    history.append(dict(result or {}))
    if len(history) > 50:
        del history[:-50]
    return state["turn_plan_compliance_v1"]
