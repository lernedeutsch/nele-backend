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
    answer_vocabulary_plural,
    answer_vocabulary_opposite,
    answer_simple_explanation,
    start_vocabulary_practice
)

from brain.memory.vocabulary_memory import (
    remember_practiced_word
)


# ==========================================
# GEÜBTES WORT SPEICHERN
# ==========================================

def remember_current_practiced_word(
    state
):

    if state is None:
        return

    word = state.get(
        "current_vocabulary_word"
    )

    if not word:
        return

    remember_practiced_word(
        word,
        state
    )


# ==========================================
# HAUPTVERARBEITUNG DES WORTSCHATZES
# ==========================================

def handle_vocabulary(
    user_message,
    state
):

    # ======================================
    # WORTSCHATZÜBUNG STARTEN
    # ======================================

    answer = start_vocabulary_practice(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # BEDEUTUNG
    # ======================================

    answer = answer_vocabulary_question(
        user_message,
        state
    )

    if answer:

        remember_current_practiced_word(
            state
        )

        return answer


    # ======================================
    # EINFACHE ERKLÄRUNG
    # ======================================

    answer = answer_simple_explanation(
        user_message,
        state
    )

    if answer:

        remember_current_practiced_word(
            state
        )

        return answer


    # ======================================
    # ARTIKEL
    # ======================================

    answer = answer_vocabulary_article(
        user_message,
        state
    )

    if answer:

        remember_current_practiced_word(
            state
        )

        return answer


    # ======================================
    # PLURAL
    # ======================================

    answer = answer_vocabulary_plural(
        user_message,
        state
    )

    if answer:

        remember_current_practiced_word(
            state
        )

        return answer


    # ======================================
    # BEISPIEL
    # ======================================

    answer = answer_vocabulary_example(
        user_message,
        state
    )

    if answer:

        remember_current_practiced_word(
            state
        )

        return answer


    # ======================================
    # VERWENDUNG
    # ======================================

    answer = answer_vocabulary_usage(
        user_message,
        state
    )

    if answer:

        remember_current_practiced_word(
            state
        )

        return answer


    # ======================================
    # ÄHNLICHES WORT
    # ======================================

    answer = answer_similar_vocabulary_word(
        user_message,
        state
    )

    if answer:

        remember_current_practiced_word(
            state
        )

        return answer


    # ======================================
    # GEGENTEIL
    # ======================================

    answer = answer_vocabulary_opposite(
        user_message,
        state
    )

    if answer:

        remember_current_practiced_word(
            state
        )

        return answer


    # ======================================
    # UNTERSCHIED – KONTEXT
    # ======================================

    answer = answer_vocabulary_difference_follow_up(
        user_message,
        state
    )

    if answer:

        remember_current_practiced_word(
            state
        )

        return answer


    # ======================================
    # UNTERSCHIED – DIREKTE FRAGE
    # ======================================

    answer = answer_explicit_vocabulary_difference(
        user_message,
        state
    )

    if answer:

        remember_current_practiced_word(
            state
        )

        return answer


    # ======================================
    # KEINE WORTSCHATZ-ANTWORT
    # ======================================

    return None
