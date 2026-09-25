"""Conversation Goal & Topic Transition Engine v1.

Decides when a free-conversation topic has had enough useful practice and when
it is pedagogically safe to move on. It never overrides explicit learner topic
changes, active correction, repetition, or current-turn struggle.
"""

ENGINE_VERSION = 1

TOPIC_ORDER = ["today", "work", "hobby", "weather", "yesterday", "holiday", "shopping", "place"]

TOPIC_GOALS = {
    "today": {"min_turns": 5, "min_independent": 2},
    "work": {"min_turns": 5, "min_independent": 2},
    "hobby": {"min_turns": 5, "min_independent": 2},
    "weather": {"min_turns": 5, "min_independent": 2},
    "yesterday": {"min_turns": 5, "min_independent": 2},
    "holiday": {"min_turns": 5, "min_independent": 2},
    "shopping": {"min_turns": 5, "min_independent": 2},
    "place": {"min_turns": 4, "min_independent": 1},
}

def _topic_turns(state, topic):
    turns = ((state or {}).get("conversation_coherence_v1") or {}).get("turns") or []
    return sum(1 for item in turns if item.get("topic") == topic)

def _has_active_learning_problem(*, struggle=False, error_result=None, teacher_policy=None):
    if struggle:
        return True
    error_result = error_result or {}
    if error_result.get("error") or error_result.get("recast"):
        return True
    action = (teacher_policy or {}).get("action")
    return action in {"REPEAT_ERROR", "CORRECT_ERROR", "SIMPLIFY", "REVIEW_WORD"}

def assess_topic_goal(state, *, topic, independent_turns=0, struggle=False,
                      error_result=None, teacher_policy=None, explicit_topic=False):
    goal = TOPIC_GOALS.get(topic, {"min_turns": 3, "min_independent": 2})
    turns = _topic_turns(state, topic)
    blocked = _has_active_learning_problem(
        struggle=struggle,
        error_result=error_result,
        teacher_policy=teacher_policy,
    )
    completed = (
        not explicit_topic
        and not blocked
        and turns >= goal["min_turns"]
        and int(independent_turns or 0) >= goal["min_independent"]
    )
    return {
        "version": ENGINE_VERSION,
        "topic": topic,
        "topic_turns": turns,
        "independent_turns": int(independent_turns or 0),
        "min_turns": goal["min_turns"],
        "min_independent": goal["min_independent"],
        "blocked": blocked,
        "completed": completed,
        "reason": (
            "explicit_learner_topic" if explicit_topic
            else "active_learning_problem" if blocked
            else "goal_reached" if completed
            else "continue_topic"
        ),
    }

def choose_next_topic(state, current_topic):
    manager = (state or {}).get("topic_transition_v1") or {}
    completed = set(manager.get("completed_topics") or [])
    recent = list((((state or {}).get("conversation_coherence_v1") or {}).get("recent_topics")) or [])
    try:
        start = TOPIC_ORDER.index(current_topic)
    except ValueError:
        start = -1
    ordered = TOPIC_ORDER[start + 1:] + TOPIC_ORDER[:start + 1]
    for topic in ordered:
        if topic != current_topic and topic not in completed and topic not in recent[-2:]:
            return topic
    for topic in ordered:
        if topic != current_topic:
            return topic
    return current_topic

def decide_topic_transition(state, *, topic, independent_turns=0, struggle=False,
                            error_result=None, teacher_policy=None, explicit_topic=False):
    assessment = assess_topic_goal(
        state,
        topic=topic,
        independent_turns=independent_turns,
        struggle=struggle,
        error_result=error_result,
        teacher_policy=teacher_policy,
        explicit_topic=explicit_topic,
    )
    next_topic = choose_next_topic(state, topic) if assessment["completed"] else topic
    result = {
        **assessment,
        "transition": bool(assessment["completed"] and next_topic != topic),
        "next_topic": next_topic,
    }
    store = state.setdefault("topic_transition_v1", {
        "version": ENGINE_VERSION,
        "completed_topics": [],
        "history": [],
    })
    if result["transition"]:
        completed = store.setdefault("completed_topics", [])
        if topic not in completed:
            completed.append(topic)
        store.setdefault("history", []).append({"from": topic, "to": next_topic, "reason": "goal_reached"})
        del store["history"][:-20]
    store["last_decision"] = dict(result)
    return result
