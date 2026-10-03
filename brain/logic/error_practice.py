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
    get_error_item,
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

    # In vocabulary transfer, a one-word target may be produced naturally
    # inside a complete sentence. Example: target "Niederländerin" and learner
    # answer "Ja, sie ist Niederländerin." This is stronger evidence than
    # repeating the isolated model word, so accept it as correct.
    if (
        error_type == "vocabulary"
        and correct_clean
        and len(correct_clean.split()) == 1
        and correct_clean in user_clean.split()
    ):
        return True


    # Natural full sentences can satisfy a one-word vocabulary target.
    if (
        error_type == "vocabulary"
        and correct_clean
        and len(correct_clean.split()) == 1
        and correct_clean in user_clean.split()
    ):
        return True


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


def get_active_error_practice_sentences(state, summary):
    """Return the concrete example currently owned by Error Practice.

    Category-level last_wrong/last_correct describe the latest remembered
    mistake, which may differ from the example selected for this practice
    turn.  The active example in session state is authoritative.
    """
    summary = summary or {}
    wrong = str(
        (state or {}).get("error_practice_example_wrong")
        or summary.get("last_wrong")
        or ""
    ).strip()
    correct = str(
        (state or {}).get("error_practice_example_correct")
        or summary.get("last_correct")
        or ""
    ).strip()
    return wrong, correct


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
# CZY PRZYKŁAD BŁĘDU MA SENS DO POWTÓRKI?
# ==========================================

def is_relevant_error_example(
    example
):

    if not isinstance(
        example,
        dict
    ):

        return False


    wrong = clean_error_practice_message(
        example.get(
            "wrong"
        )
    )

    correct = clean_error_practice_message(
        example.get(
            "correct"
        )
    )


    if not (
        wrong
        and
        correct
    ):

        return False


    # Stare przypadkowe odpowiedzi niezwiązane z zadaniem
    # nie powinny wracać w treningu błędów.
    if correct in {
        "guten morgen",
        "guten tag",
        "guten abend",
        "hallo",
        "tschüss",
        "tschuss",
    }:

        greeting_tokens = {
            "guten",
            "morgen",
            "tag",
            "abend",
            "hallo",
            "hi",
            "hey",
            "tschüss",
            "tschuss",
            "tschüs",
            "wiedersehen",
        }

        if not (
            set(
                wrong.split()
            )
            &
            greeting_tokens
        ):

            # Krótkie odpowiedzi z aktywnego pytania lekcji
            # (np. "h", "k", "p") są prawdziwymi próbami,
            # choć nie zawierają słowa powitania. Długie,
            # niezwiązane zdania nadal ignorujemy.
            wrong_words = wrong.split()

            if not (
                1 <= len(wrong_words) <= 2
                and
                len(wrong) <= 12
            ):

                return False


    return True


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


    # Stare błędnie zaklasyfikowane odpowiedzi
    # oznaczamy trwale jako ignored. Ponieważ
    # get_error_examples() zwraca te same dict-y,
    # zmiana zapisuje się w stanie ucznia.
    for example in examples:

        if not isinstance(
            example,
            dict
        ):
            continue

        if not is_relevant_error_example(
            example
        ):

            example[
                "ignored"
            ] = True

            example[
                "needs_practice"
            ] = False


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
            and
            not example.get(
                "ignored",
                False
            )
        )
    ]


    if not candidates:

        # Obsługa starszej pamięci:
        # jeżeli kategoria nadal mówi "wrong" i nie ma
        # jeszcze daty Adaptive Review, możemy aktywować
        # jeden sensowny nieopanowany przykład.
        error_item = get_error_item(
            error_type,
            state
        )

        if isinstance(
            error_item,
            dict
        ):

            legacy_immediate_review = (
                str(
                    error_item.get(
                        "last_result"
                    )
                    or
                    ""
                ).strip().lower()
                == "wrong"
                and
                not error_item.get(
                    "next_review_at"
                )
            )

            if legacy_immediate_review:

                legacy_candidates = [
                    example
                    for example in examples
                    if (
                        isinstance(
                            example,
                            dict
                        )
                        and
                        not example.get(
                            "mastered",
                            False
                        )
                        and
                        not example.get(
                            "ignored",
                            False
                        )
                    )
                ]

                if legacy_candidates:

                    legacy_candidates.sort(
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

                    legacy_candidates[0][
                        "needs_practice"
                    ] = True

                    error_item[
                        "needs_practice"
                    ] = True

                    return legacy_candidates[0]


            # Po poprawnym ćwiczeniu i przed przyszłym
            # terminem nie wolno samoczynnie wybierać
            # innego "jakiegokolwiek" przykładu.
            error_item[
                "needs_practice"
            ] = False

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
        "error_practice_transfer_attempts"
    ] = 0


    state[
        "error_practice_example_wrong"
    ] = None

    state[
        "error_practice_example_correct"
    ] = None


    state[
        "error_practice_example_context"
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
# KONTEKST KONKRETNEGO BŁĘDU
# ==========================================

def get_error_example_context(
    example,
    wrong_sentence=None,
    correct_sentence=None
):

    if isinstance(
        example,
        dict
    ):

        context = str(
            example.get(
                "context"
            )
            or
            ""
        ).strip()


        if context:
            return context


    # Kompatybilność ze starszą pamięcią:
    # wcześniej zapisywaliśmy tylko parę
    # wrong/correct. Dla najczęstszych zadań
    # Lektion 1 potrafimy odtworzyć sytuację.
    correct = clean_error_practice_message(
        correct_sentence
    )


    fallback_contexts = {
        "guten morgen":
            (
                "Stell dir vor, es ist morgens. "
                "Was sagst du zur Begrüßung?"
            ),

        "guten tag":
            (
                "Es ist tagsüber. "
                "Was sagst du zur Begrüßung?"
            ),

        "guten abend":
            (
                "Es ist Abend. "
                "Was sagst du zur Begrüßung?"
            ),

        "tschüss":
            (
                "Du verabschiedest dich von einem Freund. "
                "Was sagst du?"
            ),

        "wie heißt du":
            (
                "Du möchtest jemanden informell "
                "nach dem Namen fragen. Was sagst du?"
            ),

        "wie heißen sie":
            (
                "Du bist in einer höflichen Situation "
                "im Hotel. Wie fragst du einen Gast "
                "nach dem Namen?"
            ),

        "b":
            "Welcher Buchstabe kommt nach A?",

        "n":
            "Welcher Buchstabe kommt nach M?",

        "y":
            "Welcher Buchstabe kommt vor Z?",

        "ä, ö und ü":
            "Welche drei Umlaute gibt es im Deutschen?",

        "eszett":
            (
                "Welches besondere Zeichen gibt es "
                "außerdem im Deutschen?"
            )
    }


    return fallback_contexts.get(
        correct,
        ""
    )


def build_error_choice_prompt(
    context,
    wrong_sentence,
    correct_sentence
):

    context = str(
        context or ""
    ).strip()


    if context:

        return (
            f"{context}\n\n"
            "Welche Antwort passt hier?\n\n"
            f"1. {wrong_sentence}\n"
            f"2. {correct_sentence}"
        )


    return (
        "Welche Antwort ist richtig?\n\n"
        f"1. {wrong_sentence}\n"
        f"2. {correct_sentence}"
    )


# ==========================================
# TEN SAM CEL NAUKI = JEDNA POWTÓRKA
# ==========================================

def clear_equivalent_pending_error_examples(
    state,
    error_type,
    correct_sentence,
    context
):

    if state is None:
        return

    correct_key = clean_error_practice_message(
        correct_sentence
    )

    context_key = clean_error_practice_message(
        context
    )


    if not correct_key:
        return


    try:

        examples = get_error_examples(
            state,
            error_type
        )

    except Exception as error:

        print(
            f"Equivalent error examples cleanup: {error}"
        )

        return


    for example in examples:

        if not isinstance(
            example,
            dict
        ):

            continue


        example_correct = clean_error_practice_message(
            example.get(
                "correct"
            )
        )

        example_context = clean_error_practice_message(
            example.get(
                "context"
            )
        )


        # Różne błędne odpowiedzi na dokładnie to samo
        # pytanie i z tą samą poprawną odpowiedzią są
        # jednym celem nauki, a nie trzema ćwiczeniami.
        if (
            example_correct == correct_key
            and
            example_context == context_key
        ):

            example[
                "needs_practice"
            ] = False


    error_item = get_error_item(
        error_type,
        state
    )


    if isinstance(
        error_item,
        dict
    ):

        still_pending = any(
            isinstance(example, dict)
            and example.get(
                "needs_practice",
                False
            )
            and not example.get(
                "mastered",
                False
            )
            and not example.get(
                "ignored",
                False
            )
            for example in get_error_examples(
                state,
                error_type
            )
        )

        if not still_pending:

            error_item[
                "needs_practice"
            ] = False


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


    example = get_next_pending_error_example(
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

        wrong_sentence = None
        correct_sentence = None


    context = get_error_example_context(
        example,
        wrong_sentence,
        correct_sentence
    )


    if not wrong_sentence or not correct_sentence:

        finish_error_practice(
            state
        )

        return None


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
        "error_practice_example_context"
    ] = context or None

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

    state[
        "error_practice_transfer_attempts"
    ] = 0


    label = get_error_practice_label(
        error_type
    )


    choice_prompt = build_error_choice_prompt(
        context,
        wrong_sentence,
        correct_sentence
    )


    return choice_prompt


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

    wrong_sentence, correct_sentence = get_active_error_practice_sentences(
        state,
        summary,
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

        # Choosing from a visible 1/2 pair is recognition with assistance,
        # not independent recall. Preserve that evidence for Adaptive Review.
        state["error_practice_used_hint"] = True

        state[
            "error_practice_step"
        ] = 2


        return (
            "Genau. "
            f"Sag jetzt: „{correct_sentence}“"
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

        context = str(
            state.get(
                "error_practice_example_context"
            )
            or
            ""
        ).strip()


        choice_prompt = build_error_choice_prompt(
            context,
            wrong_sentence,
            correct_sentence
        )


        return (
            "Noch nicht. "
            f"{hint} "
            f"{choice_prompt}"
        )


    # ======================================
    # NIEJASNA ODPOWIEDŹ
    #
    # Nie zapisujemy jej jako błąd,
    # ponieważ może to być np. komenda,
    # pytanie albo niezrozumiała odpowiedź.
    # ======================================

    context = str(
        state.get(
            "error_practice_example_context"
        )
        or
        ""
    ).strip()


    choice_prompt = build_error_choice_prompt(
        context,
        wrong_sentence,
        correct_sentence
    )


    return (
        "Antworte bitte mit 1 oder 2. "
        f"{choice_prompt}"
    )


def build_error_transfer_prompt(context, correct_sentence):
    context = str(context or "").strip()
    if context:
        return (
            f"{context}\n\n"
            "Jetzt ohne Auswahl: Was sagst du?"
        )

    # If old memory has no context, use a neutral production cue. Do not
    # expose the target sentence again: this turn measures recall.
    return "Jetzt ohne Hilfe: Sag den richtigen Satz noch einmal."


# ==========================================
# KROK 2
# SAMODZIELNE POWIEDZENIE ZDANIA
# ==========================================

def handle_error_practice_step_two(
    user_message,
    state,
    summary
):

    wrong_sentence, correct_sentence = get_active_error_practice_sentences(
        state,
        summary,
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

        # Repeating a sentence that Nele has just shown is useful, but it
        # is not yet evidence of independent speaking. Remove the model
        # and ask for the same communicative act once more from context.
        state["error_practice_step"] = 3
        context = state.get("error_practice_example_context")
        return (
            "Sehr gut. "
            + build_error_transfer_prompt(context, correct_sentence)
        )

    # The learner is repeating a model Nele has just shown. A wrong attempt
    # must stay inside Error Practice instead of returning None and falling
    # through to unrelated course routing.
    increase_error_practice_attempts(state)
    state["error_practice_used_hint"] = True

    error_type = state.get("error_practice_type")
    remember_daily_error_mistake(
        state,
        error_type,
        wrong_sentence=user_message,
        correct_sentence=correct_sentence,
    )

    return f"Fast. Sag noch einmal: „{correct_sentence}“"


def handle_error_practice_step_three(
    user_message,
    state,
    summary
):
    wrong_sentence, correct_sentence = get_active_error_practice_sentences(
        state,
        summary,
    )

    if is_equivalent_correct_answer(
        user_message,
        correct_sentence,
        state.get("error_practice_type")
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


            clear_equivalent_pending_error_examples(
                state,
                error_type,
                correct_sentence,
                state.get(
                    "error_practice_example_context"
                )
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

                next_context = get_error_example_context(
                    next_example,
                    next_wrong,
                    next_correct
                )


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
                        "error_practice_example_context"
                    ] = next_context or None

                    state[
                        "error_practice_step"
                    ] = 1

                    state[
                        "error_practice_attempts"
                    ] = 0

                    state[
                        "error_practice_used_hint"
                    ] = False


                    next_choice_prompt = (
                        build_error_choice_prompt(
                            next_context,
                            next_wrong,
                            next_correct
                        )
                    )


                    return (
                        "Sehr gut. Jetzt noch eine. "
                        f"{next_choice_prompt}"
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

        return "Genau!"


    # ======================================
    # NIEUDANA PRÓBA TRANSFERU
    # ======================================

    attempts = int(state.get("error_practice_transfer_attempts", 0) or 0) + 1
    state["error_practice_transfer_attempts"] = attempts
    state["error_practice_used_hint"] = True

    if attempts == 1:
        starter = " ".join(str(correct_sentence or "").split()[:2]).strip()
        if starter:
            return f"Fast. Fang so an: „{starter} …“"
        return "Fast. Versuch es noch einmal."

    # After a failed independent attempt, scaffold again instead of
    # marking the learner as mastered. Count and remember this failed
    # production before returning to the guided repetition step.
    increase_error_practice_attempts(state)
    error_type = state.get("error_practice_type")
    remember_daily_error_mistake(
        state,
        error_type,
        wrong_sentence=user_message,
        correct_sentence=correct_sentence,
    )
    state["error_practice_step"] = 2
    return f"Ich helfe dir noch einmal: „{correct_sentence}“ Sag es mal."


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


    if step == 3:

        return handle_error_practice_step_three(
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
