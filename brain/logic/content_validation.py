"""Validation gate for production Nele learning content.

Run this before publishing new lesson knowledge or shared learner sentences.
It deliberately validates through the same lesson loader used by production.
"""
from brain.logic.lesson_loader import (
    get_available_lesson_numbers,
    load_lesson,
    load_lesson_flow,
    load_lesson_metadata,
)
from brain.logic.personal_sentences import validate_personal_sentence_catalog


class ContentValidationError(ValueError):
    pass


def _require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ContentValidationError(f"{label} must be non-empty text.")


def validate_lesson(level, lesson):
    responses = load_lesson(level, lesson)
    metadata = load_lesson_metadata(level, lesson)
    flow = load_lesson_flow(level, lesson)

    if not isinstance(metadata, dict):
        raise ContentValidationError(f"{level} lesson {lesson}: missing LESSON metadata.")
    if not isinstance(flow, dict):
        raise ContentValidationError(f"{level} lesson {lesson}: missing LESSON_FLOW.")
    if not isinstance(responses, (list, tuple)):
        raise ContentValidationError(f"{level} lesson {lesson}: LESSON_RESPONSES must be a list/tuple.")

    _require_text(metadata.get("title"), f"{level} lesson {lesson} title")
    sections = flow.get("sections")
    if not isinstance(sections, (dict, list)) or not sections:
        raise ContentValidationError(f"{level} lesson {lesson}: LESSON_FLOW.sections is empty.")

    if isinstance(sections, dict):
        names = list(sections)
    else:
        names = [
            x if isinstance(x, str) else x.get("name")
            for x in sections
            if isinstance(x, (str, dict))
        ]
    cleaned = []
    for name in names:
        _require_text(name, f"{level} lesson {lesson} section name")
        key = name.strip().casefold()
        if key in cleaned:
            raise ContentValidationError(f"{level} lesson {lesson}: duplicate section {name!r}.")
        cleaned.append(key)

    for index, item in enumerate(responses):
        if not isinstance(item, dict):
            raise ContentValidationError(f"{level} lesson {lesson}: response {index} is not a dict.")
        patterns = item.get("patterns")
        if patterns is not None:
            if not isinstance(patterns, (list, tuple)) or not any(str(x).strip() for x in patterns):
                raise ContentValidationError(
                    f"{level} lesson {lesson}: response {index} has invalid patterns."
                )
    return True


def validate_all_learning_content(level="A1"):
    validate_personal_sentence_catalog()
    lessons = get_available_lesson_numbers(level)
    if not lessons:
        raise ContentValidationError(f"No publishable {level} lessons found.")
    for lesson in lessons:
        validate_lesson(level, lesson)
    return {"level": level, "lessons": lessons, "personal_sentences": "ok"}


if __name__ == "__main__":
    result = validate_all_learning_content()
    print(
        "NELE CONTENT OK:",
        result["level"],
        "lessons=" + ",".join(map(str, result["lessons"])),
        "personal_sentences=ok",
    )
