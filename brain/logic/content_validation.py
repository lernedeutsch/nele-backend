"""Validation gate for production Nele learning content."""
from brain.logic.lesson_loader import (
    BASE_DIR,
    load_lesson,
    load_lesson_flow,
    load_lesson_metadata,
    load_lesson_module,
)
from brain.logic.personal_sentences import validate_personal_sentence_catalog


class ContentValidationError(ValueError):
    pass


def _require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ContentValidationError(f"{label} must be non-empty text.")


def get_existing_lesson_numbers(level="A1"):
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


def validate_dialogues(level, lesson):
    module = load_lesson_module(level, lesson)
    dialogues = getattr(module, "LESSON_DIALOGUES", None) if module else None
    if dialogues is None:
        return True
    if not isinstance(dialogues, list):
        raise ContentValidationError(f"{level} lesson {lesson}: LESSON_DIALOGUES must be a list.")

    seen_ids = set()
    for d_index, dialogue in enumerate(dialogues):
        if not isinstance(dialogue, dict):
            raise ContentValidationError(
                f"{level} lesson {lesson}: dialogue {d_index} is not a dict."
            )
        dialogue_id = dialogue.get("id")
        _require_text(dialogue_id, f"{level} lesson {lesson} dialogue {d_index} id")
        key = dialogue_id.strip().casefold()
        if key in seen_ids:
            raise ContentValidationError(
                f"{level} lesson {lesson}: duplicate dialogue id {dialogue_id!r}."
            )
        seen_ids.add(key)
        _require_text(
            dialogue.get("title"),
            f"{level} lesson {lesson} dialogue {dialogue_id} title",
        )
        sections = dialogue.get("sections", dialogue.get("section", []))
        if isinstance(sections, str):
            sections = [sections]
        if not isinstance(sections, list) or not any(
            isinstance(value, str) and value.strip() for value in sections
        ):
            raise ContentValidationError(
                f"{level} lesson {lesson} dialogue {dialogue_id}: missing section mapping."
            )

        register = str(dialogue.get("register") or "").strip().casefold()
        if register and register not in {"informal", "formal", "mixed"}:
            raise ContentValidationError(
                f"{level} lesson {lesson} dialogue {dialogue_id}: invalid register."
            )
        if int(dialogue.get("max_turns", 8) or 8) < 1:
            raise ContentValidationError(
                f"{level} lesson {lesson} dialogue {dialogue_id}: max_turns must be positive."
            )
        if int(dialogue.get("max_variations", 2) or 2) < 0:
            raise ContentValidationError(
                f"{level} lesson {lesson} dialogue {dialogue_id}: max_variations cannot be negative."
            )

        turns = dialogue.get("turns")
        if not isinstance(turns, list) or not turns:
            raise ContentValidationError(
                f"{level} lesson {lesson} dialogue {dialogue_id}: turns are empty."
            )

        learner_turns = 0
        for t_index, turn in enumerate(turns):
            if not isinstance(turn, dict):
                raise ContentValidationError(
                    f"{level} lesson {lesson} dialogue {dialogue_id}: "
                    f"turn {t_index} is not a dict."
                )
            role = str(turn.get("role") or "").strip().casefold()
            if role not in {"nele", "teacher", "assistant", "student", "learner", "user", "du"}:
                raise ContentValidationError(
                    f"{level} lesson {lesson} dialogue {dialogue_id}: "
                    f"turn {t_index} has invalid role."
                )
            if role in {"student", "learner", "user", "du"}:
                learner_turns += 1
                expected_intent = turn.get("expected_intent") or turn.get("intent")
                if expected_intent is not None:
                    _require_text(
                        expected_intent,
                        f"{level} lesson {lesson} dialogue {dialogue_id} turn {t_index} intent",
                    )
                accepted = turn.get("accepted", [])
                expected = turn.get("expected")
                allow_any = turn.get("allow_any") is True
                contains_all = turn.get("contains_all", [])
                if not (expected or accepted or allow_any or contains_all):
                    raise ContentValidationError(
                        f"{level} lesson {lesson} dialogue {dialogue_id}: "
                        f"learner turn {t_index} has no answer rule."
                    )
            else:
                _require_text(
                    turn.get("text"),
                    f"{level} lesson {lesson} dialogue {dialogue_id} turn {t_index} text",
                )

        # A dialogue must alternate meaningfully: no two learner turns may occur
        # without a teacher/partner turn between them.
        previous_learner = False
        for t_index, turn in enumerate(turns):
            learner = str(turn.get("role") or "").strip().casefold() in {
                "student", "learner", "user", "du"
            }
            if learner and previous_learner:
                raise ContentValidationError(
                    f"{level} lesson {lesson} dialogue {dialogue_id}: "
                    f"consecutive learner turns near {t_index}."
                )
            previous_learner = learner

        if not learner_turns:
            raise ContentValidationError(
                f"{level} lesson {lesson} dialogue {dialogue_id}: no learner turns."
            )
    return True


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

    if flow is not None:
        sections = flow.get("sections")
        if not isinstance(sections, (dict, list)) or not sections:
            raise ContentValidationError(
                f"{level} lesson {lesson}: LESSON_FLOW.sections is empty."
            )
        names = list(sections) if isinstance(sections, dict) else [
            x if isinstance(x, str) else x.get("name")
            for x in sections if isinstance(x, (str, dict))
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

    validate_dialogues(level, lesson)
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
