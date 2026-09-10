# ==========================================
# NELE – LOGIKA ROZMOWY Z PAMIĘCIĄ SESJI
# ==========================================

from brain.logic.memory import (
    get_conversation_state,
    save_conversation_state
)

from brain.logic.matcher import (
    normalize
)

from brain.logic.message_parser import (
    split_multiple_questions
)

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

from brain.logic.personalization import (
    create_personalized_exercise,
    get_personalized_exercise,
    clear_personalized_exercise,
    validate_personalized_answer,
    set_personalized_exercise_step,
    get_personalized_follow_up
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

from brain.logic.activity_resume import (
    handle_continue_last_activity
)

from brain.logic.alphabet_router import (
    handle_alphabet
)

from brain.logic.context_router import (
    handle_context
)

from brain.logic.response_engine import (
    find_response
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

from brain.memory.review import (
    handle_memory
)


# ==========================================
# ZAPISANIE STANU I ZWROT ODPOWIEDZI
# ==========================================

def return_with_memory(
    answer,
    session_id
):

    try:

        save_conversation_state(
            session_id
        )

    except Exception as error:

        print(
            f"Conversation save error: {error}"
        )

    return answer


# ==========================================
# ODPOWIEDŹ KOŃCOWA PERSONALIZOWANEJ LEKCJI
# ==========================================

def create_personalized_final_answer(
    answer,
    topic,
    value
):

    normalized_answer = normalize(
        answer
    )

    # ======================================
    # HOBBY – RADFAHREN
    # ======================================

    if (
        topic == "hobby"
        and normalize(
            value or ""
        ) == "radfahren"
    ):

        if "wochenende" in normalized_answer:
            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre am Wochenende Rad.“"
            )

        if "morgens" in normalized_answer:
            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre morgens Rad.“"
            )

        if "nachmittags" in normalized_answer:
            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre nachmittags Rad.“"
            )

        if "abends" in normalized_answer:
            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre abends Rad.“"
            )

        if "samstag" in normalized_answer:
            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre am Samstag Rad.“"
            )

        if "sonntag" in normalized_answer:
            return (
                "Sehr gut! "
                "Du kannst sagen: "
                "„Ich fahre am Sonntag Rad.“"
            )

        return (
            f"Sehr gut! "
            f"Du hast gesagt: "
            f"„{answer}“ "
            f"Das passt gut zu deinem Hobby "
            f"{value}."
        )

    # ======================================
    # INNY TEMAT
    # ======================================

    return (
        f"Sehr gut! "
        f"Du hast gesagt: "
        f"„{answer}“"
    )


# ==========================================
# ODPOWIEDŹ NA PERSONALIZOWANE ĆWICZENIE
# ==========================================

def handle_personalized_exercise_answer(
    user_message,
    state
):

    exercise = get_personalized_exercise(
        state
    )

    if not exercise:
        return None

    validation = validate_personalized_answer(
        user_message,
        state
    )

    if not validation:
        return None

    status = validation.get(
        "status"
    )

    if status == "retry":
        return validation.get(
            "answer"
        )

    answer = validation.get(
        "answer",
        user_message.strip()
    )

    topic = validation.get(
        "topic"
    )

    value = validation.get(
        "value"
    )

    # ======================================
    # ETAP 1 ZAAKCEPTOWANY
    # ======================================

    if status == "step_1_accepted":

        set_personalized_exercise_step(
            state,
            2
        )

        follow_up = get_personalized_follow_up(
            state
        )

        if follow_up:
            return follow_up

        return (
            "Sehr gut! "
            "Machen wir weiter."
        )

    # ======================================
    # ETAP 2 ZAAKCEPTOWANY
    # ======================================

    if status == "step_2_accepted":

        set_personalized_exercise_step(
            state,
            3
        )

        follow_up = get_personalized_follow_up(
            state
        )

        if follow_up:
            return follow_up

        return (
            "Super! "
            "Machen wir weiter."
        )

    # ======================================
    # ETAP 3 ZAAKCEPTOWANY
    # ======================================

    if status == "step_3_accepted":

        clear_personalized_exercise(
            state
        )

        return create_personalized_final_answer(
            answer,
            topic,
            value
        )

    # ======================================
    # STARSZY / INNY TYP ĆWICZENIA
    # ======================================

    if status == "accepted":

        clear_personalized_exercise(
            state
        )

        if topic == "learning_goal":
            return (
                f"Sehr gut! "
                f"Wir arbeiten weiter an "
                f"deinem Lernziel {value}."
            )

        return (
            f"Sehr gut! "
            f"Deine Antwort lautet: "
            f"„{answer}“"
        )

    return None


# ==========================================
# GŁÓWNA LOGIKA ROZMOWY
# ==========================================

def generate_conversation_reply(
    user_message,
    level="A1",
    lesson=1,
    session_id="default"
):

    # ======================================
    # KILKA PYTAŃ W JEDNEJ WIADOMOŚCI
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
    # PAMIĘĆ SESJI
    # ======================================

    state = get_conversation_state(
        session_id
    )

    # Te dwa pola zostają jako zabezpieczenie.
    # Jeśli dodasz je do create_empty_state()
    # w memory.py, można usunąć też to.
    state.setdefault(
        "last_activity",
        None
    )
    state.setdefault(
        "last_activity_detail",
        None
    )

    # ======================================
    # NORMALIZACJA WIADOMOŚCI
    # ======================================

    message = normalize(
        user_message
    )

    # ======================================
    # 0. PIERWSZE SPOTKANIE
    # ======================================

    if not is_onboarding_completed(
        state
    ):

        onboarding_step = get_onboarding_step(
            state
        )

        if onboarding_step > 0:

            onboarding_answer = (
                handle_onboarding_answer(
                    user_message,
                    state,
                    session_id
                )
            )

            if onboarding_answer:
                return return_with_memory(
                    onboarding_answer,
                    session_id
                )

        elif is_new_user(
            state
        ):

            return generate_welcome_reply(
                session_id
            )

        else:

            complete_onboarding(
                state
            )

    # ======================================
    # 1. KONTYNUACJA OSTATNIEJ AKTYWNOŚCI
    # ======================================

    continue_answer = (
        handle_continue_last_activity(
            user_message,
            state
        )
    )

    if continue_answer:
        return return_with_memory(
            continue_answer,
            session_id
        )

    # ======================================
    # 2. KOREKTA BŁĘDÓW
    # ======================================

    correction_answer = handle_correction(
        user_message,
        session_id
    )

    if correction_answer:
        return return_with_memory(
            correction_answer,
            session_id
        )

    # ======================================
    # 3. ALFABET
    # ======================================

    alphabet_answer = handle_alphabet(
        user_message,
        level,
        lesson
    )

    if alphabet_answer:
        return return_with_memory(
            alphabet_answer,
            session_id
        )

    # ======================================
    # 4. NOWE PERSONALIZOWANE ĆWICZENIE
    # ======================================

    personalized_exercise_commands = [
        "übe mit mir",
        "üb mit mir",
        "lass uns üben",
        "lass uns deutsch üben",
        "mach eine übung mit mir",
        "gib mir eine persönliche übung"
    ]

    if message in personalized_exercise_commands:

        personalized_answer = (
            create_personalized_exercise(
                state
            )
        )

        return return_with_memory(
            personalized_answer,
            session_id
        )

    # ======================================
    # 5. ODPOWIEDŹ NA AKTYWNE
    #    PERSONALIZOWANE ĆWICZENIE
    # ======================================

    if get_personalized_exercise(
        state
    ):

        personalized_exercise_answer = (
            handle_personalized_exercise_answer(
                user_message,
                state
            )
        )

        if personalized_exercise_answer:
            return return_with_memory(
                personalized_exercise_answer,
                session_id
            )

    # ======================================
    # 6. PAMIĘĆ I INFORMACJE O UŻYTKOWNIKU
    # ======================================

    user_memory_answer = handle_user_memory(
        user_message,
        session_id
    )

    if user_memory_answer:
        return return_with_memory(
            user_memory_answer,
            session_id
        )

    # ======================================
    # 7. PAMIĘĆ NAUKI SŁOWNICTWA
    # ======================================

    memory_answer = handle_memory(
        user_message,
        state
    )

    if memory_answer:
        return return_with_memory(
            memory_answer,
            session_id
        )

    # ======================================
    # 8. KONTYNUACJA AKTUALNEGO TEMATU
    # ======================================

    topic_answer = handle_topic_follow_up(
        user_message,
        session_id
    )

    if topic_answer:
        return return_with_memory(
            topic_answer,
            session_id
        )

    # ======================================
    # 9. PORÓWNANIA
    # ======================================

    comparison_answer = handle_comparison(
        user_message,
        state,
        session_id
    )

    if comparison_answer:
        return return_with_memory(
            comparison_answer,
            session_id
        )

    # ======================================
    # 10. SŁOWNICTWO
    # ======================================

    vocabulary_answer = handle_vocabulary(
        user_message,
        state
    )

    if vocabulary_answer:
        return return_with_memory(
            vocabulary_answer,
            session_id
        )

    # ======================================
    # 11. ROZPOZNAWANIE INTENCJI
    # ======================================

    intent_answer = handle_intent(
        user_message,
        session_id
    )

    if intent_answer:

        remember_current_topic(
            user_message,
            session_id
        )

        remember_current_comparison(
            user_message,
            session_id
        )

        return return_with_memory(
            intent_answer,
            session_id
        )

    # ======================================
    # 12. ZNANE PYTANIA I ZWROTY
    # ======================================

    known_answer = find_response(
        user_message,
        level,
        lesson,
        session_id
    )

    if known_answer:
        return return_with_memory(
            known_answer,
            session_id
        )

    # ======================================
    # 13. ODPOWIEDŹ KONTEKSTOWA
    # ======================================

    context_answer = handle_context(
        user_message,
        session_id
    )

    if context_answer:
        return return_with_memory(
            context_answer,
            session_id
        )

    # ======================================
    # 14. BRAK WIEDZY
    # ======================================

    return return_with_memory(
        (
            "Ich habe dich verstanden, "
            "aber diese Antwort habe ich "
            "noch nicht gelernt."
        ),
        session_id
    )
