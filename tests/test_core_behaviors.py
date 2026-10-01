from brain.logic.free_conversation import generate_free_conversation_reply
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
from brain.logic.welcome import generate_welcome_reply, build_returning_user_greeting
from brain.logic.response_engine import (
    _shorten_session_restart_prompt,
    get_last_lesson_recap_data,
)
from brain.nele3_upgrade.state import get_active_task
from brain.logic.lesson_loader import (
    get_available_lesson_numbers,
)
from brain.logic.onboarding import (
    extract_name_sentence,
    extract_learning_goal_sentence,
    get_short_answer_value,
    get_onboarding_retry,
)
from brain.logic.lesson_teaching import (
    is_morning_greeting,
    is_day_greeting,
    is_evening_greeting,
    is_relevant_greeting_mistake,
    handle_alphabet_section,
    handle_introduction_section,
    complete_active_section,
    register_course_success,
    remember_lesson_mistake,
)
from brain.logic.error_practice import (
    is_relevant_error_example,
    start_error_practice,
    handle_error_practice,
)
from brain.logic.wellbeing_feedback import (
    analyze_wellbeing_response,
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


    def test_mastering_first_course_section_does_not_master_later_sections(self):
        from brain.memory.lesson_progress import get_next_incomplete_section

        state = {
            "conversation_mode": "course",
            "lesson_progress": {
                "lessons": {
                    "A1:1": {
                        "level": "A1",
                        "lesson": 1,
                        "sections": [
                            "Wir begrüßen uns",
                            "Ich stelle mich vor",
                            "Das deutsche Alphabet",
                        ],
                        "completed_sections": [],
                        "current_section": "Wir begrüßen uns",
                        "completed": False,
                    }
                }
            },
            "learning_progress_v1": {
                "version": 1,
                "skills": {
                    "course:a1:1:wir_begrüßen_uns": {
                        "status": "mastered",
                    },
                },
            },
        }

        self.assertEqual(
            get_next_incomplete_section(state, "A1", 1),
            "Ich stelle mich vor",
        )


    def test_legacy_course_section_cannot_complete_before_shared_mastery(self):
        state = {
            "conversation_mode": "course",
            "lesson_teaching_active": True,
            "lesson_teaching_section": "Wir begrüßen uns",
            "lesson_teaching_step": 6,
            "learning_progress_v1": {
                "version": 1,
                "skills": {
                    "course:a1:1:wir_begrüßen_uns": {
                        "status": "practicing",
                    },
                },
            },
        }
        with patch(
            "brain.logic.lesson_teaching.get_lesson_context_for_section",
            return_value=("A1", 1),
        ), patch(
            "brain.logic.lesson_teaching.mark_section_completed"
        ) as mark_completed:
            next_section = complete_active_section(state)

        self.assertEqual(next_section, "Wir begrüßen uns")
        self.assertEqual(state["lesson_teaching_step"], 1)
        mark_completed.assert_not_called()

    def test_legacy_course_success_and_error_feed_same_mastery_skill(self):
        state = {
            "conversation_mode": "course",
            "lesson_teaching_section": "Wir begrüßen uns",
            "lesson_teaching_step": 1,
        }
        with patch(
            "brain.logic.lesson_teaching.get_lesson_context_for_section",
            return_value=("A1", 1),
        ), patch(
            "brain.logic.lesson_teaching.remember_error",
            return_value=True,
        ), patch(
            "brain.logic.lesson_teaching.record_mistake_today"
        ):
            register_course_success(state)
            remember_lesson_mistake(
                state,
                "vocabulary",
                "Guten Abend",
                "Guten Morgen",
            )

        item = state["learning_progress_v1"]["skills"]["course:a1:1:wir_begrüßen_uns"]
        self.assertEqual(item["successes"], 1)
        self.assertEqual(item["not_yet"], 1)
        self.assertEqual(item["last_result"], "NOT_YET")

    def test_legacy_assisted_success_is_not_independent_mastery_evidence(self):
        state = {
            "conversation_mode": "course",
            "lesson_teaching_section": "Wir begrüßen uns",
            "lesson_teaching_step": 1,
            "course_mastery_assistance_used": True,
        }
        with patch(
            "brain.logic.lesson_teaching.get_lesson_context_for_section",
            return_value=("A1", 1),
        ):
            register_course_success(state)

        item = state["learning_progress_v1"]["skills"]["course:a1:1:wir_begrüßen_uns"]
        self.assertEqual(item["successes"], 1)
        self.assertTrue(item["requires_independent_confirmation"])
        self.assertEqual(item["independent_confirmations"], 0)
        self.assertNotEqual(item["status"], "mastered")
        self.assertFalse(state["course_mastery_assistance_used"])

    def test_legacy_section_error_requires_fresh_full_pass_before_mastery(self):
        state = {
            "conversation_mode": "course",
            "lesson_teaching_active": True,
            "lesson_teaching_section": "Das deutsche Alphabet",
            "lesson_teaching_step": 4,
            "lesson_progress": {
                "lessons": {
                    "A1:1": {
                        "level": "A1",
                        "lesson": 1,
                        "sections": ["Das deutsche Alphabet"],
                        "completed_sections": [],
                        "current_section": "Das deutsche Alphabet",
                        "completed": False,
                    }
                }
            },
        }
        with patch(
            "brain.logic.lesson_teaching.get_lesson_context_for_section",
            return_value=("A1", 1),
        ), patch(
            "brain.logic.lesson_teaching.remember_error",
            return_value=True,
        ), patch(
            "brain.logic.lesson_teaching.record_mistake_today",
        ):
            handle_alphabet_section("A O U", state)
            handle_alphabet_section("Ä Ö Ü", state)
            handle_alphabet_section("Eszett", state)
            reply = handle_alphabet_section("M O N I", state)

        item = state["learning_progress_v1"]["skills"][
            "course:a1:1:das_deutsche_alphabet"
        ]
        self.assertNotEqual(item["status"], "mastered")
        self.assertEqual(item["independent_confirmations"], 0)
        self.assertEqual(state["lesson_teaching_step"], 1)
        self.assertIn("Das deutsche Alphabet", reply)
        self.assertFalse(state["course_mastery_section_assistance_used"])


    def test_legacy_clean_success_can_confirm_mastery_after_guided_practice(self):
        state = {
            "conversation_mode": "course",
            "lesson_teaching_section": "Wir begrüßen uns",
            "lesson_teaching_step": 1,
            "course_mastery_assistance_used": True,
        }
        with patch(
            "brain.logic.lesson_teaching.get_lesson_context_for_section",
            return_value=("A1", 1),
        ):
            register_course_success(state)  # guided practice
            register_course_success(state)  # clean practice, still not final
            register_course_success(state, final_step=True)  # final independent proof

        item = state["learning_progress_v1"]["skills"]["course:a1:1:wir_begrüßen_uns"]
        self.assertEqual(item["successes"], 3)
        self.assertEqual(item["independent_confirmations"], 1)
        self.assertEqual(item["status"], "mastered")

    def test_legacy_intermediate_successes_cannot_master_before_final_step(self):
        state = {
            "conversation_mode": "course",
            "lesson_teaching_section": "Wir begrüßen uns",
            "lesson_teaching_step": 1,
        }
        with patch(
            "brain.logic.lesson_teaching.get_lesson_context_for_section",
            return_value=("A1", 1),
        ):
            for _ in range(5):
                progress = register_course_success(state)
            self.assertNotEqual(progress["status"], "mastered")
            self.assertEqual(progress["independent_confirmations"], 0)

            progress = register_course_success(state, final_step=True)

        self.assertEqual(progress["status"], "mastered")
        self.assertEqual(progress["independent_confirmations"], 1)

    def test_a11_alphabet_wrong_answer_uses_shared_teacher_engine_and_stays_on_step(self):
        state = {
            "conversation_mode": "course",
            "lesson_teaching_active": True,
            "lesson_teaching_section": "Das deutsche Alphabet",
            "lesson_teaching_step": 4,
        }
        with patch(
            "brain.logic.lesson_teaching.get_lesson_context_for_section",
            return_value=("A1", 1),
        ), patch(
            "brain.logic.lesson_teaching.remember_error",
            return_value=True,
        ), patch(
            "brain.logic.lesson_teaching.record_mistake_today",
        ):
            reply = handle_alphabet_section("A O U", state)

        self.assertIn("Ä, Ö und Ü", reply)
        self.assertEqual(state["lesson_teaching_step"], 4)
        self.assertEqual(state["course_teacher_action"]["action"], "correct_and_retry")
        self.assertEqual(state["course_teacher_action"]["model"], "Ä, Ö und Ü")
        item = state["learning_progress_v1"]["skills"][
            "course:a1:1:das_deutsche_alphabet"
        ]
        self.assertEqual(item["last_result"], "NOT_YET")
        self.assertTrue(item["requires_independent_confirmation"])
        self.assertTrue(state["course_mastery_assistance_used"])

        retry = handle_alphabet_section("Ä Ö Ü", state)
        self.assertIn("ß", retry)
        self.assertEqual(state["lesson_teaching_step"], 5)
        self.assertEqual(item["independent_confirmations"], 0)
        self.assertNotEqual(item["status"], "mastered")


    def test_a11_alphabet_eszett_wrong_answer_uses_shared_teacher_engine(self):
        state = {
            "conversation_mode": "course",
            "lesson_teaching_active": True,
            "lesson_teaching_section": "Das deutsche Alphabet",
            "lesson_teaching_step": 5,
        }
        with patch(
            "brain.logic.lesson_teaching.get_lesson_context_for_section",
            return_value=("A1", 1),
        ), patch(
            "brain.logic.lesson_teaching.remember_error",
            return_value=True,
        ), patch(
            "brain.logic.lesson_teaching.record_mistake_today",
        ):
            reply = handle_alphabet_section("Doppel-s", state)

        self.assertIn("Eszett", reply)
        self.assertEqual(state["lesson_teaching_step"], 5)
        self.assertEqual(state["course_teacher_action"]["action"], "correct_and_retry")
        self.assertEqual(state["course_teacher_action"]["model"], "Eszett")


    def test_lesson1_successes_fade_global_speaking_help(self):
        intro_state = {
            "lesson_teaching_step": 1,
            "course_speaking_support_level": 3,
        }
        handle_introduction_section("Guten Morgen", intro_state)
        self.assertEqual(intro_state["course_speaking_support_level"], 2)

        alphabet_state = {
            "lesson_teaching_step": 1,
            "course_speaking_support_level": 3,
        }
        handle_alphabet_section("A", alphabet_state)
        self.assertEqual(alphabet_state["course_speaking_support_level"], 2)

        handle_alphabet_section("B", alphabet_state)
        self.assertEqual(alphabet_state["course_speaking_support_level"], 1)

        handle_alphabet_section("M", alphabet_state)
        self.assertEqual(alphabet_state["course_speaking_support_level"], 0)

    def test_first_a1_welcome_is_short(self):
        state = {
            "onboarding_completed": False,
            "onboarding_step": 0,
            "user_facts": {},
        }

        with patch(
            "brain.logic.welcome.get_conversation_state",
            return_value=state,
        ), patch(
            "brain.logic.welcome.save_conversation_state"
        ):
            reply = generate_welcome_reply("test-new-user")

        self.assertEqual(
            reply,
            "Hallo! Ich bin Nele. Wie heißt du?",
        )
        self.assertNotIn(
            "persönliche Deutschtrainerin",
            reply,
        )
        self.assertNotIn(
            "Schön, dich kennenzulernen",
            reply,
        )

    def test_returning_welcome_keeps_course_start_gate_after_onboarding(self):
        state = {
            "onboarding_completed": True,
            "onboarding_step": 0,
            "last_question": "start_after_onboarding",
            "user_facts": {"name": "Moni"},
            "name": "Moni",
        }

        with patch(
            "brain.logic.welcome.get_conversation_state",
            return_value=state,
        ), patch(
            "brain.logic.welcome.save_conversation_state"
        ):
            reply = generate_welcome_reply("test-course-start-gate")

        self.assertEqual(reply, "Hallo Moni! Bist du bereit?")
        self.assertEqual(state["last_question"], "start_after_onboarding")
    def test_resumed_first_a1_welcome_stays_short(self):
        state = {
            "onboarding_completed": False,
            "onboarding_step": 1,
            "user_facts": {},
        }

        with patch(
            "brain.logic.welcome.get_conversation_state",
            return_value=state,
        ), patch(
            "brain.logic.welcome.save_conversation_state"
        ):
            reply = generate_welcome_reply("test-resumed-user")

        self.assertEqual(
            reply,
            "Hallo! Ich bin Nele. Wie heißt du?",
        )

    def test_onboarding_natural_origin_fragment_keeps_only_country(self):
        self.assertEqual(get_short_answer_value("komme aus Polen", 2), "Polen")
        retry = get_onboarding_retry(2, "komme aus Polen")
        self.assertIn("Ich komme aus Polen", retry)
        self.assertNotIn("Ich komme aus Komme", retry)

    def test_onboarding_rejects_multiword_text_as_origin_shortcut(self):
        self.assertEqual(get_short_answer_value("Wie ist das Wetter", 2), "")
        self.assertEqual(get_short_answer_value("Aus Frankreich kommst du", 2), "")
        retry = get_onboarding_retry(2, "Wie ist das Wetter")
        self.assertNotIn("Ich komme aus Wie", retry)

    def test_onboarding_name_moves_to_short_origin_question(self):
        from brain.logic.onboarding import handle_onboarding_answer

        state = {
            "onboarding_completed": False,
            "onboarding_step": 1,
            "user_facts": {},
        }

        reply = handle_onboarding_answer(
            "Ich heiße Moni",
            state,
        )

        self.assertEqual(
            reply,
            "Hallo Moni! Woher kommst du?",
        )
        self.assertEqual(
            state["onboarding_step"],
            2,
        )

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

    def test_dialogue_correction_preserves_apples_and_quantity(self):
        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "dialogue",
                    "title": "In der Bäckerei",
                    "prompt": "Ich bin die Verkäuferin: Guten Morgen. Was möchten Sie?",
                    "keywords": ["ich möchte", "bitte"],
                    "model_answer": "Ich möchte zwei Brötchen, bitte.",
                }
            }
        }

        result = answer_active_task(
            state,
            "Guten Morgen ich hatte gern ein kilo apfeln",
        )

        self.assertFalse(result["completed"])
        self.assertIn("ein Kilo Äpfel", result["reply"])
        self.assertIn("hätte gern", result["reply"])
        self.assertNotIn("Brötchen", result["reply"])

    def test_work_german_accepts_natural_towel_response(self):
        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "work_german",
                    "title": "Handtuch bringen",
                    "prompt": "Gast: Entschuldigung, ich brauche noch ein Handtuch.",
                    "keywords": ["natürlich", "handtuch"],
                    "model_answer": "Natürlich. Ich bringe Ihnen sofort ein frisches Handtuch.",
                }
            }
        }

        result = answer_active_task(state, "Natürlich, ich bringe ein Tuch.")

        self.assertTrue(result["completed"])
        self.assertIn("passt", result["reply"])

    def test_work_german_accepts_natural_towel_response_without_natuerlich(self):
        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "work_german",
                    "title": "Handtuch bringen",
                    "prompt": "Gast: Entschuldigung, ich brauche noch ein Handtuch.",
                    "keywords": ["natürlich", "handtuch"],
                    "model_answer": "Natürlich. Ich bringe Ihnen sofort ein frisches Handtuch.",
                }
            }
        }

        for answer in (
            "Ich bringe Ihnen ein Tuch.",
            "Ich gebe Ihnen ein Handtuch.",
        ):
            state["nele3_upgrade"]["active_task"] = {
                "type": "work_german",
                "title": "Handtuch bringen",
                "prompt": "Gast: Entschuldigung, ich brauche noch ein Handtuch.",
                "keywords": ["natürlich", "handtuch"],
                "model_answer": "Natürlich. Ich bringe Ihnen sofort ein frisches Handtuch.",
            }
            result = answer_active_task(state, answer)
            self.assertTrue(result["completed"], answer)

    def test_dialogue_accepts_natural_product_request_without_model_product(self):
        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "dialogue",
                    "title": "In der Bäckerei",
                    "prompt": "Ich bin die Verkäuferin: Guten Morgen. Was möchten Sie?",
                    "keywords": ["ich möchte", "bitte"],
                    "model_answer": "Ich möchte zwei Brötchen, bitte.",
                }
            }
        }

        result = answer_active_task(state, "Ich möchte Äpfel, bitte.")

        self.assertTrue(result["completed"])
        self.assertNotIn("Brötchen", result["reply"])

    def test_dialogue_accepts_short_contextual_product_choice(self):
        for answer in ("Apfel", "Äpfel", "zwei Äpfel"):
            state = {
                "nele3_upgrade": {
                    "active_task": {
                        "type": "dialogue",
                        "title": "In der Bäckerei",
                        "prompt": "Ich bin die Verkäuferin: Guten Morgen. Was möchten Sie?",
                        "keywords": ["ich möchte", "bitte"],
                        "model_answer": "Ich möchte zwei Brötchen, bitte.",
                    }
                }
            }
            result = answer_active_task(state, answer)
            self.assertTrue(result["completed"], answer)
            self.assertNotIn("Brötchen", result["reply"])

    def test_dialogue_correction_never_replaces_concrete_answer_with_model(self):
        state = {
            "nele3_upgrade": {
                "active_task": {
                    "type": "dialogue",
                    "title": "In der Bäckerei",
                    "prompt": "Ich bin die Verkäuferin: Guten Morgen. Was möchten Sie?",
                    "keywords": ["ich möchte", "bitte"],
                    "model_answer": "Ich möchte zwei Brötchen, bitte.",
                }
            }
        }

        result = answer_active_task(
            state,
            "Ich möchte ein kilo Apfeln, bitt",
        )

        self.assertFalse(result["completed"])
        self.assertNotIn("Brötchen", result["reply"])
        self.assertIn("Äpfel", result["reply"])

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

    def test_a1_lesson_2_is_ready(self):
        available = get_available_lesson_numbers("A1")
        self.assertIn(2, available)

    def test_a1_lesson_2_is_beginner_friendly(self):
        from brain.logic.lesson_loader import load_lesson_flow
        from brain.logic.generic_lesson_engine import answer_matches_step

        flow = load_lesson_flow("A1", 2)
        sections = flow["sections"]

        origin = sections["Woher kommen Sie?"]
        self.assertIn("Beispiel:", origin["intro"])
        first = origin["steps"][0]
        self.assertIn("Ich komme aus", first["prompt"])
        self.assertTrue(answer_matches_step("Polen", first, {}))
        self.assertTrue(answer_matches_step("aus Polen", first, {}))

        numbers = sections["Zahlen 1–20"]["steps"]
        self.assertFalse(answer_matches_step("1 2 3 4 5", numbers[0], {}))
        self.assertFalse(answer_matches_step("6 7 8 9 10", numbers[1], {}))
        self.assertFalse(answer_matches_step("11 12 13 14 15", numbers[2], {}))
        self.assertFalse(answer_matches_step("16 17 18 19 20", numbers[3], {}))
        self.assertTrue(answer_matches_step("eins zwei drei vier fünf", numbers[0], {}))
        self.assertTrue(answer_matches_step("sechs sieben acht neun zehn", numbers[1], {}))
        self.assertTrue(answer_matches_step("elf zwölf dreizehn vierzehn fünfzehn", numbers[2], {}))
        self.assertTrue(answer_matches_step("sechzehn siebzehn achtzehn neunzehn zwanzig", numbers[3], {}))
        self.assertEqual(numbers[0]["success"], "Sehr gut.")
        self.assertFalse(numbers[1]["prompt"].startswith("Sehr gut."))

    def test_a1_lesson_2_teaches_source_page_topics(self):
        from brain.logic.lesson_loader import load_lesson_flow

        flow = load_lesson_flow("A1", 2)
        self.assertIsInstance(flow, dict)
        sections = flow.get("sections", {})
        self.assertEqual(
            list(sections.keys()),
            [
                "Woher kommen Sie?",
                "Das Verb kommen",
                "Zahlen 1–20",
            ],
        )

        origin_steps = sections["Woher kommen Sie?"]["steps"]
        self.assertTrue(
            any(
                step.get("correct_answer") == "Ich komme aus der Schweiz."
                for step in origin_steps
            )
        )
        self.assertTrue(
            any(
                step.get("correct_answer") == "Ich komme aus den USA."
                for step in origin_steps
            )
        )

        kommen_steps = sections["Das Verb kommen"]["steps"]
        self.assertEqual(len(kommen_steps), 6)

        number_steps = sections["Zahlen 1–20"]["steps"]
        self.assertEqual(len(number_steps), 4)

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


    def test_onboarding_accepts_natural_ich_bin_name(self):
        self.assertEqual(
            extract_name_sentence("Ich bin Moni"),
            "Moni",
        )
        self.assertEqual(
            extract_name_sentence("Ich heiße Moni"),
            "Moni",
        )


    def test_wellbeing_common_a1_answers_are_understood(self):
        cases = {
            "gut": ("good", "Das freut mich!"),
            "prima": ("very_good", "Super, das freut mich!"),
            "schlecht": (
                "bad",
                "Das tut mir leid. Dann machen wir es heute lieber etwas leichter.",
            ),
            "nicht schlecht": ("quite_good", "Schön zu hören!"),
            "müde": (
                "tired",
                "Verstehe. Dann machen wir heute etwas Kurzes und Leichtes.",
            ),
        }

        for answer, (expected_type, expected_reaction) in cases.items():
            with self.subTest(answer=answer):
                result = analyze_wellbeing_response(answer)
                self.assertTrue(result["recognized"])
                self.assertEqual(result["type"], expected_type)
                self.assertEqual(result["reaction"], expected_reaction)

    def test_wellbeing_gently_corrects_beginner_grammar(self):
        result = analyze_wellbeing_response("mir geht gut")
        self.assertTrue(result["recognized"])
        self.assertEqual(result["type"], "good")
        self.assertEqual(result["corrected_message"], "Mir geht es gut.")
        self.assertIn("Fast!", result["feedback"])
        self.assertIn("Mir geht es gut", result["feedback"])

    def test_onboarding_accepts_all_basic_name_forms(self):
        self.assertEqual(extract_name_sentence("Ich heiße Moni"), "Moni")
        self.assertEqual(extract_name_sentence("Mein Name ist Moni"), "Moni")
        self.assertEqual(extract_name_sentence("Ich bin Moni"), "Moni")

    def test_onboarding_rejects_wrong_ich_heissen_form(self):
        self.assertEqual(extract_name_sentence("Ich heißen Moni"), "")


    def test_onboarding_gently_corrects_wrong_ich_heissen_form(self):
        from brain.logic.onboarding import get_onboarding_retry

        reply = get_onboarding_retry(1, "Ich heißen Moni")

        self.assertIn("Fast! Richtig:", reply)
        self.assertIn("Ich heiße Moni.", reply)
        self.assertIn("Sag es bitte noch einmal.", reply)


    def test_onboarding_gently_corrects_missing_aus(self):
        from brain.logic.onboarding import get_onboarding_retry

        reply = get_onboarding_retry(2, "Ich komme Polen")

        self.assertIn("Fast! Richtig:", reply)
        self.assertIn("Ich komme aus Polen.", reply)
        self.assertIn("Sag es bitte noch einmal.", reply)

    def test_onboarding_gently_corrects_wrong_wohnen_form(self):
        from brain.logic.onboarding import get_onboarding_retry

        reply = get_onboarding_retry(3, "Ich wohnen in Heidelberg")

        self.assertIn("Fast! Richtig:", reply)
        self.assertIn("Ich wohne in Heidelberg.", reply)
        self.assertIn("Sag es bitte noch einmal.", reply)

    def test_wrong_morning_greetings_do_not_advance(self):
        from brain.logic.lesson_teaching import handle_greeting_section

        for answer in ("Gute Morgen", "Guten Nacht"):
            with self.subTest(answer=answer):
                state = {
                    "lesson_teaching_active": True,
                    "lesson_teaching_section": "Wir begrüßen uns",
                    "lesson_teaching_step": 1,
                }

                first_reply = handle_greeting_section(answer, state)

                self.assertIn("Begrüßung am Morgen", first_reply)
                self.assertNotIn("Guten Morgen", first_reply)
                self.assertEqual(state["lesson_teaching_step"], 1)

                second_reply = handle_greeting_section(answer, state)

                self.assertIn("Guten Morgen", second_reply)
                self.assertEqual(state["lesson_teaching_step"], 1)

                final_reply = handle_greeting_section("Guten Morgen", state)

                self.assertIn("Was sagst du?", final_reply)
                self.assertEqual(state["lesson_teaching_step"], 2)


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
            "Sag jetzt:",
            step_one,
        )

        transfer = handle_error_practice(
            "Y",
            state,
        )
        self.assertIn(
            "ohne Auswahl",
            transfer,
        )
        self.assertTrue(
            state.get("error_practice_active", False)
        )

        finished = handle_error_practice(
            "Y",
            state,
        )

        self.assertIn(
            "Genau!",
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
            "Sag jetzt:",
            step_one,
        )

        transfer = handle_error_practice(
            "Guten Abend",
            state,
        )
        self.assertIn(
            "ohne Auswahl",
            transfer,
        )

        finished = handle_error_practice(
            "Guten Abend",
            state,
        )
        self.assertIn(
            "Genau!",
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




    def test_error_practice_requires_independent_transfer_before_mastery(self):
        state = {}
        context = "Du möchtest jemanden informell nach dem Namen fragen. Was sagst du?"
        remember_error(
            state,
            "grammar",
            "Wie heißen du?",
            "Wie heißt du?",
            context=context,
        )

        start_error_practice(state, "grammar")
        model_prompt = handle_error_practice("2", state)
        self.assertIn("Sag jetzt:", model_prompt)

        transfer_prompt = handle_error_practice("Wie heißt du?", state)
        self.assertIn("ohne Auswahl", transfer_prompt)
        self.assertEqual(state.get("error_practice_step"), 3)
        self.assertTrue(state.get("error_practice_active", False))

        hint = handle_error_practice("weiß nicht", state)
        self.assertIn("Fang so an", hint)
        self.assertTrue(state.get("error_practice_active", False))

        retry_model = handle_error_practice("noch nicht", state)
        self.assertIn("Ich helfe dir noch einmal", retry_model)
        self.assertEqual(state.get("error_practice_step"), 2)


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


def _free_reply(message, state=None, last_question=""):
    state = state or {"student_progress": {"current_level": "A1.1"}}
    free = state.setdefault("free_conversation", {})
    free["last_question"] = last_question
    reply, _ = generate_free_conversation_reply(message, state)
    return reply, state


def test_free_speaking_greetings_and_gentle_corrections():
    reply, _ = _free_reply("Guten Morgen")
    assert "Guten Morgen!" in reply
    assert "Wie geht es dir" in reply

    reply, _ = _free_reply("Gute Morgen")
    assert "Guten Morgen" in reply
    assert "noch einmal" in reply

    reply, _ = _free_reply("Auf Wiedersehen")
    assert reply == "Auf Wiedersehen!"


def test_free_speaking_name_questions_and_errors():
    reply, _ = _free_reply("Wie heißt du?")
    assert "Ich heiße Nele" in reply
    assert "wie heißt du" in reply

    reply, _ = _free_reply("Wie heißen du?")
    assert "Wie heißt du?" in reply
    assert "Ich heiße Nele" in reply

    reply, _ = _free_reply("Ich heißen Moni")
    assert "Ich heiße Moni" in reply


def test_free_speaking_wellbeing_questions_answers_and_errors():
    reply, _ = _free_reply("Wie geht es dir?")
    assert "Mir geht es gut" in reply
    assert "Und dir?" in reply

    reply, _ = _free_reply("Wie geht du?")
    assert "Wie geht es dir?" in reply

    reply, _ = _free_reply("schlecht", last_question="Wie geht es dir heute?")
    assert "Mir geht es schlecht" in reply


def test_free_speaking_weather_questions_answers_and_errors():
    reply, _ = _free_reply("Wie ist das Wetter heute?")
    assert "Wie ist das Wetter bei dir?" in reply

    reply, _ = _free_reply("sonnig", last_question="Wie ist das Wetter bei dir?")
    assert "sonniges Wetter" in reply

    reply, _ = _free_reply("Es ist Regen", last_question="Wie ist das Wetter bei dir?")
    assert "Es regnet" in reply

    reply, _ = _free_reply("Es sonnig", last_question="Wie ist das Wetter bei dir?")
    assert "Es ist sonnig" in reply

    reply, _ = _free_reply("Es schneit", last_question="Wie ist das Wetter bei dir?")
    assert "Schnee" in reply


def test_free_speaking_continuous_a1_social_conversation():
    state = {"student_progress": {"current_level": "A1.1"}}

    reply, _ = generate_free_conversation_reply("Guten Morgen", state)
    assert "Guten Morgen!" in reply
    assert "Wie geht es dir" in reply

    reply, _ = generate_free_conversation_reply("Mir geht gut", state)
    assert "Mir geht es gut" in reply

    reply, _ = generate_free_conversation_reply("Wie geht es dir?", state)
    assert "Mir geht es gut" in reply
    assert "Und dir?" in reply

    reply, _ = generate_free_conversation_reply("gut", state)
    assert reply

    reply, _ = generate_free_conversation_reply("Wie ist das Wetter heute?", state)
    assert "Wie ist das Wetter bei dir?" in reply

    reply, _ = generate_free_conversation_reply("Es sonnig", state)
    assert "Es ist sonnig" in reply

    reply, _ = generate_free_conversation_reply("Wie heißen du?", state)
    assert "Wie heißt du?" in reply
    assert "Ich heiße Nele" in reply

    reply, _ = generate_free_conversation_reply("Ich heißen Moni", state)
    assert "Ich heiße Moni" in reply
    assert "Woher kommst du?" in reply

    reply, _ = generate_free_conversation_reply("Tschüss", state)
    assert reply == "Tschüss!"


def test_free_speaking_everyday_a1_topics_and_errors():
    state = {"student_progress": {"current_level": "A1.1"}}

    reply, _ = generate_free_conversation_reply("Was machst du heute?", state)
    assert "was machst du heute" in reply.lower()
    reply, _ = generate_free_conversation_reply("arbeiten", state)
    assert "Wann fängst du an" in reply

    reply, _ = generate_free_conversation_reply("Ich arbeiten heute", state)
    assert "Ich arbeite heute" in reply

    reply, _ = generate_free_conversation_reply("Was machst du gern in deiner Freizeit?", state)
    assert "Freizeit" in reply
    reply, _ = generate_free_conversation_reply("lesen", state)
    assert "Was liest du gern" in reply

    reply, _ = generate_free_conversation_reply("Ich fahren Rad", state)
    assert "Ich fahre Rad" in reply

    reply, _ = generate_free_conversation_reply("Gehst du gern einkaufen?", state)
    assert "Was kaufst du gern" in reply
    reply, _ = generate_free_conversation_reply("Ich kaufen Schuhe", state)
    assert "Ich kaufe Schuhe" in reply

    reply, _ = generate_free_conversation_reply("Machst du gern Urlaub?", state)
    assert "Wo machst du gern Urlaub" in reply
    reply, _ = generate_free_conversation_reply("Ich machen Urlaub in Italien", state)
    assert "Ich mache Urlaub in italien" in reply.lower()

    reply, _ = generate_free_conversation_reply("Meer", state)
    assert "Meer" in reply

def test_course_welcome_rotates_without_repeating_last_variant():
    state = {}
    first = build_returning_user_greeting(state, "Moni")
    first_key = state["course_last_welcome_variant"]
    second = build_returning_user_greeting(state, "Moni")
    second_key = state["course_last_welcome_variant"]

    assert first != second
    assert first_key != second_key
    assert "Moni" in first
    assert "Moni" in second
    assert ("Wie geht" in first) or ("Wie geht's" in first)
    assert ("Wie geht" in second) or ("Wie geht's" in second)

