# ==========================================
# NELE – POWTÓRKA CAŁEJ LEKCJI
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import normalize

from brain.memory.lesson_review import (
    mark_lesson_review_completed,
    mark_lesson_review_difficult
)

from brain.memory.daily_learning import (
    mark_lesson_reviewed_today,
    mark_exercise_completed_today
)


# ==========================================
# DAILY LEARNING MEMORY
# ZAKOŃCZONA POWTÓRKA LEKCJI
# ==========================================

def remember_daily_lesson_review_completion(
    state,
    level,
    lesson,
    result
):

    if state is None:
        return


    # ======================================
    # LEKCJA POWTÓRZONA DZISIAJ
    # ======================================

    try:

        mark_lesson_reviewed_today(
            state,
            level,
            lesson,
            result=result
        )

    except Exception as error:

        print(
            f"Daily lesson review memory error: {error}"
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
            f"Daily lesson review counter error: {error}"
        )


# ==========================================
# CZYSZCZENIE ODPOWIEDZI
# ==========================================

def clean_answer(
    text
):

    text = str(
        text or ""
    ).strip()

    return text.strip(
        " .?!„“\"'"
    )


def clean_normalized_answer(
    text
):

    return normalize(
        clean_answer(
            text
        )
    ).strip()


# ==========================================
# CZY POWTÓRKA JEST AKTYWNA
# ==========================================

def is_lesson_review_training_active(
    state
):

    if state is None:
        return False

    return bool(
        state.get(
            "lesson_review_training_active",
            False
        )
    )


# ==========================================
# ZAKOŃCZENIE TRYBU POWTÓRKI
# ==========================================

def finish_lesson_review_training(
    state
):

    if state is None:
        return


    state[
        "lesson_review_training_active"
    ] = False

    state[
        "lesson_review_training_level"
    ] = None

    state[
        "lesson_review_training_lesson"
    ] = None

    state[
        "lesson_review_training_step"
    ] = 0

    state[
        "lesson_review_training_correct"
    ] = 0

    state[
        "lesson_review_training_wrong"
    ] = 0


# ==========================================
# POPRAWNA ODPOWIEDŹ
# ==========================================

def remember_correct_answer(
    state
):

    value = state.get(
        "lesson_review_training_correct",
        0
    )

    try:

        value = int(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        value = 0


    state[
        "lesson_review_training_correct"
    ] = value + 1


# ==========================================
# BŁĘDNA ODPOWIEDŹ
# ==========================================

def remember_wrong_answer(
    state
):

    value = state.get(
        "lesson_review_training_wrong",
        0
    )

    try:

        value = int(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        value = 0


    state[
        "lesson_review_training_wrong"
    ] = value + 1


# ==========================================
# START POWTÓRKI
# ==========================================

def start_lesson_review_training(
    state,
    level="A1",
    lesson=1
):

    if state is None:
        return None


    level = str(
        level or "A1"
    ).strip().upper()


    try:

        lesson = int(
            lesson
        )

    except (
        TypeError,
        ValueError
    ):

        lesson = 1


    # ======================================
    # NA RAZIE OBSŁUGUJEMY
    # A1 LEKTION 1
    # ======================================

    if not (
        level == "A1"
        and
        lesson == 1
    ):

        return None


    state[
        "lesson_review_training_active"
    ] = True

    state[
        "lesson_review_training_level"
    ] = level

    state[
        "lesson_review_training_lesson"
    ] = lesson

    state[
        "lesson_review_training_step"
    ] = 1

    state[
        "lesson_review_training_correct"
    ] = 0

    state[
        "lesson_review_training_wrong"
    ] = 0


    return (
        "Heute ist die Wiederholung von "
        "A1, Lektion 1 dran. "
        "Wir machen eine kurze Wiederholung. "
        "Es ist morgens. Was sagst du?"
    )


# ==========================================
# SPRAWDZENIE POWITANIA
# ==========================================

def is_morning_greeting(
    text
):

    answer = clean_normalized_answer(
        text
    )

    return answer in {
        "guten morgen",
        "morgen"
    }


# ==========================================
# SPRAWDZENIE PRZEDSTAWIENIA SIĘ
# ==========================================

def is_valid_name_answer(
    text
):

    answer = clean_normalized_answer(
        text
    )


    starts = [
        "ich heiße ",
        "ich heisse ",
        "ich bin ",
        "mein name ist "
    ]


    return any(
        answer.startswith(
            start
        )
        and
        len(
            answer[
                len(start):
            ].strip()
        ) > 0
        for start in starts
    )


# ==========================================
# WIE HEISST DU?
# ==========================================

def is_informal_name_question(
    text
):

    answer = clean_normalized_answer(
        text
    )

    return answer in {
        "wie heißt du",
        "wie heisst du"
    }


# ==========================================
# WIE HEISSEN SIE?
# ==========================================

def is_formal_name_question(
    text
):

    answer = clean_normalized_answer(
        text
    )

    return answer in {
        "wie heißen sie",
        "wie heissen sie"
    }


# ==========================================
# UMLAUTY
# ==========================================

def is_umlaut_answer(
    text
):

    text = str(
        text or ""
    ).lower()


    return (
        "ä" in text
        and
        "ö" in text
        and
        "ü" in text
    )


# ==========================================
# ESZETT
# ==========================================

def is_eszett_answer(
    text
):

    text = str(
        text or ""
    ).lower()


    if "ß" in text:
        return True


    answer = clean_normalized_answer(
        text
    )


    return answer in {
        "eszett",
        "es zett",
        "scharfes s",
        "das eszett",
        "das scharfe s"
    }


# ==========================================
# ZAKOŃCZENIE CAŁEJ POWTÓRKI
# ==========================================

def complete_lesson_review_training(
    state
):

    level = state.get(
        "lesson_review_training_level",
        "A1"
    )

    lesson = state.get(
        "lesson_review_training_lesson",
        1
    )


    wrong = state.get(
        "lesson_review_training_wrong",
        0
    )


    try:

        wrong = int(
            wrong
        )

    except (
        TypeError,
        ValueError
    ):

        wrong = 0


    # ======================================
    # 0–1 BŁĘDÓW
    # -> POWTÓRKA ZALICZONA
    #
    # lesson_review.py zaplanuje
    # następny termin:
    #
    # 3 / 7 / 14 / 30 dni
    # ======================================

    if wrong <= 1:

        mark_lesson_review_completed(
            state,
            level,
            lesson,
            result="good"
        )


        # ==================================
        # DAILY LEARNING MEMORY
        # ==================================

        remember_daily_lesson_review_completion(
            state,
            level,
            lesson,
            result="good"
        )


        finish_lesson_review_training(
            state
        )

        return (
            "Sehr gut! Du hast die Wiederholung "
            "von A1, Lektion 1 geschafft. "
            "Die nächste Wiederholung wird "
            "automatisch geplant."
        )


    # ======================================
    # WIĘCEJ BŁĘDÓW
    # -> POWTÓRKA JUTRO
    # ======================================

    mark_lesson_review_difficult(
        state,
        level,
        lesson
    )


    # ======================================
    # DAILY LEARNING MEMORY
    #
    # Powtórka została dzisiaj wykonana,
    # mimo że była trudna.
    # Nie uruchamiamy jej ponownie
    # tego samego dnia.
    # ======================================

    remember_daily_lesson_review_completion(
        state,
        level,
        lesson,
        result="difficult"
    )


    finish_lesson_review_training(
        state
    )

    return (
        "Gut gemacht. Einige Dinge waren noch "
        "etwas schwierig. Deshalb wiederholen "
        "wir A1, Lektion 1 morgen noch einmal."
    )


# ==========================================
# OBSŁUGA POWTÓRKI A1 LEKTION 1
# ==========================================

def handle_a1_lesson_1_review(
    user_message,
    state
):

    step = state.get(
        "lesson_review_training_step",
        1
    )


    # ======================================
    # 1. GUTEN MORGEN
    # ======================================

    if step == 1:

        if is_morning_greeting(
            user_message
        ):

            remember_correct_answer(
                state
            )

            feedback = (
                "Richtig! „Guten Morgen“ passt."
            )

        else:

            remember_wrong_answer(
                state
            )

            feedback = (
                "Fast. Am Morgen sagt man "
                "„Guten Morgen“."
            )


        state[
            "lesson_review_training_step"
        ] = 2


        return (
            f"{feedback} "
            "Jetzt stell dich kurz vor. "
            "Wie heißt du?"
        )


    # ======================================
    # 2. ICH HEISSE ...
    # ======================================

    if step == 2:

        if is_valid_name_answer(
            user_message
        ):

            remember_correct_answer(
                state
            )

            feedback = (
                "Sehr gut!"
            )

        else:

            remember_wrong_answer(
                state
            )

            feedback = (
                "Fast. Zum Beispiel: "
                "„Ich heiße Moni.“"
            )


        state[
            "lesson_review_training_step"
        ] = 3


        return (
            f"{feedback} "
            "Wie fragst du einen Freund "
            "nach seinem Namen?"
        )


    # ======================================
    # 3. WIE HEISST DU?
    # ======================================

    if step == 3:

        if is_informal_name_question(
            user_message
        ):

            remember_correct_answer(
                state
            )

            feedback = (
                "Genau! „Wie heißt du?“"
            )

        else:

            remember_wrong_answer(
                state
            )

            feedback = (
                "Fast. Informell sagt man: "
                "„Wie heißt du?“"
            )


        state[
            "lesson_review_training_step"
        ] = 4


        return (
            f"{feedback} "
            "Und wie fragst du höflich "
            "nach dem Namen?"
        )


    # ======================================
    # 4. WIE HEISSEN SIE?
    # ======================================

    if step == 4:

        if is_formal_name_question(
            user_message
        ):

            remember_correct_answer(
                state
            )

            feedback = (
                "Richtig! „Wie heißen Sie?“"
            )

        else:

            remember_wrong_answer(
                state
            )

            feedback = (
                "Fast. Höflich sagt man: "
                "„Wie heißen Sie?“"
            )


        state[
            "lesson_review_training_step"
        ] = 5


        return (
            f"{feedback} "
            "Welche drei Umlaute gibt es "
            "im Deutschen?"
        )


    # ======================================
    # 5. Ä Ö Ü
    # ======================================

    if step == 5:

        if is_umlaut_answer(
            user_message
        ):

            remember_correct_answer(
                state
            )

            feedback = (
                "Perfekt! Ä, Ö und Ü."
            )

        else:

            remember_wrong_answer(
                state
            )

            feedback = (
                "Fast. Die drei Umlaute sind "
                "Ä, Ö und Ü."
            )


        state[
            "lesson_review_training_step"
        ] = 6


        return (
            f"{feedback} "
            "Und wie heißt dieses Zeichen: ß?"
        )


    # ======================================
    # 6. ESZETT
    # ======================================

    if step == 6:

        if is_eszett_answer(
            user_message
        ):

            remember_correct_answer(
                state
            )

            feedback = (
                "Richtig! Das ist das Eszett."
            )

        else:

            remember_wrong_answer(
                state
            )

            feedback = (
                "Fast. Das Zeichen heißt "
                "„Eszett“ oder „scharfes S“."
            )


        result = (
            complete_lesson_review_training(
                state
            )
        )


        return (
            f"{feedback}\n\n"
            f"{result}"
        )


    finish_lesson_review_training(
        state
    )

    return None


# ==========================================
# GŁÓWNA OBSŁUGA POWTÓRKI
# ==========================================

def handle_lesson_review_training(
    user_message,
    state
):

    if state is None:
        return None


    if not is_lesson_review_training_active(
        state
    ):

        return None


    level = str(
        state.get(
            "lesson_review_training_level",
            ""
        )
        or
        ""
    ).strip().upper()


    lesson = state.get(
        "lesson_review_training_lesson"
    )


    if (
        level == "A1"
        and
        lesson == 1
    ):

        return handle_a1_lesson_1_review(
            user_message,
            state
        )


    finish_lesson_review_training(
        state
    )

    return None
