"""Conversation Orchestrator v1.

Defines and validates the ownership/precedence contract between Nele's
conversation engines. It does not replace engines or generate language.
"""

ORCHESTRATOR_VERSION = 1

PIPELINE = [
    "learning_outcome",
    "response_understanding",
    "vocabulary",
    "error_engine",
    "learner_model",
    "teacher_engine",
    "teacher_policy",
    "topic_transition",
    "personalization",
    "coherence",
    "question_simplifier",
    "learning_action_executor",
    "quality_controller",
    "recovery",
    "state_commit",
]

PEDAGOGY_ACTIONS = {
    "REPEAT_ERROR", "CORRECT_ERROR", "SIMPLIFY", "MODEL_SENTENCE", "REVIEW_WORD",
}

def build_orchestration_contract(*, teacher_policy=None, struggle=False,
                                 explicit_topic=None, topic_transition=None):
    teacher_policy = teacher_policy or {}
    topic_transition = topic_transition or {}
    action = teacher_policy.get("action") or "CONTINUE"
    pedagogy_locked = action in PEDAGOGY_ACTIONS

    return {
        "version": ORCHESTRATOR_VERSION,
        "pipeline": list(PIPELINE),
        "action": action,
        "pedagogy_locked": pedagogy_locked,
        "allow_topic_transition": (
            not pedagogy_locked
            and not struggle
            and not bool(explicit_topic)
        ),
        "allow_personalization": not pedagogy_locked,
        "allow_question_simplifier": action == "SIMPLIFY" and bool(struggle),
        "allow_recovery_override": action in {"CONTINUE", "ADVANCE"},
        "topic_transition_requested": bool(topic_transition.get("transition")),
    }

def enforce_orchestration(contract, *, topic_transition=None,
                          personalized_followup=None, question_support=None,
                          recovery=None):
    contract = dict(contract or {})
    topic_transition = dict(topic_transition or {})
    recovery = dict(recovery or {})
    conflicts = []

    if topic_transition.get("transition") and not contract.get("allow_topic_transition"):
        conflicts.append("topic_transition_blocked")
        topic_transition["transition"] = False
        topic_transition["next_topic"] = topic_transition.get("topic")
        topic_transition["orchestrator_blocked"] = True

    if personalized_followup and not contract.get("allow_personalization"):
        conflicts.append("personalization_blocked")
        personalized_followup = None

    if question_support and not contract.get("allow_question_simplifier"):
        conflicts.append("question_simplifier_blocked")
        question_support = None

    if recovery.get("recovered") and not contract.get("allow_recovery_override"):
        conflicts.append("recovery_override_blocked")
        recovery["reply"] = recovery.get("original") or recovery.get("reply")
        recovery["recovered"] = False
        recovery["strategy"] = "orchestrator_blocked"

    return {
        "version": ORCHESTRATOR_VERSION,
        "contract": contract,
        "conflicts": conflicts,
        "topic_transition": topic_transition,
        "personalized_followup": personalized_followup,
        "question_support": question_support,
        "recovery": recovery,
        "valid": not conflicts,
    }

def record_orchestration(state, result):
    state["conversation_orchestrator_v1"] = dict(result or {})
    return state["conversation_orchestrator_v1"]
