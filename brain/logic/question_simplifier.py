"""Question Simplifier v1 for beginner A1 conversation.

Transforms a generated contextual question into an easier question while
preserving topic/subtopic. It is deterministic and deliberately small.
"""

SIMPLIFIER_VERSION = 1

TOPIC_SIMPLE = {
    "today": ["Machst du heute etwas?", "Arbeitest du heute?"],
    "work": ["Arbeitest du heute?", "Kochst du bei der Arbeit?"],
    "hobby": ["Hast du ein Hobby?", "Machst du gern Sport?"],
    "weather": ["Ist es heute warm?", "Ist es sonnig?"],
    "holiday": ["Machst du gern Urlaub?", "Magst du das Meer?"],
    "shopping": ["Gehst du heute einkaufen?", "Suchst du Schuhe?"],
    "place": ["Bist du zu Hause?", "Bist du in Heidelberg?"],
    "yesterday": ["Hast du gestern gearbeitet?", "War dein Tag gestern gut?"],
}

QUESTION_RULES = (
    ("Was machst du bei der Arbeit?", "Arbeitest du heute?"),
    ("Was kochst du gern bei der Arbeit?", "Kochst du gern Suppe?"),
    ("Was machst du gern in deiner Freizeit?", "Hast du ein Hobby?"),
    ("Welche Musik hörst du gern?", "Hörst du gern Musik?"),
    ("Welchen Sport machst du gern?", "Machst du gern Sport?"),
    ("Was machst du bei diesem Wetter gern?", "Gehst du gern spazieren?"),
    ("Was möchtest du heute noch machen?", "Machst du heute noch etwas?"),
    ("Was möchtest du heute machen?", "Machst du heute etwas?"),
    ("Wo machst du gern Urlaub?", "Machst du gern Urlaub?"),
    ("Was machst du gern im Urlaub?", "Magst du Urlaub am Meer?"),
)


def _norm(text):
    return " ".join(str(text or "").strip().lower().split()).strip(" ?!.")


def simplify_question(question, *, topic=None, subtopic=None, recent_questions=None):
    original = str(question or "").strip()
    recent = {_norm(q) for q in (recent_questions or []) if q}

    for source, simple in QUESTION_RULES:
        if _norm(original) == _norm(source) and _norm(simple) not in recent:
            return {
                "version": SIMPLIFIER_VERSION,
                "original": original,
                "question": simple,
                "changed": _norm(simple) != _norm(original),
                "strategy": "specific_rule",
                "topic": topic,
                "subtopic": subtopic,
            }

    candidates = list(TOPIC_SIMPLE.get(str(topic or ""), []))
    if str(topic or "") == "work" and str(subtopic or "") == "kochen":
        candidates = ["Kochst du bei der Arbeit?", "Kochst du gern Suppe?"] + candidates

    for simple in candidates:
        if _norm(simple) != _norm(original) and _norm(simple) not in recent:
            return {
                "version": SIMPLIFIER_VERSION,
                "original": original,
                "question": simple,
                "changed": True,
                "strategy": "topic_yes_no",
                "topic": topic,
                "subtopic": subtopic,
            }

    return {
        "version": SIMPLIFIER_VERSION,
        "original": original,
        "question": original,
        "changed": False,
        "strategy": "keep_original",
        "topic": topic,
        "subtopic": subtopic,
    }
