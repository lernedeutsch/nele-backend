"""Data-driven social A1 topics for free conversation.

Topic modules define WHAT Nele can talk about.  The generic router below owns HOW
learner-led questions are matched.  Add new topic data here (or load it from
knowledge) instead of adding another if/elif conversation controller.
"""
import re

def _norm(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower()).strip(" ?!.")

SOCIAL_TOPICS = {
    "identity": {
        "questions": {
            "wie heißt du": "Ich heiße Nele. Und wie heißt du?",
            "wie heisst du": "Ich heiße Nele. Und wie heißt du?",
            "wie ist dein name": "Ich heiße Nele. Und wie heißt du?",
            "wer bist du": "Ich heiße Nele. Und wie heißt du?",
            "wie heißen sie": "Ich heiße Nele. Und wie heißt du?",
            "wie heissen sie": "Ich heiße Nele. Und wie heißt du?",
            "wie ist ihr name": "Ich heiße Nele. Und wie heißt du?",
        },
    },
    "wellbeing": {
        "questions": {
            "wie geht es dir": "Mir geht es gut, danke. Und dir?",
            "wie geht's dir": "Mir geht es gut, danke. Und dir?",
            "wie gehts dir": "Mir geht es gut, danke. Und dir?",
            "wie geht es ihnen": "Mir geht es gut, danke. Und dir?",
            "wie geht's ihnen": "Mir geht es gut, danke. Und dir?",
            "wie gehts ihnen": "Mir geht es gut, danke. Und dir?",
            "wie geht's": "Mir geht es gut, danke. Und dir?",
            "wie gehts": "Mir geht es gut, danke. Und dir?",
            "alles gut": "Mir geht es gut, danke. Und dir?",
            "alles klar": "Mir geht es gut, danke. Und dir?",
        },
    },
    "weather": {
        "questions": {
            "wie ist das wetter": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "wie ist das wetter heute": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "wie ist heute das wetter": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "was macht das wetter": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "wie ist das wetter bei dir": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "ist es warm": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "ist es kalt": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "regnet es": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "regnet es heute": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "scheint die sonne": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "ist es sonnig": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "ist es windig": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "schneit es": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "ist es bewölkt": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
            "ist es bewoelkt": "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?",
        },
    },
    "everyday": {
        "questions": {
            "was machst du heute": "Heute spreche ich mit dir. Und was machst du heute?",
            "was machst du gern": "Ich spreche gern mit dir. Was machst du gern?",
            "was machst du gern in deiner freizeit": "Ich spreche gern mit dir. Und du? Was machst du gern in deiner Freizeit?",
            "hast du ein hobby": "Ja, ich mag Sprachen. Und du? Was ist dein Hobby?",
            "arbeitest du": "Ich bin deine Deutschtrainerin. Arbeitest du heute?",
            "gehst du arbeiten": "Ich arbeite hier mit dir. Und du? Arbeitest du heute?",
            "gehst du gern einkaufen": "Ich kann mit dir über Einkaufen sprechen. Was kaufst du gern?",
            "was kaufst du gern": "Ich mag Wörter und Gespräche. Was kaufst du gern?",
            "machst du gern urlaub": "Ich kann mit dir über Urlaub sprechen. Wo machst du gern Urlaub?",
            "wo machst du urlaub": "Ich reise nicht wirklich. Und du? Wo machst du gern Urlaub?",
        },
    },
    "greeting": {
        "questions": {
            "hallo": "Hallo! Wie geht's dir heute?",
            "hi": "Hi! Wie geht's dir heute?",
            "hey": "Hallo! Wie geht's dir heute?",
            "guten morgen": "Guten Morgen! Wie geht's dir heute?",
            "guten tag": "Guten Tag! Wie geht es dir heute?",
            "guten abend": "Guten Abend! Wie geht's dir heute?",
            "moin": "Moin! Wie geht's dir heute?",
            "servus": "Servus! Wie geht's dir heute?",
            "grüß gott": "Grüß Gott! Wie geht es dir heute?",
            "gruss gott": "Grüß Gott! Wie geht es dir heute?",
        },
    },
}

def social_topic_reply(message):
    """Return a reply from topic data, without owning conversation state."""
    key = _norm(message)
    if not key:
        return None
    for topic in SOCIAL_TOPICS.values():
        reply = topic.get("questions", {}).get(key)
        if reply:
            return reply
    return None
