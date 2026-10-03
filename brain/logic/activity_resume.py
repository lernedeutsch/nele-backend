# ==========================================
# NELE – KONTYNUACJA AKTYWNEGO TRENINGU
# TEACHER MODE
# ==========================================

from brain.logic.matcher import (
    normalize
)

from brain.logic.vocabulary_modules.practice import (
    start_vocabulary_practice,
    is_vocabulary_practice_active,
    get_practice_opposite
)

from brain.logic.vocabulary_modules.helpers import (
    display_vocabulary_word
)

from brain.logic.error_practice import (
    is_error_practice_active
)

from brain.memory.error_memory import (
    get_error_summary
)

from brain.logic.lesson_teaching import (
    is_lesson_teaching_active,
    get_current_lesson_prompt
)

from brain.logic.dialogue_engine import (
    is_dialogue_active,
    get_current_dialogue_prompt,
)

from brain.logic.personal_sentences import (
    get_current_personal_sentence_practice_prompt,
)


# ==========================================
# WZNOWIENIE AKTYWNEGO SŁOWNICTWA
# ==========================================

def resume_vocabulary_training(
    state
):

    if state is None:
        return None


    if not is_vocabulary_practice_active(
        state
    ):

        return None


    word = state.get(
        "vocabulary_practice_word"
    )


    if not word:
        return None


    practice_type = state.get(
        "vocabulary_practice_type"
    )


    display_word = display_vocabulary_word(
        word
    )


    # ======================================
    # ZNACZENIE SŁOWA
    # ======================================

    if practice_type == "meaning":

        return (
            "Jetzt machen wir weiter. "
            f"Was bedeutet „{display_word}“?"
        )


    # ======================================
    # PRZECIWIEŃSTWO
    # ======================================

    if practice_type == "opposite":

        opposite = get_practice_opposite(
            word
        )


        if not opposite:
            return None


        return (
            "Jetzt machen wir weiter. "
            f"Was ist das Gegenteil von "
            f"„{display_word}“?"
        )


    return None


# ==========================================
# WZNOWIENIE AKTYWNEGO ĆWICZENIA BŁĘDU
# ==========================================

def resume_error_training(
    state
):

    if state is None:
        return None


    if not is_error_practice_active(
        state
    ):

        return None


    error_type = state.get(
        "error_practice_type"
    )


    if not error_type:
        return None


    summary = get_error_summary(
        state,
        error_type
    )


    if not summary:
        return None


    wrong_sentence = summary.get(
        "last_wrong"
    )

    correct_sentence = summary.get(
        "last_correct"
    )


    step = state.get(
        "error_practice_step",
        1
    )


    try:

        step = int(
            step
        )

    except (
        TypeError,
        ValueError
    ):

        step = 1


    # ======================================
    # KROK 1
    # WYBÓR 1 / 2
    # ======================================

    if (
        step == 1
        and
        wrong_sentence
        and
        correct_sentence
    ):

        return (
            "Jetzt machen wir weiter. "
            "Welcher Satz ist richtig?\n\n"
            f"1. {wrong_sentence}\n"
            f"2. {correct_sentence}"
        )


    # ======================================
    # KROK 2
    # SAMODZIELNE POWIEDZENIE ZDANIA
    # ======================================

    if step == 2:

        return (
            "Jetzt machen wir weiter. "
            "Sag den richtigen Satz "
            "jetzt bitte selbst."
        )


    if step == 3:

        return (
            "Jetzt machen wir genau dort weiter. "
            "Jetzt ohne Auswahl: Was sagst du?"
        )


    return None


# ==========================================
# WZNOWIENIE:
# WIR BEGRÜSSEN UNS
# ==========================================

def resume_greeting_lesson(
    step
):

    if step == 1:

        return (
            "Jetzt machen wir weiter. "
            "Es ist Morgen. "
            "Was sagst du?"
        )


    if step == 2:

        return (
            "Jetzt machen wir weiter. "
            "Jetzt ist es tagsüber. "
            "Was sagst du?"
        )


    if step == 3:

        return (
            "Jetzt machen wir weiter. "
            "Jetzt ist es Abend. "
            "Was sagst du?"
        )


    if step == 4:

        return (
            "Jetzt machen wir weiter. "
            "Wenn du jemanden ganz locker "
            "begrüßt, was kannst du sagen?"
        )


    if step == 5:

        return (
            "Jetzt machen wir weiter. "
            "Du verabschiedest dich von "
            "einem Freund. "
            "Was sagst du?"
        )


    return None


# ==========================================
# WZNOWIENIE:
# ICH STELLE MICH VOR
# ==========================================

def resume_introduction_lesson(
    step
):

    if step == 1:

        return (
            "Jetzt machen wir weiter. "
            "Stell dich bitte vor. "
            "Wie heißt du?"
        )


    if step == 2:

        return (
            "Jetzt machen wir weiter. "
            "Wie fragst du informell "
            "nach dem Namen?"
        )


    if step == 3:

        return (
            "Jetzt machen wir weiter. "
            "Wie fragst du einen Gast "
            "im Hotel höflich nach dem Namen?"
        )


    return None


# ==========================================
# WZNOWIENIE AKTYWNEJ LEKCJI
# ==========================================

def resume_lesson_training(
    state
):

    if state is None:
        return None


    if not is_lesson_teaching_active(
        state
    ):

        return None


    # Główny, wspólny mechanizm wznowienia.
    # Działa zarówno dla starej Lektion 1,
    # jak i dla przyszłych lekcji opartych
    # na Generic Lesson Engine.
    current_prompt = get_current_lesson_prompt(
        state
    )


    if current_prompt:

        return current_prompt


    # Poniżej zostaje tylko kompatybilność
    # ze starszymi zapisami stanu.
    section = state.get(
        "lesson_teaching_section"
    )


    if not section:
        return None


    step = state.get(
        "lesson_teaching_step",
        1
    )


    try:

        step = int(
            step
        )

    except (
        TypeError,
        ValueError
    ):

        step = 1


    section_normalized = normalize(
        section
    )


    # ======================================
    # WIR BEGRÜSSEN UNS
    # ======================================

    if (
        section_normalized
        ==
        normalize(
            "Wir begrüßen uns"
        )
    ):

        return resume_greeting_lesson(
            step
        )


    # ======================================
    # ICH STELLE MICH VOR
    # ======================================

    if (
        section_normalized
        ==
        normalize(
            "Ich stelle mich vor"
        )
    ):

        return resume_introduction_lesson(
            step
        )


    return None


# ==========================================
# GŁÓWNE WZNOWIENIE TRENINGU
# ==========================================
#
# Niczego tutaj NIE rozpoczynamy od nowa.
#
# Funkcja jedynie odczytuje aktualny stan
# i przypomina dokładnie pytanie, na którym
# uczeń został przerwany.
#
# PRIORYTET:
#
# 1. aktywne ćwiczenie błędu
# 2. aktywne słownictwo
# 3. aktywna lekcja
# ==========================================

def resume_current_training(
    state
):

    if state is None:
        return None


    # ======================================
    # 1. BŁĄD
    # ======================================

    answer = resume_error_training(
        state
    )

    if answer:
        return answer


    # ======================================
    # 2. SŁOWNICTWO
    # ======================================

    answer = resume_vocabulary_training(
        state
    )

    if answer:
        return answer


    # ======================================
    # 3. DIALOG KURSOWY
    # ======================================

    if is_dialogue_active(state):
        answer = get_current_dialogue_prompt(state)
        if answer:
            return answer


    # ======================================
    # 4. MEINE SÄTZE
    # ======================================

    answer = get_current_personal_sentence_practice_prompt(
        state
    )

    if answer:
        return "Jetzt machen wir genau dort weiter. " + answer


    # ======================================
    # 5. LEKCJA
    # ======================================

    answer = resume_lesson_training(
        state
    )

    if answer:
        return answer


    return None


# ==========================================
# STARY MECHANIZM:
# ODPOWIEDŹ NA
# "MÖCHTEST DU DAMIT WEITERMACHEN?"
#
# ZOSTAWIAMY TYMCZASOWO DLA
# KOMPATYBILNOŚCI ZE STARSZYMI DANYMI.
#
# TEACHER MODE NIE POWINIEN JUŻ
# STANDARDOWO Z TEGO KORZYSTAĆ.
# ==========================================

def handle_continue_last_activity(
    user_message,
    state
):

    if state is None:
        return None


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
            and
            last_activity_detail
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
            "Wir machen weiter."
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
            "Kein Problem."
        )


    # ======================================
    # INNA ODPOWIEDŹ
    # ======================================

    return None
