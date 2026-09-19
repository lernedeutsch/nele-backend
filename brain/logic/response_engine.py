# ==========================================
# NELE – SILNIK ODPOWIEDZI
# TEACHER MODE
# SESSION COACH
# ==========================================

import random

from brain.logic.memory import (
    get_conversation_state
)

from brain.logic.matcher import (
    normalize,
    pattern_matches
)

from brain.logic.lesson_loader import (
    load_lesson
)

from brain.logic.error_practice import (
    start_error_practice,
    get_error_practice_label
)

from brain.logic.new_learning_resume import (
    set_new_learning_offer,
    handle_new_learning_resume
)

from brain.logic.wellbeing_feedback import (
    analyze_wellbeing_response
)

from brain.logic.vocabulary_modules.practice import (
    start_vocabulary_practice
)

from brain.logic.lesson_review_training import (
    start_lesson_review_training
)


from brain.logic.lesson_teaching import (
    is_lesson_teaching_active,
    get_current_lesson_prompt
)

from brain.memory.error_review import (
    refresh_error_reviews,
    get_due_error_reviews
)


from brain.memory.error_memory import (
    get_error_summary
)

from brain.memory.next_learning_step import (
    get_next_new_learning_step,
    get_teacher_learning_plan,
    get_review_plan,
    get_errors_for_review,
    get_lessons_for_review
)

from brain.memory.daily_learning import (
    get_daily_learning_summary,
    was_word_reviewed_today,
    was_error_reviewed_today,
    mark_lesson_recap_today,
    mark_daily_plan_completed
)

from brain.nele3_upgrade.teacher_brain import (
    build_adaptive_recommendation
)

from brain.nele3_upgrade.state import (
    set_pending_recommendation
)


# ==========================================
# CZY BŁĄD MA BYĆ ĆWICZONY W TEJ SESJI
# ==========================================

def should_review_error_in_session(
    state,
    error_type
):

    if not error_type:
        return False


    # Jeśli tego typu błędu jeszcze dziś
    # nie ćwiczyliśmy, normalnie go bierzemy.
    if not was_error_reviewed_today(
        state,
        error_type
    ):

        return True


    # Ważne: po wcześniejszej powtórce tego
    # samego dnia uczeń może popełnić NOWY
    # błąd z tej samej kategorii. Wtedy nie
    # wolno go blokować tylko dlatego, że np.
    # "Wortschatz" był już dziś ćwiczony.
    try:

        summary = get_error_summary(
            state,
            error_type
        )

    except Exception as error:

        print(
            f"Session error summary error: {error}"
        )

        return False


    if not isinstance(
        summary,
        dict
    ):

        return False


    return bool(
        summary.get(
            "needs_practice",
            False
        )
        and
        summary.get(
            "last_result"
        )
        == "wrong"
    )


# ==========================================
# ODPOWIEDZI TAK / NIE
# ==========================================

YES_ANSWERS = {
    "ja",
    "ja gerne",
    "ja gern",
    "gerne",
    "gern",
    "okay",
    "ok",
    "klar",
    "natürlich",
    "machen wir",
    "ja machen wir"
}


NO_ANSWERS = {
    "nein",
    "nein danke",
    "nicht jetzt",
    "später",
    "lieber nicht",
    "jetzt nicht"
}


# ==========================================
# ZAPAMIĘTYWANIE PYTANIA NELE
# ==========================================

def remember_follow_up(
    question,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )

    question_normalized = normalize(
        question
    )


    if (
        "wie heißt du"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "name"


    elif (
        "wie heißen sie"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "name"


    elif (
        "woher kommst du"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "origin"


    elif (
        "wo wohnst du"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "residence"


    elif (
        "wo wohnen sie"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "residence"


    elif (
        "wie geht es dir"
        in question_normalized
    ):

        state[
            "last_question"
        ] = "wellbeing"


    else:

        state[
            "last_question"
        ] = None


# ==========================================
# NAZWA AKTYWNOŚCI DO WYŚWIETLENIA
# ==========================================

def display_activity_word(
    word
):

    if not word:
        return ""

    word = str(
        word
    ).strip()

    if not word:
        return ""

    return (
        word[:1].upper()
        + word[1:]
    )


# ==========================================
# POŁĄCZENIE ELEMENTÓW PO NIEMIECKU
# ==========================================

def join_german_items(
    items
):

    clean_items = []

    for item in items:

        item = str(
            item or ""
        ).strip()

        if item:

            clean_items.append(
                item
            )


    if not clean_items:
        return ""


    if len(
        clean_items
    ) == 1:

        return clean_items[0]


    if len(
        clean_items
    ) == 2:

        return (
            clean_items[0]
            + " und "
            + clean_items[1]
        )


    return (
        ", ".join(
            clean_items[:-1]
        )
        + " und "
        + clean_items[-1]
    )


# ==========================================
# KRÓTKA CZĘŚĆ ODPOWIEDZI
# ==========================================

def get_short_answer(
    answer
):

    if not answer:
        return ""

    answer = str(
        answer
    ).strip()

    if not answer:
        return ""

    endings = [
        "!",
        ".",
        "?"
    ]

    positions = []

    for ending in endings:

        position = answer.find(
            ending
        )

        if position >= 0:

            positions.append(
                position
            )


    if not positions:

        return answer


    first_position = min(
        positions
    )


    return answer[
        :first_position + 1
    ].strip()


# ==========================================
# POŁĄCZENIE POPRAWKI
# Z NORMALNĄ ODPOWIEDZIĄ NELE
# ==========================================

def combine_wellbeing_feedback(
    feedback,
    answer
):

    feedback = str(
        feedback or ""
    ).strip()

    answer = str(
        answer or ""
    ).strip()


    if (
        feedback
        and
        answer
    ):

        return (
            f"{feedback}\n\n"
            f"{answer}"
        )


    if feedback:

        return feedback


    return answer


# ==========================================
# WYCZYSZCZENIE OCZEKUJĄCEJ
# PROPOZYCJI POWTÓRKI
# ==========================================

def clear_pending_error_review(
    state
):

    if state is None:
        return


    state[
        "pending_error_review"
    ] = None


    if (
        state.get(
            "last_question"
        )
        ==
        "continue_error_review"
    ):

        state[
            "last_question"
        ] = None


# ==========================================
# ZAPISANIE PROPOZYCJI POWTÓRKI
# ==========================================

def set_pending_error_review(
    state,
    error_type
):

    if state is None:
        return False

    if not error_type:
        return False


    state[
        "pending_error_review"
    ] = error_type

    state[
        "last_question"
    ] = "continue_error_review"


    return True


# ==========================================
# CZY UŻYTKOWNIK ODPOWIADA
# NA STARĄ PROPOZYCJĘ POWTÓRKI?
# ==========================================

def handle_pending_error_review_reply(
    user_message,
    state
):

    if state is None:

        return (
            False,
            None
        )


    if (
        state.get(
            "last_question"
        )
        !=
        "continue_error_review"
    ):

        return (
            False,
            None
        )


    error_type = state.get(
        "pending_error_review"
    )


    if not error_type:

        clear_pending_error_review(
            state
        )

        return (
            False,
            None
        )


    message = normalize(
        user_message
    ).strip(
        " .?!„“\"'"
    )


    if message in YES_ANSWERS:

        clear_pending_error_review(
            state
        )

        answer = start_error_practice(
            state,
            error_type
        )

        return (
            True,
            answer
        )


    if message in NO_ANSWERS:

        clear_pending_error_review(
            state
        )

        return (
            True,
            (
                "Okay. "
                "Dann machen wir mit der "
                "Lektion weiter."
            )
        )


    clear_pending_error_review(
        state
    )

    return (
        False,
        None
    )


# ==========================================
# NALEŻNA POWTÓRKA BŁĘDU
# ==========================================

def get_due_error_review(
    state
):

    if state is None:
        return None


    try:

        refresh_error_reviews(
            state
        )

    except Exception as error:

        print(
            f"Error review refresh error: {error}"
        )

        return None


    due_errors = get_due_error_reviews(
        state
    )


    if not due_errors:
        return None


    return due_errors[0]


# ==========================================
# STARA PROPOZYCJA POWTÓRKI
# ==========================================

def create_due_error_review_offer(
    state,
    short_answer
):

    error_type = get_due_error_review(
        state
    )


    if not error_type:
        return None


    label = get_error_practice_label(
        error_type
    )


    set_pending_error_review(
        state,
        error_type
    )


    return (
        f"{short_answer} "
        f"Heute sollten wir kurz "
        f"{label} wiederholen. "
        f"Möchtest du das zuerst machen?"
    )


# ==========================================
# STARY PLAN KONTYNUACJI LEKCJI
# ==========================================

def create_lesson_continuation_offer(
    state,
    short_answer
):

    if state is None:
        return None


    try:

        plan = get_next_new_learning_step(
            state
        )

    except Exception as error:

        print(
            f"Next learning step error: {error}"
        )

        return None


    if not isinstance(
        plan,
        dict
    ):

        return None


    plan_type = str(
        plan.get(
            "type",
            ""
        )
        or
        ""
    ).strip().lower()


    section = plan.get(
        "section"
    )

    level = plan.get(
        "level"
    )

    lesson = plan.get(
        "lesson"
    )

    message = str(
        plan.get(
            "message",
            ""
        )
        or
        ""
    ).strip()


    last_activity = state.get(
        "last_activity"
    )

    last_detail = state.get(
        "last_activity_detail"
    )


    if last_detail:

        last_detail = str(
            last_detail
        ).strip()


    if section:

        section = str(
            section
        ).strip()


        offer_saved = (
            set_new_learning_offer(
                state,
                plan
            )
        )


        if offer_saved:

            if (
                last_activity == "lesson"
                and
                last_detail
                and
                normalize(
                    last_detail
                )
                ==
                normalize(
                    section
                )
            ):

                return (
                    f"{short_answer} "
                    f"Zuletzt waren wir bei "
                    f"„{section}“. "
                    f"Möchtest du dort "
                    f"weitermachen?"
                )


            if (
                last_activity == "lesson"
                and
                last_detail
            ):

                return (
                    f"{short_answer} "
                    f"Zuletzt haben wir "
                    f"„{last_detail}“ gemacht. "
                    f"Als Nächstes kommt "
                    f"„{section}“. "
                    f"Möchtest du weitermachen?"
                )


            return (
                f"{short_answer} "
                f"Als Nächstes kommt "
                f"„{section}“. "
                f"Möchtest du weitermachen?"
            )


    if (
        plan_type == "new_lesson"
        and
        level
        and
        lesson
    ):

        offer_saved = (
            set_new_learning_offer(
                state,
                plan
            )
        )


        if offer_saved:

            if (
                last_activity == "lesson"
                and
                last_detail
            ):

                return (
                    f"{short_answer} "
                    f"Zuletzt haben wir "
                    f"„{last_detail}“ gemacht. "
                    f"Jetzt geht es mit "
                    f"{level}, Lektion {lesson} "
                    f"weiter. "
                    f"Möchtest du anfangen?"
                )


            return (
                f"{short_answer} "
                f"Als Nächstes kommt "
                f"{level}, Lektion {lesson}. "
                f"Möchtest du anfangen?"
            )


    if message:

        return (
            f"{short_answer} "
            f"{message}"
        )


    return None


# ==========================================
# STAN POCZĄTKU NOWEJ SESJI
# ==========================================

def get_session_start_flow(
    state
):

    if state is None:
        return None


    flow = state.get(
        "session_start_flow"
    )


    if not isinstance(
        flow,
        dict
    ):

        return None


    if not flow.get(
        "active",
        False
    ):

        return None


    return flow


# ==========================================
# KLUCZ LEKCJI DLA DAILY MEMORY
# ==========================================

def get_daily_lesson_key(
    level,
    lesson,
    section=None
):

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


    key = (
        f"{level}:{lesson}"
    )


    if section:

        section = str(
            section
        ).strip()

        if section:

            key += (
                ":"
                + section
            )


    return key


# ==========================================
# CZY PEŁNA POWTÓRKA LEKCJI
# BYŁA JUŻ DZISIAJ
# ==========================================

def was_lesson_reviewed_today(
    state,
    level,
    lesson
):

    try:

        summary = get_daily_learning_summary(
            state
        )

    except Exception as error:

        print(
            f"Daily lesson review check error: {error}"
        )

        return False


    key = get_daily_lesson_key(
        level,
        lesson
    ).lower()


    reviews = summary.get(
        "lesson_reviews",
        []
    )


    return any(
        str(
            item or ""
        ).strip().lower()
        ==
        key
        for item in reviews
    )


# ==========================================
# CZY KRÓTKIE PRZYPOMNIENIE
# TEGO MIEJSCA LEKCJI
# BYŁO JUŻ DZISIAJ
# ==========================================

def was_lesson_recap_done_today(
    state,
    level,
    lesson,
    section=None
):

    try:

        summary = get_daily_learning_summary(
            state
        )

    except Exception as error:

        print(
            f"Daily lesson recap check error: {error}"
        )

        return False


    key = get_daily_lesson_key(
        level,
        lesson,
        section
    ).lower()


    recaps = summary.get(
        "lesson_recaps",
        []
    )


    return any(
        str(
            item or ""
        ).strip().lower()
        ==
        key
        for item in recaps
    )


# ==========================================
# OPIS LEKCJI Z KLUCZA
# ==========================================

def display_daily_lesson_key(
    value
):

    value = str(
        value or ""
    ).strip()


    if not value:
        return ""


    parts = value.split(
        ":"
    )


    if len(
        parts
    ) < 2:

        return value


    level = parts[0].strip().upper()

    lesson = parts[1].strip()


    if not level or not lesson:
        return value


    return (
        f"{level}, Lektion {lesson}"
    )


# ==========================================
# CO UŻYTKOWNIK ZROBIŁ JUŻ DZISIAJ
# ==========================================

def create_daily_progress_message(
    state
):

    if state is None:
        return ""


    try:

        summary = get_daily_learning_summary(
            state
        )

    except Exception as error:

        print(
            f"Daily learning summary error: {error}"
        )

        return ""


    try:

        session_count = int(
            summary.get(
                "session_count",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        session_count = 0


    if session_count <= 1:
        return ""


    practiced_items = []


    reviewed_words = summary.get(
        "reviewed_words",
        []
    )


    if (
        isinstance(
            reviewed_words,
            list
        )
        and
        reviewed_words
    ):

        word = display_activity_word(
            reviewed_words[-1]
        )

        if word:

            practiced_items.append(
                f"„{word}“"
            )


    reviewed_errors = summary.get(
        "reviewed_errors",
        []
    )


    if (
        isinstance(
            reviewed_errors,
            list
        )
        and
        reviewed_errors
    ):

        error_type = str(
            reviewed_errors[-1]
            or
            ""
        ).strip()


        if error_type:

            label = get_error_practice_label(
                error_type
            )

            if label:

                practiced_items.append(
                    label
                )


    messages = []


    if practiced_items:

        practiced_text = join_german_items(
            practiced_items
        )


        if practiced_text:

            messages.append(
                "Heute hast du schon "
                f"{practiced_text} geübt."
            )


    lesson_reviews = summary.get(
        "lesson_reviews",
        []
    )


    if (
        isinstance(
            lesson_reviews,
            list
        )
        and
        lesson_reviews
    ):

        lesson_description = (
            display_daily_lesson_key(
                lesson_reviews[-1]
            )
        )


        if lesson_description:

            messages.append(
                f"{lesson_description} "
                "hast du heute schon wiederholt."
            )


    if not messages:

        try:

            completed = int(
                summary.get(
                    "completed_exercises",
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            completed = 0


        if completed > 0:

            messages.append(
                "Heute hast du schon etwas geübt."
            )


    if not messages:
        return ""


    messages.append(
        "Wir machen jetzt weiter."
    )


    return " ".join(
        messages
    )


# ==========================================
# DANE KRÓTKIEGO PRZYPOMNIENIA
# OSTATNIEJ LEKCJI
# ==========================================

def get_last_lesson_recap_data(
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
            f"Last lesson recap error: {error}"
        )

        return None


    if not isinstance(
        plan,
        dict
    ):

        return None


    level = str(
        plan.get(
            "level",
            ""
        )
        or
        ""
    ).strip().upper()


    lesson = plan.get(
        "lesson"
    )


    section = plan.get(
        "section"
    )


    last_activity = state.get(
        "last_activity"
    )

    last_detail = state.get(
        "last_activity_detail"
    )


    recap_section = None


    if (
        last_activity == "lesson"
        and
        last_detail
    ):

        recap_section = str(
            last_detail
        ).strip()


    if (
        not recap_section
        and
        section
    ):

        recap_section = str(
            section
        ).strip()


    message = ""


    if (
        level
        and
        lesson
        and
        recap_section
    ):

        message = (
            "Zur kurzen Erinnerung: "
            f"Du bist bei {level}, "
            f"Lektion {lesson}. "
            "Zuletzt waren wir bei "
            f"„{recap_section}“."
        )


    elif recap_section:

        message = (
            "Zur kurzen Erinnerung: "
            "Zuletzt waren wir bei "
            f"„{recap_section}“."
        )


    elif (
        level
        and
        lesson
    ):

        message = (
            "Zur kurzen Erinnerung: "
            f"Du bist bei {level}, "
            f"Lektion {lesson}."
        )


    if not message:
        return None


    return {

        "message":
            message,

        "level":
            level or "A1",

        "lesson":
            lesson,

        "section":
            recap_section
    }


# ==========================================
# OSTATNIA LEKCJA – KRÓTKIE PRZYPOMNIENIE
# ==========================================

def create_last_lesson_recap(
    state
):

    data = get_last_lesson_recap_data(
        state
    )


    if not isinstance(
        data,
        dict
    ):

        return ""


    return str(
        data.get(
            "message",
            ""
        )
        or
        ""
    ).strip()


# ==========================================
# SESSION COACH
#
# Tworzy plan JEDNEJ sesji.
#
# W jednej sesji maksymalnie:
#
# 1. jedno należne słowo
# 2. jeden należny błąd
# 3. krótkie przypomnienie lekcji
# 4. jedna należna pełna powtórka lekcji
# 5. dalsza nauka
#
# Wszystko, co wykonano już dzisiaj,
# zostaje pominięte.
# ==========================================

def build_session_coach_plan(
    state,
    flow
):

    if state is None:
        return flow


    if not isinstance(
        flow,
        dict
    ):

        return flow


    if flow.get(
        "coach_plan_created",
        False
    ):

        return flow


    # ======================================
    # 1. JEDNO SŁOWO NA TĘ SESJĘ
    # ======================================

    planned_word = None


    try:

        review_words = get_review_plan(
            state
        )

    except Exception as error:

        print(
            f"Session Coach vocabulary error: {error}"
        )

        review_words = []


    for word in review_words:

        word = str(
            word or ""
        ).strip()


        if not word:
            continue


        if was_word_reviewed_today(
            state,
            word
        ):

            continue


        planned_word = word

        break


    # ======================================
    # 2. JEDEN BŁĄD NA TĘ SESJĘ
    # ======================================

    planned_error = None


    try:

        errors = get_errors_for_review(
            state,
            limit=10
        )

    except Exception as error:

        print(
            f"Session Coach error review error: {error}"
        )

        errors = []


    for item in errors:

        error_type = None


        if isinstance(
            item,
            dict
        ):

            error_type = item.get(
                "error_type"
            )


        elif isinstance(
            item,
            str
        ):

            error_type = item


        error_type = str(
            error_type or ""
        ).strip()


        if not error_type:
            continue


        if not should_review_error_in_session(
            state,
            error_type
        ):

            continue


        planned_error = item

        break


    # ======================================
    # 3. KRÓTKIE PRZYPOMNIENIE
    # ======================================

    planned_recap = (
        get_last_lesson_recap_data(
            state
        )
    )


    if isinstance(
        planned_recap,
        dict
    ):

        recap_level = planned_recap.get(
            "level",
            "A1"
        )

        recap_lesson = planned_recap.get(
            "lesson",
            1
        )

        recap_section = planned_recap.get(
            "section"
        )


        if was_lesson_recap_done_today(
            state,
            recap_level,
            recap_lesson,
            recap_section
        ):

            planned_recap = None


    # ======================================
    # 4. NALEŻNA PEŁNA POWTÓRKA LEKCJI
    # ======================================

    planned_lesson_review = None


    try:

        lesson_reviews = get_lessons_for_review(
            state,
            limit=10
        )

    except Exception as error:

        print(
            f"Session Coach lesson review error: {error}"
        )

        lesson_reviews = []


    for item in lesson_reviews:

        if not isinstance(
            item,
            dict
        ):

            continue


        level = item.get(
            "level",
            "A1"
        )

        lesson = item.get(
            "lesson",
            1
        )


        if was_lesson_reviewed_today(
            state,
            level,
            lesson
        ):

            continue


        planned_lesson_review = item

        break


    # ======================================
    # ZAPIS PLANU SESJI
    # ======================================

    flow[
        "planned_word"
    ] = planned_word

    flow[
        "planned_error"
    ] = planned_error

    flow[
        "planned_recap"
    ] = planned_recap

    flow[
        "planned_lesson_review"
    ] = planned_lesson_review

    flow[
        "coach_plan_created"
    ] = True


    return flow


# ==========================================
# URUCHOMIENIE DALSZEGO MATERIAŁU
# ==========================================

def start_next_new_learning(
    state
):

    if state is None:
        return ""


    # Jeżeli uczeń przerwał lekcję w połowie,
    # wracamy dokładnie do zapisanego kroku,
    # zamiast uruchamiać sekcję od początku.
    if is_lesson_teaching_active(
        state
    ):

        resume_prompt = get_current_lesson_prompt(
            state
        )

        if resume_prompt:
            return resume_prompt


    try:

        plan = get_next_new_learning_step(
            state
        )

    except Exception as error:

        print(
            f"Start next new learning error: {error}"
        )

        return ""


    if not isinstance(
        plan,
        dict
    ):

        return ""


    # ======================================
    # LEKCJA UKOŃCZONA
    # -> ADAPTACYJNA PROPOZYCJA TRENINGU
    #
    # To miejsce jest używane przez
    # SESSION COACH na początku sesji.
    # Wcześniej właśnie tutaj Nele zwracała
    # tylko:
    # "Du hast A1, Lektion 1 vollständig
    # abgeschlossen."
    #
    # Teraz po zakończonej lekcji Teacher
    # Brain analizuje wyniki i proponuje
    # sensowny trening.
    # ======================================

    plan_type = str(
        plan.get(
            "type",
            ""
        )
        or
        ""
    ).strip().lower()


    if plan_type == "lesson_completed":

        try:

            recommendation = (
                build_adaptive_recommendation(
                    state
                )
            )

        except Exception as error:

            print(
                f"Adaptive session recommendation error: {error}"
            )

            recommendation = None


        if isinstance(
            recommendation,
            dict
        ):

            set_pending_recommendation(
                state,
                recommendation
            )

            recommendation_message = str(
                recommendation.get(
                    "message",
                    ""
                )
                or
                ""
            ).strip()


            if recommendation_message:

                return recommendation_message


    offer_saved = (
        set_new_learning_offer(
            state,
            plan
        )
    )


    if offer_saved:

        started_answer = (
            handle_new_learning_resume(
                "ja",
                state
            )
        )


        if started_answer:

            return started_answer


    return str(
        plan.get(
            "message",
            ""
        )
        or
        ""
    ).strip()


# ==========================================
# POCZĄTEK NOWEJ SESJI
#
# SESSION COACH
#
# KOLEJNOŚĆ:
#
# 1. jedno należne słowo
# 2. jeden należny błąd
# 3. krótkie przypomnienie ostatniej lekcji
# 4. należna pełna powtórka lekcji
# 5. dalsza lekcja / materiał
#
# Daily Learning Memory pilnuje,
# aby tego samego elementu
# nie powtarzać drugi raz tego samego dnia.
# ==========================================

def create_session_start_follow_up(
    state,
    short_answer=""
):

    flow = get_session_start_flow(
        state
    )


    if not flow:
        return None


    # ======================================
    # UTWORZENIE PLANU TEJ SESJI
    # ======================================

    build_session_coach_plan(
        state,
        flow
    )


    # ======================================
    # INFORMACJA:
    # CO JUŻ ZROBIONO DZISIAJ
    # ======================================

    daily_progress = ""


    if not flow.get(
        "daily_progress_shown",
        False
    ):

        daily_progress = (
            create_daily_progress_message(
                state
            )
        )

        flow[
            "daily_progress_shown"
        ] = True


    # ======================================
    # 1. JEDNO NALEŻNE SŁOWO
    # ======================================

    if not flow.get(
        "vocabulary_done",
        False
    ):

        flow[
            "vocabulary_done"
        ] = True


        word = flow.get(
            "planned_word"
        )


        word = str(
            word or ""
        ).strip()


        if (
            word
            and
            not was_word_reviewed_today(
                state,
                word
            )
        ):

            exercise = (
                start_vocabulary_practice(
                    (
                        "übe mit mir das wort "
                        + word
                    ),
                    state
                )
            )


            if exercise:

                parts = []


                if short_answer:

                    parts.append(
                        short_answer
                    )


                if daily_progress:

                    parts.append(
                        daily_progress
                    )


                parts.append(
                    "Wir beginnen mit einem Wort, "
                    "das heute wiederholt werden soll."
                )


                parts.append(
                    exercise
                )


                return "\n\n".join(
                    parts
                )


    # ======================================
    # 2. JEDEN NALEŻNY BŁĄD
    # ======================================

    if not flow.get(
        "errors_done",
        False
    ):

        flow[
            "errors_done"
        ] = True


        first_error = flow.get(
            "planned_error"
        )


        error_type = None

        label = ""


        if isinstance(
            first_error,
            dict
        ):

            error_type = first_error.get(
                "error_type"
            )

            label = str(
                first_error.get(
                    "label",
                    ""
                )
                or
                ""
            ).strip()


        elif isinstance(
            first_error,
            str
        ):

            error_type = first_error


        error_type = str(
            error_type or ""
        ).strip()


        if (
            error_type
            and
            should_review_error_in_session(
                state,
                error_type
            )
        ):

            if not label:

                label = (
                    get_error_practice_label(
                        error_type
                    )
                )


            exercise = start_error_practice(
                state,
                error_type
            )


            if exercise:

                parts = []


                if short_answer:

                    parts.append(
                        short_answer
                    )


                if daily_progress:

                    parts.append(
                        daily_progress
                    )


                if label:

                    parts.append(
                        "Jetzt wiederholen wir kurz "
                        f"{label}."
                    )

                else:

                    parts.append(
                        "Jetzt wiederholen wir kurz "
                        "einen wichtigen Fehler."
                    )


                parts.append(
                    exercise
                )


                return "\n\n".join(
                    parts
                )


    # ======================================
    # 3. KRÓTKIE PRZYPOMNIENIE LEKCJI
    # ======================================

    recap = ""


    if not flow.get(
        "last_lesson_recap_done",
        False
    ):

        flow[
            "last_lesson_recap_done"
        ] = True


        recap_data = flow.get(
            "planned_recap"
        )


        if isinstance(
            recap_data,
            dict
        ):

            recap_level = recap_data.get(
                "level",
                "A1"
            )

            recap_lesson = recap_data.get(
                "lesson",
                1
            )

            recap_section = recap_data.get(
                "section"
            )


            if not was_lesson_recap_done_today(
                state,
                recap_level,
                recap_lesson,
                recap_section
            ):

                recap = str(
                    recap_data.get(
                        "message",
                        ""
                    )
                    or
                    ""
                ).strip()


                if recap:

                    try:

                        mark_lesson_recap_today(
                            state,
                            recap_level,
                            recap_lesson,
                            recap_section
                        )

                    except Exception as error:

                        print(
                            f"Daily lesson recap memory error: {error}"
                        )


    # ======================================
    # 4. NALEŻNA PEŁNA POWTÓRKA LEKCJI
    # ======================================

    if not flow.get(
        "lesson_review_done",
        False
    ):

        flow[
            "lesson_review_done"
        ] = True


        lesson_review = flow.get(
            "planned_lesson_review"
        )


        if isinstance(
            lesson_review,
            dict
        ):

            level = lesson_review.get(
                "level",
                "A1"
            )

            lesson = lesson_review.get(
                "lesson",
                1
            )


            if not was_lesson_reviewed_today(
                state,
                level,
                lesson
            ):

                review_answer = (
                    start_lesson_review_training(
                        state,
                        level,
                        lesson
                    )
                )


                if review_answer:

                    parts = []


                    if short_answer:

                        parts.append(
                            short_answer
                        )


                    if daily_progress:

                        parts.append(
                            daily_progress
                        )


                    if recap:

                        parts.append(
                            recap
                        )


                    parts.append(
                        review_answer
                    )


                    return "\n\n".join(
                        parts
                    )


    # ======================================
    # 5. PLAN STARTOWY SESSION COACH
    # ZOSTAŁ PRZEJŚCIANY
    #
    # Słówko, błąd, przypomnienie
    # i ewentualna powtórka lekcji
    # są już obsłużone.
    #
    # Została dalsza nauka.
    # ======================================

    flow[
        "active"
    ] = False


    # ======================================
    # NA RAZIE NIE OZNACZAMY JESZCZE
    # PLANU DNIA JAKO UKOŃCZONEGO.
    #
    # Najpierw uruchamiamy dalszą naukę.
    # ======================================

    flow[
        "waiting_for_new_learning_completion"
    ] = False


    next_learning = start_next_new_learning(
        state
    )


    # ======================================
    # CZY RZECZYWIŚCIE URUCHOMIŁA SIĘ
    # AKTYWNA CZĘŚĆ LEKCJI?
    #
    # Jeżeli TAK:
    # czekamy aż użytkownik ją ukończy.
    #
    # lesson_teaching.py po ukończeniu
    # części ustawi:
    #
    # daily_plan_completed = True
    # ======================================

    lesson_started = bool(
        state.get(
            "lesson_teaching_active",
            False
        )
    )


    if lesson_started:

        flow[
            "waiting_for_new_learning_completion"
        ] = True


    # ======================================
    # JEŻELI NIE MA NOWEJ AKTYWNEJ
    # CZĘŚCI LEKCJI,
    # PLAN NA DZISIAJ MOŻEMY UZNAĆ
    # ZA ZAKOŃCZONY JUŻ TERAZ.
    #
    # Przykład:
    #
    # A1 Lektion 1 jest ukończona
    # i nie dodaliśmy jeszcze Lektion 2.
    # ======================================

    else:

        try:

            daily_summary = (
                get_daily_learning_summary(
                    state
                )
            )


            if not daily_summary.get(
                "daily_plan_completed",
                False
            ):

                mark_daily_plan_completed(
                    state
                )

        except Exception as error:

            print(
                f"Daily plan completed error: {error}"
            )


    # ======================================
    # ODPOWIEDŹ SESSION COACH
    # ======================================

    parts = []


    if short_answer:

        parts.append(
            short_answer
        )


    if daily_progress:

        parts.append(
            daily_progress
        )


    if recap:

        parts.append(
            recap
        )


    if next_learning:

        parts.append(
            next_learning
        )


    if parts:

        return "\n\n".join(
            parts
        )


    return None


# ==========================================
# TEACHER MODE
# ==========================================

def create_teacher_directed_follow_up(
    state,
    short_answer=""
):

    if state is None:
        return short_answer


    # ======================================
    # NOWA SESJA
    # -> SESSION COACH
    # ======================================

    session_answer = (
        create_session_start_follow_up(
            state,
            short_answer
        )
    )


    if session_answer:

        return session_answer


    # ======================================
    # NORMALNY PLAN NAUCZYCIELA
    # ======================================

    try:

        plan = get_teacher_learning_plan(
            state
        )

    except Exception as error:

        print(
            f"Teacher learning plan error: {error}"
        )

        return short_answer


    if not isinstance(
        plan,
        dict
    ):

        return short_answer


    priority = str(
        plan.get(
            "priority",
            ""
        )
        or
        ""
    ).strip().lower()


    plan_type = str(
        plan.get(
            "type",
            ""
        )
        or
        ""
    ).strip().lower()


    message = str(
        plan.get(
            "message",
            ""
        )
        or
        ""
    ).strip()


    # ======================================
    # 1. POWTÓRKA BŁĘDU
    # ======================================

    if priority == "error_review":

        errors = plan.get(
            "errors",
            []
        )

        error_type = None


        if (
            isinstance(
                errors,
                list
            )
            and
            errors
        ):

            first_error = errors[0]


            if isinstance(
                first_error,
                dict
            ):

                error_type = first_error.get(
                    "error_type"
                )


            elif isinstance(
                first_error,
                str
            ):

                error_type = first_error


        if error_type:

            exercise = start_error_practice(
                state,
                error_type
            )


            parts = []


            if short_answer:

                parts.append(
                    short_answer
                )


            if message:

                parts.append(
                    message
                )


            if exercise:

                parts.append(
                    exercise
                )


            if parts:

                return "\n\n".join(
                    parts
                )


    # ======================================
    # 2. POWTÓRKA SŁOWNICTWA
    # ======================================

    if priority == "vocabulary_review":

        words = plan.get(
            "words",
            []
        )

        word = None


        if (
            isinstance(
                words,
                list
            )
            and
            words
        ):

            word = str(
                words[0]
            ).strip()


        if word:

            exercise = (
                start_vocabulary_practice(
                    (
                        "übe mit mir das wort "
                        + word
                    ),
                    state
                )
            )


            parts = []


            if short_answer:

                parts.append(
                    short_answer
                )


            if message:

                parts.append(
                    message
                )


            if exercise:

                parts.append(
                    exercise
                )


            if parts:

                return "\n\n".join(
                    parts
                )


    # ======================================
    # 3. NALEŻNA POWTÓRKA LEKCJI
    # ======================================

    if priority == "lesson_review":

        lesson_reviews = plan.get(
            "lesson_reviews",
            []
        )

        lesson_review = None


        if (
            isinstance(
                lesson_reviews,
                list
            )
            and
            lesson_reviews
        ):

            lesson_review = (
                lesson_reviews[0]
            )


        if isinstance(
            lesson_review,
            dict
        ):

            level = lesson_review.get(
                "level",
                "A1"
            )

            lesson = lesson_review.get(
                "lesson",
                1
            )


            if not was_lesson_reviewed_today(
                state,
                level,
                lesson
            ):

                review_answer = (
                    start_lesson_review_training(
                        state,
                        level,
                        lesson
                    )
                )


                if review_answer:

                    parts = []


                    if short_answer:

                        parts.append(
                            short_answer
                        )


                    if message:

                        parts.append(
                            message
                        )


                    parts.append(
                        review_answer
                    )


                    return "\n\n".join(
                        parts
                    )


    # ======================================
    # 4. NOWY MATERIAŁ / LEKCJA
    # ======================================

    new_learning_plan = plan


    if plan_type == "teacher_plan":

        next_plan = plan.get(
            "next"
        )


        if isinstance(
            next_plan,
            dict
        ):

            new_learning_plan = next_plan


    if isinstance(
        new_learning_plan,
        dict
    ):

        offer_saved = (
            set_new_learning_offer(
                state,
                new_learning_plan
            )
        )


        if offer_saved:

            started_answer = (
                handle_new_learning_resume(
                    "ja",
                    state
                )
            )


            if started_answer:

                if short_answer:

                    return (
                        f"{short_answer}\n\n"
                        f"{started_answer}"
                    )


                return started_answer


    # ======================================
    # 5. ADAPTACYJNA PROPOZYCJA TRENINGU
    #
    # Gdy bieżąca lekcja jest ukończona i
    # nie ma pilnej powtórki, Nele nie kończy
    # na komunikacie o zakończonej lekcji.
    # Analizuje wyniki ucznia i proponuje
    # konkretny trening.
    # ======================================

    if plan_type == "lesson_completed":

        try:

            recommendation = (
                build_adaptive_recommendation(
                    state
                )
            )

        except Exception as error:

            print(
                f"Adaptive teacher recommendation error: {error}"
            )

            recommendation = None


        if isinstance(
            recommendation,
            dict
        ):

            set_pending_recommendation(
                state,
                recommendation
            )

            recommendation_message = str(
                recommendation.get(
                    "message",
                    ""
                )
                or
                ""
            ).strip()


            if recommendation_message:

                parts = []

                if short_answer:
                    parts.append(
                        short_answer
                    )

                if message:
                    parts.append(
                        message
                    )

                parts.append(
                    recommendation_message
                )

                return "\n\n".join(
                    parts
                )


    # ======================================
    # FALLBACK
    # ======================================

    if message:

        if short_answer:

            return (
                f"{short_answer}\n\n"
                f"{message}"
            )


        return message


    return short_answer


# ==========================================
# ODPOWIEDŹ PO POWITANIU
# ==========================================

def create_returning_user_follow_up(
    state,
    normal_answer,
    wellbeing_type=""
):

    short_answer = get_short_answer(
        normal_answer
    )


    teacher_answer = (
        create_teacher_directed_follow_up(
            state,
            short_answer
        )
    )


    if teacher_answer:

        return teacher_answer


    state[
        "last_question"
    ] = None


    if short_answer:

        return (
            f"{short_answer} "
            "Wir machen jetzt weiter."
        )


    return (
        "Wir machen jetzt weiter."
    )


# ==========================================
# OBSŁUGA ODPOWIEDZI:
# WIE GEHT ES DIR?
# ==========================================

def handle_wellbeing_reply(
    user_message,
    state
):

    if state is None:
        return None


    if (
        state.get(
            "last_question"
        )
        !=
        "wellbeing"
    ):

        return None


    analysis = analyze_wellbeing_response(
        user_message
    )


    if not analysis.get(
        "recognized",
        False
    ):

        return None


    wellbeing_type = analysis.get(
        "type"
    )

    reaction = analysis.get(
        "reaction"
    )

    feedback = analysis.get(
        "feedback"
    )


    answer = create_returning_user_follow_up(
        state,
        reaction,
        wellbeing_type
    )


    return combine_wellbeing_feedback(
        feedback,
        answer
    )


# ==========================================
# ZNANE ZWROTY Z LEKCJI
# ==========================================

def find_response(
    user_message,
    level="A1",
    lesson=1,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )


    (
        error_review_handled,
        error_review_answer
    ) = handle_pending_error_review_reply(
        user_message,
        state
    )


    if error_review_handled:

        return error_review_answer


    previous_question = state.get(
        "last_question"
    )


    # ======================================
    # WIE GEHT ES DIR?
    # ======================================

    if previous_question == "wellbeing":

        wellbeing_answer = (
            handle_wellbeing_reply(
                user_message,
                state
            )
        )


        if wellbeing_answer:

            return wellbeing_answer


    # ======================================
    # NORMALNE ODPOWIEDZI Z LEKCJI
    # ======================================

    responses = load_lesson(
        level,
        lesson
    )

    matches = []


    for item in responses:

        patterns = item.get(
            "patterns",
            []
        )


        for pattern in patterns:

            if pattern_matches(
                user_message,
                pattern
            ):

                pattern_normalized = normalize(
                    pattern
                )


                matches.append(
                    {
                        "item":
                            item,

                        "pattern":
                            pattern_normalized,

                        "length":
                            len(
                                pattern_normalized
                            )
                    }
                )


    if not matches:
        return None


    matches.sort(
        key=lambda match:
            match[
                "length"
            ],
        reverse=True
    )


    best_match = matches[
        0
    ]


    item = best_match[
        "item"
    ]


    intent = item.get(
        "intent",
        ""
    )


    answers = item.get(
        "responses",
        []
    )


    follow_up = item.get(
        "follow_up",
        []
    )


    if answers:

        answer = random.choice(
            answers
        )

    else:

        answer = ""


    wellbeing_intents = {
        "user_wellbeing_good",
        "user_wellbeing_bad"
    }


    if (
        previous_question == "wellbeing"
        and
        intent in wellbeing_intents
    ):

        return (
            create_returning_user_follow_up(
                state,
                answer,
                intent
            )
        )


    if follow_up:

        question = random.choice(
            follow_up
        )


        remember_follow_up(
            question,
            session_id
        )


        if answer:

            answer += (
                " "
                + question
            )

        else:

            answer = question


    else:

        state[
            "last_question"
        ] = None


    return answer
