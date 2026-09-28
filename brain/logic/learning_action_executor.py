"""Learning Action Executor v1.

Executes Teacher Policy v2 decisions. It does not decide which action is best.
Conversation Engine remains responsible for ordinary contextual questions.
"""

EXECUTOR_VERSION = 2

# Single source of truth for the Planner -> Executor contract. The handler
# names document which branch below owns each action; required fields are
# validated before execution instead of being guessed by the executor.
ACTION_CONTRACT = {
    "REPEAT_ERROR": {"handler": "repeat_error", "required": ("model",)},
    "CORRECT_ERROR": {"handler": "correct_error", "required": ("model",)},
    "MODEL_SENTENCE": {"handler": "model_sentence", "required": ("model",)},
    "SIMPLIFY": {"handler": "simplify", "required": ()},
    "REVIEW_WORD": {"handler": "review_word", "required": ("target_word",)},
    "INTRODUCE_WORD": {"handler": "introduce_word", "required": ("target_word",)},
    "ADVANCE": {"handler": "advance", "required": ()},
    "CONTINUE": {"handler": "continue", "required": ()},
}


def validate_learning_action(policy):
    """Return missing inputs for a known planner action."""
    policy = policy or {}
    action = policy.get("action") or "CONTINUE"
    contract = ACTION_CONTRACT.get(action)
    if contract is None:
        return {"valid": False, "action": action, "missing": (), "reason": "unknown_action"}
    missing = tuple(field for field in contract["required"] if not policy.get(field))
    return {
        "valid": not missing,
        "action": action,
        "handler": contract["handler"],
        "missing": missing,
        "reason": None if not missing else "required_input_missing",
    }



def _clean_example(entry):
    example = str((entry or {}).get("example") or "").strip()
    if example.lower().startswith("beispiel:"):
        example = example.split(":", 1)[1].strip()
    return example.strip("„”").strip()


def _vocabulary_entry(target_word, vocabulary_context):
    for entry in (vocabulary_context or {}).get("suggestions") or []:
        if str(entry.get("word") or "").lower() == str(target_word or "").lower():
            return entry
    return {}


def resolve_learning_action(policy, *, teacher_action=None, error_result=None):
    """Resolve a pedagogical policy into an executable action contract."""
    resolved = dict(policy or {})
    teacher_action = teacher_action or {}
    error_result = error_result or {}
    action = resolved.get("action") or "CONTINUE"
    resolved["planned_action"] = action
    error = error_result.get("error") or {}
    model = resolved.get("model") or teacher_action.get("model")
    if not model and action in {"REPEAT_ERROR", "CORRECT_ERROR"}:
        model = error.get("correct")
    if model:
        resolved["model"] = model
    elif action in {"REPEAT_ERROR", "CORRECT_ERROR", "MODEL_SENTENCE"}:
        resolved["requested_action"] = action
        resolved["action"] = "CONTINUE"
        resolved["fallback_reason"] = "model_required_but_unavailable"
        resolved["reason"] = "model_required_but_unavailable"
    return resolved


def execute_learning_action(
    policy,
    *,
    teacher_action=None,
    vocabulary_context=None,
    fallback_question="",
):
    policy = policy or {}
    teacher_action = teacher_action or {}
    action = policy.get("action") or "CONTINUE"
    planned_action = policy.get("planned_action") or action
    fallback_reason = policy.get("fallback_reason")
    model = policy.get("model") or teacher_action.get("model")
    target_word = policy.get("target_word") or teacher_action.get("word")
    fallback_question = str(fallback_question or "").strip()

    result = {
        "version": EXECUTOR_VERSION,
        "action": action,
        "planned_action": planned_action,
        "executed_action": action,
        "fallback_reason": fallback_reason,
        "executed": True,
        "target_word": target_word,
        "model": model,
        "expects_outcome": None,
        "reply": fallback_question,
    }

    if action == "REPEAT_ERROR":
        if model:
            result["reply"] = f"Richtig ist: „{model}“ Sag es bitte noch einmal."
            result["expects_outcome"] = "repeat_correct_form"
            return result
        result["action"] = "CONTINUE"
        result["expects_outcome"] = "continue_conversation"
        result["reply"] = fallback_question
        return result

    if action == "CORRECT_ERROR":
        if model:
            prefix = f"Du kannst sagen: „{model}“"
            result["reply"] = f"{prefix} {fallback_question}".strip()
            result["expects_outcome"] = "continue_after_correction"
            return result
        result["action"] = "CONTINUE"
        result["expects_outcome"] = "continue_conversation"
        result["reply"] = fallback_question
        return result

    if action == "MODEL_SENTENCE":
        if model:
            prefix = f"Du kannst sagen: „{model}“"
            result["reply"] = f"{prefix} {fallback_question}".strip()
            result["expects_outcome"] = "use_full_sentence"
            return result
        result["action"] = "CONTINUE"
        result["expects_outcome"] = "continue_conversation"
        result["reply"] = fallback_question
        return result

    if action == "SIMPLIFY":
        # SIMPLIFY means making the next turn easier. Do not attach a generic
        # emotional reaction here: this executor cannot know whether the
        # learner expressed a problem or simply made an ordinary statement.
        result["reply"] = fallback_question
        result["expects_outcome"] = "answer_with_support"
        return result

    if action in {"REVIEW_WORD", "INTRODUCE_WORD"} and target_word:
        entry = _vocabulary_entry(target_word, vocabulary_context)
        example = _clean_example(entry)
        if action == "REVIEW_WORD":
            if example:
                result["reply"] = f"Kennst du noch „{target_word}“? {example}"
            else:
                result["reply"] = f"Kennst du noch das Wort „{target_word}“? Benutze es bitte in einem Satz."
            result["expects_outcome"] = "recall_target_word"
        else:
            if example:
                result["reply"] = f"Ein neues Wort: „{target_word}“. {example} {fallback_question}".strip()
            else:
                result["reply"] = f"Ein neues Wort: „{target_word}“. {fallback_question}".strip()
            result["expects_outcome"] = "notice_new_word"
        return result

    if action == "ADVANCE":
        result["reply"] = fallback_question
        result["expects_outcome"] = "independent_answer"
        return result

    result["expects_outcome"] = "continue_conversation"
    return result
