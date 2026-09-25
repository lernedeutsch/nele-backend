"""Validation gate for production Nele learning content.

The gate checks every numeric lesson module that exists, not only lessons already
considered publishable by the runtime loader. Legacy response-only lessons remain
valid, while every lesson that declares LESSON_FLOW is checked strictly.
"""
from pathlib import Path

from brain.logic.lesson_loader import (
    BASE_DIR,
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


def get_existing_lesson_numbers(level="A1"):
    """Return every numeric lesson module present on disk.

    This deliberately does not use get_available_lesson_numbers(): an incomplete
    new lesson must be visible to validation instead of silently disappearing.
    """
    level = str(level or "A1").strip().upper()
    directory = BASE_DIR / "responses" / level
    if not directory.exists():
        return []

    result = []
    for path in directory.glob("*.py"):
        try:
            number = int(path.stem)
        except (TypeError, ValueError):
            continue
        if number > 0:
            result.append(number)
    return sorted(set(result))


def validate_lesson(level, lesson):
    responses = load_lesson(level, lesson)
    metadata = load_lesson_metadata(level, lesson)
    flow = load_lesson_flow(level, lesson)

    if not isinstance(metadata, dict):
        raise ContentValidationError(f"{level} lesson {lesson}: missing LESSON metadata.")
    if not isinstance(responses, (list, tuple)):
        raise ContentValidationError(
            f"{level} lesson {lesson}: LESSON_RESPONSES must be a list/tuple."
        )

    _require_text(metadata.get("title"), f"{level} lesson {lesson} title")

    try:
        declared_number = int(metadata.get("lesson"))
    except (TypeError, ValueError):
        raise ContentValidationError(
            f"{level} lesson {lesson}: LESSON.lesson must be an integer."
        )
    if declared_number != int(lesson):
        raise ContentValidationError(
            f"{level} lesson {lesson}: LESSON.lesson is {declared_number}."
        )

    declared_level = str(metadata.get("level") or "").strip().upper()
    if declared_level != str(level).strip().upper():
        raise ContentValidationError(
            f"{level} lesson {lesson}: LESSON.level is {metadata.get('level')!r}."
        )

    # Legacy lessons can contain reusable knowledge responses without an active
    # guided flow. Once LESSON_FLOW is present, however, its contract is strict.
    if flow is not None:
        sections = flow.get("sections")
        if not isinstance(sections, (dict, list)) or not sections:
            raise ContentValidationError(
                f"{level} lesson {lesson}: LESSON_FLOW.sections is empty."
            )

        if isinstance(sections, dict):
            names = list(sections)
        else:
            names = [
                x if isinstance(x, str) else x.get("name")
                for x in sections
                if isinstance(x, (str, dict))
            ]

        cleaned = set()
        for name in names:
            _require_text(name, f"{level} lesson {lesson} section name")
            key = name.strip().casefold()
            if key in cleaned:
                raise ContentValidationError(
                    f"{level} lesson {lesson}: duplicate section {name!r}."
                )
            cleaned.add(key)

    seen_intents = set()
    for index, item in enumerate(responses):
        if not isinstance(item, dict):
            raise ContentValidationError(
                f"{level} lesson {lesson}: response {index} is not a dict."
            )

        patterns = item.get("patterns")
        if not isinstance(patterns, (list, tuple)) or not any(
            isinstance(x, str) and x.strip() for x in patterns
        ):
            raise ContentValidationError(
                f"{level} lesson {lesson}: response {index} has invalid patterns."
            )

        replies = item.get("responses")
        if not isinstance(replies, (list, tuple)) or not any(
            isinstance(x, str) and x.strip() for x in replies
        ):
            raise ContentValidationError(
                f"{level} lesson {lesson}: response {index} has invalid responses."
            )

        intent = item.get("intent")
        _require_text(intent, f"{level} lesson {lesson} response {index} intent")
        intent_key = intent.strip().casefold()
        if intent_key in seen_intents:
            raise ContentValidationError(
                f"{level} lesson {lesson}: duplicate intent {intent!r}."
            )
        seen_intents.add(intent_key)

    return True


def validate_all_learning_content(level="A1"):
    validate_personal_sentence_catalog()
    lessons = get_existing_lesson_numbers(level)
    if not lessons:
        raise ContentValidationError(f"No {level} lesson modules found.")

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
