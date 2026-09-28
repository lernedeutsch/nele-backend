"""Mode-specific policy over shared conversation engines."""

def apply_mode_policy(turn_plan, mode="free"):
    plan = dict(turn_plan or {})
    mode = str(mode or "free").strip().lower()
    plan["mode"] = mode
    if mode == "free":
        plan.update(
            conversation_priority="learner_led",
            correction_policy="selective",
            knowledge_policy="contextual",
            prefer_natural_short_answers=True,
        )
    else:
        plan.update(
            conversation_priority="learning_goal",
            correction_policy="instructional",
            knowledge_policy="lesson_goal",
            prefer_natural_short_answers=False,
        )
    return plan
