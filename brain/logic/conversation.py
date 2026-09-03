# ==========================================
# NELE – LOGIKA ROZMOWY Z PAMIĘCIĄ SESJI
# ==========================================

from brain.responses.corrections import find_correction

from brain.logic.memory import get_conversation_state

from brain.logic.matcher import (
    normalize,
    clean_short_answer,
    capitalize_value
)

from brain.logic.user_info import (
    extract_user_information
)

from brain.logic.memory_answers import (
    answer_from_memory
)

from brain.logic.context import (
    handle_context_answer
)

from brain.logic.alphabet import (
    handle_alphabet_question
)

from brain.logic.lesson_loader import (
    load_lesson_module
)

from brain.logic.response_engine import (
    find_response
)

from brain.logic.intent_handler import (
    handle_intent
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

    get_conversation_state(
        session_id
    )


    # ======================================
    # 1. KOREKTA BŁĘDÓW
    # ======================================

    correction = find_correction(
        user_message
    )

    if correction:

        corrected = correction[
            "correct"
        ]

        explanation = correction[
            "explanation"
        ]

        corrected_clean = (
            clean_short_answer(
                corrected
            )
        )

        corrected_normalized = (
            normalize(
                corrected_clean
            )
        )


        # ==================================
        # POPRAWIONE IMIĘ
        # ==================================

        if corrected_normalized.startswith(
            "ich heiße "
        ):

            value = corrected_clean[
                len("Ich heiße "):
            ].strip()

            value = capitalize_value(
                value
            )

            corrected = (
                f"Ich heiße {value}."
            )


        elif corrected_normalized.startswith(
            "mein name ist "
        ):

            value = corrected_clean[
                len("Mein Name ist "):
            ].strip()

            value = capitalize_value(
                value
            )

            corrected = (
                f"Mein Name ist {value}."
            )


        # ==================================
        # POPRAWIONE ZDANIE DO PAMIĘCI
        # ==================================

        continuation = (
            extract_user_information(
                corrected,
                session_id
            )
        )

        if continuation:

            return (
                f"{explanation} "
                f"Richtig ist: "
                f"{corrected} "
                f"{continuation}"
            )


        return (
            f"{explanation} "
            f"Richtig ist: "
            f"{corrected}"
        )


    # ======================================
    # 2. ALFABET
    # ======================================

    alphabet_answer = (
        handle_alphabet_question(
            user_message,
            load_lesson_module,
            level,
            lesson
        )
    )

    if alphabet_answer:
        return alphabet_answer


    # ======================================
    # 3. PYTANIA O PAMIĘĆ
    # ======================================

    memory_answer = (
        answer_from_memory(
            user_message,
            session_id
        )
    )

    if memory_answer:
        return memory_answer


    # ======================================
    # 4. ROZPOZNAWANIE INTENCJI
    # ======================================

    intent_answer = (
        handle_intent(
            user_message
        )
    )

    if intent_answer:
        return intent_answer


    # ======================================
    # 5. INFORMACJE O UŻYTKOWNIKU
    # ======================================

    extracted_answer = (
        extract_user_information(
            user_message,
            session_id
        )
    )

    if extracted_answer:
        return extracted_answer


    # ======================================
    # 6. ZNANE PYTANIA I ZWROTY
    # ======================================

    known_answer = (
        find_response(
            user_message,
            level,
            lesson,
            session_id
        )
    )

    if known_answer:
        return known_answer


    # ======================================
    # 7. ODPOWIEDŹ KONTEKSTOWA
    # ======================================

    context_answer = (
        handle_context_answer(
            user_message,
            session_id
        )
    )

    if context_answer:
        return context_answer


    # ======================================
    # 8. BRAK WIEDZY
    # ======================================

    return (
        "Ich habe dich verstanden, "
        "aber diese Antwort habe ich "
        "noch nicht gelernt."
    )
