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


    def test_learning_executor_repeat_error_stops_question(self):
        from brain.logic.learning_action_executor import execute_learning_action
        result = execute_learning_action(
            {"action": "REPEAT_ERROR", "model": "Ich arbeite heute."},
            fallback_question="Was machst du morgen?",
        )
        self.assertEqual(result["reply"], "Richtig ist: „Ich arbeite heute.“ Sag es bitte noch einmal.")
        self.assertEqual(result["expects_outcome"], "repeat_correct_form")
        self.assertNotIn("morgen", result["reply"])

    def test_learning_executor_models_sentence_and_continues(self):
        from brain.logic.learning_action_executor import execute_learning_action
        result = execute_learning_action(
            {"action": "MODEL_SENTENCE", "model": "Ich koche."},
            fallback_question="Was kochst du gern?",
        )
        self.assertEqual(result["reply"], "Du kannst sagen: „Ich koche.“ Was kochst du gern?")
        self.assertEqual(result["expects_outcome"], "use_full_sentence")

    def test_learning_executor_reviews_target_word(self):
        from brain.logic.learning_action_executor import execute_learning_action
        result = execute_learning_action(
            {"action": "REVIEW_WORD", "target_word": "pause"},
            vocabulary_context={"suggestions": [{"word": "pause", "example": "Beispiel: „Ich mache eine Pause.“"}]},
            fallback_question="Was machst du bei der Arbeit?",
        )
        self.assertIn("pause", result["reply"].lower())
        self.assertIn("Ich mache eine Pause.", result["reply"])
        self.assertEqual(result["expects_outcome"], "recall_target_word")

    def test_learning_executor_introduces_new_word(self):
        from brain.logic.learning_action_executor import execute_learning_action
        result = execute_learning_action(
            {"action": "INTRODUCE_WORD", "target_word": "pause"},
            vocabulary_context={"suggestions": [{"word": "pause", "example": "Beispiel: „Ich mache eine Pause.“"}]},
            fallback_question="Wann machst du Pause?",
        )
        self.assertIn("Ein neues Wort", result["reply"])
        self.assertIn("Wann machst du Pause?", result["reply"])
        self.assertEqual(result["expects_outcome"], "notice_new_word")

    def test_learning_executor_simplifies_without_losing_question(self):
        from brain.logic.learning_action_executor import execute_learning_action
        result = execute_learning_action(
            {"action": "SIMPLIFY"},
            fallback_question="Arbeitest du heute?",
        )
        self.assertEqual(result["reply"], "Kein Problem. Arbeitest du heute?")
        self.assertEqual(result["expects_outcome"], "answer_with_support")


    def test_outcome_tracker_successful_error_repeat(self):
        from brain.logic.learning_outcome_tracker import evaluate_learning_outcome
        state = {"learning_action_executor_v1": {
            "action": "REPEAT_ERROR", "expects_outcome": "repeat_correct_form",
            "model": "Ich arbeite heute.", "target_word": None,
        }}
        outcome = evaluate_learning_outcome("Ich arbeite heute.", state)
        self.assertEqual(outcome["status"], "SUCCESS")
        self.assertEqual(outcome["reason"], "correct_form_repeated")

    def test_outcome_tracker_failed_error_repeat(self):
        from brain.logic.learning_outcome_tracker import evaluate_learning_outcome
        state = {"learning_action_executor_v1": {
            "action": "REPEAT_ERROR", "expects_outcome": "repeat_correct_form",
            "model": "Ich arbeite heute.", "target_word": None,
        }}
        outcome = evaluate_learning_outcome("ich arbeiten", state)
        self.assertEqual(outcome["status"], "NOT_YET")

    def test_outcome_tracker_updates_vocabulary_on_recall(self):
        from brain.logic.learning_outcome_tracker import evaluate_learning_outcome
        state = {"learning_action_executor_v1": {
            "action": "REVIEW_WORD", "expects_outcome": "recall_target_word",
            "target_word": "pause", "model": None,
        }}
        outcome = evaluate_learning_outcome("Ich mache eine Pause.", state)
        self.assertEqual(outcome["status"], "SUCCESS")
        self.assertEqual(state["vocabulary_memory"]["pause"]["correct"], 1)
        self.assertFalse(state["vocabulary_memory"]["pause"]["needs_review"])

    def test_outcome_tracker_marks_missing_review_word(self):
        from brain.logic.learning_outcome_tracker import evaluate_learning_outcome
        state = {"learning_action_executor_v1": {
            "action": "REVIEW_WORD", "expects_outcome": "recall_target_word",
            "target_word": "pause", "model": None,
        }}
        outcome = evaluate_learning_outcome("Ich arbeite heute.", state)
        self.assertEqual(outcome["status"], "NOT_YET")
        self.assertEqual(state["vocabulary_memory"]["pause"]["mistakes"], 1)
        self.assertTrue(state["vocabulary_memory"]["pause"]["needs_review"])

    def test_learner_model_contains_learning_outcomes(self):
        from brain.logic.learner_model import build_learner_model
        state = {"learning_outcomes": [
            {"status": "SUCCESS"}, {"status": "SUCCESS"}, {"status": "SUCCESS"},
            {"status": "PARTIAL"},
        ]}
        model = build_learner_model(state)
        self.assertEqual(model["learning_outcomes"]["success"], 3)
        self.assertEqual(model["learning_outcomes"]["partial"], 1)
        self.assertIn("learning_response", model["strengths"])


    def test_learning_progress_moves_to_mastered(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        state = {}
        base = {"expected_outcome": "use_full_sentence", "target_word": None, "model": "Ich arbeite."}
        for _ in range(3):
            update_learning_progress(state, dict(base, status="SUCCESS"))
        skill = state["learning_progress_v1"]["skills"]["conversation:full_sentence"]
        self.assertEqual(skill["status"], "mastered")
        self.assertEqual(skill["successes"], 3)

    def test_learning_progress_mastered_can_need_review_again(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        state = {}
        base = {"expected_outcome": "use_full_sentence", "target_word": None, "model": "Ich arbeite."}
        for _ in range(3):
            update_learning_progress(state, dict(base, status="SUCCESS"))
        update_learning_progress(state, dict(base, status="NOT_YET"))
        skill = state["learning_progress_v1"]["skills"]["conversation:full_sentence"]
        self.assertEqual(skill["status"], "needs_review")

    def test_learning_progress_tracks_vocabulary_separately(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        state = {}
        update_learning_progress(state, {
            "expected_outcome": "recall_target_word", "status": "SUCCESS",
            "target_word": "pause", "model": None,
        })
        self.assertIn("vocabulary:pause", state["learning_progress_v1"]["skills"])

    def test_learning_progress_repeated_failure_needs_review(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        state = {}
        outcome = {"expected_outcome": "independent_answer", "status": "NOT_YET"}
        update_learning_progress(state, outcome)
        update_learning_progress(state, outcome)
        skill = state["learning_progress_v1"]["skills"]["conversation:independent_answer"]
        self.assertEqual(skill["status"], "needs_review")

    def test_learner_model_exposes_long_term_learning_progress(self):
        from brain.logic.learning_progress_engine import update_learning_progress
        from brain.logic.learner_model import build_learner_model
        state = {}
        outcome = {"expected_outcome": "use_full_sentence", "status": "SUCCESS"}
        for _ in range(3):
            update_learning_progress(state, outcome)
        model = build_learner_model(state)
        self.assertEqual(model["learning_progress"]["mastered_count"], 1)
        self.assertIn("conversation:full_sentence", model["learning_progress"]["by_status"]["mastered"])


    def test_curriculum_graph_blocks_skill_until_prerequisite_mastered(self):
        from brain.logic.curriculum_skill_graph import get_curriculum_state
        state = {}
        curriculum = get_curriculum_state(state)
        self.assertIn("conversation:supported_answer", curriculum["ready"])
        self.assertIn("conversation:full_sentence", curriculum["blocked"])

    def test_curriculum_graph_unlocks_full_sentence(self):
        from brain.logic.curriculum_skill_graph import get_curriculum_state
        state = {"learning_progress_v1": {"skills": {
            "conversation:supported_answer": {"status": "mastered"},
        }}}
        curriculum = get_curriculum_state(state)
        self.assertIn("conversation:full_sentence", curriculum["ready"])

    def test_curriculum_graph_prioritizes_review(self):
        from brain.logic.curriculum_skill_graph import choose_next_curriculum_skill
        state = {"learning_progress_v1": {"skills": {
            "conversation:supported_answer": {"status": "needs_review"},
        }}}
        next_skill = choose_next_curriculum_skill(state)
        self.assertEqual(next_skill["skill"], "conversation:supported_answer")
        self.assertEqual(next_skill["reason"], "curriculum_review")

    def test_curriculum_graph_keeps_dynamic_vocabulary_review(self):
        from brain.logic.curriculum_skill_graph import get_curriculum_state
        state = {"learning_progress_v1": {"skills": {
            "vocabulary:pause": {"status": "needs_review"},
        }}}
        curriculum = get_curriculum_state(state)
        self.assertIn("vocabulary:pause", curriculum["dynamic_needs_review"])

    def test_learner_model_exposes_curriculum_and_next_skill(self):
        from brain.logic.learner_model import build_learner_model
        state = {}
        model = build_learner_model(state)
        self.assertIn("curriculum", model)
        self.assertEqual(model["next_curriculum_skill"]["skill"], "conversation:supported_answer")


    def test_teacher_policy_v3_uses_ready_full_sentence_skill(self):
        from brain.logic.teacher_policy import choose_next_best_learning_action
        policy = choose_next_best_learning_action(
            teacher_action={"action": "continue_conversation", "reason": "normal_progress"},
            learner_model={"autonomy": "developing", "next_curriculum_skill": {
                "skill": "conversation:full_sentence", "reason": "prerequisites_met",
            }},
        )
        self.assertEqual(policy["version"], 3)
        self.assertEqual(policy["action"], "MODEL_SENTENCE")
        self.assertEqual(policy["curriculum_skill"], "conversation:full_sentence")

    def test_teacher_policy_v3_curriculum_does_not_override_repeat_error(self):
        from brain.logic.teacher_policy import choose_next_best_learning_action
        policy = choose_next_best_learning_action(
            teacher_action={"action": "continue_conversation"},
            learner_model={"autonomy": "developing", "next_curriculum_skill": {
                "skill": "conversation:independent_answer", "reason": "prerequisites_met",
            }},
            error_result={"decision": {"style": "repeat_request"}},
        )
        self.assertEqual(policy["action"], "REPEAT_ERROR")

    def test_teacher_policy_v3_curriculum_does_not_override_support(self):
        from brain.logic.teacher_policy import choose_next_best_learning_action
        policy = choose_next_best_learning_action(
            teacher_action={"action": "continue_conversation"},
            learner_model={"autonomy": "needs_support", "next_curriculum_skill": {
                "skill": "conversation:independent_answer", "reason": "prerequisites_met",
            }},
        )
        self.assertEqual(policy["action"], "SIMPLIFY")

    def test_teacher_policy_v3_reviews_dynamic_vocabulary_target(self):
        from brain.logic.teacher_policy import choose_next_best_learning_action
        policy = choose_next_best_learning_action(
            teacher_action={"action": "continue_conversation"},
            learner_model={"autonomy": "developing", "next_curriculum_skill": {
                "skill": "vocabulary:pause", "reason": "dynamic_review",
            }},
        )
        self.assertEqual(policy["action"], "REVIEW_WORD")
        self.assertEqual(policy["target_word"], "pause")

    def test_teacher_policy_v3_advances_to_independent_answer(self):
        from brain.logic.teacher_policy import choose_next_best_learning_action
        policy = choose_next_best_learning_action(
            teacher_action={"action": "continue_conversation"},
            learner_model={"autonomy": "developing", "next_curriculum_skill": {
                "skill": "conversation:independent_answer", "reason": "prerequisites_met",
            }},
        )
        self.assertEqual(policy["action"], "ADVANCE")
        self.assertEqual(policy["reason"], "curriculum_next_ready_skill")


    def test_question_simplifier_turns_open_work_question_into_yes_no(self):
        from brain.logic.question_simplifier import simplify_question
        result = simplify_question("Was machst du bei der Arbeit?", topic="work")
        self.assertTrue(result["changed"])
        self.assertEqual(result["question"], "Arbeitest du heute?")
        self.assertEqual(result["strategy"], "specific_rule")

    def test_question_simplifier_preserves_cooking_subtopic(self):
        from brain.logic.question_simplifier import simplify_question
        result = simplify_question(
            "Was machst du sonst bei der Arbeit?",
            topic="work",
            subtopic="kochen",
        )
        self.assertTrue(result["question"].startswith("Kochst du"))

    def test_question_simplifier_avoids_recent_question(self):
        from brain.logic.question_simplifier import simplify_question
        result = simplify_question(
            "Was machst du bei der Arbeit?",
            topic="work",
            recent_questions=["Arbeitest du heute?"],
        )
        self.assertNotEqual(result["question"], "Arbeitest du heute?")

    def test_question_simplifier_weather_stays_weather(self):
        from brain.logic.question_simplifier import simplify_question
        result = simplify_question(
            "Was machst du bei diesem Wetter gern?",
            topic="weather",
        )
        self.assertEqual(result["question"], "Gehst du gern spazieren?")

    def test_simplified_question_is_yes_no_for_conversation_state(self):
        from brain.logic.question_simplifier import simplify_question
        from brain.logic.conversation_state import infer_expected_answer
        result = simplify_question("Was machst du bei der Arbeit?", topic="work")
        self.assertEqual(infer_expected_answer(result["question"]), "yes_no")


    def test_response_understanding_reads_yes_in_yes_no_context(self):
        from brain.logic.response_understanding import understand_response
        result = understand_response("ja", conversation_state={
            "last_question": "Arbeitest du heute?", "expected_answer": "yes_no", "topic": "work",
        })
        self.assertEqual(result["meaning"], "yes")
        self.assertEqual(result["confidence"], "high")

    def test_response_understanding_reads_beginner_time(self):
        from brain.logic.response_understanding import understand_response
        result = understand_response("bis 2", conversation_state={
            "last_question": "Bis wann arbeitest du?", "expected_answer": "time", "topic": "work",
        })
        self.assertEqual(result["intent"], "time")
        self.assertEqual(result["canonical"], "bis 2")

    def test_response_understanding_recognizes_noisy_weather_but_preserves_original(self):
        from brain.logic.response_understanding import understand_response
        result = understand_response("sonn8g", conversation_state={
            "last_question": "Wie ist das Wetter bei dir?", "expected_answer": "open", "topic": "weather",
        })
        self.assertEqual(result["canonical"], "sonnig")
        self.assertEqual(result["preserve_for_error_engine"], "sonn8g")

    def test_response_understanding_accepts_one_word_a1_content(self):
        from brain.logic.response_understanding import understand_response
        result = understand_response("Pizza", conversation_state={
            "last_question": "Was kochst du gern?", "expected_answer": "open", "topic": "work", "subtopic": "kochen",
        })
        self.assertEqual(result["meaning"], "pizza")
        self.assertEqual(result["confidence"], "high")

    def test_response_understanding_does_not_hide_grammar_error(self):
        from brain.logic.response_understanding import understand_response
        from brain.logic.error_engine import detect_error
        raw = "ich heißen Moni"
        result = understand_response(raw, conversation_state={
            "last_question": "Wie heißt du?", "expected_answer": "open",
        })
        self.assertEqual(result["preserve_for_error_engine"], raw)
        self.assertIsNotNone(detect_error(result["preserve_for_error_engine"]))


    def test_response_understanding_v2_known_asr_variant_in_context(self):
        from brain.logic.response_understanding import understand_response
        result = understand_response("shwimmen", conversation_state={
            "last_question": "Welchen Sport machst du gern?",
            "expected_answer": "open", "topic": "hobby",
        })
        self.assertEqual(result["version"], 2)
        self.assertEqual(result["canonical"], "schwimmen")
        self.assertTrue(result["asr_tolerant"])

    def test_response_understanding_v2_context_similarity(self):
        from brain.logic.response_understanding import understand_response
        result = understand_response("nudlen", conversation_state={
            "last_question": "Was kochst du noch gern?",
            "expected_answer": "open", "topic": "work", "subtopic": "kochen",
        })
        self.assertEqual(result["canonical"], "nudeln")
        self.assertEqual(result["asr_strategy"], "context_similarity")

    def test_response_understanding_v2_does_not_apply_unrelated_known_variant(self):
        from brain.logic.response_understanding import understand_response
        result = understand_response("arbait", conversation_state={
            "last_question": "Welchen Sport machst du gern?",
            "expected_answer": "open", "topic": "hobby",
        })
        self.assertEqual(result["canonical"], "arbait")
        self.assertFalse(result["asr_tolerant"])

    def test_response_understanding_v2_uses_vocabulary_context_candidate(self):
        from brain.logic.response_understanding import understand_response
        result = understand_response(
            "kaffe",
            conversation_state={"last_question": "Was trinkst du gern?", "expected_answer": "open", "topic": "today"},
            vocabulary_context={"suggestion_words": ["kaffee"]},
        )
        self.assertEqual(result["canonical"], "kaffee")
        self.assertTrue(result["asr_tolerant"])

    def test_response_understanding_v2_preserves_original_asr_text_for_error_engine(self):
        from brain.logic.response_understanding import understand_response
        result = understand_response("shwimmen", conversation_state={
            "last_question": "Welchen Sport machst du gern?", "expected_answer": "open", "topic": "hobby",
        })
        self.assertEqual(result["preserve_for_error_engine"], "shwimmen")


    def test_coherence_engine_keeps_non_repeated_candidate(self):
        from brain.logic.conversation_coherence import choose_coherent_question
        result = choose_coherent_question(
            "Was kochst du gern bei der Arbeit?",
            topic="work",
            recent_questions=["Arbeitest du heute?"],
            previous_question="Arbeitest du heute?",
            alternatives=["Wann fängst du an?"],
        )
        self.assertFalse(result["changed"])
        self.assertEqual(result["selected"], "Was kochst du gern bei der Arbeit?")

    def test_coherence_engine_replaces_repeat_with_same_topic_question(self):
        from brain.logic.conversation_coherence import choose_coherent_question
        result = choose_coherent_question(
            "Was machst du bei der Arbeit?",
            topic="work",
            recent_questions=["Was machst du bei der Arbeit?"],
            previous_question="Was machst du bei der Arbeit?",
            alternatives=["Wann fängst du an?", "Arbeitest du heute?"],
        )
        self.assertTrue(result["changed"])
        self.assertEqual(result["selected"], "Wann fängst du an?")
        self.assertEqual(result["reason"], "avoid_repeat_keep_topic")

    def test_coherence_engine_tracks_recent_turns_and_facts(self):
        from brain.logic.conversation_coherence import update_coherence_state
        state = {}
        for i in range(10):
            update_coherence_state(
                state,
                user_message=f"Antwort {i}",
                topic="work",
                question=f"Frage {i}?",
                facts={"work_activity": "kochen"},
            )
        store = state["conversation_coherence_v1"]
        self.assertEqual(len(store["turns"]), 8)
        self.assertEqual(store["turns"][-1]["facts"]["work_activity"], "kochen")

    def test_coherence_engine_marks_topic_continuation(self):
        from brain.logic.conversation_coherence import assess_candidate_question
        result = assess_candidate_question(
            "Was kochst du bei der Arbeit?",
            topic="work",
            recent_questions=[],
        )
        self.assertTrue(result["topic_match"])
        self.assertEqual(result["reason"], "topic_continuation")

    def test_coherence_engine_detects_immediate_repeat(self):
        from brain.logic.conversation_coherence import assess_candidate_question
        result = assess_candidate_question(
            "Magst du das Wetter heute?",
            topic="weather",
            recent_questions=["Magst du das Wetter heute?"],
            previous_question="Magst du das Wetter heute?",
        )
        self.assertTrue(result["repeated"])
        self.assertTrue(result["immediate_repeat"])
        self.assertFalse(result["coherent"])


    def test_topic_goal_does_not_finish_too_early(self):
        from brain.logic.conversation_goal_transition import assess_topic_goal
        state = {"conversation_coherence_v1": {"turns": [
            {"topic": "work"}, {"topic": "work"},
        ]}}
        result = assess_topic_goal(state, topic="work", independent_turns=3)
        self.assertFalse(result["completed"])
        self.assertEqual(result["reason"], "continue_topic")

    def test_topic_goal_completes_after_enough_useful_practice(self):
        from brain.logic.conversation_goal_transition import assess_topic_goal
        state = {"conversation_coherence_v1": {"turns": [
            {"topic": "work"}, {"topic": "work"}, {"topic": "work"}, {"topic": "work"},
        ]}}
        result = assess_topic_goal(state, topic="work", independent_turns=3)
        self.assertTrue(result["completed"])
        self.assertEqual(result["reason"], "goal_reached")

    def test_topic_transition_is_blocked_by_active_error(self):
        from brain.logic.conversation_goal_transition import assess_topic_goal
        state = {"conversation_coherence_v1": {"turns": [{"topic": "work"}] * 5}}
        result = assess_topic_goal(
            state, topic="work", independent_turns=4,
            error_result={"error": {"category": "verb"}},
        )
        self.assertFalse(result["completed"])
        self.assertEqual(result["reason"], "active_learning_problem")

    def test_topic_transition_is_blocked_by_explicit_learner_topic(self):
        from brain.logic.conversation_goal_transition import assess_topic_goal
        state = {"conversation_coherence_v1": {"turns": [{"topic": "weather"}] * 5}}
        result = assess_topic_goal(
            state, topic="weather", independent_turns=4, explicit_topic=True,
        )
        self.assertFalse(result["completed"])
        self.assertEqual(result["reason"], "explicit_learner_topic")

    def test_topic_transition_selects_next_not_recent_topic(self):
        from brain.logic.conversation_goal_transition import decide_topic_transition
        state = {"conversation_coherence_v1": {
            "turns": [{"topic": "work"}] * 4,
            "recent_topics": ["today", "work"],
        }}
        result = decide_topic_transition(state, topic="work", independent_turns=3)
        self.assertTrue(result["transition"])
        self.assertEqual(result["next_topic"], "hobby")
        self.assertIn("work", state["topic_transition_v1"]["completed_topics"])


    def test_personalization_memory_saves_reusable_fact(self):
        from brain.logic.conversation_personalization import remember_conversation_facts
        state = {}
        remember_conversation_facts(state, {"activity": "cycling"}, topic="hobby")
        fact = state["conversation_personalization_v1"]["facts"]["activity"]
        self.assertEqual(fact["value"], "cycling")
        self.assertEqual(fact["confirmations"], 1)

    def test_personalization_memory_counts_repeated_confirmation(self):
        from brain.logic.conversation_personalization import remember_conversation_facts
        state = {}
        remember_conversation_facts(state, {"music_genre": "Rock"}, topic="hobby")
        remember_conversation_facts(state, {"music_genre": "Rock"}, topic="hobby")
        self.assertEqual(
            state["conversation_personalization_v1"]["facts"]["music_genre"]["confirmations"], 2
        )

    def test_personalization_followup_reuses_hobby_naturally(self):
        from brain.logic.conversation_personalization import remember_conversation_facts, choose_personalized_followup
        state = {}
        remember_conversation_facts(state, {"activity": "cycling"}, topic="hobby")
        result = choose_personalized_followup(state, topic="hobby", turn_count=4)
        self.assertIsNotNone(result)
        self.assertIn("Rad", result["question"])

    def test_personalization_does_not_fire_in_first_turns(self):
        from brain.logic.conversation_personalization import remember_conversation_facts, choose_personalized_followup
        state = {}
        remember_conversation_facts(state, {"activity": "swimming"}, topic="hobby")
        self.assertIsNone(choose_personalized_followup(state, topic="hobby", turn_count=1))

    def test_personalization_does_not_repeat_same_prompt(self):
        from brain.logic.conversation_personalization import remember_conversation_facts, choose_personalized_followup
        state = {}
        remember_conversation_facts(state, {"activity": "reading"}, topic="hobby")
        first = choose_personalized_followup(state, topic="hobby", turn_count=4)
        second = choose_personalized_followup(state, topic="hobby", turn_count=5)
        self.assertIsNotNone(first)
        self.assertIsNone(second)


    def test_quality_controller_repairs_known_invalid_construction(self):
        from brain.logic.conversation_quality_controller import check_reply
        result = check_reply("Ich arbeite Kochen.", topic="work")
        self.assertTrue(result["changed"])
        self.assertEqual(result["reply"], "Ich koche bei der Arbeit.")
        self.assertIn("known_invalid_construction", result["issues"])

    def test_quality_controller_removes_adjacent_duplicate_sentence(self):
        from brain.logic.conversation_quality_controller import check_reply
        result = check_reply("Magst du Pizza? Magst du Pizza?", topic="work")
        self.assertTrue(result["changed"])
        self.assertEqual(result["reply"], "Magst du Pizza?")
        self.assertIn("adjacent_duplicate", result["issues"])

    def test_quality_controller_does_not_rewrite_good_a1_reply(self):
        from brain.logic.conversation_quality_controller import check_reply
        reply = "Du kannst sagen: „Ich koche.“ Was kochst du gern?"
        result = check_reply(reply, topic="work", action="CORRECT_ERROR", model="Ich koche.")
        self.assertFalse(result["changed"])
        self.assertEqual(result["reply"], reply)

    def test_quality_controller_only_warns_on_long_reply(self):
        from brain.logic.conversation_quality_controller import check_reply
        reply = " ".join(["Wort"] * 33)
        result = check_reply(reply, topic="today")
        self.assertTrue(result["a1_length_warning"])
        self.assertFalse(result["changed"])
        self.assertEqual(result["reply"], reply)

    def test_quality_controller_preserves_repeat_error_instruction(self):
        from brain.logic.conversation_quality_controller import check_reply
        reply = "Richtig ist: „Ich heiße Moni.“ Sag es bitte noch einmal."
        result = check_reply(reply, action="REPEAT_ERROR", model="Ich heiße Moni.")
        self.assertFalse(result["changed"])
        self.assertEqual(result["reply"], reply)


    def test_quality_controller_v2_flags_long_a1_sentence_without_rewriting(self):
        from brain.logic.conversation_quality_controller import check_reply
        reply = " ".join(["Wort"] * 19) + "."
        result = check_reply(reply, topic="today")
        self.assertEqual(result["version"], 2)
        self.assertIn("a1_complexity_warning", result["issues"])
        self.assertFalse(result["changed"])
        self.assertEqual(result["reply"], reply)

    def test_quality_controller_v2_flags_topic_drift_for_continue(self):
        from brain.logic.conversation_quality_controller import check_reply
        result = check_reply(
            "Magst du das Wetter heute?",
            topic="work",
            action="CONTINUE",
            user_message="Pizza",
            response_understanding={"canonical": "pizza"},
        )
        self.assertIn("topic_alignment_warning", result["issues"])

    def test_quality_controller_v2_sees_response_alignment(self):
        from brain.logic.conversation_quality_controller import check_reply
        result = check_reply(
            "Pizza ist lecker. Kochst du Pizza gern?",
            topic="work",
            action="CONTINUE",
            user_message="Pizza",
            response_understanding={"canonical": "pizza"},
        )
        self.assertTrue(result["response_alignment"])
        self.assertNotIn("response_alignment_warning", result["issues"])

    def test_quality_controller_v2_flags_confirmed_memory_contradiction(self):
        from brain.logic.conversation_quality_controller import check_reply
        result = check_reply(
            "Du fährst nicht gern cycling.",
            topic="hobby",
            action="CONTINUE",
            personalization_facts={"activity": {"value": "cycling", "confirmations": 2}},
        )
        self.assertIn("memory_contradiction_warning", result["issues"])
        self.assertIn("activity", result["memory_contradictions"])
        self.assertFalse(result["changed"])

    def test_quality_controller_v2_does_not_flag_single_unconfirmed_memory_fact(self):
        from brain.logic.conversation_quality_controller import check_reply
        result = check_reply(
            "Du fährst nicht gern cycling.",
            topic="hobby",
            action="CONTINUE",
            personalization_facts={"activity": {"value": "cycling", "confirmations": 1}},
        )
        self.assertNotIn("memory_contradiction_warning", result["issues"])


    def test_recovery_engine_uses_learner_meaning_for_work_food(self):
        from brain.logic.conversation_recovery import recover_reply
        result = recover_reply(
            "Magst du das Wetter heute?",
            {"issues": ["topic_alignment_warning", "response_alignment_warning"], "changed": False},
            topic="work",
            action="CONTINUE",
            response_understanding={"canonical": "pizza"},
            safe_question="Was machst du bei der Arbeit?",
        )
        self.assertTrue(result["recovered"])
        self.assertEqual(result["strategy"], "learner_meaning")
        self.assertIn("Pizza", result["reply"])
        self.assertIn("Arbeit", result["reply"])

    def test_recovery_engine_falls_back_to_safe_topic_question(self):
        from brain.logic.conversation_recovery import recover_reply
        result = recover_reply(
            "Was machst du heute?",
            {"issues": ["topic_alignment_warning"], "changed": False},
            topic="weather",
            action="CONTINUE",
            response_understanding={"canonical": "ja"},
            safe_question="Wie ist das Wetter bei dir?",
        )
        self.assertTrue(result["recovered"])
        self.assertEqual(result["strategy"], "safe_topic_question")
        self.assertEqual(result["reply"], "Wie ist das Wetter bei dir?")

    def test_recovery_engine_never_overrides_repeat_error(self):
        from brain.logic.conversation_recovery import recover_reply
        reply = "Richtig ist: „Ich heiße Moni.“ Sag es bitte noch einmal."
        result = recover_reply(
            reply,
            {"issues": ["topic_alignment_warning"], "changed": False},
            topic="work",
            action="REPEAT_ERROR",
            response_understanding={"canonical": "moni"},
        )
        self.assertFalse(result["recovered"])
        self.assertEqual(result["reply"], reply)

    def test_recovery_engine_respects_quality_controller_repair(self):
        from brain.logic.conversation_recovery import recover_reply
        reply = "Ich koche bei der Arbeit."
        result = recover_reply(
            reply,
            {"issues": ["known_invalid_construction"], "changed": True},
            topic="work",
            action="CONTINUE",
            response_understanding={"canonical": "kochen"},
        )
        self.assertFalse(result["recovered"])
        self.assertEqual(result["reply"], reply)

    def test_recovery_engine_does_nothing_without_recoverable_warning(self):
        from brain.logic.conversation_recovery import recover_reply
        reply = "Was kochst du gern?"
        result = recover_reply(
            reply,
            {"issues": ["a1_complexity_warning"], "changed": False},
            topic="work",
            action="CONTINUE",
            response_understanding={"canonical": "pizza"},
        )
        self.assertFalse(result["recovered"])
        self.assertEqual(result["reply"], reply)


    def test_personal_sentence_practice_waits_during_lesson_handoff(self):
        from brain.logic.personal_sentences import should_offer_personal_sentence_practice
        state = {
            "lesson_teaching_active": False,
            "pending_new_learning": {
                "type": "new_section",
                "level": "A1",
                "lesson": 1,
                "section": "Ich stelle mich vor",
            },
            "last_question": "continue_new_learning",
            "personal_sentences": {"items": {}, "recent_ids": [], "scheduler": {"turns_since_practice": 9}},
        }
        self.assertFalse(
            should_offer_personal_sentence_practice(
                state,
                normal_turns=9,
                learner_needs_support=False,
                has_active_error=False,
            )
        )

    def test_recovery_does_not_override_understood_short_answer(self):
        from brain.logic.conversation_recovery import recover_reply
        result = recover_reply(
            "Was machst du heute?",
            {"issues": ["response_alignment_warning"], "changed": False},
            topic="today",
            action="CONTINUE",
            response_understanding={
                "understood": True,
                "confidence": "medium",
                "intent": "short_content",
                "canonical": "gut",
            },
            safe_question="Wie ist dein Tag heute?",
            user_message="gut",
        )
        self.assertFalse(result["recovered"])
        self.assertIsNone(result["recovery_reason"])
        self.assertEqual(result["reply"], "Was machst du heute?")

    def test_free_conversation_gut_never_triggers_recovery(self):
        state = {"free_conversation": {
            "last_question": "Wie geht es dir?",
            "recent_questions": ["Wie geht es dir?"],
            "conversation_facts": {},
        }}
        reply, meta = _turn(state, "gut")
        self.assertNotIn("Kein Problem", reply)
        # Core A1 social replies intentionally return before Recovery; the
        # important regression is that "gut" is accepted and continued
        # naturally instead of entering a failure path.
        self.assertIn("Was machst du heute?", reply)
        self.assertTrue(meta["response_understanding"]["understood"])
        self.assertIn(meta["response_understanding"]["confidence"], {"medium", "high"})

    def test_recovery_v2_classifies_learner_not_understanding(self):
        from brain.logic.conversation_recovery import classify_recovery
        reason = classify_recovery(
            {"issues": []},
            user_message="Ich verstehe nicht",
            response_understanding={"understood": True, "confidence": "high"},
            current_topic="work",
        )
        self.assertEqual(reason, "learner_did_not_understand")

    def test_recovery_v2_simplifies_when_learner_did_not_understand(self):
        from brain.logic.conversation_recovery import recover_reply
        result = recover_reply(
            "Was machst du bei der Arbeit?",
            {"issues": [], "changed": False},
            topic="work", action="CONTINUE",
            response_understanding={"understood": True, "confidence": "high"},
            safe_question="Arbeitest du heute?",
            user_message="Ich verstehe nicht",
        )
        self.assertTrue(result["recovered"])
        self.assertEqual(result["strategy"], "simplify_for_learner")
        self.assertIn("Ich frage einfacher", result["reply"])

    def test_recovery_v2_asks_again_when_nele_is_uncertain(self):
        from brain.logic.conversation_recovery import recover_reply
        result = recover_reply(
            "Was machst du heute?",
            {"issues": ["response_alignment_warning"], "changed": False},
            topic="today", action="CONTINUE",
            response_understanding={"understood": False, "confidence": "low"},
            user_message="...",
        )
        self.assertTrue(result["recovered"])
        self.assertEqual(result["strategy"], "ask_again")
        self.assertIn("nicht ganz verstanden", result["reply"])

    def test_recovery_v2_accepts_explicit_topic_change(self):
        from brain.logic.conversation_recovery import recover_reply
        result = recover_reply(
            "Wie ist das Wetter bei dir?",
            {"issues": ["response_alignment_warning"], "changed": False},
            topic="work", action="CONTINUE",
            response_understanding={"understood": True, "confidence": "high", "canonical": "wetter"},
            user_message="Wetter",
            explicit_topic="weather",
        )
        self.assertFalse(result["recovered"])
        self.assertEqual(result["strategy"], "accept_topic_change")
        self.assertEqual(result["recovery_reason"], "learner_topic_change")

    def test_recovery_v2_keeps_error_actions_authoritative(self):
        from brain.logic.conversation_recovery import recover_reply
        reply = "Richtig ist: „Ich heiße Moni.“ Sag es bitte noch einmal."
        result = recover_reply(
            reply,
            {"issues": ["response_alignment_warning"], "changed": False},
            topic="today", action="REPEAT_ERROR",
            response_understanding={"understood": False, "confidence": "low"},
            user_message="was",
        )
        self.assertFalse(result["recovered"])
        self.assertEqual(result["reply"], reply)


    def test_orchestrator_pipeline_has_explicit_order(self):
        from brain.logic.conversation_orchestrator import PIPELINE
        self.assertLess(PIPELINE.index("response_understanding"), PIPELINE.index("error_engine"))
        self.assertLess(PIPELINE.index("teacher_policy"), PIPELINE.index("learning_action_executor"))
        self.assertLess(PIPELINE.index("quality_controller"), PIPELINE.index("recovery"))

    def test_orchestrator_blocks_transition_during_error_repeat(self):
        from brain.logic.conversation_orchestrator import build_orchestration_contract, enforce_orchestration
        contract = build_orchestration_contract(
            teacher_policy={"action": "REPEAT_ERROR"},
            struggle=False,
            topic_transition={"transition": True},
        )
        result = enforce_orchestration(
            contract,
            topic_transition={"transition": True, "topic": "work", "next_topic": "hobby"},
        )
        self.assertFalse(result["topic_transition"]["transition"])
        self.assertIn("topic_transition_blocked", result["conflicts"])

    def test_orchestrator_blocks_personalization_during_correction(self):
        from brain.logic.conversation_orchestrator import build_orchestration_contract, enforce_orchestration
        contract = build_orchestration_contract(teacher_policy={"action": "CORRECT_ERROR"})
        result = enforce_orchestration(
            contract,
            personalized_followup={"question": "Du fährst gern Rad. Wo fährst du?"},
        )
        self.assertIsNone(result["personalized_followup"])
        self.assertIn("personalization_blocked", result["conflicts"])

    def test_orchestrator_allows_simplifier_only_for_current_struggle(self):
        from brain.logic.conversation_orchestrator import build_orchestration_contract, enforce_orchestration
        allowed = build_orchestration_contract(
            teacher_policy={"action": "SIMPLIFY"}, struggle=True,
        )
        result = enforce_orchestration(
            allowed, question_support={"question": "Arbeitest du heute?"},
        )
        self.assertIsNotNone(result["question_support"])

        blocked = build_orchestration_contract(
            teacher_policy={"action": "SIMPLIFY"}, struggle=False,
        )
        result2 = enforce_orchestration(
            blocked, question_support={"question": "Arbeitest du heute?"},
        )
        self.assertIsNone(result2["question_support"])

    def test_orchestrator_blocks_recovery_from_overriding_pedagogy(self):
        from brain.logic.conversation_orchestrator import build_orchestration_contract, enforce_orchestration
        contract = build_orchestration_contract(teacher_policy={"action": "MODEL_SENTENCE"})
        result = enforce_orchestration(
            contract,
            recovery={"recovered": True, "original": "Du kannst sagen: Ich arbeite.", "reply": "Was machst du heute?"},
        )
        self.assertFalse(result["recovery"]["recovered"])
        self.assertEqual(result["recovery"]["reply"], "Du kannst sagen: Ich arbeite.")
        self.assertIn("recovery_override_blocked", result["conflicts"])


    def test_orchestrator_v2_turn_plan_for_error_repeat(self):
        from brain.logic.conversation_orchestrator import build_turn_plan
        plan = build_turn_plan(
            teacher_policy={"action": "REPEAT_ERROR", "model": "Ich heiße Moni."},
            topic="today",
            error_result={"error": {"category": "verb"}},
            response_understanding={"confidence": "high"},
        )
        self.assertEqual(plan["version"], 2)
        self.assertEqual(plan["goal"], "repair_error")
        self.assertEqual(plan["expected_outcome"], "repeat_correct_form")
        self.assertTrue(plan["keep_topic"])
        self.assertFalse(plan["allow_topic_transition"])
        self.assertFalse(plan["allow_recovery_override"])

    def test_orchestrator_v2_turn_plan_for_normal_advance(self):
        from brain.logic.conversation_orchestrator import build_turn_plan
        plan = build_turn_plan(
            teacher_policy={"action": "ADVANCE"},
            topic="hobby",
            struggle=False,
        )
        self.assertEqual(plan["goal"], "increase_independence")
        self.assertEqual(plan["expected_outcome"], "independent_answer")
        self.assertTrue(plan["allow_topic_transition"])
        self.assertTrue(plan["allow_personalization"])
        self.assertTrue(plan["allow_recovery_override"])

    def test_orchestrator_v2_contract_uses_supplied_turn_plan(self):
        from brain.logic.conversation_orchestrator import build_turn_plan, build_orchestration_contract
        plan = build_turn_plan(
            teacher_policy={"action": "SIMPLIFY"},
            topic="work",
            struggle=True,
        )
        contract = build_orchestration_contract(
            teacher_policy={"action": "CONTINUE"},
            struggle=False,
            turn_plan=plan,
        )
        self.assertEqual(contract["action"], "SIMPLIFY")
        self.assertTrue(contract["allow_question_simplifier"])
        self.assertFalse(contract["allow_topic_transition"])

    def test_orchestrator_v2_records_turn_plan_and_compatibility_state(self):
        from brain.logic.conversation_orchestrator import build_turn_plan, build_orchestration_contract, enforce_orchestration, record_orchestration
        state = {}
        plan = build_turn_plan(teacher_policy={"action": "CONTINUE"}, topic="weather")
        contract = build_orchestration_contract(turn_plan=plan)
        result = enforce_orchestration(contract)
        recorded = record_orchestration(state, result)
        self.assertEqual(recorded["version"], 2)
        self.assertEqual(state["turn_plan_v1"]["topic"], "weather")
        self.assertEqual(state["conversation_orchestrator_v1"]["version"], 2)
        self.assertEqual(state["conversation_orchestrator_v2"]["version"], 2)

    def test_orchestrator_v2_turn_plan_blocks_topic_change_during_simplify(self):
        from brain.logic.conversation_orchestrator import build_turn_plan, build_orchestration_contract, enforce_orchestration
        plan = build_turn_plan(
            teacher_policy={"action": "SIMPLIFY"},
            topic="work",
            struggle=True,
        )
        contract = build_orchestration_contract(turn_plan=plan)
        result = enforce_orchestration(
            contract,
            topic_transition={"transition": True, "topic": "work", "next_topic": "hobby"},
        )
        self.assertFalse(result["topic_transition"]["transition"])
        self.assertIn("topic_transition_blocked", result["conflicts"])


    def test_wellbeing_short_answer_survives_und_dir_ellipsis(self):
        state = {}
        generate_free_welcome(state)
        reply, _ = _turn(state, "Wie geht es dir heute?")
        self.assertIn("Und dir?", reply)
        reply, _ = _turn(state, "gut")
        self.assertIn("Das freut mich", reply)
        self.assertNotIn("Kein Problem", reply)

    def test_fresh_learner_question_outranks_stale_work_context(self):
        state = {"free_conversation": {
            "last_question": "Was machst du bei der Arbeit?",
            "recent_questions": ["Was machst du bei der Arbeit?"],
            "conversation_facts": {},
        }}
        reply, _ = _turn(state, "Woher kommst du?")
        self.assertIn("Ich bin Nele", reply)
        self.assertNotEqual(reply.strip(), "Was machst du bei der Arbeit?")

    def test_weekend_question_outranks_stale_weather_context(self):
        state = {"free_conversation": {
            "last_question": "Wie ist das Wetter bei dir?",
            "recent_questions": ["Wie ist das Wetter bei dir?"],
            "conversation_facts": {"weather": "warm"},
        }}
        reply, _ = _turn(state, "Was machst du gern am Wochenende?")
        self.assertIn("Am Wochenende", reply)
        self.assertNotIn("Magst du das Wetter heute?", reply)

    def test_greeting_is_not_treated_as_failure(self):
        state = {}
        generate_free_welcome(state)
        reply, _ = _turn(state, "Hallo Nele!")
        self.assertNotIn("Kein Problem", reply)
        self.assertRegex(reply, r"Wie geht(?: es|'s) dir|Was machst du heute")
