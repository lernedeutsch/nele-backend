# ==========================================
# NELE – OBSŁUGA ALFABETU
# ==========================================

from brain.logic.matcher import normalize


def handle_alphabet_question(
    user_message,
    load_lesson_module,
    level="A1",
    lesson=1
):

    message = normalize(
        user_message
    )

    module = load_lesson_module(
        level,
        lesson
    )

    if module is None:
        return None

    alphabet = getattr(
        module,
        "ALPHABET",
        {}
    )

    if not alphabet:
        return None


    # ======================================
    # JAK WYMAWIA SIĘ LITERĘ?
    # ======================================

    if (
        "wie spricht man" in message
        and "aus" in message
    ):

        words = message.split()

        for word in words:

            clean_word = (
                word
                .strip()
                .strip("?!.:,")
                .lower()
            )

            if clean_word in alphabet:

                pronunciation = alphabet[
                    clean_word
                ]

                display_letter = (
                    clean_word.upper()
                )

                if clean_word == "ß":
                    display_letter = "ß"

                return (
                    f"{display_letter} "
                    f"spricht man "
                    f"„{pronunciation}“ aus."
                )


    # ======================================
    # JAK NAZYWA SIĘ LITERA?
    # ======================================

    if (
        "wie heißt" in message
        or "wie heisst" in message
    ):

        words = message.split()

        for word in words:

            clean_word = (
                word
                .strip()
                .strip("?!.:,")
                .lower()
            )

            if clean_word in alphabet:

                pronunciation = alphabet[
                    clean_word
                ]

                display_letter = (
                    clean_word.upper()
                )

                if clean_word == "ß":
                    display_letter = "ß"

                return (
                    f"{display_letter} "
                    f"heißt "
                    f"„{pronunciation}“."
                )


    # ======================================
    # ESZETT
    # ======================================

    if message in [
        "was ist ß",
        "wie heißt ß",
        "wie heisst ß"
    ]:

        return (
            "Das Zeichen ß heißt Eszett."
        )


    return None
