import unittest

from brain.logic.free_conversation import (
    generate_free_conversation_reply,
    generate_free_welcome,
)


def _turn(state, message):
    reply, meta = generate_free_conversation_reply(message, state)
    return reply, meta


class GeneratedTests(unittest.TestCase):
    def test_beginner_work_dialog_keeps_context(self):
        state = {}
        generate_free_welcome(state)

        # Force the exact question being regression-tested.
        free = state["free_conversation"]
        free["last_question"] = "Was machst du bei der Arbeit?"

        reply, _ = _turn(state, "Kochen")

        self.assertTrue("Ich koche." in reply)
        self.assertTrue("Ich arbeite Kochen" not in reply)
        self.assertTrue("Arbeit" in reply)


    def test_beginner_work_time_dialog_understands_bis_two(self):
        state = {"free_conversation": {
        "last_question": "Bis wann arbeitest du heute?",
        "recent_questions": ["Bis wann arbeitest du heute?"],
        "conversation_facts": {},
        }}

        reply, _ = _turn(state, "Bis 2")

        self.assertTrue("Ich arbeite bis 2 Uhr" in reply)
        self.assertTrue("danach" in reply.lower())


    def test_beginner_food_dialog_understands_pizza(self):
        state = {"free_conversation": {
        "last_question": "Was isst du gern?",
        "recent_questions": ["Was isst du gern?"],
        "conversation_facts": {},
        }}

        reply, _ = _turn(state, "Pizza")

        self.assertTrue("Pizza" in reply)
        self.assertTrue("Isst du das oft?" in reply)


    def test_beginner_hobby_dialog_understands_company(self):
        state = {"free_conversation": {
        "last_question": "Machst du das lieber allein oder mit jemandem?",
        "recent_questions": ["Machst du das lieber allein oder mit jemandem?"],
        "conversation_facts": {},
        }}

        reply, _ = _turn(state, "Mit meinem Mann")

        self.assertTrue("zusammen" in reply.lower())


    def test_weather_yes_does_not_repeat_same_question(self):
        state = {"free_conversation": {
        "last_question": "Magst du das Wetter heute?",
        "recent_questions": ["Magst du das Wetter heute?"],
        "conversation_facts": {"weather": "warm"},
        }}

        reply, _ = _turn(state, "Ja")

        self.assertTrue("Magst du das Wetter heute?" not in reply)
        self.assertTrue("bei diesem Wetter" in reply)


    def test_typo_sonnig_gets_gentle_help_and_stays_weather(self):
        state = {"free_conversation": {
        "last_question": "Wie ist das Wetter bei dir?",
        "recent_questions": ["Wie ist das Wetter bei dir?"],
        "conversation_facts": {},
        }}

        reply, _ = _turn(state, "Sonn8g")

        self.assertTrue("sonnig" in reply)
        self.assertTrue("warm" in reply.lower())


    def test_free_conversation_multi_turn_regression(self):
        state = {"free_conversation": {
        "last_question": "Was machst du heute?",
        "recent_questions": ["Was machst du heute?"],
        "conversation_facts": {},
        }}

        first, _ = _turn(state, "Arbeit")
        self.assertTrue("arbeit" in first.lower())

        # Simulate a natural work follow-up explicitly; this isolates learner
        # interpretation from randomized/open fallback wording.
        state["free_conversation"]["last_question"] = "Was machst du bei der Arbeit?"
        second, _ = _turn(state, "Kochen")
        self.assertTrue("Ich koche." in second)
        self.assertTrue("Ich arbeite Kochen" not in second)

        state["free_conversation"]["last_question"] = "Was isst du gern?"
        third, _ = _turn(state, "Pizza")
        self.assertTrue("Pizza" in third)
        self.assertTrue(third != second)

    def test_real_work_sequence_does_not_restart_after_kochen_yes(self):
        state = {"free_conversation": {
        "last_question": "Was machst du gerade?",
        "recent_questions": ["Was machst du gerade?"],
        "conversation_facts": {},
        }}

        first, _ = _turn(state, "Arbeit")
        self.assertTrue("Wann fängst du an?" in first)

        second, _ = _turn(state, "8")
        self.assertTrue("Ich fange um 8 Uhr an." in second)
        self.assertTrue("Was machst du bei der Arbeit?" in second)

        third, _ = _turn(state, "kochen")
        self.assertTrue("Ich koche." in third)
        self.assertTrue("Kochst du jeden Tag bei der Arbeit?" in third)

        fourth, _ = _turn(state, "ja")
        self.assertTrue("Wann fängst du" not in fourth)
        self.assertTrue("Was machst du bei der Arbeit?" not in fourth)
        self.assertTrue("Was kochst du gern bei der Arbeit?" in fourth)

    def test_work_cooking_food_chain_keeps_context(self):
        state = {"free_conversation": {
            "last_question": "Was kochst du gern bei der Arbeit?",
            "recent_questions": ["Was kochst du gern bei der Arbeit?"],
            "conversation_facts": {"work_activity": "kochen"},
        }}

        first, _ = _turn(state, "suppe")
        self.assertTrue("Ich koche gern Suppe." in first)
        self.assertTrue("etwas anderes" in first)

        second, _ = _turn(state, "pizza")
        self.assertTrue("Ich koche auch gern Pizza." in second)
        self.assertTrue("Wann fängst du" not in second)
        self.assertTrue("Was machst du bei der Arbeit?" not in second)



    def test_free_conversation_exposes_vocabulary_engine_context(self):
        state = {"free_conversation": {
            "last_question": "Wie ist das Wetter bei dir?",
            "recent_questions": ["Wie ist das Wetter bei dir?"],
            "conversation_facts": {},
        }}
        reply, meta = _turn(state, "warm")
        self.assertTrue(reply)
        self.assertIn("vocabulary", meta)
        self.assertTrue(meta["vocabulary"]["memory_aware"])
        self.assertEqual(meta["vocabulary"]["topic"], "alltag" if meta["vocabulary"]["topic"] == "alltag" else meta["vocabulary"]["topic"])
        self.assertIn("suggestions", meta["vocabulary"])

    def test_work_food_chain_keeps_vocabulary_context(self):
        state = {"free_conversation": {
            "last_question": "Was kochst du gern bei der Arbeit?",
            "recent_questions": ["Was kochst du gern bei der Arbeit?"],
            "last_topic": "work",
            "conversation_facts": {"work_activity": "kochen"},
        }}
        reply, meta = _turn(state, "suppe")
        self.assertIn("Ich koche gern Suppe.", reply)
        self.assertIn("vocabulary", meta)
        self.assertTrue(meta["vocabulary"]["memory_aware"])
        self.assertEqual(meta["vocabulary"]["topic"], "arbeit")


    def test_cooking_chain_suppe_pizza_nudeln_keeps_context(self):
        state = {"free_conversation": {
            "last_question": "Was kochst du gern bei der Arbeit?",
            "recent_questions": ["Was kochst du gern bei der Arbeit?"],
            "last_topic": "work",
            "conversation_facts": {"work_activity": "kochen"},
        }}

        first, _ = _turn(state, "suppe")
        self.assertIn("Ich koche gern Suppe.", first)

        second, _ = _turn(state, "pizza")
        self.assertIn("Ich koche auch gern Pizza.", second)
        self.assertIn("Was kochst du am liebsten?", second)

        third, _ = _turn(state, "nudeln")
        self.assertIn("Am liebsten koche ich Nudeln.", third)
        self.assertNotIn("Was machst du bei der Arbeit?", third)
        self.assertNotIn("Wie ist dein Tag heute?", third)


    def test_cooking_yes_after_suppe_stays_in_context(self):
        state = {"free_conversation": {
            "last_question": "Was kochst du gern bei der Arbeit?",
            "recent_questions": ["Was kochst du gern bei der Arbeit?"],
            "last_topic": "work",
            "conversation_facts": {"work_activity": "kochen"},
        }}

        first, _ = _turn(state, "suppe")
        self.assertIn("Kochst du auch gern etwas anderes?", first)

        second, _ = _turn(state, "ja")
        self.assertIn("Was kochst du noch gern?", second)
        self.assertNotIn("Was machst du bei der Arbeit?", second)
        self.assertNotIn("Wie ist dein Tag heute?", second)

        third, _ = _turn(state, "pizza")
        self.assertIn("Ich koche auch gern Pizza.", third)
        self.assertIn("Was kochst du am liebsten?", third)

        fourth, _ = _turn(state, "nudeln")
        self.assertIn("Am liebsten koche ich Nudeln.", fourth)
        self.assertNotIn("Was machst du bei der Arbeit?", fourth)


    def test_conversation_state_v2_tracks_cooking_context(self):
        state = {}
        generate_free_welcome(state)
        free = state["free_conversation"]
        free["last_topic"] = "work"
        free["last_question"] = "Was kochst du gern bei der Arbeit?"
        free.setdefault("conversation_facts", {})["work_activity"] = "kochen"

        reply, meta = _turn(state, "suppe")
        cs = meta["conversation_state"]
        self.assertEqual(cs["version"], 2)
        self.assertEqual(cs["topic"], "work")
        self.assertEqual(cs["subtopic"], "kochen")
        self.assertEqual(cs["last_question"], "Kochst du auch gern etwas anderes?")
        self.assertEqual(cs["expected_answer"], "yes_no")
        self.assertEqual(cs["activity"], "kochen")
        self.assertEqual(cs["food"], "Suppe")
        self.assertEqual(cs["conversation_goal"], "über Arbeit und Kochen sprechen")
        self.assertEqual(cs["support_level"], "A1")
        self.assertGreaterEqual(cs["turn_number"], 1)

    def test_conversation_state_v2_updates_after_yes(self):
        state = {}
        generate_free_welcome(state)
        free = state["free_conversation"]
        free["last_topic"] = "work"
        free["last_question"] = "Was kochst du gern bei der Arbeit?"
        free.setdefault("conversation_facts", {})["work_activity"] = "kochen"

        _turn(state, "suppe")
        reply, meta = _turn(state, "ja")
        cs = meta["conversation_state"]
        self.assertEqual(cs["topic"], "work")
        self.assertEqual(cs["subtopic"], "kochen")
        self.assertEqual(cs["last_question"], "Was kochst du noch gern?")
        self.assertEqual(cs["expected_answer"], "open")
        self.assertEqual(cs["food"], "Suppe")
        self.assertNotIn("Was machst du bei der Arbeit?", reply)


    def test_topic_manager_keeps_work_cooking_for_short_answers(self):
        state = {}
        generate_free_welcome(state)
        free = state["free_conversation"]
        free["last_topic"] = "work"
        free["last_question"] = "Was kochst du gern bei der Arbeit?"
        free.setdefault("conversation_facts", {})["work_activity"] = "kochen"
        # Seed the central state as it would exist after the preceding work turn.
        from brain.logic.conversation_state import sync_conversation_state
        sync_conversation_state(state, topic="work", last_question=free["last_question"], level="A1.1")

        _, meta = _turn(state, "suppe")
        self.assertEqual(meta["topic"], "work")
        self.assertEqual(meta["conversation_state"]["subtopic"], "kochen")
        self.assertEqual(meta["topic_manager"]["topic"], "work")

        _, meta = _turn(state, "ja")
        self.assertEqual(meta["topic_manager"]["topic"], "work")
        self.assertEqual(meta["topic_manager"]["subtopic"], "kochen")

        _, meta = _turn(state, "pizza")
        self.assertEqual(meta["topic_manager"]["topic"], "work")
        self.assertEqual(meta["conversation_state"]["subtopic"], "kochen")

    def test_topic_manager_allows_clear_topic_change(self):
        state = {}
        generate_free_welcome(state)
        free = state["free_conversation"]
        free["last_topic"] = "work"
        free["last_question"] = "Was machst du bei der Arbeit?"
        free.setdefault("conversation_facts", {})["work_activity"] = "kochen"
        from brain.logic.conversation_state import sync_conversation_state
        sync_conversation_state(state, topic="work", last_question=free["last_question"], level="A1.1")

        _, meta = _turn(state, "Das Wetter ist warm")
        self.assertEqual(meta["topic"], "weather")
        self.assertEqual(meta["topic_manager"]["topic"], "weather")


    def test_error_engine_gently_recasts_clear_a1_error(self):
        state = {}
        generate_free_welcome(state)
        reply, meta = _turn(state, "ich arbeiten")
        engine = meta["error_engine"]
        self.assertTrue(engine["detected"])
        self.assertEqual(engine["error"]["type"], "verb")
        self.assertEqual(engine["error"]["correct"], "Ich arbeite.")
        self.assertEqual(engine["decision"]["style"], "natural_recast")
        self.assertIn("Ich arbeite.", reply)

    def test_error_engine_does_not_correct_valid_short_answer(self):
        state = {}
        generate_free_welcome(state)
        _, meta = _turn(state, "gut")
        engine = meta["error_engine"]
        self.assertFalse(engine["detected"])
        self.assertFalse(engine["decision"]["correct"])

    def test_error_engine_records_in_student_error_memory(self):
        state = {}
        generate_free_welcome(state)
        _turn(state, "ich arbeiten")
        from brain.memory.error_memory import get_error_summary
        summary = get_error_summary(state, "verb")
        self.assertIsNotNone(summary)
        self.assertGreaterEqual(summary["count"], 1)
        self.assertEqual(summary["last_wrong"], "ich arbeiten")
        self.assertEqual(summary["last_correct"], "Ich arbeite.")


    def test_error_engine_centralizes_social_and_weather_errors(self):
        from brain.logic.error_engine import detect_error
        cases = {
            "wie heißen du": "Wie heißt du?",
            "wie geht du": "Wie geht es dir?",
            "wie wetter heute": "Wie ist das Wetter heute?",
            "sonn8g": "Es ist sonnig.",
            "gute morgen": "Guten Morgen!",
            "es ist regen": "Es regnet.",
            "ich gut": "Mir geht es gut.",
            "ich heißen Moni": "Ich heiße moni.",
        }
        for wrong, correct in cases.items():
            with self.subTest(wrong=wrong):
                error = detect_error(wrong)
                self.assertIsNotNone(error)
                self.assertEqual(error["correct"].lower(), correct.lower())

    def test_error_engine_keeps_correct_social_language_unflagged(self):
        from brain.logic.error_engine import detect_error
        for text in ("Wie heißt du?", "Wie geht es dir?", "Guten Morgen!", "Es regnet.", "Mir geht es gut."):
            with self.subTest(text=text):
                self.assertIsNone(detect_error(text))


    def test_error_engine_v2_uses_natural_recast_first(self):
        from brain.logic.error_engine import process_error
        state = {}
        result = process_error("ich arbeiten", state, support_level=1)
        self.assertEqual(result["decision"]["style"], "natural_recast")
        self.assertEqual(result["recast"], "Ah, Ich arbeite.")

    def test_error_engine_v2_uses_explicit_model_with_more_support(self):
        from brain.logic.error_engine import process_error
        state = {}
        result = process_error("ich arbeiten", state, support_level=2)
        self.assertEqual(result["decision"]["style"], "explicit_model")
        self.assertEqual(result["recast"], "Du kannst sagen: „Ich arbeite.“")

    def test_error_engine_v2_requests_repeat_for_recurring_error(self):
        from brain.logic.error_engine import process_error
        state = {}
        process_error("ich arbeiten", state, support_level=1)
        process_error("ich arbeiten", state, support_level=1)
        third = process_error("ich arbeiten", state, support_level=1)
        self.assertEqual(third["decision"]["style"], "repeat_request")
        self.assertIn("Sag es bitte noch einmal.", third["recast"])

    def test_error_engine_v2_does_not_interrupt_without_clear_error(self):
        from brain.logic.error_engine import process_error
        state = {}
        result = process_error("Ich arbeite heute.", state, support_level=1)
        self.assertFalse(result["decision"]["correct"])
        self.assertEqual(result["decision"]["style"], "none")
        self.assertIsNone(result["recast"])


    def test_teacher_engine_models_full_sentence_for_kochen(self):
        from brain.logic.teacher_engine import choose_teacher_action
        action = choose_teacher_action(
            "kochen",
            conversation_state={"topic": "work", "subtopic": "kochen", "expected_answer": "open"},
            topic_manager={"topic": "work", "subtopic": "kochen"},
            error_result={"decision": {"correct": False}},
            support_level=1,
        )
        self.assertEqual(action["action"], "model_full_sentence")
        self.assertEqual(action["model"], "Ich koche.")

    def test_teacher_engine_uses_error_engine_for_ich_kochen_suppe(self):
        from brain.logic.error_engine import process_error
        from brain.logic.teacher_engine import choose_teacher_action
        state = {}
        error = process_error("ich kochen Suppe", state, support_level=2)
        action = choose_teacher_action(
            "ich kochen Suppe",
            conversation_state={"topic": "work", "subtopic": "kochen", "expected_answer": "open"},
            topic_manager={"topic": "work", "subtopic": "kochen"},
            error_result=error,
            support_level=2,
        )
        self.assertTrue(error["detected"])
        self.assertEqual(error["error"]["correct"], "Ich koche Suppe.")
        self.assertEqual(action["action"], "correct_and_continue")

    def test_teacher_engine_does_not_treat_valid_yes_as_error(self):
        from brain.logic.teacher_engine import choose_teacher_action
        action = choose_teacher_action(
            "ja",
            conversation_state={"topic": "work", "subtopic": "kochen", "expected_answer": "yes_no"},
            error_result={"decision": {"correct": False}},
            support_level=1,
        )
        self.assertEqual(action["action"], "continue_conversation")
        self.assertEqual(action["reason"], "valid_expected_short_answer")

    def test_teacher_engine_repeat_request_pauses_next_question(self):
        from brain.logic.teacher_engine import choose_teacher_action
        action = choose_teacher_action(
            "ich arbeiten",
            conversation_state={"topic": "work", "expected_answer": "open"},
            error_result={
                "error": {"correct": "Ich arbeite."},
                "decision": {"correct": True, "style": "repeat_request"},
            },
            support_level=1,
        )
        self.assertEqual(action["action"], "ask_repeat")
        self.assertFalse(action["continue_conversation"])


    def test_teacher_engine_reviews_problem_vocabulary_first(self):
        from brain.logic.teacher_engine import choose_teacher_action
        action = choose_teacher_action(
            "Ich arbeite heute.",
            conversation_state={"topic": "work", "expected_answer": "open"},
            error_result={"decision": {"correct": False}},
            support_level=1,
            independent_turns=2,
            vocabulary_context={
                "suggestions": [{"word": "kollege", "level": "A1"}],
                "memory": {"kollege": {"seen": 2, "correct": 0, "mistakes": 1, "needs_review": True}},
            },
        )
        self.assertEqual(action["action"], "review_vocabulary")
        self.assertEqual(action["word"], "kollege")

    def test_teacher_engine_can_introduce_unseen_topic_word(self):
        from brain.logic.teacher_engine import choose_teacher_action
        action = choose_teacher_action(
            "Ich arbeite heute.",
            conversation_state={"topic": "work", "expected_answer": "open"},
            error_result={"decision": {"correct": False}},
            support_level=1,
            independent_turns=2,
            vocabulary_context={
                "suggestions": [{"word": "pause", "level": "A1"}],
                "memory": {},
            },
        )
        self.assertEqual(action["action"], "introduce_vocabulary")
        self.assertEqual(action["word"], "pause")

    def test_teacher_engine_does_not_push_new_word_during_struggle(self):
        from brain.logic.teacher_engine import choose_teacher_action
        action = choose_teacher_action(
            "?",
            conversation_state={"topic": "work", "expected_answer": "open"},
            error_result={"decision": {"correct": False}},
            support_level=3,
            struggle=True,
            vocabulary_context={
                "suggestions": [{"word": "kollege", "level": "A1"}],
                "memory": {},
            },
        )
        self.assertEqual(action["action"], "simplify_next_question")


    def test_learner_model_summarizes_vocabulary_and_autonomy(self):
        from brain.logic.learner_model import build_learner_model
        state = {
            "student_progress": {"current_level": "A1.1"},
            "free_conversation": {"independent_turns": 4, "struggle_turns": 0, "support_level": 1},
            "vocabulary_memory": {
                "arbeit": {"seen": 4, "correct": 4, "mistakes": 0, "correct_streak": 3, "needs_review": False},
                "kollege": {"seen": 2, "correct": 0, "mistakes": 1, "correct_streak": 0, "needs_review": True},
            },
        }
        model = build_learner_model(state)
        self.assertEqual(model["autonomy"], "independent")
        self.assertIn("arbeit", model["vocabulary"]["mastered"])
        self.assertIn("kollege", model["vocabulary"]["review_due"])
        self.assertIn("conversation_independence", model["strengths"])

    def test_learner_model_detects_need_for_support(self):
        from brain.logic.learner_model import build_learner_model
        state = {
            "student_progress": {"current_level": "A1.1"},
            "free_conversation": {"independent_turns": 0, "struggle_turns": 2, "support_level": 3},
        }
        model = build_learner_model(state)
        self.assertEqual(model["autonomy"], "needs_support")
        self.assertIn("conversation_support", model["weaknesses"])

    def test_teacher_engine_uses_learner_model_support(self):
        from brain.logic.teacher_engine import choose_teacher_action
        action = choose_teacher_action(
            "Ich arbeite heute.",
            conversation_state={"topic": "work", "expected_answer": "open"},
            error_result={"decision": {"correct": False}},
            support_level=1,
            independent_turns=4,
            learner_model={"autonomy": "needs_support", "adaptive_support": 3},
        )
        self.assertEqual(action["action"], "simplify_next_question")

    def test_teacher_engine_can_advance_independent_learner(self):
        from brain.logic.teacher_engine import choose_teacher_action
        action = choose_teacher_action(
            "Ich arbeite heute.",
            conversation_state={"topic": "work", "expected_answer": "open"},
            error_result={"decision": {"correct": False}},
            support_level=1,
            independent_turns=1,
            learner_model={"autonomy": "independent", "adaptive_support": 1},
        )
        self.assertEqual(action["action"], "advance")


    def test_teacher_policy_repeat_error_has_top_priority(self):
        from brain.logic.teacher_policy import choose_next_best_learning_action
        policy = choose_next_best_learning_action(
            teacher_action={"action": "introduce_vocabulary", "word": "Pause"},
            learner_model={"autonomy": "independent", "course_level": "A1.1"},
            error_result={"decision": {"style": "repeat_request"}},
        )
        self.assertEqual(policy["action"], "REPEAT_ERROR")
        self.assertEqual(policy["priority"], 100)
        self.assertFalse(policy["continue_conversation"])

    def test_teacher_policy_support_overrides_enrichment(self):
        from brain.logic.teacher_policy import choose_next_best_learning_action
        policy = choose_next_best_learning_action(
            teacher_action={"action": "introduce_vocabulary", "word": "Kollege"},
            learner_model={"autonomy": "needs_support", "adaptive_support": 3, "course_level": "A1.1"},
        )
        self.assertEqual(policy["action"], "SIMPLIFY")
        self.assertEqual(policy["reason"], "learner_model_needs_support")

    def test_teacher_policy_preserves_vocabulary_review(self):
        from brain.logic.teacher_policy import choose_next_best_learning_action
        policy = choose_next_best_learning_action(
            teacher_action={"action": "review_vocabulary", "word": "Kollege", "reason": "vocabulary_needs_review"},
            learner_model={"autonomy": "developing", "course_level": "A1.1"},
            conversation_state={"topic": "work"},
        )
        self.assertEqual(policy["action"], "REVIEW_WORD")
        self.assertEqual(policy["target_word"], "Kollege")
        self.assertEqual(policy["topic"], "work")

    def test_teacher_policy_allows_advance_for_independent_learner(self):
        from brain.logic.teacher_policy import choose_next_best_learning_action
        policy = choose_next_best_learning_action(
            teacher_action={"action": "advance", "reason": "learner_is_independent"},
            learner_model={"autonomy": "independent", "course_level": "A1.1"},
        )
        self.assertEqual(policy["action"], "ADVANCE")
        self.assertEqual(policy["priority"], 30)
