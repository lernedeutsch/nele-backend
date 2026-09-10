# ==========================================
# NELE – KONTYNUACJA OSTATNIEJ AKTYWNOŚCI
# ==========================================

from brain.logic.matcher import (
    normalize
)

from brain.logic.vocabulary_modules.practice import (
    start_vocabulary_practice
)


# ==========================================
# KONTYNUACJA OSTATNIEJ AKTYWNOŚCI
# ==========================================

def handle_continue_last_activity(
    user_message,
    state
):

    if state.get(
        "last_question"
    ) != "continue_last_activity":

        return None


    message = normalize(
        user_message
    )


    # ======================================
    # TAK
    # ======================================

    yes_answers = {
        "ja",
        "ja gern",
        "ja gerne",
        "gerne",
        "gern",
        "klar",
        "okay",
        "ok",
        "natürlich",
        "ja bitte",
        "machen wir",
        "weiter"
    }


    if message in yes_answers:

        last_activity = state.get(
            "last_activity"
        )

        last_activity_detail = state.get(
            "last_activity_detail"
        )


        # ==================================
        # OSTATNIO – SŁOWNICTWO
        # ==================================

        if (
            last_activity == "vocabulary"
            and last_activity_detail
        ):

            state[
                "last_question"
            ] = None

            practice_answer = (
                start_vocabulary_practice(
                    (
                        "übe mit mir das wort "
                        + str(
                            last_activity_detail
                        )
                    ),
                    state
                )
            )

            if practice_answer:

                return (
                    "Gerne! "
                    + practice_answer
                )


        # ==================================
        # BRAK MOŻLIWOŚCI WZNOWIENIA
        # ==================================

        state[
            "last_question"
        ] = None

        return (
            "Gerne! "
            "Was möchtest du heute üben?"
        )


    # ======================================
    # NIE
    # ======================================

    no_answers = {
        "nein",
        "nein danke",
        "nein lieber nicht",
        "nicht heute",
        "lieber nicht",
        "etwas anderes",
        "was anderes"
    }


    if message in no_answers:

        state[
            "last_question"
        ] = None

        return (
            "Kein Problem. "
            "Was möchtest du heute üben?"
        )


    # ======================================
    # INNA ODPOWIEDŹ
    # ======================================

    return None
