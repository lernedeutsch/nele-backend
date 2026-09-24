"""Learning Action Executor v1.

Executes Teacher Policy v2 decisions. It does not decide which action is best.
Conversation Engine remains responsible for ordinary contextual questions.
"""

EXECUTOR_VERSION = 1


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
    model = policy.get("model") or teacher_action.get("model")
    target_word = policy.get("target_word") or teacher_action.get("word")
    fallback_question = str(fallback_question or "").strip()

    result = {
        "version": EXECUTOR_VERSION,
        "action": action,
        "executed": True,
        "target_word": target_word,
        "model": model,
        "expects_outcome": None,
        "reply": fallback_question,
    }

    if action == "REPEAT_ERROR" and model:
        result["reply"] = f"Richtig ist: „{model}“ Sag es bitte noch einmal."
        result["expects_outcome"] = "repeat_correct_form"
        return result

    if action == "CORRECT_ERROR" and model:
        prefix = f"Du kannst sagen: „{model}“"
        result["reply"] = f"{prefix} {fallback_question}".strip()
        result["expects_outcome"] = "continue_after_correction"
        return result

    if action == "MODEL_SENTENCE" and model:
        prefix = f"Du kannst sagen: „{model}“"
        result["reply"] = f"{prefix} {fallback_question}".strip()
        result["expects_outcome"] = "use_full_sentence"
        return result

    if action == "SIMPLIFY":
        result["reply"] = f"Kein Problem. {fallback_question}".strip()
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
