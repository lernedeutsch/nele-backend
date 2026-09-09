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
    validate_personalized_answer
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


    # ======================================
    # WALIDACJA ODPOWIEDZI
    # ======================================

    validation = validate_personalized_answer(
        user_message,
        state
    )

    if not validation:
        return None

    status = validation.get(
        "status"
    )


    # ======================================
    # ODPOWIEDŹ DO PONOWIENIA
    # ======================================

    if status == "retry":

        return validation.get(
            "answer"
        )


    # ======================================
    # ODPOWIEDŹ ZAAKCEPTOWANA
    # ======================================

    if status != "accepted":
        return None

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
    # ĆWICZENIE ZAKOŃCZONE
    # ======================================

    clear_personalized_exercise(
        state
    )


    # ======================================
    # HOBBY
    # ======================================

    if topic == "hobby":

        return (
            f"Sehr gut! "
            f"Das ist ein passender Satz "
            f"zu deinem Hobby {value}. "
            f"Dein Satz lautet: "
            f"„{answer}“"
        )


    # ======================================
    # ULUBIONY KOLOR
    # ======================================

    if topic == "favorite_color":

        return (
            f"Sehr gut! "
            f"Du hast einen Satz über "
            f"deine Lieblingsfarbe "
            f"{value} gebildet: "
            f"„{answer}“"
        )


    # ======================================
    # ULUBIONE SŁOWO
    # ======================================

    if topic == "favorite_word":

        return (
            f"Sehr gut! "
            f"Du hast einen Satz mit "
            f"deinem Lieblingswort "
            f"„{value}“ gebildet: "
            f"„{answer}“"
        )


    # ======================================
    # CEL NAUKI
    # ======================================

    if topic == "learning_goal":

        return (
            f"Sehr gut! "
            f"Wir arbeiten weiter an "
            f"deinem Lernziel {value}."
        )


    # ======================================
    # INNY TEMAT
    # ======================================

    return (
        f"Sehr gut! "
        f"Dein Satz lautet: "
        f"„{answer}“"
    )


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

    if "current_topic" not in state:
        state["current_topic"] = None

    if "current_comparison" not in state:
        state["current_comparison"] = None

    if "current_expression" not in state:
        state["current_expression"] = None

    if "last_example_expression" not in state:
        state["last_example_expression"] = None

    if "example_index" not in state:
        state["example_index"] = -1

    if "current_vocabulary_word" not in state:
        state["current_vocabulary_word"] = None

    if "current_vocabulary_related_word" not in state:
        state["current_vocabulary_related_word"] = None

    if "vocabulary_memory" not in state:
        state["vocabulary_memory"] = {}

    if "user_facts" not in state:
        state["user_facts"] = {}

    if "personalization_exercise" not in state:
        state["personalization_exercise"] = None


    # ======================================
    # NORMALIZACJA WIADOMOŚCI
    # ======================================

    message = normalize(
        user_message
    )


    # ======================================
    # 1. KOREKTA BŁĘDÓW
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
    # 2. ALFABET
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
    # 3. PAMIĘĆ I INFORMACJE O UŻYTKOWNIKU
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
    # 5. ODPOWIEDŹ NA PERSONALIZOWANE
    #    ĆWICZENIE
    # ======================================

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
    # 6. PAMIĘĆ NAUKI SŁOWNICTWA
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
    # 7. KONTYNUACJA AKTUALNEGO TEMATU
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
    # 8. PORÓWNANIA
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
    # 9. SŁOWNICTWO
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
    # 10. ROZPOZNAWANIE INTENCJI
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
    # 11. ZNANE PYTANIA I ZWROTY
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
    # 12. ODPOWIEDŹ KONTEKSTOWA
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
    # 13. BRAK WIEDZY
    # ======================================

    return return_with_memory(
        (
            "Ich habe dich verstanden, "
            "aber diese Antwort habe ich "
            "noch nicht gelernt."
        ),
        session_id
        )
