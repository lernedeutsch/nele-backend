import unittest
from unittest.mock import patch

from brain.nele3_upgrade.activities import (
    _items_for_level,
    _looks_like_prompt_echo,
    answer_active_task,
    resume_active_task,
)
from brain.nele3_upgrade.router import handle_upgrade_message
from brain.nele3_upgrade.teacher_brain import build_adaptive_recommendation
from brain.nele3_upgrade.state import (
    get_last_completed_activity,
    mark_activity_completed,
    update_skill,
)
from brain.nele3_upgrade.content import (
    DIALOGUES,
    LISTENING_TASKS,
    WRITING_TASKS,
    WORK_GERMAN,
    PRONUNCIATION_TARGETS,
)
from brain.logic.welcome import generate_welcome_reply
from brain.logic.response_engine import (
    _shorten_session_restart_prompt,
    get_last_lesson_recap_data,
)
from brain.nele3_upgrade.state import get_active_task
from brain.logic.lesson_loader import (
    get_available_lesson_numbers,
)
from brain.logic.onboarding import (
    extract_learning_goal_sentence,
    get_short_answer_value,
)
from brain.logic.lesson_teaching import (
    is_morning_greeting,
    is_day_greeting,
    is_evening_greeting,
    is_relevant_greeting_mistake,
)
from brain.logic.error_practice import (
    is_relevant_error_example,
    start_error_practice,
    handle_error_practice,
)
from brain.memory.error_memory import (
    remember_error,
    get_error_item,
)
from brain.memory.error_review import (
    refresh_error_reviews,
    get_due_error_reviews,
    is_error_due_for_review,
)


class NeleCoreBehaviorTests(unittest.TestCase):

    def test_a1_addon_content_never_returns_a2_items(self):
        groups = [
            DIALOGUES,
            LISTENING_TASKS,
            WRITING_TASKS,
            WORK_GERMAN,
            PRONUNCIATION_TARGETS,
        ]

        for group in groups:
            selected = _items_for_level(group, "A1")
            self.assertTrue(selected)
            self.assertTrue(
                all(
                    str(item.get("level") or "A1").upper() == "A1"
                    for item in selected
                )
            )

    def test_a2_addon_content_uses_a2_when_available(self):
        for group in [
            DIALOGUES,
            LISTENING_TASKS,
            WRITING_TASKS,
            WORK_GERMAN,
            PRONUNCIATION_TARGETS,
        ]:
            selected = _items_for_level(group, "A2")
            self.assertTrue(selected)
            self.assertTrue(
                all(
                    str(item.get("level") or "").upper() == "A2"
                    for item in selected
                )
            )

    def test_writing_prompt_copy_is_detected(self):
        prompt = (
            "Schreib zwei kurze Sätze: "
            "Du kommst heute zehn Minuten später zur Arbeit."
        )

        self.assertTrue(
            _looks_like_prompt_echo(
                "Du kommst heute zehn Minuten später zur Arbeit.",
                prompt,
            )
        )

        self.assertFalse(
            _looks_like_prompt_echo(
                "Ich komme heute zehn Minuten später. Entschuldigung.",
                prompt,
            )
        )

    def test_writing_corrects_etschuldigung_instead_of_accepting_it(self):
        item = next(
            task
            for task in WRITING_TASKS
            if task.get("id") == "short_message"
        )

        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "writing",
                    "title": item["title"],
                    "prompt": item["prompt"],
                    "keywords": item.get("keywords", []),
                    "required": item.get("required", []),
                    "min_words": item.get("min_words", 5),
                    "min_sentences": item.get("min_sentences", 1),
                    "spelling_corrections": item.get(
                        "spelling_corrections",
                        {},
                    ),
                    "model_answer": item.get("model_answer"),
                }
            }
        }

        result = answer_active_task(
            state,
            (
                "etschuldigung, ich komme heute "
                "zehn Minuten später zur Arbeit."
            ),
        )

        self.assertFalse(result["completed"])
        self.assertIn("Entschuldigung", result["reply"])
        self.assertTrue(
            get_active_task(state)
        )

    def test_writing_accepts_natural_short_message_after_correction(self):
        item = next(
            task
            for task in WRITING_TASKS
            if task.get("id") == "short_message"
        )

        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "writing",
                    "title": item["title"],
                    "prompt": item["prompt"],
                    "keywords": item.get("keywords", []),
                    "required": item.get("required", []),
                    "min_words": item.get("min_words", 5),
                    "min_sentences": item.get("min_sentences", 1),
                    "spelling_corrections": item.get(
                        "spelling_corrections",
                        {},
                    ),
                    "model_answer": item.get("model_answer"),
                }
            }
        }

        result = answer_active_task(
            state,
            (
                "Entschuldigung, ich komme heute "
                "zehn Minuten später zur Arbeit."
            ),
        )

        self.assertTrue(result["completed"])
        self.assertIn(
            "Das klingt natürlich",
            result["reply"],
        )
        self.assertIsNone(
            get_active_task(state)
        )

    def test_short_message_prompt_and_model_no_longer_contradict_each_other(self):
        item = next(
            task
            for task in WRITING_TASKS
            if task.get("id") == "short_message"
        )

        self.assertIn(
            "Schreib eine kurze Nachricht",
            item["prompt"],
        )
        self.assertEqual(
            item.get("min_sentences"),
            1,
        )
        self.assertEqual(
            item.get("spelling_corrections", {}).get(
                "etschuldigung"
            ),
            "Entschuldigung",
        )


    def test_interrupted_writing_task_can_resume(self):
        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "writing",
                    "prompt": "Schreib zwei kurze Sätze.",
                }
            }
        }

        result = resume_active_task(state)

        self.assertIsInstance(result, dict)
        self.assertIn("Schreib zwei kurze Sätze.", result["reply"])
        self.assertTrue(result["meta"]["resumed"])

    def test_interrupted_listening_task_keeps_audio_text(self):
        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "listening",
                    "prompt": "Um wie viel Uhr fährt der Zug?",
                    "speak_text": "Der Zug fährt um acht Uhr zwanzig.",
                }
            }
        }

        result = resume_active_task(state)

        self.assertEqual(
            result["speak_text"],
            "Der Zug fährt um acht Uhr zwanzig.",
        )
        self.assertEqual(
            result["meta"]["activity"],
            "listening",
        )

    def test_empty_a1_lesson_2_is_not_treated_as_ready(self):
        available = get_available_lesson_numbers("A1")
        self.assertNotIn(2, available)

    def test_wellbeing_reply_is_not_consumed_by_interrupted_addon_task(self):
        state = {
            "last_question": "wellbeing",
            "nele3_upgrade": {
                "active_task": {
                    "type": "writing",
                    "prompt": "Schreib zwei kurze Sätze.",
                    "keywords": ["komme", "später"],
                    "required": ["ich"],
                    "min_words": 6,
                    "min_sentences": 2,
                }
            }
        }

        handled, answer, meta = handle_upgrade_message(
            "Gut",
            state,
        )

        self.assertFalse(handled)
        self.assertIsNone(answer)
        self.assertEqual(meta, {})
        self.assertEqual(
            state["nele3_upgrade"]["active_task"]["type"],
            "writing",
        )

    def test_old_memory_backfills_last_completed_activity_from_events(self):
        state = {
            "nele3_upgrade": {
                "events": [
                    {
                        "type": "activity_completed",
                        "detail": {
                            "activity_type": "writing",
                            "detail": "Verspätung melden",
                        },
                        "result": {"score": 100},
                    }
                ]
            }
        }

        self.assertEqual(
            get_last_completed_activity(state),
            "writing",
        )

        recommendation = build_adaptive_recommendation(state)

        self.assertIsInstance(recommendation, dict)
        self.assertNotEqual(
            recommendation.get("activity"),
            "writing",
        )



    def test_fresh_conversation_clears_only_active_task(self):
        state = {
            "onboarding_completed": True,
            "user_facts": {
                "name": "Moni",
            },
            "nele3_upgrade": {
                "active_task": {
                    "type": "listening",
                    "prompt": "Um wie viel Uhr fährt der Zug?",
                },
                "skills": {
                    "listening": {
                        "attempts": 3,
                        "correct": 2,
                        "score_avg": 80.0,
                        "last_score": 100,
                        "last_practiced": "2026-09-19T00:00:00+00:00",
                    }
                },
            },
        }

        with patch(
            "brain.logic.session_service.get_conversation_state",
            return_value=state,
        ), patch(
            "brain.logic.session_service.save_conversation_state"
        ), patch(
            "brain.logic.session_service.generate_welcome_reply",
            return_value="Hallo Moni!",
        ):
            from server.app import create_welcome_reply

            reply = create_welcome_reply(
                "test-user",
                preserve_active_task=False,
            )

        self.assertEqual(reply, "Hallo Moni!")
        self.assertIsNone(
            get_active_task(state)
        )
        self.assertEqual(
            state["nele3_upgrade"]["skills"]["listening"]["attempts"],
            3,
        )


    def test_interrupted_onboarding_step_two_has_no_double_greeting(self):
        state = {
            "onboarding_completed": False,
            "onboarding_step": 2,
            "user_facts": {
                "name": "Moni",
            },
        }

        with patch(
            "brain.logic.welcome.get_conversation_state",
            return_value=state,
        ), patch(
            "brain.logic.welcome.save_conversation_state"
        ):
            reply = generate_welcome_reply(
                "test-user"
            )

        self.assertEqual(
            reply,
            (
                "Hallo Moni! "
                "Schön, dass du wieder da bist. "
                "Woher kommst du?"
            ),
        )
        self.assertNotIn(
            "Schön, dich kennenzulernen",
            reply,
        )


    def test_onboarding_rejects_unrelated_learning_goal(self):
        self.assertEqual(
            extract_learning_goal_sentence("ich will spielen"),
            "",
        )
        self.assertEqual(
            extract_learning_goal_sentence("ich möchte A1 erreichen"),
            "Deutsch A1",
        )

    def test_residence_retry_does_not_invent_place_from_asr_fragment(self):
        self.assertEqual(
            get_short_answer_value("Yvonne in Heidelberg", 3),
            "",
        )
        self.assertEqual(
            get_short_answer_value("Heidelberg", 3),
            "Heidelberg",
        )
        self.assertEqual(
            get_short_answer_value("Sonne Heidelberg", 3),
            "",
        )

    def test_lesson_recap_is_short_and_does_not_use_zuletzt(self):
        state = {
            "last_activity": "lesson",
            "last_activity_detail": "Wir begrüßen uns",
        }

        with patch(
            "brain.logic.response_engine.get_next_new_learning_step",
            return_value={
                "type": "continue_lesson",
                "level": "A1",
                "lesson": 1,
                "section": "Wir begrüßen uns",
            },
        ):
            recap = get_last_lesson_recap_data(state)

        self.assertEqual(
            recap.get("message"),
            "Wir machen mit Lektion 1 weiter.",
        )
        self.assertNotIn(
            "Zuletzt",
            recap.get("message"),
        )

    def test_alphabet_restart_uses_short_natural_intro(self):
        state = {
            "last_activity": "lesson",
            "last_activity_detail": "Ich stelle mich vor",
        }

        with patch(
            "brain.logic.response_engine.get_next_new_learning_step",
            return_value={
                "type": "continue_lesson",
                "level": "A1",
                "lesson": 1,
                "section": "Das deutsche Alphabet",
            },
        ):
            recap = get_last_lesson_recap_data(state)

        self.assertEqual(
            recap.get("message"),
            "Wir machen mit dem Alphabet weiter.",
        )
        self.assertEqual(
            _shorten_session_restart_prompt(
                (
                    "Super, dann machen wir eine kurze "
                    "Übung zum deutschen Alphabet. "
                    "Welcher Buchstabe kommt nach A?"
                )
            ),
            "Welcher Buchstabe kommt nach A?",
        )

    def test_completed_lesson_has_no_stale_section_recap(self):
        state = {
            "last_activity": "lesson",
            "last_activity_detail": "Das deutsche Alphabet",
        }

        with patch(
            "brain.logic.response_engine.get_next_new_learning_step",
            return_value={
                "type": "lesson_completed",
                "level": "A1",
                "lesson": 1,
            },
        ):
            recap = get_last_lesson_recap_data(state)

        self.assertIsNone(recap)


    def test_greeting_steps_require_full_expression(self):
        self.assertFalse(is_morning_greeting("morgen"))
        self.assertFalse(is_day_greeting("tag"))
        self.assertFalse(is_evening_greeting("abend"))
        self.assertTrue(is_morning_greeting("Guten Morgen"))
        self.assertTrue(is_day_greeting("Guten Tag"))
        self.assertTrue(is_evening_greeting("Guten Abend"))

    def test_unrelated_sentence_is_not_saved_as_greeting_mistake(self):
        self.assertFalse(
            is_relevant_greeting_mistake("ich will spielen")
        )
        self.assertTrue(
            is_relevant_greeting_mistake("guten Morgen")
        )
        self.assertTrue(
            is_relevant_greeting_mistake("h")
        )
        self.assertTrue(
            is_relevant_greeting_mistake("p")
        )

    def test_old_unrelated_greeting_error_is_skipped(self):
        self.assertFalse(
            is_relevant_error_example(
                {
                    "wrong": "ich will spielen",
                    "correct": "Guten Tag",
                    "needs_practice": True,
                }
            )
        )
        self.assertTrue(
            is_relevant_error_example(
                {
                    "wrong": "Guten Morgen",
                    "correct": "Guten Tag",
                    "needs_practice": True,
                }
            )
        )
        self.assertTrue(
            is_relevant_error_example(
                {
                    "wrong": "h",
                    "correct": "Guten Morgen",
                    "needs_practice": True,
                }
            )
        )


    def test_short_wrong_greeting_attempts_are_saved_for_review(self):
        state = {
            "lesson_teaching_active": True,
            "lesson_teaching_section": "Wir begrüßen uns",
            "lesson_teaching_step": 1,
        }

        from brain.logic.lesson_teaching import handle_greeting_section

        handle_greeting_section("h", state)
        handle_greeting_section("k", state)
        handle_greeting_section("g", state)
        handle_greeting_section("Guten Morgen", state)

        item = get_error_item(
            "vocabulary",
            state,
        )

        self.assertTrue(
            item.get(
                "needs_practice",
                False,
            )
        )

        first = start_error_practice(
            state,
            "vocabulary",
        )

        self.assertIn(
            "Guten Morgen",
            first,
        )


    def test_same_learning_target_is_practiced_only_once(self):
        state = {}
        context = "Welcher Buchstabe kommt vor Z?"

        for wrong in ("u", "i", "l"):
            remember_error(
                state,
                "spelling",
                wrong,
                "Y",
                context=context,
            )

        first = start_error_practice(
            state,
            "spelling",
        )

        self.assertIn(
            context,
            first,
        )
        self.assertNotIn(
            "Erinnerst du dich an die Situation?",
            first,
        )

        step_one = handle_error_practice(
            "2",
            state,
        )
        self.assertIn(
            "Sag die richtige Antwort",
            step_one,
        )

        finished = handle_error_practice(
            "Y",
            state,
        )

        self.assertIn(
            "Diesen Fehler hast du jetzt geübt",
            finished,
        )
        self.assertNotIn(
            "Jetzt noch eine",
            finished,
        )
        self.assertFalse(
            state.get(
                "error_practice_active",
                False,
            )
        )


    def test_completed_greeting_error_does_not_repeat_on_reopen(self):
        state = {}

        remember_error(
            state,
            "vocabulary",
            "ich will spielen",
            "Guten Tag",
            context=(
                "Es ist tagsüber. "
                "Was sagst du zur Begrüßung?"
            ),
        )

        remember_error(
            state,
            "vocabulary",
            "Guten Morgen",
            "Guten Abend",
            context=(
                "Es ist Abend. "
                "Was sagst du zur Begrüßung?"
            ),
        )

        first = start_error_practice(
            state,
            "vocabulary",
        )

        self.assertIsInstance(first, str)
        self.assertIn("Guten Abend", first)
        self.assertNotIn("ich will spielen", first)

        step_one = handle_error_practice(
            "2",
            state,
        )
        self.assertIn(
            "Sag die richtige Antwort",
            step_one,
        )

        finished = handle_error_practice(
            "Guten Abend",
            state,
        )
        self.assertIn(
            "Diesen Fehler hast du jetzt geübt",
            finished,
        )
        self.assertNotIn(
            "Genau richtig:",
            finished,
        )

        item = get_error_item(
            "vocabulary",
            state,
        )

        self.assertFalse(
            item.get(
                "needs_practice",
                True,
            )
        )

        bad_example = next(
            example
            for example in item.get("examples", [])
            if example.get("wrong") == "ich will spielen"
        )
        self.assertTrue(
            bad_example.get(
                "ignored",
                False,
            )
        )

        refresh_error_reviews(
            state,
        )

        self.assertNotIn(
            "vocabulary",
            get_due_error_reviews(
                state,
            ),
        )

        reopened = start_error_practice(
            state,
            "vocabulary",
        )

        self.assertIsNone(
            reopened
        )


    def test_stale_category_flag_with_only_ignored_pending_example_is_not_due(self):
        state = {
            "error_memory": {
                "vocabulary": {
                    "count": 1,
                    "needs_practice": True,
                    "mastered": False,
                    "examples": [
                        {
                            "wrong": "ich will spielen",
                            "correct": "Guten Tag",
                            "needs_practice": True,
                            "mastered": False,
                            "ignored": True,
                        }
                    ],
                }
            }
        }

        self.assertFalse(
            is_error_due_for_review(
                state,
                "vocabulary",
            )
        )

        item = get_error_item(
            "vocabulary",
            state,
        )

        self.assertFalse(
            item.get(
                "needs_practice",
                True,
            )
        )

    def test_teacher_brain_never_recommends_listening_or_writing(self):
        state = {}

        for _ in range(8):
            recommendation = build_adaptive_recommendation(state)
            self.assertIsInstance(recommendation, dict)
            self.assertNotIn(
                recommendation.get("activity"),
                {"listening", "writing"},
            )

            activity = recommendation.get("activity")
            update_skill(state, activity, 100)
            mark_activity_completed(
                state,
                activity,
                detail="Test",
                score=100,
            )

    def test_old_listening_or_writing_task_is_not_resumed(self):
        for activity_type in ("listening", "writing"):
            state = {
                "nele3_upgrade": {
                    "active_task": {
                        "type": activity_type,
                        "prompt": "Alte Aufgabe",
                    }
                }
            }

            handled, answer, meta = handle_upgrade_message(
                "Hallo",
                state,
            )

            self.assertFalse(handled)
            self.assertIsNone(answer)
            self.assertEqual(meta, {})
            self.assertIsNone(
                get_active_task(state)
            )

    def test_explicit_listening_and_writing_commands_stay_disabled(self):
        cases = [
            ("Hören üben", "listening"),
            ("Schreiben üben", "writing"),
        ]

        for message, activity in cases:
            state = {}

            handled, answer, meta = handle_upgrade_message(
                message,
                state,
            )

            self.assertTrue(handled)
            self.assertTrue(answer)
            self.assertEqual(
                meta.get("activity_disabled"),
                activity,
            )
            self.assertIsNone(
                get_active_task(state)
            )


    def test_teacher_brain_does_not_repeat_just_completed_skill(self):
        state = {}

        update_skill(state, "writing", 40)
        update_skill(state, "writing", 100)
        mark_activity_completed(
            state,
            "writing",
            detail="Verspätung melden",
            score=100,
        )

        recommendation = build_adaptive_recommendation(state)

        self.assertIsInstance(recommendation, dict)
        self.assertNotEqual(
            recommendation.get("activity"),
            "writing",
        )


if __name__ == "__main__":
    unittest.main()
