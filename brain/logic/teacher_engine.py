"""Teacher Engine v1 for Nele free conversation.

The Teacher Engine does not detect errors and does not choose the topic.
It combines Conversation State, Topic Manager and Error Engine signals into
one pedagogical next-action decision.
"""

import re


SHORT_CONTENT = {
    "kochen": "Ich koche.",
    "arbeiten": "Ich arbeite.",
    "arbeit": "Ich arbeite.",
    "lernen": "Ich lerne.",
    "lesen": "Ich lese gern.",
    "radfahren": "Ich fahre gern Rad.",
    "schwimmen": "Ich schwimme gern.",
}


def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip(" ?!.")


def _word_count(text):
    return len(re.findall(r"[A-Za-zÄÖÜäöüß0-9-]+", str(text or "")))


def choose_teacher_action(
    user_message,
    *,
    conversation_state=None,
    topic_manager=None,
    error_result=None,
    support_level=1,
    struggle=False,
    independent_turns=0,
    vocabulary_context=None,
    learner_model=None,
):
    """Return one central pedagogical action for the next response."""
    conversation_state = conversation_state or {}
    topic_manager = topic_manager or {}
    error_result = error_result or {}
    vocabulary_context = vocabulary_context or {}
    learner_model = learner_model or {}
    decision = error_result.get("decision") or {}
    error = error_result.get("error") or {}

    if decision.get("style") == "repeat_request":
        return {
            "action": "ask_repeat",
            "reason": "recurring_error",
            "model": error.get("correct"),
            "continue_conversation": False,
        }

    if decision.get("correct"):
        return {
            "action": "correct_and_continue",
            "reason": decision.get("reason") or "clear_error",
            "model": error.get("correct"),
            "continue_conversation": True,
        }

    low = _norm(user_message)
    expected = conversation_state.get("expected_answer")
    topic = conversation_state.get("topic") or topic_manager.get("topic")
    subtopic = conversation_state.get("subtopic") or topic_manager.get("subtopic")

    # A single meaningful word often proves comprehension at A1. Model a full
    # sentence, but do not call it an error.
    if _word_count(user_message) == 1 and low in SHORT_CONTENT:
        return {
            "action": "model_full_sentence",
            "reason": "understood_but_short",
            "model": SHORT_CONTENT[low],
            "continue_conversation": True,
        }

    learner_autonomy = learner_model.get("autonomy")
    learner_support = int(learner_model.get("adaptive_support", support_level) or support_level or 1)

    # A valid short A1 answer is successful communication, not evidence that
    # the learner failed. Honour the current answer before using historical
    # support signals. This keeps free conversation natural for beginners.
    if expected == "yes_no" and low in {"ja", "nein", "ja gern", "nein danke"}:
        return {
            "action": "continue_conversation",
            "reason": "valid_expected_short_answer",
            "model": None,
            "continue_conversation": True,
        }

    # Historical support still matters for genuinely open/long answers.
    # Expected short answers were already accepted above, so a correct "ja",
    # "nein", place, time or short content reply is not punished.
    if struggle or (
        (learner_support >= 3 or learner_autonomy == "needs_support")
        and expected not in {"yes_no", "place", "time", "short_content"}
    ):
        return {
            "action": "simplify_next_question",
            "reason": "current_turn_struggle",
            "model": None,
            "continue_conversation": True,
        }

    if expected == "yes_no" and low in {"ja", "nein", "ja gern", "nein danke"}:
        return {
            "action": "continue_conversation",
            "reason": "valid_expected_short_answer",
            "model": None,
            "continue_conversation": True,
        }

    suggestions = vocabulary_context.get("suggestions") or []
    if suggestions:
        candidate = suggestions[0] or {}
        word = candidate.get("word")
        vocabulary_memory = vocabulary_context.get("memory") or {}
        word_memory = vocabulary_memory.get(word, {}) if word else {}
        if word and (word_memory.get("needs_review") or int(word_memory.get("mistakes", 0) or 0) > int(word_memory.get("correct", 0) or 0)):
            return {
                "action": "review_vocabulary",
                "reason": "vocabulary_needs_review",
                "word": word,
                "vocabulary": candidate,
                "continue_conversation": True,
            }
        if word and int(word_memory.get("seen", 0) or 0) == 0 and int(independent_turns or 0) >= 1:
            return {
                "action": "introduce_vocabulary",
                "reason": "useful_unseen_topic_word",
                "word": word,
                "vocabulary": candidate,
                "continue_conversation": True,
            }

    if _word_count(user_message) >= 3 and (learner_autonomy == "independent" or int(independent_turns or 0) >= 3):
        return {
            "action": "advance",
            "reason": "learner_is_independent",
            "model": None,
            "continue_conversation": True,
        }

    return {
        "action": "continue_conversation",
        "reason": "normal_progress",
        "model": None,
        "continue_conversation": True,
        "topic": topic,
        "subtopic": subtopic,
    }


def render_teacher_prefix(action):
    """Render only pedagogical support; the Conversation Engine supplies question."""
    if not action:
        return ""
    kind = action.get("action")
    model = action.get("model")
    if kind == "ask_repeat" and model:
        return f"Richtig ist: „{model}“ Sag es bitte noch einmal."
    if kind == "correct_and_continue" and model:
        return f"Du kannst sagen: „{model}“"
    if kind == "model_full_sentence" and model:
        return f"Du kannst sagen: „{model}“"
    if kind == "simplify_next_question":
        return "Kein Problem."
    return ""
