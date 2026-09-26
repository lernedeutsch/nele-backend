# Free Conversation Core Refactor — Stage 1

## Hardcoding to migrate
- `free_conversation.py`: fixed FALLBACKS, exact yes/no follow-ups, large `_social_a1_reply()`, local recast patterns.
- `a1_everyday_conversation.py`: exact last-question routing and fixed direct Q/A map.
- topic names differ between modules (work/arbeit, hobby/freizeit, food/essen).
- dialogue knowledge already has a reusable engine, while general free conversation still has parallel local banks.

## Keep as local exceptions
Identity/capability truthfulness, explicit recovery/safety boundaries, truly language-specific irregular corrections, and dialogue exit/completion mechanics.

## Migration rule
Do not delete legacy behavior first. Move one capability behind a shared interface, add regression coverage, test Nele Live, then remove only the replaced branch.

## Target flow
input -> understand -> topic/intent -> learner model -> knowledge retrieval -> TurnPlan -> mode policy -> response -> quality/coherence -> state commit.

## Acceptance
Long free conversation accepts short answers, answers learner questions, changes topic cleanly, avoids loops, uses lesson/dialogue/personal knowledge contextually, corrects selectively, adapts support, and keeps Free/Course policies separate over shared engines.
