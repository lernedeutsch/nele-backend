import re
from difflib import SequenceMatcher

from brain.memory.daily_learning import mark_exercise_completed_today
from brain.memory.student_progress import (
    remember_completed_exercise,
    remember_learning_topic,
    get_current_level,
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

def _task_semantic_score(message, task):
    """Score whether the learner fulfils the situation, not a memorised sentence."""
    message_n = _normalize(message)
    tokens = _tokens(message)
    prompt_tokens = _tokens((task or {}).get("prompt"))
    model_tokens = _tokens((task or {}).get("model_answer"))
    keywords = [_normalize(value) for value in (task or {}).get("keywords", []) if _normalize(value)]

    if not message_n or not tokens:
        return 0

    # Content nouns from the situation/model are useful evidence even when the
    # learner chooses a different polite formulation.
    content = {
        token for token in (prompt_tokens | model_tokens)
        if len(token) >= 4 and token not in {
            "gast", "bitte", "guten", "morgen", "ihnen", "ihre", "einen",
            "eine", "noch", "sehr", "gerne", "sofort", "möchten", "mochten",
            "verkäuferin", "verkauferin", "entschuldigung", "brauche",
            "bringe", "bringen", "natürlich", "naturlich", "frisches",
        }
    }
    content_hit = bool(tokens & content)

    # Recognise common service/response acts generically instead of requiring
    # every literal keyword from one model answer.
    response_markers = {
        "bringe", "bringen", "hole", "holen", "kümmere", "kuemmere",
        "darum", "natürlich", "naturlich", "gerne", "gern", "möchte",
        "mochte", "hätte", "hatte", "nehme", "brauche",
    }
    response_hit = bool(tokens & response_markers)
    keyword_hit = any(keyword in message_n for keyword in keywords)

    # A semantic pass needs both situation content and a response act. This
    # keeps weak keyword overlap ("ich möchte abfallen") from being accepted.
    if not (content_hit and response_hit):
        return 0

    score = 70
    if keyword_hit:
        score += 15
    if len(tokens) >= 4:
        score += 10
    return min(100, score)


def _preserve_dialogue_intent_correction(message):
    """Correct a few high-confidence A1 forms without replacing learner meaning."""
    raw = str(message or "").strip()
    if not raw:
        return None

    corrected = raw
    replacements = [
        (r"\bich\s+hatte\s+gern\b", "Ich hätte gern"),
        (r"\bich\s+mochte\b", "Ich möchte"),
        (r"\bich\s+möchte\b", "Ich möchte"),
        (r"\bein\s+kilo\b", "ein Kilo"),
        (r"\bapfeln\b", "Äpfel"),
        (r"\bäpfeln\b", "Äpfel"),
        (r"\bapfel\b", "Äpfel"),
        (r"\bbitt\b", "bitte"),
    ]
    for pattern, value in replacements:
        corrected = re.sub(pattern, value, corrected, flags=re.IGNORECASE)

    corrected = corrected.strip(" .")
    if corrected and not corrected.endswith((".", "!", "?")):
        corrected += "."

    if _normalize(corrected) == _normalize(raw):
        return None
    return corrected


def _sentence_count(text):
    raw = str(text or "").strip()
    if not raw:
        return 0

    # A1: kropka, !, ?, średnik lub nowa linia
    # mogą rozdzielać dwa krótkie zdania.
    parts = [
        part.strip()
        for part in re.split(r"[.!?;]+|\n+", raw)
        if part.strip()
    ]

    return len(parts)


def _find_writing_spelling_corrections(message, corrections):
    """Return task-specific obvious spelling corrections found in a message."""

    raw = str(message or "")
    found = []

    if not isinstance(corrections, dict):
        return found

    for wrong, correct in corrections.items():
        wrong_text = str(wrong or "").strip()
        correct_text = str(correct or "").strip()

        if not wrong_text or not correct_text:
            continue

        pattern = rf"\b{re.escape(wrong_text)}\b"

        if re.search(
            pattern,
            raw,
            flags=re.IGNORECASE,
        ):
            found.append(
                (wrong_text, correct_text)
            )

    return found


def _looks_like_prompt_echo(message, prompt):
    message_n = _normalize(message)
    prompt = str(prompt or "").strip()

    if not message_n or not prompt:
        return False

    # W wielu zadaniach po dwukropku stoi
    # sama sytuacja, np.:
    # "Du kommst heute zehn Minuten später ..."
    scenario = prompt.split(":", 1)[-1]
    scenario_n = _normalize(scenario)

    if not scenario_n:
        return False

    if message_n == scenario_n:
        return True

    # Nie odrzucamy poprawnej odpowiedzi
    # "Ich komme ..." tylko dlatego, że jest
    # podobna do sytuacji "Du kommst ...".
    if "ich" in _tokens(message_n):
        return False

    return SequenceMatcher(
        None,
        message_n,
        scenario_n
    ).ratio() >= 0.92


def _finish(state, activity_type, detail, score, update_skill_score=True):
    if update_skill_score:
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


def _resolve_level(state, level=None):
    value = str(
        level
        or get_current_level(state)
        or "A1"
    ).strip().upper()

    if value not in {"A1", "A2"}:
        return "A1"

    return value


def _items_for_level(items, level):
    level = str(level or "A1").strip().upper()

    matched = [
        item
        for item in (items or [])
        if isinstance(item, dict)
        and str(item.get("level") or "A1").strip().upper() == level
    ]

    if matched:
        return matched

    # Bezpieczny fallback: jeżeli dla danego poziomu
    # nie ma jeszcze treści, użyj prostszego A1 zamiast
    # przypadkowo podawać trudniejsze zadanie.
    return [
        item
        for item in (items or [])
        if isinstance(item, dict)
        and str(item.get("level") or "A1").strip().upper() == "A1"
    ]


def resume_active_task(state):
    task = get_active_task(state)

    if not isinstance(task, dict):
        return None

    activity_type = str(task.get("type") or "").strip().lower()
    prompt = str(task.get("prompt") or "").strip()

    if activity_type == "listening":
        return {
            "reply": (
                "Wir machen mit der Hörübung weiter.\n\n"
                + prompt
            ).strip(),
            "speak_text": str(task.get("speak_text") or "").strip(),
            "meta": {
                "activity": "listening",
                "resumed": True,
            },
        }

    if activity_type == "pronunciation":
        target = str(task.get("target") or "").strip()
        return {
            "reply": prompt or f"Sprich bitte nach: „{target}“",
            "speak_text": str(task.get("speak_text") or target).strip(),
            "meta": {
                "activity": "pronunciation",
                "expects_audio": True,
                "resumed": True,
            },
        }

    return {
        "reply": (
            ("Wir machen hier weiter. " + prompt)
            if prompt
            else "Wir machen hier weiter."
        ),
        "meta": {
            "activity": activity_type,
            "resumed": True,
        },
    }


def start_activity(state, activity_type, level=None):
    activity_type = str(activity_type or "").strip().lower()
    level = _resolve_level(state, level)

    if activity_type in {"dialog", "dialogue", "rollenspiel"}:
        item = _pick(_items_for_level(DIALOGUES, level), state, f"dialogue_{level}")
        task = {
            "type": "dialogue",
            "level": level,
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
        item = _pick(_items_for_level(LISTENING_TASKS, level), state, f"listening_{level}")
        task = {
            "type": "listening",
            "level": level,
            "title": item["title"],
            "prompt": item["question"],
            "speak_text": item["text"],
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
        item = _pick(_items_for_level(WRITING_TASKS, level), state, f"writing_{level}")
        task = {
            "type": "writing",
            "level": level,
            "title": item["title"],
            "prompt": item["prompt"],
            "keywords": item.get("keywords", []),
            "required": item.get("required", []),
            "min_words": item.get("min_words", 5),
            "min_sentences": item.get("min_sentences", 1),
            "spelling_corrections": item.get("spelling_corrections", {}),
            "model_answer": item.get("model_answer"),
        }
        set_active_task(state, task)
        return {
            "reply": item["prompt"],
            "task": task,
            "meta": {"activity": "writing"},
        }

    if activity_type in {"work", "work_german", "arbeitsdeutsch", "hotel", "housekeeping"}:
        item = _pick(_items_for_level(WORK_GERMAN, level), state, f"work_german_{level}")
        task = {
            "type": "work_german",
            "level": level,
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
        item = _pick(_items_for_level(PRONUNCIATION_TARGETS, level), state, f"pronunciation_{level}")
        task = {
            "type": "pronunciation",
            "level": level,
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


def answer_active_task(state, message, transcript=None, input_mode=None):
    task = get_active_task(state)
    if not task:
        return None

    activity_type = task.get("type", "speaking")
    message = str(message or "").strip()
    transcript = str(transcript or "").strip()

    if activity_type == "pronunciation":
        input_mode = str(
            input_mode
            or state.get("last_input_mode")
            or state.get("input_mode")
            or ""
        ).strip().lower()

        voice_input = input_mode in {"voice", "speech", "microphone", "mic"}

        # Niektóre starsze wersje frontendu używają Web Speech API:
        # mikrofon rozpoznaje słowo poprawnie, ale do /chat trafia tylko tekst
        # bez zachowanego znacznika input_mode="voice".
        # Nie blokujemy wtedy ćwiczenia — oceniamy rozpoznany tekst.
        heard = transcript or message
        if not heard:
            return {
                "completed": False,
                "reply": "Ich habe nichts erkannt. Sprich das Wort bitte noch einmal.",
                "meta": {"activity": "pronunciation", "expects_audio": True},
            }
        result = evaluate_pronunciation(state, task.get("target", ""), heard)
        score = result["score"]
        completed = score >= 80
        if completed:
            # evaluate_pronunciation() hat den Skill-Wert
            # bereits genau einmal aktualisiert.
            _finish(
                state,
                "pronunciation",
                task.get("title", "Aussprache"),
                score,
                update_skill_score=False
            )
            set_active_task(state, None)
        return {
            "completed": completed,
            "reply": result["feedback"],
            "score": score,
            "result": result,
            "meta": {
                "activity": "pronunciation",
                "retry": not completed,
                "expects_audio": True,
                "voice_input": voice_input,
                "input_mode": input_mode or None,
            },
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

        required = [
            _normalize(value)
            for value in task.get("required", [])
            if _normalize(value)
        ]
        message_n = _normalize(message)
        required_ok = all(
            value in message_n
            for value in required
        )

        try:
            min_sentences = max(
                1,
                int(task.get("min_sentences", 1) or 1)
            )
        except (TypeError, ValueError):
            min_sentences = 1

        sentences_ok = (
            _sentence_count(message) >= min_sentences
        )

        copied_task = _looks_like_prompt_echo(
            message,
            task.get("prompt", "")
        )

        spelling_corrections = (
            _find_writing_spelling_corrections(
                message,
                task.get(
                    "spelling_corrections",
                    {}
                ),
            )
        )

        if spelling_corrections:
            score = min(
                score,
                70,
            )

        completed = (
            score >= 55
            and required_ok
            and sentences_ok
            and not copied_task
            and not spelling_corrections
        )

        model = task.get("model_answer")

        if spelling_corrections:
            wrong, correct = (
                spelling_corrections[0]
            )
            reply = (
                f"Fast richtig. „{wrong}“ schreibt man "
                f"„{correct}“. "
                "Schreib die Nachricht bitte noch einmal."
            )
        elif completed:
            reply = (
                "Sehr gut. Das klingt natürlich "
                "und passt zur Situation."
            )
        elif copied_task:
            reply = (
                "Das ist die Aufgabe. "
                "Schreib bitte selbst zwei kurze Sätze."
            )
            if model:
                reply += f" Zum Beispiel: „{model}“"
        elif not required_ok:
            reply = (
                "Schreib die Nachricht bitte aus deiner Sicht, "
                "zum Beispiel mit „Ich ...“"
            )
            if model:
                reply += f" Zum Beispiel: „{model}“"
        elif not sentences_ok:
            reply = (
                f"Schreib bitte {min_sentences} kurze Sätze."
            )
            if model:
                reply += f" Zum Beispiel: „{model}“"
        else:
            reply = "Ergänze bitte noch die wichtigsten Informationen."
            if model:
                reply += f" Zum Beispiel: „{model}“"

    elif activity_type in {"dialogue", "work_german", "speaking", "grammar"}:
        score = _keyword_score(message, task.get("keywords", []))
        if not task.get("keywords"):
            score = min(100, 45 + len(_normalize(message).split()) * 8)
        model_score = _similarity_score(message, task.get("model_answer")) if task.get("model_answer") else 0
        semantic_score = _task_semantic_score(message, task)
        correction = (
            _preserve_dialogue_intent_correction(message)
            if activity_type == "dialogue"
            else None
        )
        keyword_count = len(task.get("keywords", []) or [])
        keyword_pass = score >= 60 and (
            keyword_count <= 1
            or score >= 100
        )
        completed = (
            keyword_pass
            or model_score >= 55
            or (semantic_score >= 70 and not correction)
        )
        if completed:
            reply = "Sehr gut. Das passt in dieser Situation."
        else:
            model = task.get("model_answer")
            reply = ("Gut, ein Teil passt. Ergänze bitte noch den fehlenden Teil." if activity_type == "speaking" and score > 0 else "Das passt noch nicht ganz zur Situation. Versuch es noch einmal.")
            if correction:
                reply += f" Du kannst sagen: „{correction}“"
            elif model and len(_normalize(message).split()) <= 2:
                # A model answer is only a fallback for an unusably short answer.
                # It must not overwrite concrete information supplied by the learner.
                reply += f" Zum Beispiel: „{model}“"

    else:
        score = min(100, 50 + len(_normalize(message).split()) * 7)
        completed = score >= 60
        reply = "Gut gemacht." if completed else "Sag bitte noch einen vollständigen Satz."

    # Teacher Brain powinien widzieć również nieudane próby,
    # a nie tylko ćwiczenia zakończone sukcesem.
    update_skill(
        state,
        activity_type if activity_type in {
            "speaking", "listening", "writing", "vocabulary", "grammar",
            "dialogue", "work_german"
        } else "speaking",
        score
    )

    if completed:
        _finish(
            state,
            activity_type,
            task.get("title", activity_type),
            score,
            update_skill_score=False
        )
        set_active_task(state, None)
        record_event(state, "activity_answer", detail=activity_type, result={"score": score})

    return {
        "completed": completed,
        "reply": reply,
        "score": score,
        "meta": {"activity": activity_type, "retry": not completed},
    }
