import re
from difflib import SequenceMatcher

from brain.logic.pronunciation_coach import process_pronunciation_result
from brain.nele3_upgrade.state import update_skill, record_event


def _normalize(text):
    text = str(text or "").lower().strip()
    text = re.sub(r"[^a-zäöüß0-9\s'-]", " ", text)
    return " ".join(text.split())


def _word_overlap(target, heard):
    a = set(_normalize(target).split())
    b = set(_normalize(heard).split())
    if not a:
        return 0.0
    return len(a & b) / len(a)


def pronunciation_score(target, transcript):
    target_n = _normalize(target)
    transcript_n = _normalize(transcript)
    if not target_n or not transcript_n:
        return 0

    char_ratio = SequenceMatcher(None, target_n, transcript_n).ratio()
    word_ratio = _word_overlap(target_n, transcript_n)

    # For one-word targets the character ratio is more useful.
    if len(target_n.split()) == 1:
        score = char_ratio * 100
    else:
        score = (char_ratio * 0.65 + word_ratio * 0.35) * 100

    return int(round(max(0, min(100, score))))


def pronunciation_feedback(score, target):
    # Wir bewerten hier den erkannten Text,
    # nicht Klang, Akzent oder einzelne Laute.
    if score >= 92:
        return f"Sehr gut. Ich habe „{target}“ richtig erkannt."
    if score >= 80:
        return f"Gut. Ich habe „{target}“ erkannt."
    if score >= 65:
        return f"Fast. Ich habe „{target}“ nur teilweise erkannt. Sag es bitte noch einmal langsam."
    return f"Noch einmal. Sag „{target}“ bitte langsam und deutlich."


def evaluate_pronunciation(state, target, transcript):
    target = str(target or "").strip()
    transcript = str(transcript or "").strip()
    score = pronunciation_score(target, transcript)

    target_type = "word" if len(target.split()) == 1 else "sentence"

    # Reuse Nele 1's existing pronunciation memory/coach.
    try:
        process_pronunciation_result(
            state,
            target_type=target_type,
            target=target,
            score=score,
        )
    except Exception as error:
        print(f"Nele3 pronunciation memory error: {error}")

    update_skill(state, "pronunciation", score)
    record_event(
        state,
        "pronunciation",
        detail=target,
        result={"score": score, "transcript": transcript},
    )

    return {
        "target": target,
        "transcript": transcript,
        "score": score,
        "feedback": pronunciation_feedback(score, target),
        "method": "whisper_transcript_similarity",
    }
