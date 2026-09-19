# ==========================================
# NELE – ĆWICZENIE Z BŁĘDÓW UCZNIA
# STUDENT MEMORY 2.0
# ADAPTIVE REVIEW 2.0
# ==========================================

from brain.logic.matcher import normalize

from brain.logic.new_learning_resume import (
    set_new_learning_offer
)

from brain.memory.next_learning_step import (
    get_next_new_learning_step
)

from brain.memory.error_memory import (
    get_error_summary,
    get_errors_for_practice,
    get_error_difficulty,
    get_error_examples,
    get_next_error_example,
    mark_error_example_practiced,
    mark_error_practiced
)

from brain.memory.adaptive_review import (
    calculate_answer_quality,
    build_adaptive_review_plan,
    QUALITY_WITH_HELP,
    QUALITY_DIFFICULT,
    QUALITY_GOOD,
    QUALITY_EASY
)

from brain.memory.daily_learning import (
    mark_error_reviewed_today,
    mark_exercise_completed_today,
    record_mistake_today
)


# ==========================================
# NAZWY RODZAJÓW BŁĘDÓW
# ==========================================

ERROR_PRACTICE_LABELS = {

    "word_order":
        "die Wortstellung",

    "article":
        "die Artikel",

    "grammar":
        "die Grammatik",

    "vocabulary":
        "den Wortschatz",

    "spelling":
        "die Rechtschreibung",

    "verb":
        "die Verben",

    "preposition":
        "die Präpositionen"
}


# ==========================================
# DAILY LEARNING MEMORY
# ZAKOŃCZONY TRENING BŁĘDU
# ==========================================

def remember_daily_error_completion(
    state,
    error_type
):

    if state is None:
        return

    if not error_type:
        return


    # ======================================
    # TYP BŁĘDU PRZEĆWICZONY DZISIAJ
    # ======================================

    try:

        mark_error_reviewed_today(
            state,
            error_type
        )

    except Exception as error:

        print(
            f"Daily error review memory error: {error}"
        )


    # ======================================
    # LICZNIK UKOŃCZONYCH ĆWICZEŃ
    # ======================================

    try:

        mark_exercise_completed_today(
            state
        )

    except Exception as error:

        print(
            f"Daily error exercise counter error: {error}"
        )


# ==========================================
# DAILY LEARNING MEMORY
# BŁĘDNA PRÓBA PODCZAS TRENINGU
# ==========================================

def remember_daily_error_mistake(
    state,
    error_type,
    wrong_sentence=None,
    correct_sentence=None
):

    if state is None:
        return

    if not error_type:
        return


    try:

        record_mistake_today(
            state,
            error_type,
            wrong=wrong_sentence,
            correct=correct_sentence
        )

    except Exception as error:

        print(
            f"Daily error mistake memory error: {error}"
        )


# ==========================================
# TEKST DO PORÓWNANIA
# ==========================================

def clean_error_practice_message(
    text
):

    if not text:
        return ""

    text = normalize(
        text
    )

    return text.strip(
        " .?!„“\"'"
    )


# ==========================================
# ŁADNA NAZWA BŁĘDU
# ==========================================

def get_error_practice_label(
    error_type
):

    return ERROR_PRACTICE_LABELS.get(
        error_type,
        "diesen Bereich"
    )


# ==========================================
# RÓWNOWAŻNE POPRAWNE ODPOWIEDZI
# ==========================================

def is_equivalent_correct_answer(
    user_message,
    correct_sentence,
    error_type=None
):

    user_clean = clean_error_practice_message(
        user_message
    )

    correct_clean = clean_error_practice_message(
        correct_sentence
    )


    if (
        user_clean
        and
        user_clean == correct_clean
    ):

        return True


    error_type = str(
        error_type or ""
    ).strip().lower()


    # Przy umlautach kolejność nie ma znaczenia:
    # "Ö Ä Ü" jest tak samo poprawne jak
    # "Ä, Ö und Ü".
    if error_type == "spelling":

        target_umlauts = {
            char
            for char in "äöü"
            if char in correct_clean
        }

        if target_umlauts == {
            "ä",
            "ö",
            "ü"
        }:

            user_umlauts = {
                char
                for char in "äöü"
                if char in user_clean
            }

            if user_umlauts == target_umlauts:
                return True


    return False


# ==========================================
# CZY ĆWICZENIE JEST AKTYWNE
# ==========================================

def is_error_practice_active(
    state
):

    if not state:
        return False

    return bool(
        state.get(
            "error_practice_active",
            False
        )
    )


# ==========================================
# CZY ODPOWIEDŹ POCHODZIŁA Z MIKROFONU
# ==========================================

def is_voice_input(
    state
):

    if not state:
        return False


    input_mode = (
        state.get(
            "last_input_mode"
        )
        or
        state.get(
            "input_mode"
        )
        or
        ""
    )


    input_mode = str(
        input_mode
    ).strip().lower()


    return input_mode in {
        "voice",
        "speech",
        "microphone",
        "mic"
    }


# ==========================================
# LICZNIK NIEUDANYCH PRÓB
# ==========================================

def increase_error_practice_attempts(
    state
):

    attempts = state.get(
        "error_practice_attempts",
        0
    )


    try:

        attempts = int(
            attempts
        )

    except (
        TypeError,
        ValueError
    ):

        attempts = 0


    attempts += 1


    state[
        "error_practice_attempts"
    ] = attempts


    return attempts


# ==========================================
# ZMIANA TRUDNOŚCI
# ==========================================

def calculate_updated_difficulty(
    current_difficulty,
    quality
):

    try:

        difficulty = float(
            current_difficulty
        )

    except (
        TypeError,
        ValueError
    ):

        difficulty = 0.5


    if quality >= QUALITY_EASY:

        difficulty -= 0.08

    elif quality == QUALITY_GOOD:

        difficulty -= 0.04

    elif quality == QUALITY_DIFFICULT:

        difficulty += 0.04

    elif quality <= QUALITY_WITH_HELP:

        difficulty += 0.08


    return max(
        0.0,
        min(
            1.0,
            difficulty
        )
    )


# ==========================================
# KOLEJNY KONKRETNY BŁĄD W TEJ KATEGORII
# ==========================================

def get_next_pending_error_example(
    state,
    error_type
):

    try:

        examples = get_error_examples(
            state,
            error_type
        )

    except Exception as error:

        print(
            f"Pending error example error: {error}"
        )

        return None


    if not isinstance(
        examples,
        list
    ):

        return None


    candidates = [
        example
        for example in examples
        if (
            isinstance(
                example,
                dict
            )
            and
            example.get(
                "needs_practice",
                False
            )
            and
            not example.get(
                "mastered",
                False
            )
        )
    ]


    if not candidates:
        return None


    candidates.sort(
        key=lambda example: (
            int(
                example.get(
                    "count",
                    0
                )
                or
                0
            ),
            -int(
                example.get(
                    "practice_count",
                    0
                )
                or
                0
            )
        ),
        reverse=True
    )


    return candidates[0]


# ==========================================
# ZAKOŃCZENIE ĆWICZENIA
# ==========================================

def finish_error_practice(
    state
):

    if state is None:
        return


    state[
        "error_practice_active"
    ] = False

    state[
        "error_practice_type"
    ] = None

    state[
        "error_practice_step"
    ] = 0

    state[
        "error_practice_attempts"
    ] = 0

    state[
        "error_practice_used_hint"
    ] = False


    state[
        "error_practice_example_wrong"
    ] = None

    state[
        "error_practice_example_correct"
    ] = None


# ==========================================
# NASTĘPNY KROK PO ĆWICZENIU BŁĘDU
#
# STARA FUNKCJA ZOSTAJE
# DLA KOMPATYBILNOŚCI.
#
# W NOWYM TEACHER MODE NIE JEST JUŻ
# WYWOŁYWANA AUTOMATYCZNIE PO ZAKOŃCZENIU
# BŁĘDU.
#
# DALSZYM KROKIEM STERUJE:
#
# conversation_error_training.py
# ->
# create_teacher_directed_follow_up()
#
# Dzięki temu nie uruchamiamy
# następnej lekcji dwa razy.
# ==========================================

def prepare_learning_after_error(
    state
):

    if state is None:
        return None


    try:

        plan = get_next_new_learning_step(
            state
        )

    except Exception as error:

        print(
            f"Next learning after error: {error}"
        )

        return None


    if not plan:
        return None


    message = str(
        plan.get(
            "message",
            ""
        )
        or
        ""
    ).strip()


    if not message:
        return None


    try:

        offer_saved = set_new_learning_offer(
            state,
            plan
        )

    except Exception as error:

        print(
            f"New learning offer after error: {error}"
        )

        offer_saved = False


    if offer_saved:

        if message.endswith(
            "?"
        ):

            return message


        return (
            f"{message} "
            "Möchtest du damit anfangen?"
        )


    return message


# ==========================================
# ROZPOCZĘCIE ĆWICZENIA
# ==========================================

def start_error_practice(
    state,
    error_type=None
):

    if state is None:

        return (
            "Im Moment kann ich kein "
            "Fehlertraining starten."
        )


    # ======================================
    # JEŚLI NIE PODANO TYPU BŁĘDU,
    # BIORĘ PIERWSZY DO POWTÓRKI
    # ======================================

    if not error_type:

        errors = get_errors_for_practice(
            state
        )


        if not errors:

            return (
                "Wir machen später mit deinen "
                "Fehlern weiter. "
                "Im Moment gibt es nichts zu üben."
            )


        error_type = errors[0]


    # ======================================
    # POBRANIE PRZYKŁADU
    # ======================================

    summary = get_error_summary(
        state,
        error_type
    )


    if not summary:

        return (
            "Dazu habe ich noch kein "
            "passendes Beispiel gespeichert."
        )


    example = get_next_error_example(
        state,
        error_type
    )


    if isinstance(
        example,
        dict
    ):

        wrong_sentence = example.get(
            "wrong"
        )

        correct_sentence = example.get(
            "correct"
        )

    else:

        wrong_sentence = summary.get(
            "last_wrong"
        )

        correct_sentence = summary.get(
            "last_correct"
        )


    if not wrong_sentence or not correct_sentence:

        return (
            "Dazu habe ich noch kein "
            "vollständiges Beispiel gespeichert."
        )


    # ======================================
    # USTAWIENIE AKTYWNEGO ĆWICZENIA
    # ======================================

    state[
        "error_practice_active"
    ] = True

    state[
        "error_practice_type"
    ] = error_type

    state[
        "error_practice_example_wrong"
    ] = str(
        wrong_sentence
    ).strip()

    state[
        "error_practice_example_correct"
    ] = str(
        correct_sentence
    ).strip()

    state[
        "error_practice_step"
    ] = 1


    # ======================================
    # ADAPTIVE REVIEW
    # ======================================

    state[
        "error_practice_attempts"
    ] = 0

    state[
        "error_practice_used_hint"
    ] = False


    label = get_error_practice_label(
        error_type
    )


    return (
        f"Dann üben wir kurz {label}. "
        f"Welche Antwort ist richtig?\n\n"
        f"1. {wrong_sentence}\n"
        f"2. {correct_sentence}"
    )


# ==========================================
# CZY ODPOWIEDŹ OZNACZA:
# DRUGI WARIANT
# ==========================================

def is_second_answer(
    user_message
):

    message = clean_error_practice_message(
        user_message
    )

    answers = {
        "2",
        "satz 2",
        "nummer 2",
        "die 2",
        "der zweite",
        "der zweite satz",
        "zweite",
        "zwei"
    }

    return message in answers


# ==========================================
# CZY ODPOWIEDŹ OZNACZA:
# PIERWSZY WARIANT
# ==========================================

def is_first_answer(
    user_message
):

    message = clean_error_practice_message(
        user_message
    )

    answers = {
        "1",
        "satz 1",
        "nummer 1",
        "die 1",
        "der erste",
        "der erste satz",
        "erste",
        "eins"
    }

    return message in answers


# ==========================================
# CZY UŻYTKOWNIK CHCE ZAKOŃCZYĆ
# ==========================================

def wants_to_stop_error_practice(
    user_message
):

    message = clean_error_practice_message(
        user_message
    )

    stop_answers = {
        "stop",
        "stopp",
        "aufhören",
        "ich möchte aufhören",
        "nicht mehr",
        "ende"
    }

    return message in stop_answers


# ==========================================
# KROK 1
# WYBÓR POPRAWNEGO ZDANIA
# ==========================================

def handle_error_practice_step_one(
    user_message,
    state,
    summary
):

    wrong_sentence = summary.get(
        "last_wrong"
    )

    correct_sentence = summary.get(
        "last_correct"
    )


    user_clean = clean_error_practice_message(
        user_message
    )

    correct_clean = clean_error_practice_message(
        correct_sentence
    )

    wrong_clean = clean_error_practice_message(
        wrong_sentence
    )


    # ======================================
    # DOBRA ODPOWIEDŹ
    # ======================================

    if (
        is_second_answer(
            user_message
        )
        or
        is_equivalent_correct_answer(
            user_message,
            correct_sentence,
            state.get(
                "error_practice_type"
            )
        )
    ):

        state[
            "error_practice_step"
        ] = 2


        return (
            "Richtig! Sehr gut. "
            f"„{correct_sentence}“ ist korrekt. "
            "Sag die richtige Antwort "
            "jetzt bitte selbst."
        )


    # ======================================
    # ZŁA ODPOWIEDŹ
    # ======================================

    if (
        is_first_answer(
            user_message
        )
        or
        user_clean == wrong_clean
    ):

        increase_error_practice_attempts(
            state
        )


        error_type = state.get(
            "error_practice_type"
        )


        remember_daily_error_mistake(
            state,
            error_type,
            wrong_sentence=wrong_sentence,
            correct_sentence=correct_sentence
        )


        hints = {
            "word_order": "Achte auf die Wortstellung.",
            "grammar": "Achte auf die richtige Formulierung.",
            "vocabulary": "Achte auf den passenden Ausdruck.",
            "spelling": "Achte auf die richtige Schreibweise.",
            "verb": "Achte auf die richtige Verbform.",
            "article": "Achte auf den richtigen Artikel.",
            "preposition": "Achte auf die richtige Präposition.",
        }

        hint = hints.get(
            str(error_type or "").strip().lower(),
            "Achte auf die richtige Form."
        )

        return (
            "Noch nicht. "
            f"{hint} "
            "Welche Antwort ist richtig?\n\n"
            f"1. {wrong_sentence}\n"
            f"2. {correct_sentence}"
        )


    # ======================================
    # NIEJASNA ODPOWIEDŹ
    #
    # Nie zapisujemy jej jako błąd,
    # ponieważ może to być np. komenda,
    # pytanie albo niezrozumiała odpowiedź.
    # ======================================

    return (
        "Antworte bitte mit 1 oder 2. "
        "Welche Antwort ist richtig?\n\n"
        f"1. {wrong_sentence}\n"
        f"2. {correct_sentence}"
    )


# ==========================================
# KROK 2
# SAMODZIELNE POWIEDZENIE ZDANIA
# ==========================================

def handle_error_practice_step_two(
    user_message,
    state,
    summary
):

    correct_sentence = summary.get(
        "last_correct"
    )

    wrong_sentence = summary.get(
        "last_wrong"
    )


    user_clean = clean_error_practice_message(
        user_message
    )

    correct_clean = clean_error_practice_message(
        correct_sentence
    )


    # ======================================
    # DOBRA ODPOWIEDŹ
    # ======================================

    if is_equivalent_correct_answer(
        user_message,
        correct_sentence,
        state.get(
            "error_practice_type"
        )
    ):

        error_type = state.get(
            "error_practice_type"
        )


        if error_type:

            # ==================================
            # ILE WCZEŚNIEJ BYŁO BŁĘDNYCH PRÓB?
            # ==================================

            attempts = state.get(
                "error_practice_attempts",
                0
            )


            try:

                attempts = int(
                    attempts
                )

            except (
                TypeError,
                ValueError
            ):

                attempts = 0


            attempts = max(
                0,
                attempts
            )


            # ==================================
            # CZY UŻYTKOWNIK DOSTAŁ PODPOWIEDŹ?
            # ==================================

            used_hint = bool(
                state.get(
                    "error_practice_used_hint",
                    False
                )
            )


            # ==================================
            # OCENA JAKOŚCI 1–4
            # ==================================

            quality = calculate_answer_quality(
                attempts=attempts,
                used_hint=used_hint
            )


            # ==================================
            # OBECNA TRUDNOŚĆ
            # ==================================

            current_difficulty = (
                get_error_difficulty(
                    state,
                    error_type
                )
            )


            # ==================================
            # NOWA TRUDNOŚĆ
            # ==================================

            new_difficulty = (
                calculate_updated_difficulty(
                    current_difficulty,
                    quality
                )
            )


            # ==================================
            # DOTYCHCZASOWA SERIA
            # ==================================

            current_streak = summary.get(
                "correct_streak",
                0
            )


            try:

                current_streak = int(
                    current_streak
                )

            except (
                TypeError,
                ValueError
            ):

                current_streak = 0


            current_streak = max(
                0,
                current_streak
            )


            # ==================================
            # ADAPTIVE REVIEW 2.0
            # ==================================

            review_plan = (
                build_adaptive_review_plan(
                    attempts=attempts,
                    used_hint=used_hint,
                    correct_streak=current_streak,
                    difficulty=new_difficulty
                )
            )


            result = review_plan.get(
                "quality_name",
                "correct"
            )


            next_review_at = (
                review_plan.get(
                    "next_review_at"
                )
            )


            # ==================================
            # CZY ODPOWIEDŹ BYŁA GŁOSOWA
            # ==================================

            spoken = is_voice_input(
                state
            )


            # ==================================
            # STUDENT MEMORY 2.0
            # ==================================

            mark_error_practiced(
                state,
                error_type,
                result=result,
                spoken=spoken,
                quality=quality,
                next_review_at=next_review_at,
                difficulty=new_difficulty
            )


            mark_error_example_practiced(
                state,
                error_type,
                wrong_sentence,
                correct_sentence,
                result="correct"
            )


            # ==================================
            # DAILY LEARNING MEMORY
            #
            # Błąd został poprawnie
            # przećwiczony i zakończony.
            # ==================================

            remember_daily_error_completion(
                state,
                error_type
            )


            # ==================================
            # CZY W TEJ SAMEJ KATEGORII
            # ZOSTAŁ JESZCZE INNY BŁĄD?
            #
            # Jeżeli tak, ćwiczymy go od razu.
            # Użytkownik nie musi zamykać
            # i ponownie otwierać Nele.
            # ==================================

            next_example = (
                get_next_pending_error_example(
                    state,
                    error_type
                )
            )


            if isinstance(
                next_example,
                dict
            ):

                next_wrong = str(
                    next_example.get(
                        "wrong"
                    )
                    or
                    ""
                ).strip()

                next_correct = str(
                    next_example.get(
                        "correct"
                    )
                    or
                    ""
                ).strip()


                if (
                    next_wrong
                    and
                    next_correct
                ):

                    state[
                        "error_practice_active"
                    ] = True

                    state[
                        "error_practice_type"
                    ] = error_type

                    state[
                        "error_practice_example_wrong"
                    ] = next_wrong

                    state[
                        "error_practice_example_correct"
                    ] = next_correct

                    state[
                        "error_practice_step"
                    ] = 1

                    state[
                        "error_practice_attempts"
                    ] = 0

                    state[
                        "error_practice_used_hint"
                    ] = False


                    return (
                        "Sehr gut! Genau richtig: "
                        f"„{correct_sentence}“ "
                        "In diesem Bereich ist noch ein "
                        "anderer Fehler offen. "
                        "Schauen wir ihn uns gleich an. "
                        "Welche Antwort ist richtig?\n\n"
                        f"1. {next_wrong}\n"
                        f"2. {next_correct}"
                    )


        # ======================================
        # KONIEC ĆWICZENIA BŁĘDU
        # ======================================

        finish_error_practice(
            state
        )


        # ======================================
        # WAŻNE:
        #
        # NIE URUCHAMIAMY TUTAJ
        # NASTĘPNEJ LEKCJI.
        #
        # conversation_error_training.py
        # wykryje zakończenie ćwiczenia
        # i wywoła:
        #
        # create_teacher_directed_follow_up()
        #
        # Dzięki temu działa jedna kolejność:
        #
        # słówka
        # -> błędy
        # -> przypomnienie lekcji
        # -> ewentualna powtórka lekcji
        # -> dalsza nauka
        #
        # bez podwójnego komunikatu.
        # ======================================

        return (
            "Sehr gut! Genau richtig: "
            f"„{correct_sentence}“ "
            "Diesen Fehler hast du jetzt geübt."
        )


    # ======================================
    # ZŁA ODPOWIEDŹ
    # ======================================

    increase_error_practice_attempts(
        state
    )


    state[
        "error_practice_used_hint"
    ] = True


    error_type = state.get(
        "error_practice_type"
    )


    remember_daily_error_mistake(
        state,
        error_type,
        wrong_sentence=user_message,
        correct_sentence=correct_sentence
    )


    return (
        "Fast. "
        f"Richtig ist: „{correct_sentence}“ "
        "Sag die richtige Antwort bitte noch einmal."
    )


# ==========================================
# GŁÓWNA OBSŁUGA AKTYWNEGO ĆWICZENIA
# ==========================================

def handle_error_practice(
    user_message,
    state
):

    if state is None:
        return None


    if not is_error_practice_active(
        state
    ):

        return None


    # ======================================
    # STOP
    # ======================================

    if wants_to_stop_error_practice(
        user_message
    ):

        finish_error_practice(
            state
        )

        return (
            "Okay, wir beenden das "
            "Fehlertraining."
        )


    # ======================================
    # AKTUALNY TYP BŁĘDU
    # ======================================

    error_type = state.get(
        "error_practice_type"
    )


    if not error_type:

        finish_error_practice(
            state
        )

        return None


    summary = get_error_summary(
        state,
        error_type
    )


    if not summary:

        finish_error_practice(
            state
        )

        return None


    active_wrong = str(
        state.get(
            "error_practice_example_wrong"
        )
        or
        ""
    ).strip()

    active_correct = str(
        state.get(
            "error_practice_example_correct"
        )
        or
        ""
    ).strip()


    if active_wrong and active_correct:

        summary = dict(
            summary
        )

        summary[
            "last_wrong"
        ] = active_wrong

        summary[
            "last_correct"
        ] = active_correct


    step = state.get(
        "error_practice_step",
        1
    )


    # ======================================
    # KROK 1
    # ======================================

    if step == 1:

        return handle_error_practice_step_one(
            user_message,
            state,
            summary
        )


    # ======================================
    # KROK 2
    # ======================================

    if step == 2:

        return handle_error_practice_step_two(
            user_message,
            state,
            summary
        )


    # ======================================
    # NIEZNANY KROK
    # ======================================

    finish_error_practice(
        state
    )

    return None
