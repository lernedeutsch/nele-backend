# NELE Dialogue Knowledge Standard

Single contract for adding dialogue content to the current production backend.

## Core rule

Lesson/dialogue files own CONTENT. brain/logic/dialogue_engine.py owns BEHAVIOR. Never add lesson-specific conversation control flow to the global engine.

## Required dialogue fields

id, title, section/sections, turns. Recommended semantic fields: level, lesson, topic, situation, register, learning_goals, grammar, vocabulary, slots, allowed_variations, forbidden_variations, next_allowed_topics, max_turns, max_variations.

Each learner turn should define expected_intent or intent plus expected / accepted_patterns / accepted / contains_all / allow_any. accepted_patterns may contain safe slots such as {country}.

## Import pipeline

RAW DIALOG -> NORMALIZE -> LEVEL CHECK -> INTENTS -> TURNS -> SLOTS -> ACCEPTED PATTERNS -> ERROR PATTERNS -> CONSTRAINTS -> VALIDATOR -> GOLDEN TESTS -> ACTIVE KNOWLEDGE -> DIALOGUE ENGINE -> NELE.

Raw dialogue text must never be pasted directly into a conversation prompt.

## Meaning-first correction

Evaluate in this order: MEANING -> GRAMMAR -> NATURALNESS. A short but semantically correct A1 answer must not be marked wrong merely because it is not identical to the model sentence.

## Mixing policy

Topic changes are denied by default. A transition is allowed only when the target appears in next_allowed_topics. Formal and informal registers must not be mixed unless the dialogue explicitly declares register=mixed.

## Loop policy

Every dialogue has a hard turn budget. Repeated slot variation has its own budget. Completing an intent records it once in session state. Reaching the hard limit ends the micro-dialogue instead of asking indefinitely.

## Release gate

A new dialogue is production-ready only when content validation, dialogue golden tests, and existing regression tests pass. Every new dialogue should test: canonical answer, natural variant, short answer, minor error, unrelated answer, slot change, person change, continuation, completion, and anti-loop behavior.
