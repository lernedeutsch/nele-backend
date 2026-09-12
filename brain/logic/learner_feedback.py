# ==========================================
# NELE – FEEDBACK FÜR LERNENDE
# NATÜRLICHES DEUTSCH IM ALLTAG
# ==========================================

from brain.logic.matcher import normalize


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
# Ważne:
#
# Nele rozumie błędne zdanie,
# ale pokazuje użytkownikowi
# naturalną wersję.
#
# Nie przerywamy przez to rozmowy.
# ==========================================

KNOWN_CORRECTIONS = {

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
# PRZYGOTOWANIE WIADOMOŚCI
# DO NORMALNEJ ROZMOWY
# ==========================================

def prepare_message_with_feedback(
    user_message
):
    """
    Zwraca:

    (
        wiadomość do dalszej obsługi,
        krótki feedback dla ucznia
    )

    Przykład:

    użytkownik:
    Was soll ich lernen heute?

    wynik:
    (
        "Was soll ich heute lernen?",
        "Fast! Natürlicher sagt man:
         „Was soll ich heute lernen?“"
    )
    """

    feedback = get_learner_feedback(
        user_message
    )


    if not feedback:

        return (
            user_message,
            None
        )


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
