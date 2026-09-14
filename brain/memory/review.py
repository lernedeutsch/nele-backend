# ==========================================
# NELE – WIEDERHOLUNG UND LERNFORTSCHRITT
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import normalize

from brain.logic.new_learning_resume import (
    set_new_learning_offer
)

from brain.memory.vocabulary_memory import (
    get_vocabulary_memory,
    get_words_for_review
)

from brain.memory.student_progress import (
    get_student_progress,
    get_recent_learning_topics
)

from brain.memory.next_learning_step import (
    get_next_learning_step,
    get_next_new_learning_step,
    get_teacher_learning_plan
)


# ==========================================
# WORT SCHÖN ANZEIGEN
# ==========================================

def display_memory_word(
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
# WORT AUS LERNTHEMA HOLEN
# ==========================================

def get_word_from_learning_topic(
    topic
):

    if not topic:
        return None

    topic = str(
        topic
    ).strip()

    if not topic.startswith(
        "Wortschatz:"
    ):
        return None

    word = topic.split(
        ":",
        1
    )[1].strip()

    if not word:
        return None

    return word


# ==========================================
# FRAGE NACH DER LETZTEN LERNAKTIVITÄT
# ==========================================

def is_last_learning_request(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!"
    )

    questions = [
        "was habe ich zuletzt geübt",
        "was habe ich zuletzt gelernt",
        "was haben wir zuletzt geübt",
        "was haben wir zuletzt gelernt",
        "was war meine letzte übung",
        "was war meine letzte lernaktivität",
        "was habe ich als letztes geübt",
        "was habe ich als letztes gelernt",
        "womit habe ich zuletzt geübt"
    ]

    return message in questions


# ==========================================
# ANTWORT – LETZTE LERNAKTIVITÄT
# ==========================================

def answer_last_learning(
    user_message,
    state
):

    if not is_last_learning_request(
        user_message
    ):
        return None


    progress = get_student_progress(
        state
    )

    last_topic = progress.get(
        "last_learning_topic"
    )


    # ======================================
    # HISTORIA STUDENT MEMORY 2.0
    # ======================================

    recent_topics = get_recent_learning_topics(
        state,
        limit=2
    )


    if recent_topics:

        last_topic = recent_topics[0]


    # ======================================
    # OSTATNIE SŁOWO
    # ======================================

    last_word = get_word_from_learning_topic(
        last_topic
    )


    if last_word:

        last_word_display = display_memory_word(
            last_word
        )


        state[
            "last_activity"
        ] = "vocabulary"

        state[
            "last_activity_detail"
        ] = last_word

        state[
            "last_question"
        ] = "continue_last_activity"


        previous_text = ""


        if len(
            recent_topics
        ) >= 2:

            previous_topic = recent_topics[1]

            previous_word = (
                get_word_from_learning_topic(
                    previous_topic
                )
            )


            if previous_word:

                previous_display = (
                    display_memory_word(
                        previous_word
                    )
                )

                previous_text = (
                    f" Davor hast du "
                    f"„{previous_display}“ geübt."
                )

            else:

                previous_text = (
                    f" Davor hast du "
                    f"„{previous_topic}“ geübt."
                )


        return (
            "Zuletzt hast du das Wort "
            f"„{last_word_display}“ geübt."
            f"{previous_text} "
            f"Möchtest du mit "
            f"„{last_word_display}“ "
            "weitermachen?"
        )


    # ======================================
    # INNY OSTATNI TEMAT
    # ======================================

    if last_topic:

        return (
            "Zuletzt hast du "
            f"„{last_topic}“ geübt."
        )


    # ======================================
    # ZGODNOŚĆ ZE STARSZĄ PAMIĘCIĄ
    # ======================================

    last_activity = state.get(
        "last_activity"
    )

    last_detail = state.get(
        "last_activity_detail"
    )


    if (
        last_activity == "vocabulary"
        and last_detail
    ):

        display_word = display_memory_word(
            last_detail
        )


        state[
            "last_question"
        ] = "continue_last_activity"


        return (
            "Zuletzt hast du das Wort "
            f"„{display_word}“ geübt. "
            f"Möchtest du mit "
            f"„{display_word}“ "
            "weitermachen?"
        )


    return (
        "Ich habe noch keine letzte "
        "Lernaktivität gespeichert. "
        "Lass uns etwas üben!"
    )


# ==========================================
# FRAGE:
# WAS SOLL ICH ÜBEN?
# ==========================================

def is_next_practice_request(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!"
    )

    questions = [
        "was soll ich heute üben",
        "was soll ich üben",
        "was üben wir heute",
        "was soll ich als nächstes üben",
        "womit soll ich weiterüben",
        "was kann ich heute üben",
        "was empfiehlst du mir zum üben"
    ]

    return message in questions


# ==========================================
# ANTWORT:
# WAS SOLL ICH ÜBEN?
# ==========================================

def answer_next_practice_step(
    user_message,
    state
):

    if not is_next_practice_request(
        user_message
    ):
        return None


    plan = get_next_learning_step(
        state
    )


    if not plan:

        return (
            "Lass uns mit einer "
            "kleinen Übung anfangen."
        )


    message = plan.get(
        "message"
    )

    words = plan.get(
        "words",
        []
    )


    if not message:

        return (
            "Lass uns mit einer "
            "kleinen Übung anfangen."
        )


    # ======================================
    # PLAN MA KONKRETNE SŁOWA
    # ======================================

    if words:

        first_word = words[0]

        first_word_display = (
            display_memory_word(
                first_word
            )
        )


        state[
            "last_activity"
        ] = "vocabulary"

        state[
            "last_activity_detail"
        ] = first_word

        state[
            "last_question"
        ] = "continue_last_activity"


        if message.strip().endswith(
            "?"
        ):

            return message


        return (
            f"{message} "
            f"Möchtest du mit "
            f"„{first_word_display}“ "
            "anfangen?"
        )


    return message


# ==========================================
# FRAGE:
# WAS SOLL ICH LERNEN?
# ==========================================

def is_next_new_learning_request(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!"
    )

    questions = [
        "was soll ich heute lernen",
        "was soll ich lernen",
        "was soll ich lernen heute",
        "was lernen wir heute",
        "was soll ich als nächstes lernen",
        "was kann ich heute lernen",
        "was ist der nächste lernstoff",
        "was ist mein nächster lernstoff",
        "was ist mein nächster lernschritt",
        "was soll ich neu lernen"
    ]

    return message in questions


# ==========================================
# ANTWORT:
# WAS SOLL ICH LERNEN?
# ==========================================

def answer_next_new_learning_step(
    user_message,
    state
):

    if not is_next_new_learning_request(
        user_message
    ):
        return None


    # ======================================
    # UŻYTKOWNIK WYBRAŁ NOWĄ NAUKĘ
    # ======================================

    state[
        "last_question"
    ] = None

    state[
        "vocabulary_practice_active"
    ] = False

    state[
        "vocabulary_practice_word"
    ] = None

    state[
        "vocabulary_practice_type"
    ] = None


    # ======================================
    # WYBÓR NOWEGO MATERIAŁU
    # ======================================

    plan = get_next_new_learning_step(
        state
    )


    if not plan:

        return (
            "Lass uns mit etwas Neuem "
            "anfangen."
        )


    message = plan.get(
        "message"
    )


    if not message:

        return (
            "Lass uns mit etwas Neuem "
            "anfangen."
        )


    # ======================================
    # ZAPAMIĘTANIE OFERTY
    # ======================================

    offer_saved = set_new_learning_offer(
        state,
        plan
    )


    if offer_saved:

        return (
            f"{message} "
            "Möchtest du damit anfangen?"
        )


    return message


# ==========================================
# PYTANIE DO "NAUCZYCIELA"
#
# Użytkownik nie wybiera sam:
# - ćwiczenia,
# - nowego materiału,
# - błędu.
#
# Pyta Nele, co ONA poleca.
# ==========================================

def is_teacher_recommendation_request(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!"
    )


    questions = [

        "was soll ich heute machen",

        "was sollen wir heute machen",

        "was machen wir heute",

        "was empfiehlst du mir heute",

        "was empfiehlst du mir",

        "was würdest du mir heute empfehlen",

        "was würdest du mir empfehlen",

        "womit sollen wir anfangen",

        "womit fangen wir an",

        "womit soll ich anfangen",

        "was machen wir als nächstes",

        "was machen wir jetzt",

        "wie soll ich weitermachen",

        "was ist der nächste schritt",

        "was wäre heute sinnvoll",

        "was soll ich als nächstes machen"
    ]


    return message in questions


# ==========================================
# PLAN NAUCZYCIELA – PRZYGOTOWANIE
# KONTYNUACJI
# ==========================================

def prepare_teacher_plan_follow_up(
    plan,
    state
):

    if not plan:

        return False


    plan_type = str(
        plan.get(
            "type",
            ""
        )
        or
        ""
    ).strip().lower()


    words = plan.get(
        "words",
        []
    )


    # ======================================
    # PLAN SŁOWNICTWA
    # ======================================

    if words:

        first_word = words[0]

        if first_word:

            state[
                "last_activity"
            ] = "vocabulary"

            state[
                "last_activity_detail"
            ] = first_word

            state[
                "last_question"
            ] = "continue_last_activity"

            return True


    # ======================================
    # NOWA CZĘŚĆ / NOWA LEKCJA
    #
    # Jeżeli plan nauczyciela wybrał
    # nowy materiał, przygotowujemy
    # normalne "Ja".
    # ======================================

    new_learning_types = {
        "new_learning",
        "new_section",
        "new_lesson",
        "continue_lesson"
    }


    if (
        plan_type in new_learning_types
        or
        plan.get(
            "section"
        )
    ):

        return bool(
            set_new_learning_offer(
                state,
                plan
            )
        )


    return False


# ==========================================
# ODPOWIEDŹ NAUCZYCIELA
# ==========================================

def answer_teacher_recommendation(
    user_message,
    state
):

    if not is_teacher_recommendation_request(
        user_message
    ):
        return None


    # ======================================
    # NELE SAMA WYBIERA PRIORYTET
    #
    # Student Memory 2.0:
    #
    # 1. ważny błąd
    # 2. potrzebna powtórka
    # 3. nowy materiał
    # ======================================

    plan = get_teacher_learning_plan(
        state
    )


    if not plan:

        return (
            "Lass uns mit einer kleinen "
            "Übung anfangen."
        )


    message = str(
        plan.get(
            "message",
            ""
        )
        or
        ""
    ).strip()


    if not message:

        return (
            "Lass uns mit einer kleinen "
            "Übung anfangen."
        )


    plan_type = str(
        plan.get(
            "type",
            ""
        )
        or
        ""
    ).strip().lower()


    words = plan.get(
        "words",
        []
    )


    # ======================================
    # SŁOWNICTWO
    # ======================================

    if words:

        first_word = words[0]

        first_word_display = (
            display_memory_word(
                first_word
            )
        )


        prepare_teacher_plan_follow_up(
            plan,
            state
        )


        if message.endswith(
            "?"
        ):

            return message


        return (
            f"{message} "
            f"Möchtest du mit "
            f"„{first_word_display}“ "
            "anfangen?"
        )


    # ======================================
    # NOWY MATERIAŁ
    # ======================================

    new_learning_types = {
        "new_learning",
        "new_section",
        "new_lesson",
        "continue_lesson"
    }


    if (
        plan_type in new_learning_types
        or
        plan.get(
            "section"
        )
    ):

        offer_saved = (
            prepare_teacher_plan_follow_up(
                plan,
                state
            )
        )


        if (
            offer_saved
            and not message.endswith(
                "?"
            )
        ):

            return (
                f"{message} "
                "Möchtest du damit anfangen?"
            )


        return message


    # ======================================
    # BŁĄD / POWTÓRKA BŁĘDU
    #
    # get_teacher_learning_plan()
    # może wybrać błąd jako najważniejszy.
    #
    # Tutaj nie zmieniamy ręcznie stanu
    # error_practice, ponieważ zarządza nim
    # osobny moduł Student Memory 2.0.
    # ======================================

    return message


# ==========================================
# ALLGEMEINE EMPFEHLUNG
#
# Starsza nazwa zostaje dla zgodności.
# Teraz korzysta z planu nauczyciela.
# ==========================================

def is_general_recommendation_request(
    user_message
):

    return is_teacher_recommendation_request(
        user_message
    )


# ==========================================
# ANTWORT – ALLGEMEINE EMPFEHLUNG
# ==========================================

def answer_general_recommendation(
    user_message,
    state
):

    return answer_teacher_recommendation(
        user_message,
        state
    )


# ==========================================
# FRAGE NACH GEÜBTEN WÖRTERN
# ==========================================

def is_practiced_words_request(
    user_message
):

    message = normalize(
        user_message
    )

    questions = [
        "welche wörter habe ich geübt",
        "welche wörter habe ich schon geübt",
        "welche wörter haben wir geübt",
        "welche wörter haben wir schon geübt",
        "was habe ich geübt",
        "was haben wir geübt",
        "was habe ich schon gelernt",
        "welche wörter habe ich gelernt"
    ]

    return message.strip(
        " .?!"
    ) in questions


# ==========================================
# FRAGE NACH ANZAHL DER ÜBUNGEN
# ==========================================

def extract_practice_count_word(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!„“\"'"
    )

    patterns = [
        "wie oft habe ich ",
        "wie oft haben wir "
    ]

    for pattern in patterns:

        if not message.startswith(
            pattern
        ):
            continue

        content = message[
            len(pattern):
        ].strip()

        endings = [
            " geübt",
            " schon geübt"
        ]

        for ending in endings:

            if content.endswith(
                ending
            ):

                word = content[
                    :-len(ending)
                ].strip(
                    " .?!„“\"'"
                )

                if word:
                    return word

    return None


# ==========================================
# WORTLISTE FORMATIEREN
# ==========================================

def format_word_list(
    words
):

    if not words:
        return ""

    if len(words) == 1:
        return words[0]

    if len(words) == 2:

        return (
            words[0]
            + " und "
            + words[1]
        )

    return (
        ", ".join(
            words[:-1]
        )
        + " und "
        + words[-1]
    )


# ==========================================
# ANTWORT – GEÜBTE WÖRTER
# ==========================================

def answer_practiced_words(
    user_message,
    state
):

    if not is_practiced_words_request(
        user_message
    ):
        return None

    vocabulary_memory = get_vocabulary_memory(
        state
    )

    words = list(
        vocabulary_memory.keys()
    )

    if not words:

        return (
            "Du hast noch keine Wörter geübt."
        )

    word_list = format_word_list(
        words
    )

    return (
        "Du hast diese Wörter geübt: "
        + word_list
        + "."
    )


# ==========================================
# ANTWORT – WIE OFT
# ==========================================

def answer_practice_count(
    user_message,
    state
):

    word = extract_practice_count_word(
        user_message
    )

    if not word:
        return None

    vocabulary_memory = get_vocabulary_memory(
        state
    )

    word_memory = vocabulary_memory.get(
        word
    )

    if not word_memory:

        return (
            f"Du hast „{word}“ noch nicht geübt."
        )

    count = word_memory.get(
        "seen",
        0
    )

    if count == 1:

        return (
            f"Du hast „{word}“ 1-mal geübt."
        )

    return (
        f"Du hast „{word}“ {count}-mal geübt."
    )


# ==========================================
# FRAGE NACH WIEDERHOLUNG
# ==========================================

def is_review_request(
    user_message
):

    message = normalize(
        user_message
    )

    questions = [
        "was soll ich wiederholen",
        "welche wörter soll ich wiederholen",
        "was muss ich wiederholen",
        "welche wörter muss ich wiederholen",
        "welche wörter soll ich üben"
    ]

    return message.strip(
        " .?!"
    ) in questions


# ==========================================
# ANTWORT – WIEDERHOLUNG
# ==========================================

def answer_review_words(
    user_message,
    state
):

    if not is_review_request(
        user_message
    ):
        return None

    words = get_words_for_review(
        state
    )

    if not words:

        return (
            "Im Moment musst du "
            "keine Wörter wiederholen."
        )

    word_list = format_word_list(
        words
    )

    return (
        "Diese Wörter solltest du "
        "wiederholen: "
        + word_list
        + "."
    )


# ==========================================
# FRAGE NACH GUT GEKONNTEN WÖRTERN
# ==========================================

def is_mastered_words_request(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!"
    )

    questions = [
        "welche wörter kann ich schon gut",
        "welche wörter kann ich gut",
        "welche wörter beherrsche ich schon",
        "welche wörter habe ich schon gut gelernt",
        "was kann ich schon gut"
    ]

    return message in questions


# ==========================================
# GUT GEKONNTE WÖRTER
# ==========================================

def get_mastered_words(
    state
):

    vocabulary_memory = get_vocabulary_memory(
        state
    )

    words = []


    for word, word_memory in vocabulary_memory.items():

        correct_streak = word_memory.get(
            "correct_streak",
            0
        )

        needs_review = word_memory.get(
            "needs_review",
            False
        )


        if (
            correct_streak >= 3
            and not needs_review
        ):

            words.append(
                word
            )


    return words


# ==========================================
# ANTWORT – GUT GEKONNTE WÖRTER
# ==========================================

def answer_mastered_words(
    user_message,
    state
):

    if not is_mastered_words_request(
        user_message
    ):
        return None

    words = get_mastered_words(
        state
    )

    if not words:

        return (
            "Du hast noch keine Wörter "
            "sicher gelernt."
        )

    word_list = format_word_list(
        words
    )

    return (
        "Diese Wörter kannst du "
        "schon gut: "
        + word_list
        + "."
    )


# ==========================================
# FRAGE NACH SCHWIERIGEN WÖRTERN
# ==========================================

def is_difficult_words_request(
    user_message
):

    message = normalize(
        user_message
    ).strip(
        " .?!"
    )

    questions = [
        "welche wörter sind schwierig für mich",
        "welche wörter sind für mich schwierig",
        "mit welchen wörtern habe ich probleme",
        "welche wörter machen mir probleme",
        "wo mache ich noch fehler",
        "bei welchen wörtern mache ich fehler"
    ]

    return message in questions


# ==========================================
# SCHWIERIGE WÖRTER
# ==========================================

def get_difficult_words(
    state
):

    vocabulary_memory = get_vocabulary_memory(
        state
    )

    words = []


    for word, word_memory in vocabulary_memory.items():

        mistakes = word_memory.get(
            "mistakes",
            0
        )

        needs_review = word_memory.get(
            "needs_review",
            False
        )


        if (
            mistakes > 0
            or needs_review
        ):

            words.append(
                word
            )


    return words


# ==========================================
# ANTWORT – SCHWIERIGE WÖRTER
# ==========================================

def answer_difficult_words(
    user_message,
    state
):

    if not is_difficult_words_request(
        user_message
    ):
        return None

    words = get_difficult_words(
        state
    )

    if not words:

        return (
            "Im Moment sehe ich "
            "keine schwierigen Wörter."
        )

    word_list = format_word_list(
        words
    )

    return (
        "Diese Wörter waren für dich "
        "schwierig: "
        + word_list
        + "."
    )


# ==========================================
# MEMORY-ROUTER
# ==========================================

def handle_memory(
    user_message,
    state
):

    # ======================================
    # OSTATNIA AKTYWNOŚĆ
    # ======================================

    answer = answer_last_learning(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # CO ĆWICZYĆ
    # ======================================

    answer = answer_next_practice_step(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # CZEGO NOWEGO SIĘ UCZYĆ
    # ======================================

    answer = answer_next_new_learning_step(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # PLAN NAUCZYCIELA
    #
    # Nele sama decyduje, co jest
    # najważniejsze dla ucznia.
    # ======================================

    answer = answer_teacher_recommendation(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # ĆWICZONE SŁOWA
    # ======================================

    answer = answer_practiced_words(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # LICZBA ĆWICZEŃ
    # ======================================

    answer = answer_practice_count(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # POWTÓRKI
    # ======================================

    answer = answer_review_words(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # OPANOWANE
    # ======================================

    answer = answer_mastered_words(
        user_message,
        state
    )

    if answer:
        return answer


    # ======================================
    # TRUDNE
    # ======================================

    answer = answer_difficult_words(
        user_message,
        state
    )

    if answer:
        return answer


    return None
