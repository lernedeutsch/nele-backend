"""Teacher Policy v3 / Curriculum-Aware Next Best Learning Action for Nele.

Selects exactly one pedagogical priority from already-computed engine signals.
It does not detect errors, own memory, choose topics or render conversation.
"""

POLICY_VERSION = 3

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

CURRICULUM_ACTIONS = {
    "conversation:supported_answer": "SIMPLIFY",
    "conversation:full_sentence": "MODEL_SENTENCE",
    "conversation:continue_after_correction": "CONTINUE",
    "conversation:continuation": "CONTINUE",
    "conversation:independent_answer": "ADVANCE",
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
    # A teacher action that already recognized a valid short answer as normal
    # continuation may pass through; otherwise a learner who currently needs
    # support should not be pushed into enrichment or advancement.
    valid_short_answer = (
        teacher_action.get("action") == "continue_conversation"
        and teacher_action.get("reason") == "valid_expected_short_answer"
    )
    if learner_model.get("autonomy") == "needs_support" and not valid_short_answer and action in {
        "REVIEW_WORD", "INTRODUCE_WORD", "ADVANCE", "CONTINUE"
    }:
        action = "SIMPLIFY"
        reason = "learner_model_needs_support"

    # A recurring error requiring retrieval must not be displaced by curriculum.
    error_decision = error_result.get("decision") or {}
    if error_decision.get("style") == "repeat_request":
        action = "REPEAT_ERROR"
        reason = "recurring_error_active_retrieval"

    next_skill = learner_model.get("next_curriculum_skill") or {}
    curriculum_skill = next_skill.get("skill")
    curriculum_reason = next_skill.get("reason")

    # Curriculum may steer only low-priority normal/enrichment actions. Direct
    # correction, repetition, support and an explicit sentence model remain
    # authoritative for the current turn.
    if action in {"REVIEW_WORD", "INTRODUCE_WORD", "ADVANCE", "CONTINUE"} and curriculum_skill:
        if curriculum_reason in {"curriculum_review", "dynamic_review"}:
            if curriculum_skill.startswith("vocabulary:"):
                action = "REVIEW_WORD"
                reason = "curriculum_vocabulary_review"
            elif curriculum_skill.startswith("correct_form:"):
                # A concrete correction model is required before active repeat.
                # Without one, keep the normal action but surface the target.
                reason = "curriculum_correct_form_review_pending_context"
            else:
                action = CURRICULUM_ACTIONS.get(curriculum_skill, action)
                reason = "curriculum_skill_review"
        elif curriculum_reason == "prerequisites_met":
            action = CURRICULUM_ACTIONS.get(curriculum_skill, action)
            reason = "curriculum_next_ready_skill"

    # Model-dependent actions are executable only with a concrete model.
    # Keep the published policy consistent with what the executor can do.
    if action in {"REPEAT_ERROR", "CORRECT_ERROR", "MODEL_SENTENCE"} and not teacher_action.get("model"):
        action = "CONTINUE"
        reason = "model_required_but_unavailable"

    selected = {
        "version": POLICY_VERSION,
        "action": action,
        "priority": PRIORITY[action],
        "reason": reason,
        "continue_conversation": action != "REPEAT_ERROR",
        "topic": conversation_state.get("topic") or topic_manager.get("topic"),
        "subtopic": conversation_state.get("subtopic") or topic_manager.get("subtopic"),
        "target_word": (
            curriculum_skill.split(":", 1)[1]
            if action == "REVIEW_WORD" and curriculum_skill and curriculum_skill.startswith("vocabulary:")
            else teacher_action.get("word")
        ),
        "model": teacher_action.get("model"),
        "course_level": learner_model.get("course_level"),
        "next_curriculum_skill": next_skill or None,
        "curriculum_skill": curriculum_skill,
        "curriculum_reason": curriculum_reason,
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
