# ==========================================
# NELE – ROUTER SŁOWNICTWA
# ==========================================

from brain.logic.vocabulary import (
    answer_vocabulary_question,
    answer_vocabulary_example,
    answer_vocabulary_usage,
    answer_similar_vocabulary_word,
    answer_vocabulary_difference_follow_up,
    answer_explicit_vocabulary_difference
)


# ==========================================
# GŁÓWNA OBSŁUGA SŁOWNICTWA
# ==========================================

def handle_vocabulary(
    user_message,
    state
):

    # ======================================
    # ZNACZENIE SŁOWA
    # ======================================

    answer = answer_vocabulary_question(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # PRZYKŁAD
    # ======================================

    answer = answer_vocabulary_example(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # UŻYCIE SŁOWA
    # ======================================

    answer = answer_vocabulary_usage(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # PODOBNE SŁOWO
    # ======================================

    answer = answer_similar_vocabulary_word(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # RÓŻNICA – KONTYNUACJA ROZMOWY
    # ======================================

    answer = answer_vocabulary_difference_follow_up(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # RÓŻNICA – PEŁNE PYTANIE
    # ======================================

    answer = answer_explicit_vocabulary_difference(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # BRAK ODPOWIEDZI SŁOWNIKOWEJ
    # ======================================

    return None
