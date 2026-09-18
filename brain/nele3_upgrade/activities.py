import re

from brain.memory.daily_learning import mark_exercise_completed_today
from brain.memory.student_progress import (
    remember_completed_exercise,
    remember_learning_topic,
)
from brain.nele3_upgrade.content import (
    DIALOGUES,
    LISTENING_TASKS,
    WRITING_TASKS,
    WORK_GERMAN,
    PRONUNCIATION_TARGETS,
    COURSE_TASKS,
)
from brain.nele3_upgrade.pronunciation import evaluate_pronunciation
from brain.nele3_upgrade.state import (
    next_cursor,
    set_active_task,
    get_active_task,
    update_skill,
    mark_activity_completed,
    record_event,
)


def _normalize(text):
    text = str(text or "").lower().strip()
    text = re.sub(r"[^a-zäöüß0-9\s'-]", " ", text)
    return " ".join(text.split())


def _tokens(text):
    return set(_normalize(text).split())


def _keyword_score(message, keywords):
    message_n = _normalize(message)
    if not keywords:
        return 70 if message_n else 0
    hits = 0
    for kw in keywords:
        if _normalize(kw) in message_n:
            hits += 1
    return int(round(100 * hits / len(keywords)))


def _similarity_score(message, expected):
    expected_tokens = _tokens(expected)
    got = _tokens(message)
    if not expected_tokens or not got:
        return 0
    overlap = len(expected_tokens & got) / len(expected_tokens)
    return int(round(overlap * 100))


def _finish(state, activity_type, detail, score):
    update_skill(state, activity_type if activity_type in {
        "speaking", "listening", "writing", "vocabulary", "grammar",
        "pronunciation", "dialogue", "work_german"
    } else "speaking", score)
    mark_activity_completed(state, activity_type, detail=detail, score=score)
    try:
        remember_completed_exercise(state)
    except Exception as error:
        print(f"Nele3 progress error: {error}")
    try:
        mark_exercise_completed_today(state, activity_type=activity_type, detail=detail)
    except Exception as error:
        print(f"Nele3 daily memory error: {error}")
    try:
        remember_learning_topic(state, detail)
    except Exception as error:
        print(f"Nele3 topic memory error: {error}")


def _pick(items, state, cursor_key):
    if not items:
        return None
    idx = next_cursor(state, cursor_key, len(items))
    return items[idx]


def start_activity(state, activity_type, level=None):
    activity_type = str(activity_type or "").strip().lower()
    level = str(level or "A1").strip().upper()

    if activity_type in {"dialog", "dialogue", "rollenspiel"}:
        item = _pick(DIALOGUES, state, "dialogue")
        task = {
            "type": "dialogue",
            "title": item["title"],
            "prompt": item["prompt"],
            "keywords": item.get("keywords", []),
            "model_answer": item.get("model_answer"),
        }
        set_active_task(state, task)
        return {
            "reply": f"Rollenspiel: {item['prompt']}",
            "task": task,
            "meta": {"activity": "dialogue"},
        }

    if activity_type in {"listening", "hoeren", "hören", "hörübung"}:
        item = _pick(LISTENING_TASKS, state, "listening")
        task = {
            "type": "listening",
            "title": item["title"],
            "prompt": item["question"],
            "speak_text": f"Hör gut zu. {item['text']} {item['question']}",
            "answers": item.get("answers", []),
        }
        set_active_task(state, task)
        return {
            "reply": f"Hör gut zu.\n\n{item['question']}",
            "speak_text": item["text"],
            "task": task,
            "meta": {"activity": "listening"},
        }

    if activity_type in {"writing", "schreiben", "schreibübung"}:
        item = _pick(WRITING_TASKS, state, "writing")
        task = {
            "type": "writing",
            "title": item["title"],
            "prompt": item["prompt"],
            "keywords": item.get("keywords", []),
            "min_words": item.get("min_words", 5),
            "model_answer": item.get("model_answer"),
        }
        set_active_task(state, task)
        return {
            "reply": item["prompt"],
            "task": task,
            "meta": {"activity": "writing"},
        }

    if activity_type in {"work", "work_german", "arbeitsdeutsch", "hotel", "housekeeping"}:
        item = _pick(WORK_GERMAN, state, "work_german")
        task = {
            "type": "work_german",
            "title": item["title"],
            "prompt": item["prompt"],
            "keywords": item.get("keywords", []),
            "model_answer": item.get("model_answer"),
        }
        set_active_task(state, task)
        return {
            "reply": f"Arbeitsdeutsch: {item['prompt']}",
            "task": task,
            "meta": {"activity": "work_german"},
        }

    if activity_type in {"pronunciation", "aussprache"}:
        item = _pick(PRONUNCIATION_TARGETS, state, "pronunciation")
        task = {
            "type": "pronunciation",
            "title": item["title"],
            "target": item["target"],
            "prompt": f"Sprich bitte nach: „{item['target']}“",
            "speak_text": item["target"],
        }
        set_active_task(state, task)
        return {
            "reply": task["prompt"],
            "speak_text": item["target"],
            "task": task,
            "meta": {"activity": "pronunciation", "expects_audio": True},
        }

    # Generic course/speaking activity for A1/A2.
    tasks = COURSE_TASKS.get(level) or COURSE_TASKS.get("A1") or []
    item = _pick(tasks, state, f"course_{level}")
    if not item:
        return {"reply": "Wir machen eine kurze Sprechübung. Erzähl mir etwas über deinen Tag.", "task": None, "meta": {"activity": "speaking"}}

    task = {
        "type": item.get("type", "speaking"),
        "title": item["title"],
        "prompt": item["prompt"],
        "keywords": item.get("keywords", []),
        "level": level,
    }
    set_active_task(state, task)
    return {
        "reply": item["prompt"],
        "task": task,
        "meta": {"activity": task["type"], "level": level},
    }


def answer_active_task(state, message, transcript=None):
    task = get_active_task(state)
    if not task:
        return None

    activity_type = task.get("type", "speaking")
    message = str(message or "").strip()
    transcript = str(transcript or "").strip()

    if activity_type == "pronunciation":
        heard = transcript or message
        if not heard:
            return {
                "completed": False,
                "reply": "Ich brauche deine Aufnahme oder den erkannten Text. Sprich den Satz bitte noch einmal.",
                "meta": {"activity": "pronunciation", "expects_audio": True},
            }
        result = evaluate_pronunciation(state, task.get("target", ""), heard)
        score = result["score"]
        completed = score >= 65
        if completed:
            _finish(state, "pronunciation", task.get("title", "Aussprache"), score)
            set_active_task(state, None)
        return {
            "completed": completed,
            "reply": result["feedback"],
            "score": score,
            "result": result,
            "meta": {"activity": "pronunciation", "retry": not completed},
        }

    if not message:
        return {"completed": False, "reply": "Sag oder schreib bitte deine Antwort.", "meta": {"activity": activity_type, "retry": True}}

    if activity_type == "listening":
        answers = task.get("answers", [])
        score = max((_similarity_score(message, a) for a in answers), default=0)
        if any(_normalize(a) in _normalize(message) for a in answers):
            score = max(score, 95)
        completed = score >= 55
        reply = "Richtig. Sehr gut gehört." if completed else "Noch einmal: Hör genau auf die wichtigste Information."

    elif activity_type == "writing":
        words = len(_normalize(message).split())
        keyword_score = _keyword_score(message, task.get("keywords", []))
        length_score = min(100, int(100 * words / max(1, int(task.get("min_words", 5)))))
        score = int(round(keyword_score * 0.65 + length_score * 0.35))
        completed = score >= 55
        if completed:
            reply = "Gut geschrieben. Die Nachricht ist verständlich und enthält die wichtigsten Informationen."
        else:
            model = task.get("model_answer")
            reply = "Ergänze bitte noch die wichtigsten Informationen."
            if model:
                reply += f" Zum Beispiel: „{model}“"

    elif activity_type in {"dialogue", "work_german", "speaking", "grammar"}:
        score = _keyword_score(message, task.get("keywords", []))
        if not task.get("keywords"):
            score = min(100, 45 + len(_normalize(message).split()) * 8)
        completed = score >= 45
        if completed:
            reply = "Sehr gut. Das passt in dieser Situation."
        else:
            model = task.get("model_answer")
            reply = "Fast. Versuch es noch einmal als kurzen, natürlichen Satz."
            if model:
                reply += f" Du kannst sagen: „{model}“"

    else:
        score = min(100, 50 + len(_normalize(message).split()) * 7)
        completed = score >= 60
        reply = "Gut gemacht." if completed else "Sag bitte noch einen vollständigen Satz."

    if completed:
        _finish(state, activity_type, task.get("title", activity_type), score)
        set_active_task(state, None)
        record_event(state, "activity_answer", detail=activity_type, result={"score": score})

    return {
        "completed": completed,
        "reply": reply,
        "score": score,
        "meta": {"activity": activity_type, "retry": not completed},
    }
