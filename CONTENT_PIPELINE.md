# Nele Content Pipeline

This is the mandatory safe path for adding learning material to production Nele.

## One rule

**Content says WHAT Nele teaches. Shared engines say HOW Nele teaches.**

Do not add a new router or one-off teaching mechanism for every lesson.

## Adding a course lesson

1. Put the lesson's teaching/response data in `brain/responses/<LEVEL>/<NUMBER>.py`.
2. Keep the standard contract: `LESSON`, `LESSON_FLOW`, and `LESSON_RESPONSES`.
3. Reuse `generic_lesson_engine.py`, teacher policy, speaking support and existing memory.
4. Run `python -m brain.logic.content_validation`.
5. Run the regression test suite.
6. Only publish/deploy when both pass.

A lesson is not considered publishable by the loader until it has real flow sections.

## Adding reusable knowledge / Meine Saetze

For everyday sentences that should work across lessons, add one catalogue item to
`brain/logic/personal_sentences.py`. Do not copy it into individual lessons.

Required fields: `id`, `text`, `reply`. Recommended: `category`, `aliases`,
`practice_prompt`.

The validation gate rejects duplicate IDs/texts and incomplete entries.

## Definition of done

New content is done only when:
- production loader can import it,
- content validation passes,
- regression tests pass,
- existing lessons remain green,
- no production route was duplicated,
- live check is performed after deployment when behaviour changed.

## Recovery rule

If validation fails, do not patch around the validator. Fix the content contract or,
if the contract itself genuinely needs extension, change the shared contract with
regression coverage first.
