# Nele Production Project Map

> This document describes the **current production architecture** of Nele.
> It is a navigation map for maintainers and AI coding assistants. It does not replace `ARCHITECTURE_RULES.md`.

## Production boundary

- Frontend repository: `lernedeutsch/deutschsprechen`
- Main UI: `nele.html`
- Frontend controller: `nele/nele.js`
- Pronunciation UI/controller: `nele/nele-pronunciation.js`
- Production backend repository: `lernedeutsch/nele-backend`
- Production backend: `https://nele-backend.onrender.com`
- Flask entry point: `server/app.py`
- Production database: Render PostgreSQL `nele-database`
- `nele-backend-3` is experimental and must not be treated as production unless explicitly requested.

## Request flow

```text
deutschsprechen/nele.html
  |
  +-- nele/nele.js
  |     +-- course mode: "Mit dem Kurs ueben"
  |     +-- free mode: "Frei sprechen"
  |
  +-- nele/nele-pronunciation.js
        +-- pronunciation / recorded audio
                |
                v
https://nele-backend.onrender.com
                |
          server/app.py
```

The frontend stores and sends a learner/session id and a `conversation_mode`.
The backend is the authoritative place for conversation and learner logic.

## Free conversation

Primary entry:
- `brain/logic/free_conversation.py`

Important cooperating modules include:
- `brain/logic/conversation_orchestrator.py`
- `brain/logic/teacher_engine.py`
- `brain/logic/teacher_policy.py`
- `brain/logic/topic_manager.py`
- `brain/logic/topic_follow_up_engine.py`
- `brain/logic/response_understanding.py`
- `brain/logic/conversation_coherence.py`
- `brain/logic/conversation_personalization.py`
- `brain/logic/conversation_quality_controller.py`
- `brain/logic/global_conversation_guard.py`
- `brain/logic/learner_model.py`
- `brain/logic/learning_action_executor.py`
- `brain/logic/learning_outcome_tracker.py`

Rule: fix reusable conversation behaviour globally where possible. Do not hard-code a one-sentence or one-lesson patch when the problem is general.

## Course practice

Course requests enter through `server/app.py` and use the production conversation/teaching routers rather than the free-conversation branch.

Relevant areas include:
- `brain/logic/conversation.py`
- `brain/logic/lesson_loader.py`
- `brain/logic/lesson_teaching.py`
- `brain/logic/generic_lesson_engine.py`
- `brain/logic/teacher_engine.py`
- `brain/logic/teacher_policy.py`
- `brain/logic/lesson_progress_router.py`
- `brain/logic/lesson_review_training.py`
- `brain/logic/curriculum_skill_graph.py`

Lesson content determines **what** Nele teaches. Shared engines determine **how** Nele teaches.

## Meine Saetze / personal sentences

Primary module:
- `brain/logic/personal_sentences.py`

It owns the reusable learner sentence catalogue and practice state, including use counts, mastery, recent items and selection for later practice. Personal sentences can be recognised in both free and course modes.

Do not duplicate personal sentences directly inside individual lesson logic when they belong to the shared learner layer.

## Learner state and memory

Important production memory areas:
- `brain/memory/persistent_memory.py`
- `brain/memory/error_memory.py`
- `brain/memory/vocabulary_memory.py`
- `brain/memory/pronunciation_memory.py`
- `brain/memory/lesson_progress.py`
- `brain/memory/student_progress.py`
- `brain/memory/user_facts.py`
- `brain/logic/conversation_memory.py`
- `brain/logic/learner_model.py`

Persistent production data is backed by Render PostgreSQL `nele-database`.

### Legacy warning

`memory/student_memory.py` is an older local JSON-based memory implementation with hard-coded examples. Do not assume it is the authoritative production learner memory and do not modify/delete it until dependencies have been checked.

## Speech

### TTS

- Production TTS implementation: `speech/speaker.py`
- Engine: Piper
- Current production voice model: `piper/de_DE-kerstin-low.onnx`

Visible teaching placeholders are normalized before speech so pedagogical underscores are not spoken.

### ASR / microphone

`speech/listener.py` is explicitly a **legacy local microphone listener** and is not the production Flask speech path.

Production voice input uses:
- browser speech recognition where applicable, or
- recorded audio sent to the backend and transcribed with faster-whisper.

Pronunciation-related backend logic includes:
- `brain/logic/pronunciation_audio.py`
- `brain/logic/pronunciation_coach.py`
- `brain/logic/pronunciation_feedback.py`

Frontend pronunciation handling is in `deutschsprechen/nele/nele-pronunciation.js`.

## Server and API

`server/app.py` is the production Flask application. It:
- exposes health/status endpoints,
- handles learner/session locking,
- refreshes and saves conversation state,
- routes free vs course conversation,
- handles personal sentences,
- exposes speech/pronunciation functionality,
- registers the Nele 3 upgrade blueprint while preserving the existing production router.

Do not infer from the presence of `brain/nele3_upgrade/` that the separate experimental `nele-backend-3` is production.

## Tests

Regression and integration tests live under `tests/`.

Important coverage includes:
- free conversation and short answers,
- learner-led topic switching,
- lesson conversations,
- verb correction,
- conversation guard and speaking support,
- personal sentences,
- topic follow-ups,
- vocabulary,
- learner feedback,
- conversation simulations,
- TTS speech normalization,
- turn-plan compliance,
- architecture/security.

There is also `test_nele_live.py` for live Nele checks.

When changing shared behaviour, add or update a regression test that represents the reported failure.

## Diagnostic routing

Use this map before editing:

| Symptom | Start here |
| --- | --- |
| Free conversation repeats, loses context, or changes topic badly | `free_conversation.py`, orchestrator, coherence, topic manager, global guard |
| Course practice behaves incorrectly | course/lesson routers, teacher engine/policy, lesson teaching |
| Nele does not remember learner progress/errors | persistent memory, learner model, relevant memory module, PostgreSQL |
| Meine Saetze are not recognised/practised correctly | `personal_sentences.py` |
| Nele hears the learner incorrectly | production audio/transcription path, pronunciation audio, faster-whisper |
| Nele speaks incorrectly | `speech/speaker.py`, Piper/TTS normalization |
| Frontend sends wrong mode/session/request | `deutschsprechen/nele/nele.js` |
| Pronunciation UI/request is wrong | `deutschsprechen/nele/nele-pronunciation.js` |
| Deployment/runtime failure | Render deploy + production logs |

## Safe workflow

1. Reproduce or identify the reported behaviour.
2. Trace it through this map before editing.
3. Check `ARCHITECTURE_RULES.md`.
4. Prefer a global reusable fix over a lesson-specific patch.
5. Add/update a regression test.
6. Verify CI/tests.
7. Verify the production deploy and logs when deployment occurs.
8. Do not modify `nele-backend-3` unless explicitly requested.
9. Never expose secrets, database credentials, tokens or private environment values in code or documentation.

## Source of truth

If this map conflicts with current executable code, the current production code and deployment configuration are authoritative. Update this document when architecture changes.
