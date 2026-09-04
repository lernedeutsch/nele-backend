# ==========================================
# NELE – ROUTER KOREKTY ZDAŃ
# ==========================================

from brain.responses.corrections import (
    find_correction
)

from brain.logic.matcher import (
    normalize,
    clean_short_answer,
    capitalize_value
)

from brain.logic.user_info import (
    extract_user_information
)


# ==========================================
# OBSŁUGA KOREKTY
# ==========================================

def handle_correction(
    user_message,
    session_id="default"
):

    correction = find_correction(
        user_message
    )

    if not correction:
        return None

    corrected = correction.get(
        "correct"
    )

    explanation = correction.get(
        "explanation"
    )

    if not corrected:
        return None

    if not explanation:
        explanation = "Fast richtig."


    # ======================================
    # CZYSZCZENIE POPRAWIONEGO ZDANIA
    # ======================================

    corrected_clean = clean_short_answer(
        corrected
    )

    corrected_normalized = normalize(
        corrected_clean
    )


    # ======================================
    # ICH HEISSE / ICH HEIẞE
    # ======================================

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


    # ======================================
    # MEIN NAME IST
    # ======================================

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


    # ======================================
    # ZAPAMIĘTANIE INFORMACJI O UŻYTKOWNIKU
    # ======================================

    continuation = extract_user_information(
        corrected,
        session_id
    )

    if continuation:

        return (
            f"{explanation} "
            f"Richtig ist: "
            f"{corrected} "
            f"{continuation}"
        )


    # ======================================
    # ZWYKŁA ODPOWIEDŹ KOREKTY
    # ======================================

    return (
        f"{explanation} "
        f"Richtig ist: "
        f"{corrected}"
    )
