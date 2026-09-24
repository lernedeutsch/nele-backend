"""Conversation Orchestrator v2 with Turn Plan.

Defines and validates the ownership/precedence contract between Nele's
conversation engines. It does not replace engines or generate language.
"""

ORCHESTRATOR_VERSION = 2

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


EXPECTED_OUTCOMES = {
    "REPEAT_ERROR": "repeat_correct_form",
    "CORRECT_ERROR": "continue_after_correction",
    "MODEL_SENTENCE": "use_full_sentence",
    "SIMPLIFY": "answer_with_support",
    "REVIEW_WORD": "recall_target_word",
    "INTRODUCE_WORD": "notice_new_word",
    "ADVANCE": "independent_answer",
    "CONTINUE": "continue_conversation",
}

def build_turn_plan(*, teacher_policy=None, topic=None, struggle=False,
                    explicit_topic=None, error_result=None,
                    response_understanding=None):
    teacher_policy = teacher_policy or {}
    error_result = error_result or {}
    action = teacher_policy.get("action") or "CONTINUE"
    pedagogy_locked = action in PEDAGOGY_ACTIONS
    goal = {
        "REPEAT_ERROR": "repair_error",
        "CORRECT_ERROR": "repair_error",
        "MODEL_SENTENCE": "model_full_sentence",
        "SIMPLIFY": "restore_understanding",
        "REVIEW_WORD": "review_vocabulary",
        "INTRODUCE_WORD": "expand_vocabulary",
        "ADVANCE": "increase_independence",
        "CONTINUE": "continue_conversation",
    }.get(action, "continue_conversation")
    return {
        "version": ORCHESTRATOR_VERSION,
        "goal": goal,
        "topic": topic,
        "action": action,
        "model": teacher_policy.get("model"),
        "target_word": teacher_policy.get("target_word"),
        "expected_outcome": EXPECTED_OUTCOMES.get(action, "continue_conversation"),
        "pedagogy_locked": pedagogy_locked,
        "keep_topic": bool(pedagogy_locked or struggle),
        "allow_topic_transition": not pedagogy_locked and not struggle and not bool(explicit_topic),
        "allow_personalization": not pedagogy_locked,
        "allow_question_simplifier": action == "SIMPLIFY" and bool(struggle),
        "allow_recovery_override": action in {"CONTINUE", "ADVANCE"},
        "learner_topic_change": explicit_topic if explicit_topic and explicit_topic != topic else None,
        "has_active_error": bool(error_result.get("error") or error_result.get("recast")),
        "response_confidence": (response_understanding or {}).get("confidence"),
    }


def build_orchestration_contract(*, teacher_policy=None, struggle=False,
                                 explicit_topic=None, topic_transition=None,
                                 turn_plan=None):
    teacher_policy = teacher_policy or {}
    topic_transition = topic_transition or {}
    plan = dict(turn_plan or build_turn_plan(
        teacher_policy=teacher_policy,
        struggle=struggle,
        explicit_topic=explicit_topic,
    ))
    return {
        "version": ORCHESTRATOR_VERSION,
        "pipeline": list(PIPELINE),
        "turn_plan": plan,
        "action": plan["action"],
        "pedagogy_locked": plan["pedagogy_locked"],
        "allow_topic_transition": plan["allow_topic_transition"],
        "allow_personalization": plan["allow_personalization"],
        "allow_question_simplifier": plan["allow_question_simplifier"],
        "allow_recovery_override": plan["allow_recovery_override"],
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
    state["conversation_orchestrator_v2"] = dict(result or {})
    state["conversation_orchestrator_v1"] = dict(result or {})
    state["turn_plan_v1"] = dict(((result or {}).get("contract") or {}).get("turn_plan") or {})
    return state["conversation_orchestrator_v2"]
