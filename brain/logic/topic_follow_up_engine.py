# ==========================================
# NELE – TOPIC FOLLOW-UP ENGINE v1
# Natural A1 follow-ups without repeating the same question.
# ==========================================

from brain.logic.vocabulary_engine import normalize_text


TOPIC_QUESTIONS = {
    "freizeit": [
        ("activity", "Was machst du gern in deiner Freizeit?"),
        ("company", "Machst du das lieber allein oder mit jemandem?"),
        ("frequency", "Wie oft machst du das?"),
        ("place", "Wo machst du das gern?"),
        ("time", "Wann machst du das normalerweise?"),
    ],
    "wetter": [
        ("temperature", "Ist es bei dir warm oder kalt?"),
        ("preference", "Magst du dieses Wetter?"),
        ("activity", "Was machst du gern bei diesem Wetter?"),
        ("season", "Welche Jahreszeit magst du am liebsten?"),
    ],
    "arbeit": [
        ("job", "Was machst du bei der Arbeit?"),
        ("time", "Bis wann arbeitest du heute?"),
        ("company", "Arbeitest du allein oder mit Kollegen?"),
        ("preference", "Was gefällt dir an deiner Arbeit?"),
    ],
    "essen": [
        ("preference", "Was isst du gern?"),
        ("cooking", "Kochst du gern?"),
        ("time", "Was isst du normalerweise zum Frühstück?"),
        ("drink", "Was trinkst du gern?"),
    ],
    "hotel": [
        ("work", "Was machst du im Hotel?"),
        ("room", "Arbeitest du oft in den Zimmern?"),
        ("guest", "Sprichst du bei der Arbeit mit Gästen?"),
        ("preference", "Was machst du bei der Arbeit im Hotel gern?"),
    ],
}


def _asked_for_topic(state, topic):
    history = state.setdefault("conversation_topic_questions", {})
    asked = history.get(topic, [])
    return asked if isinstance(asked, list) else []


def reset_topic_questions(state, topic=None):
    if state is None:
        return

    if topic is None:
        state["conversation_topic_questions"] = {}
        return

    history = state.setdefault("conversation_topic_questions", {})
    history.pop(normalize_text(topic), None)


def next_topic_follow_up(state, topic=None):
    """
    Return the next unused A1 follow-up for a topic.
    Returns None after all configured questions have been used.
    """
    if state is None:
        return None

    topic = normalize_text(
        topic or state.get("conversation_vocabulary_topic")
    )

    questions = TOPIC_QUESTIONS.get(topic)
    if not questions:
        return None

    asked = _asked_for_topic(state, topic)

    for question_id, question in questions:
        if question_id in asked:
            continue

        asked.append(question_id)
        state.setdefault("conversation_topic_questions", {})[topic] = asked
        state["conversation_last_follow_up_id"] = question_id
        state["conversation_last_follow_up_topic"] = topic
        return question

    return None
