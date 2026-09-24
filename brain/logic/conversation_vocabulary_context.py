# ==========================================
# NELE – CONVERSATION VOCABULARY CONTEXT
# Bridges Vocabulary Engine v1 with normal free conversation.
# It enriches state only; it never steals a learner turn.
# ==========================================

from brain.logic.vocabulary_engine import (
    build_conversation_vocabulary,
)


def update_conversation_vocabulary_context(user_message, state):
    """
    Analyse the learner message and store compact vocabulary context.

    This is deliberately non-blocking: normal conversation routers still
    decide what Nele says. Conversation Engine can use this state later
    for topic continuity, vocabulary suggestions and adaptive questions.
    """
    if state is None:
        return None

    previous_topic = state.get("conversation_vocabulary_topic")

    context = build_conversation_vocabulary(
        user_message,
        topic=None,
        limit=8,
    )

    detected_topic = context.get("topic")
    used_words = context.get("used_words", [])

    # A short answer such as "ja" or "gern" often contains no topic word.
    # Keep the previous topic instead of losing conversation continuity.
    if not detected_topic and previous_topic:
        context = build_conversation_vocabulary(
            user_message,
            topic=previous_topic,
            limit=8,
        )
        detected_topic = previous_topic

    state["conversation_vocabulary_topic"] = detected_topic
    state["conversation_vocabulary_used_words"] = used_words
    state["conversation_vocabulary_suggestions"] = [
        item.get("word")
        for item in context.get("suggestions", [])
        if item.get("word")
    ]

    return context


def get_conversation_vocabulary_context(state):
    if state is None:
        return {
            "level": "A1",
            "topic": None,
            "used_words": [],
            "suggestions": [],
        }

    return {
        "level": "A1",
        "topic": state.get("conversation_vocabulary_topic"),
        "used_words": list(
            state.get("conversation_vocabulary_used_words", [])
        ),
        "suggestions": list(
            state.get("conversation_vocabulary_suggestions", [])
        ),
    }
