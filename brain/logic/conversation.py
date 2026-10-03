# ==========================================
from brain.nele3_upgrade.state import get_pending_recommendation
# NELE – GŁÓWNY ROUTER ROZMOWY
# TEACHER MODE
# ==========================================

from brain.logic.memory import (
    get_conversation_state
)

from brain.logic.message_parser import (
    split_multiple_questions
)

from brain.logic.matcher import normalize

from brain.logic.conversation_context import (
    remember_current_topic,
    remember_current_comparison,
    handle_topic_follow_up
)

from brain.logic.correction_router import (
    handle_correction
)

from brain.logic.user_memory_router import (
    handle_user_memory
)

from brain.logic.personalization_router import (
    handle_personalization
)

from brain.logic.onboarding import (
    is_onboarding_completed,
    is_new_user,
    get_onboarding_step,
    handle_onboarding_answer,
    complete_onboarding
)

from brain.logic.welcome import (
    generate_welcome_reply
)

from brain.logic.new_learning_resume import (
    handle_new_learning_resume
)

from brain.logic.lesson_teaching import (
    handle_lesson_teaching
)

from brain.logic.dialogue_engine import (
    auto_start_dialogue_from_message,
    is_dialogue_active,
    handle_dialogue,
)

from brain.logic.personal_sentences import (
    should_offer_personal_sentence_practice,
    start_personal_sentence_practice,
    note_personal_sentence_practice_started,
)

from brain.logic.lesson_review_training import (
    handle_lesson_review_training,
    is_lesson_review_training_active,
    start_lesson_review_training,
)

from brain.logic.error_progress import (
    handle_error_progress
)

from brain.logic.learner_feedback import (
    prepare_message_with_feedback
)

from brain.logic.activity_resume import (
    handle_continue_last_activity
)

from brain.logic.lesson_progress_router import (
    handle_lesson_progress
)

from brain.logic.alphabet_router import (
    handle_alphabet
)

from brain.logic.context_router import (
    handle_context
)

from brain.logic.response_engine import (
    find_response,
    create_teacher_directed_follow_up
)

from brain.logic.intent_handler import (
    handle_intent
)

from brain.logic.comparison_router import (
    handle_comparison
)

from brain.logic.vocabulary_router import (
    handle_vocabulary
)

from brain.logic.vocabulary_modules.practice import (
    is_vocabulary_practice_active
)

from brain.logic.conversation_commands import (
    handle_repeat_request,
    handle_return_to_training_request
)

from brain.logic.conversation_vocabulary import (
    handle_vocabulary_explanation_request
)

from brain.logic.conversation_vocabulary_context import (
    update_conversation_vocabulary_context
)

from brain.logic.topic_follow_up_engine import (
    next_topic_follow_up
)

from brain.logic.conversation_error_training import (
    handle_priority_error_practice,
    handle_active_error_practice
)

from brain.logic.error_memory_router import (
    is_error_practice_start_request,
)

from brain.logic.error_practice import (
    is_error_practice_active,
)

from brain.logic.conversation_wellbeing import (
    handle_wellbeing_reply
)

from brain.logic.conversation_continuation import (
    continue_after_side_answer,
    continue_after_finished_training
)

from brain.logic.conversation_memory import (
    handle_conversation_memory
)

from brain.logic.conversation_output import (
    merge_feedback_texts,
    return_with_memory,
    return_with_feedback
)

from brain.memory.error_review import (
    refresh_error_reviews
)


def _selected_course_context(state):
    """Return the lesson selected by the real course progress store."""
    state = state or {}
    student_progress = state.get("student_progress") or {}
    level = (
        student_progress.get("current_level")
        or state.get("selected_level")
        or state.get("level")
        or "A1"
    )
    lesson = (
        student_progress.get("current_lesson")
        or state.get("selected_lesson")
        or state.get("lesson")
        or 1
    )
    return level, lesson


def _resume_course_after_side_answer(answer, state):
    """Append the suspended course prompt once a side question was answered."""
    if not state.pop("course_side_question_pending", False):
        return answer
    return continue_after_side_answer(answer, state)


def _release_wellbeing_for_course_dialogue_intent(user_message, state, level):
    """Do not trap an explicit learner question inside returning-welcome small talk."""
    del level  # kept in the signature for course-routing compatibility
    if (
        str((state or {}).get("conversation_mode") or "").strip().lower() != "course"
        or (state or {}).get("last_question") != "wellbeing"
        or "?" not in str(user_message or "")
    ):
        return False
    state["last_question"] = None
    return True


# ==========================================
# GŁÓWNY ROUTER
# ==========================================

def generate_conversation_reply(
    user_message,
    level="A1",
    lesson=1,
    session_id="default"
):

    # ======================================
    # KILKA PYTAŃ
    # ======================================

    multiple_questions = split_multiple_questions(
        user_message
    )

    if multiple_questions:

        answers = []

        for question in multiple_questions:

            answer = generate_conversation_reply(
                question,
                level,
                lesson,
                session_id
            )

            if answer:

                answers.append(
                    answer
                )

        if answers:

            return return_with_memory(
                "\n\n".join(
                    answers
                ),
                session_id
            )


    # ======================================
    # STAN
    # ======================================

    state = get_conversation_state(
        session_id
    )


    # ======================================
    # START PO ZAKOŃCZENIU ONBOARDINGU
    #
    # Po pytaniu "Möchtest du gleich anfangen?"
    # odpowiedź "ja" ma naprawdę rozpocząć naukę,
    # zamiast wpadać do fallbacku.
    # ======================================

    if (
        is_onboarding_completed(
            state
        )
        and
        state.get(
            "last_question"
        )
        ==
        "start_after_onboarding"
    ):

        start_message = str(
            user_message or ""
        ).strip().lower()

        start_message = start_message.strip(
            " .?!„“\"'"
        )

        yes_answers = {
            "ja",
            "ja gern",
            "ja gerne",
            "gerne",
            "gern",
            "okay",
            "ok",
            "klar",
            "natürlich",
            "ja bitte",
            "machen wir",
            "bereit",
            "ich bin bereit"
        }

        no_answers = {
            "nein",
            "nein danke",
            "nicht jetzt",
            "später",
            "lieber nicht",
            "jetzt nicht"
        }

        if start_message in yes_answers:

            state[
                "last_question"
            ] = None

            answer = (
                create_teacher_directed_follow_up(
                    state,
                    ""
                )
            )

            if not answer:

                answer = (
                    "Super. Dann legen wir los."
                )

            return return_with_memory(
                answer,
                session_id
            )

        if start_message in no_answers:

            state[
                "last_question"
            ] = None

            return return_with_memory(
                (
                    "Okay. Kein Problem. "
                    "Sag einfach Bescheid, "
                    "wenn du anfangen möchtest."
                ),
                session_id
            )


    # ======================================
    # KOMENDA GLOBALNA: POWTÓRZ
    #
    # Musi działać także podczas aktywnej
    # lekcji, powtórki błędów, onboardingu
    # i innych ćwiczeń. Dlatego sprawdzamy
    # ją zanim odpowiedź ucznia trafi do
    # konkretnego treningu.
    # ======================================

    (
        repeat_handled,
        repeat_answer,
        repeat_feedback
    ) = handle_repeat_request(
        user_message,
        state
    )

    if repeat_handled:

        return return_with_feedback(
            repeat_answer,
            repeat_feedback,
            session_id
        )


    # ======================================
    # 0. ONBOARDING
    # ======================================

    if not is_onboarding_completed(
        state
    ):

        onboarding_step = get_onboarding_step(
            state
        )

        if onboarding_step > 0:

            answer = handle_onboarding_answer(
                user_message,
                state,
                session_id
            )

            if answer:

                return return_with_memory(
                    answer,
                    session_id
                )

        elif is_new_user(
            state
        ):

            return return_with_memory(
                generate_welcome_reply(
                    session_id
                ),
                session_id
            )

        else:

            complete_onboarding(
                state
            )

            return_with_memory(
                None,
                session_id
            )


    # ======================================
    # 1. POWTÓRKI BŁĘDÓW
    # ======================================

    try:

        refresh_error_reviews(
            state
        )

    except Exception as error:

        print(
            f"Error review refresh error: {error}"
        )


    # A returning-course welcome asks about wellbeing, but an explicit
    # validated course-dialogue intent must be allowed to start the selected
    # learning activity instead of being trapped as an invalid wellbeing
    # answer. This is generic across dialogue knowledge: no sentence or lesson
    # is hard-coded here.
    _release_wellbeing_for_course_dialogue_intent(
        user_message,
        state,
        level,
    )


    # ======================================
    # 2. SAMOPOCZUCIE
    #
    # conversation_wellbeing.py
    #
    # Musi być przed pamięcią użytkownika,
    # aby np. "Ich bin müde."
    # nie zostało potraktowane jako imię.
    # ======================================

    (
        wellbeing_handled,
        wellbeing_answer,
        wellbeing_feedback
    ) = handle_wellbeing_reply(
        user_message,
        state
    )

    if wellbeing_handled:

        return return_with_feedback(
            wellbeing_answer,
            wellbeing_feedback,
            session_id
        )


    # ======================================
    # 3. LEARNER FEEDBACK
    # ======================================

    processed_message, feedback_text = (
        prepare_message_with_feedback(
            user_message,
            state
        )
    )

    # Vocabulary Engine enriches the state; existing routers keep priority.
    update_conversation_vocabulary_context(
        processed_message,
        state
    )


    # ======================================
    # 4A. AKTYWNA POWTÓRKA CAŁEJ LEKCJI
    #
    # lesson_review_training.py
    #
    # Jeżeli pełna powtórka lekcji
    # jest już aktywna, odpowiedź ucznia
    # musi trafić najpierw tutaj.
    #
    # Po zakończeniu powtórki przechodzimy
    # automatycznie do kolejnego kroku
    # Teacher Mode.
    # ======================================

    was_lesson_review_active = (
        is_lesson_review_training_active(
            state
        )
    )

    # Explicit Error Practice is a routing command, not an answer to the
    # current review task. Let the shared memory router start the temporary
    # detour; the active review state stays intact for exact resumption.
    error_practice_start_requested = is_error_practice_start_request(
        processed_message
    )

    if (
        was_lesson_review_active
        and not error_practice_start_requested
        and not is_error_practice_active(state)
    ):

        answer = handle_lesson_review_training(
            processed_message,
            state
        )

        if answer:

            is_still_lesson_review_active = (
                is_lesson_review_training_active(
                    state
                )
            )

            if (
                was_lesson_review_active
                and
                not is_still_lesson_review_active
            ):

                answer = (
                    continue_after_finished_training(
                        answer,
                        state
                    )
                )

            return return_with_feedback(
                answer,
                feedback_text,
                session_id
            )


    # An explicit learner request to repeat the selected lesson is a routing
    # command, not an answer to the currently active exercise. Give that intent
    # priority before lesson/error routers can grade it as course content.
    review_intent = normalize(processed_message).strip(" .?!„“\"'")
    if (
        str((state or {}).get("conversation_mode") or "").strip().lower() == "course"
        and "lektion" in review_intent
        and "wiederhol" in review_intent
    ):
        selected_level, selected_lesson = _selected_course_context(state)
        answer = start_lesson_review_training(
            state,
            selected_level,
            selected_lesson,
        )
        if answer:
            return return_with_feedback(
                answer,
                feedback_text,
                session_id
            )


    # ======================================
    # 4B. AKTYWNE FEHLERTRAINING
    #
    # conversation_error_training.py
    #
    # Fehlertraining ma pierwszeństwo
    # przed zwykłymi komendami.
    # ======================================

    (
        handled,
        answer
    ) = handle_priority_error_practice(
        processed_message,
        state
    )

    if handled:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 4C. POWTÓRZ
    # ======================================

    (
        handled,
        answer,
        command_feedback
    ) = handle_repeat_request(
        processed_message,
        state
    )

    if handled:

        return return_with_feedback(
            answer,
            merge_feedback_texts(
                feedback_text,
                command_feedback
            ),
            session_id
        )


    # ======================================
    # 4D. WRÓĆ DO TRENINGU
    # ======================================

    (
        handled,
        answer,
        command_feedback
    ) = handle_return_to_training_request(
        processed_message,
        state
    )

    if handled:

        return return_with_feedback(
            answer,
            merge_feedback_texts(
                feedback_text,
                command_feedback
            ),
            session_id
        )


    # ======================================
    # 4E. PYTANIE O ZNACZENIE SŁOWA
    #
    # conversation_vocabulary.py
    # ======================================

    (
        handled,
        answer,
        vocabulary_feedback
    ) = handle_vocabulary_explanation_request(
        processed_message,
        state
    )

    if handled:

        return return_with_feedback(
            continue_after_side_answer(
                answer,
                state
            ),
            merge_feedback_texts(
                feedback_text,
                vocabulary_feedback
            ),
            session_id
        )


    # ======================================
    # 5. PAMIĘĆ
    #
    # conversation_memory.py
    # ======================================

    (
        handled,
        answer
    ) = handle_conversation_memory(
        processed_message,
        state
    )

    if handled:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 6. AKTYWNE FEHLERTRAINING
    #
    # conversation_error_training.py
    # ======================================

    answer = handle_active_error_practice(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 7. POSTĘP BŁĘDÓW
    # ======================================

    answer = handle_error_progress(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 8. NOWA NAUKA
    # ======================================

    answer = handle_new_learning_resume(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )

    # A completed course dialogue may create the next-section offer during
    # this same turn. When the learner answers "ja" on the following turn,
    # no other router may consume it first just because the dialogue is now
    # inactive. Keep the pending course handoff authoritative.
    if (
        str((state or {}).get("conversation_mode") or "").strip().lower() == "course"
        and state.get("pending_new_learning")
        and state.get("last_question") == "continue_new_learning"
    ):
        normalized_resume = normalize(processed_message).strip(" .?!„“\"'")
        if normalized_resume in {"ja", "ja gern", "ja gerne", "gern", "gerne", "klar", "okay", "ok", "natürlich", "ja bitte", "machen wir", "los gehts", "los geht's", "weiter", "und jetzt", "was jetzt", "weiter bitte"}:
            answer = handle_new_learning_resume(processed_message, state)
            if answer:
                return return_with_feedback(
                    answer,
                    feedback_text,
                    session_id
                )


    # A learner may naturally acknowledge the lesson-completion message.
    # Keep that turn inside the course instead of falling through to the
    # generic "Antwort ... noch nicht gelernt" response.
    if (
        str((state or {}).get("conversation_mode") or "").strip().lower() == "course"
        and state.get("last_question") == "course_lesson_completed"
    ):
        normalized_completion = normalize(processed_message).strip(" .?!„“\\\"'")
        if normalized_completion in {
            "ja", "ja gern", "ja gerne", "okay", "ok", "gut", "super",
            "danke", "danke schön", "dankeschön", "bis morgen",
        }:
            state["last_question"] = None
            return return_with_feedback(
                "Genau. Die Lektion ist abgeschlossen. Bis morgen!",
                feedback_text,
                session_id,
            )
        state["last_question"] = None


    # ======================================
    # 9. AKTYWNA LEKCJA
    # ======================================

    answer = handle_lesson_teaching(
        processed_message,
        state
    )

    if answer:

        # Occasionally weave a learner-owned real-life sentence into course mode.
        # Never do this on correction/support turns, and never replace lesson content.
        personal_memory = state.setdefault("personal_sentences", {})
        scheduler = personal_memory.setdefault("scheduler", {"turns_since_practice": 0})
        scheduler["turns_since_practice"] = int(scheduler.get("turns_since_practice", 0) or 0) + 1
        answer_low = str(answer or "").lower()
        support_turn = any(marker in answer_low for marker in (
            "fast.", "richtig:", "sag bitte", "noch einmal", "du kannst sagen"
        ))
        if (
            get_pending_recommendation(state) is None
            and should_offer_personal_sentence_practice(
                state,
                normal_turns=scheduler["turns_since_practice"],
                learner_needs_support=support_turn,
                has_active_error=bool(state.get("active_error_practice")),
            )
        ):
            personal_prompt = start_personal_sentence_practice(state)
            if personal_prompt:
                note_personal_sentence_practice_started(state)
                answer = f"{answer} {personal_prompt}"

        return return_with_feedback(
            answer,
            feedback_text,
            session_id
        )


    # ======================================
    # 9B. AUTOMATYCZNY ROUTER DIALOGUE KNOWLEDGE
    #
    # W Frei sprechen użytkownik może rozpocząć
    # aktywny dialog samym pytaniem. Jeśli nie
    # ma już aktywnego dialogu, wspólny router
    # wybiera właściwy wpis z aktywnej wiedzy.
    # Nigdy nie nadpisuje aktywnego dialogu ani
    # aktywnej lekcji.
    # ======================================

    if not state.get("lesson_teaching_active") and not is_dialogue_active(state):
        dialogue_answer = auto_start_dialogue_from_message(
            processed_message,
            state,
            level=level,
        )
        if dialogue_answer:
            return return_with_feedback(
                dialogue_answer,
                feedback_text,
                session_id
            )

    # ======================================
    # 9C. AKTYWNY DIALOGUE KNOWLEDGE
    #
    # Once a reusable dialogue owns the turn, it must be handled before
    # legacy free-conversation continuations. Otherwise old topic follow-ups
    # can leak into the dialogue and ignore short contextual answers.
    # ======================================

    if is_dialogue_active(state) and not state.get("course_side_question_pending"):
        dialogue_answer = handle_dialogue(
            processed_message,
            state,
        )
        if dialogue_answer:
            return return_with_feedback(
                dialogue_answer,
                feedback_text,
                session_id
            )


    # ======================================
    # 10. KONTYNUACJA AKTYWNOŚCI
    # ======================================

    answer = handle_continue_last_activity(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 11. KOREKTA
    # ======================================

    answer = handle_correction(
        processed_message,
        session_id
    )

    if answer:

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 12. ALFABET
    # ======================================

    answer = handle_alphabet(
        processed_message,
        level,
        lesson
    )

    if answer:

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 13. POSTĘP LEKCJI
    # ======================================

    answer = handle_lesson_progress(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 14. PERSONALIZACJA
    # ======================================

    answer = handle_personalization(
        processed_message,
        state
    )

    if answer:

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 15. PAMIĘĆ UŻYTKOWNIKA
    # ======================================

    answer = handle_user_memory(
        processed_message,
        session_id
    )

    if answer:

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 16. TEMAT
    # ======================================

    answer = handle_topic_follow_up(
        processed_message,
        session_id
    )

    if answer:

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 17. PORÓWNANIA
    # ======================================

    answer = handle_comparison(
        processed_message,
        state,
        session_id
    )

    if answer:

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 18. SŁOWNICTWO
    # ======================================

    was_active = (
        is_vocabulary_practice_active(
            state
        )
    )

    answer = handle_vocabulary(
        processed_message,
        state
    )

    if answer:

        if (
            was_active
            and
            not is_vocabulary_practice_active(
                state
            )
        ):

            answer = (
                continue_after_finished_training(
                    answer,
                    state
                )
            )

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 19. INTENCJE
    # ======================================

    answer = handle_intent(
        processed_message,
        session_id
    )

    if answer:

        remember_current_topic(
            processed_message,
            session_id
        )

        remember_current_comparison(
            processed_message,
            session_id
        )

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 20. ZNANE PYTANIA
    # ======================================

    answer = find_response(
        processed_message,
        level,
        lesson,
        session_id
    )

    if answer:

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 21. KONTEKST
    # ======================================

    answer = handle_context(
        processed_message,
        session_id
    )

    if answer:

        return return_with_feedback(
            _resume_course_after_side_answer(answer, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 22. NATÜRLICHE THEMENFORTSETZUNG
    #
    # Nur wenn kein spezialisierter Router
    # geantwortet hat. So bleiben Lektionen,
    # Korrekturen und Trainings unverändert.
    # ======================================

    topic_follow_up = next_topic_follow_up(
        state
    )

    if topic_follow_up:

        return return_with_feedback(
            _resume_course_after_side_answer(topic_follow_up, state),
            feedback_text,
            session_id
        )


    # ======================================
    # 23. FALLBACK
    # ======================================

    return return_with_feedback(
        _resume_course_after_side_answer(
            (
                "Ich habe dich verstanden, "
                "aber diese Antwort habe ich "
                "noch nicht gelernt."
            ),
            state,
        ),
        feedback_text,
        session_id
                )
