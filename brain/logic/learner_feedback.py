# ==========================================
# NELE – FEEDBACK FÜR LERNENDE
# NATÜRLICHES DEUTSCH IM ALLTAG
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import normalize

from brain.memory.error_memory import (
    remember_error
)


# ==========================================
# TEXT FÜR VERGLEICH BEREINIGEN
# ==========================================

def clean_feedback_message(
    text
):

    text = normalize(
        text
    )

    return text.strip(
        " .?!„“\"'"
    )


# ==========================================
# BEKANNTE KORREKTUREN
# ==========================================
#
# Nele rozumie błędne zdanie,
# pokazuje naturalną wersję
# i może zapisać błąd
# w Student Memory 2.0.
#
# Rozmowa nie jest przerywana.
# ==========================================

KNOWN_CORRECTIONS = {

    # ======================================
    # NATÜRLICHE A1-GESPRÄCHE
    # ======================================

    "mit mein mann": {
        "corrected_message": "Mit meinem Mann.",
        "feedback": (
            "Fast richtig 😊 Du kannst sagen: "
            "„Mit meinem Mann.“"
        ),
        "error_type": "dative_possessive",
    },

    "ich fahren fahrrad": {
        "corrected_message": "Ich fahre Fahrrad.",
        "feedback": (
            "Fast richtig 😊 Du kannst sagen: "
            "„Ich fahre Fahrrad.“"
        ),
        "error_type": "verb_conjugation",
    },

    "ich fahren gern fahrrad": {
        "corrected_message": "Ich fahre gern Fahrrad.",
        "feedback": (
            "Fast richtig 😊 Du kannst sagen: "
            "„Ich fahre gern Fahrrad.“"
        ),
        "error_type": "verb_conjugation",
    },

    "ich arbeiten heute": {
        "corrected_message": "Ich arbeite heute.",
        "feedback": (
            "Fast richtig 😊 Du kannst sagen: "
            "„Ich arbeite heute.“"
        ),
        "error_type": "verb_conjugation",
    },

    "ich kochen": {
        "corrected_message": "Ich koche.",
        "feedback": (
            "Fast richtig 😊 Du kannst sagen: "
            "„Ich koche.“"
        ),
        "error_type": "verb_conjugation",
    },


    # ======================================
    # WAS SOLL ICH HEUTE LERNEN?
    # ======================================

    "was soll ich lernen heute": {

        "corrected_message":
            "Was soll ich heute lernen?",

        "feedback":
            (
                "Fast! Natürlicher sagt man: "
                "„Was soll ich heute lernen?“"
            ),

        "error_type":
            "word_order"
    },


    # ======================================
    # WAS SOLL ICH HEUTE ÜBEN?
    # ======================================

    "was soll ich üben heute": {

        "corrected_message":
            "Was soll ich heute üben?",

        "feedback":
            (
                "Fast! Natürlicher sagt man: "
                "„Was soll ich heute üben?“"
            ),

        "error_type":
            "word_order"
    },


    # ======================================
    # WAS MACHEN WIR HEUTE?
    # ======================================

    "was machen heute wir": {

        "corrected_message":
            "Was machen wir heute?",

        "feedback":
            (
                "Fast! Natürlicher sagt man: "
                "„Was machen wir heute?“"
            ),

        "error_type":
            "word_order"
    }
}


# ==========================================
# FEEDBACK SUCHEN
# ==========================================

def get_learner_feedback(
    user_message
):

    message = clean_feedback_message(
        user_message
    )

    if not message:
        return None


    correction = KNOWN_CORRECTIONS.get(
        message
    )


    if not correction:
        return None


    return {

        "original_message":
            user_message,

        "corrected_message":
            correction.get(
                "corrected_message"
            ),

        "feedback":
            correction.get(
                "feedback"
            ),

        "error_type":
            correction.get(
                "error_type"
            )
    }


# ==========================================
# CZY ZNALEZIONO BŁĄD
# ==========================================

def has_learner_feedback(
    user_message
):

    return (
        get_learner_feedback(
            user_message
        )
        is not None
    )


# ==========================================
# POPRAWIONA WIADOMOŚĆ DO DALSZEJ OBSŁUGI
# ==========================================

def get_corrected_user_message(
    user_message
):

    feedback = get_learner_feedback(
        user_message
    )


    if not feedback:
        return user_message


    corrected_message = feedback.get(
        "corrected_message"
    )


    if not corrected_message:
        return user_message


    return corrected_message


# ==========================================
# TEKST FEEDBACKU DLA UŻYTKOWNIKA
# ==========================================

def get_feedback_text(
    user_message
):

    feedback = get_learner_feedback(
        user_message
    )


    if not feedback:
        return None


    return feedback.get(
        "feedback"
    )


# ==========================================
# ZAPIS BŁĘDU W STUDENT MEMORY 2.0
# ==========================================

def remember_learner_feedback_error(
    feedback,
    state
):

    if state is None:
        return False


    if not feedback:
        return False


    error_type = feedback.get(
        "error_type"
    )

    original_message = feedback.get(
        "original_message"
    )

    corrected_message = feedback.get(
        "corrected_message"
    )


    if not error_type:
        return False


    return remember_error(
        state,
        error_type,
        original_message,
        corrected_message
    )


# ==========================================
# PRZYGOTOWANIE WIADOMOŚCI
# DO NORMALNEJ ROZMOWY
# ==========================================

def prepare_message_with_feedback(
    user_message,
    state=None
):
    """
    Zwraca:

    (
        wiadomość do dalszej obsługi,
        krótki feedback dla ucznia
    )

    Jeżeli przekazano state,
    znaleziony błąd zostaje również
    zapisany w Student Memory 2.0.

    Przykład:

    użytkownik:
    Was soll ich lernen heute?

    wynik:

    (
        "Was soll ich heute lernen?",
        "Fast! Natürlicher sagt man:
         „Was soll ich heute lernen?“"
    )

    pamięć:

    word_order:
        count += 1
        last_wrong =
            "Was soll ich lernen heute?"
        last_correct =
            "Was soll ich heute lernen?"
        needs_practice = True
    """


    feedback = get_learner_feedback(
        user_message
    )


    if not feedback:

        return (
            user_message,
            None
        )


    # ======================================
    # BŁĄD ZAPISUJEMY W PAMIĘCI
    # ======================================

    if state is not None:

        remember_learner_feedback_error(
            feedback,
            state
        )


    # ======================================
    # POPRAWIONA WIADOMOŚĆ
    # ======================================

    corrected_message = feedback.get(
        "corrected_message"
    )

    feedback_text = feedback.get(
        "feedback"
    )


    if not corrected_message:

        corrected_message = user_message


    return (
        corrected_message,
        feedback_text
    )
