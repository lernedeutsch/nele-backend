"""Teacher Policy v2 / Next Best Learning Action for Nele.

Selects exactly one pedagogical priority from already-computed engine signals.
It does not detect errors, own memory, choose topics or render conversation.
"""

POLICY_VERSION = 2

ACTION_MAP = {
    "ask_repeat": "REPEAT_ERROR",
    "correct_and_continue": "CORRECT_ERROR",
    "model_full_sentence": "MODEL_SENTENCE",
    "simplify_next_question": "SIMPLIFY",
    "review_vocabulary": "REVIEW_WORD",
    "introduce_vocabulary": "INTRODUCE_WORD",
    "advance": "ADVANCE",
    "continue_conversation": "CONTINUE",
}

PRIORITY = {
    "REPEAT_ERROR": 100,
    "CORRECT_ERROR": 90,
    "SIMPLIFY": 80,
    "MODEL_SENTENCE": 70,
    "REVIEW_WORD": 60,
    "INTRODUCE_WORD": 40,
    "ADVANCE": 30,
    "CONTINUE": 10,
}


def choose_next_best_learning_action(
    *,
    teacher_action=None,
    learner_model=None,
    conversation_state=None,
    topic_manager=None,
    error_result=None,
    vocabulary_context=None,
):
    teacher_action = teacher_action or {}
    learner_model = learner_model or {}
    conversation_state = conversation_state or {}
    topic_manager = topic_manager or {}
    error_result = error_result or {}
    vocabulary_context = vocabulary_context or {}

    action = ACTION_MAP.get(teacher_action.get("action"), "CONTINUE")
    reason = teacher_action.get("reason") or "normal_progress"

    # Safety/teaching guard: global learner support outranks enrichment.
    if learner_model.get("autonomy") == "needs_support" and action in {
        "REVIEW_WORD", "INTRODUCE_WORD", "ADVANCE", "CONTINUE"
    }:
        action = "SIMPLIFY"
        reason = "learner_model_needs_support"

    # A recurring error requiring retrieval must not be displaced by vocabulary.
    error_decision = error_result.get("decision") or {}
    if error_decision.get("style") == "repeat_request":
        action = "REPEAT_ERROR"
        reason = "recurring_error_active_retrieval"

    selected = {
        "version": POLICY_VERSION,
        "action": action,
        "priority": PRIORITY[action],
        "reason": reason,
        "continue_conversation": action != "REPEAT_ERROR",
        "topic": conversation_state.get("topic") or topic_manager.get("topic"),
        "subtopic": conversation_state.get("subtopic") or topic_manager.get("subtopic"),
        "target_word": teacher_action.get("word"),
        "model": teacher_action.get("model"),
        "course_level": learner_model.get("course_level"),
    }
    return selected


def policy_to_teacher_action(policy, teacher_action=None):
    """Keep Teacher Engine rendering backward compatible while policy leads."""
    teacher_action = dict(teacher_action or {})
    reverse = {
        "REPEAT_ERROR": "ask_repeat",
        "CORRECT_ERROR": "correct_and_continue",
        "MODEL_SENTENCE": "model_full_sentence",
        "SIMPLIFY": "simplify_next_question",
        "REVIEW_WORD": "review_vocabulary",
        "INTRODUCE_WORD": "introduce_vocabulary",
        "ADVANCE": "advance",
        "CONTINUE": "continue_conversation",
    }
    teacher_action["action"] = reverse.get(policy.get("action"), teacher_action.get("action", "continue_conversation"))
    teacher_action["policy_reason"] = policy.get("reason")
    teacher_action["policy_priority"] = policy.get("priority")
    teacher_action["continue_conversation"] = policy.get("continue_conversation", True)
    return teacher_action
