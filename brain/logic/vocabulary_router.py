# ==========================================
# NELE – WORTSCHATZ-ROUTER
# ==========================================

from brain.logic.vocabulary import (
    answer_vocabulary_question,
    answer_vocabulary_example,
    answer_vocabulary_usage,
    answer_similar_vocabulary_word,
    answer_vocabulary_difference_follow_up,
    answer_explicit_vocabulary_difference,
    answer_vocabulary_article,
    answer_vocabulary_plural
)


# ==========================================
# HAUPTVERARBEITUNG DES WORTSCHATZES
# ==========================================

def handle_vocabulary(
    user_message,
    state
):

    # ======================================
    # BEDEUTUNG
    # ======================================

    answer = answer_vocabulary_question(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # ARTIKEL
    # ======================================

    answer = answer_vocabulary_article(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # PLURAL
    # ======================================

    answer = answer_vocabulary_plural(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # BEISPIEL
    # ======================================

    answer = answer_vocabulary_example(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # VERWENDUNG
    # ======================================

    answer = answer_vocabulary_usage(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # ÄHNLICHES WORT
    # ======================================

    answer = answer_similar_vocabulary_word(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # UNTERSCHIED – KONTEXT
    # ======================================

    answer = answer_vocabulary_difference_follow_up(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # UNTERSCHIED – DIREKTE FRAGE
    # ======================================

    answer = answer_explicit_vocabulary_difference(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # KEINE WORTSCHATZ-ANTWORT
    # ======================================

    return None
