# ==========================================
# NELE – NASTĘPNY KROK NAUKI
# STUDENT MEMORY 2.0
# ==========================================

from brain.memory.vocabulary_memory import (
    get_vocabulary_memory,
    get_words_for_review
)

from brain.memory.student_progress import (
    get_recent_learning_topics,
    get_current_level,
    get_current_lesson,
    is_lesson_completed
)

from brain.memory.lesson_progress import (
    get_lesson_progress,
    set_lesson_sections,
    get_next_incomplete_section,
    get_lesson_completion_percent,
    is_lesson_fully_completed
)

from brain.knowledge.A1.lessons import (
    lesson_exists as a1_lesson_exists,
    get_lesson_sections as get_a1_lesson_sections,
    get_next_lesson_number as get_next_a1_lesson_number
)


# ==========================================
# ŁADNE WYŚWIETLANIE SŁOWA
# ==========================================

def display_word(
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
# USUWANIE DUPLIKATÓW
# ==========================================

def unique_items(
    items
):

    result = []
    seen = set()

    for item in items:

        if not item:
            continue

        value = str(
            item
        ).strip()

        if not value:
            continue

        key = value.lower()

        if key in seen:
            continue

        seen.add(
            key
        )

        result.append(
            value
        )

    return result


# ==========================================
# FORMATOWANIE LISTY SŁÓW
# ==========================================

def format_word_list(
    words
):

    words = [
        f"„{display_word(word)}“"
        for word in words
        if word
    ]

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
# TRUDNE SŁOWA
# ==========================================

def get_difficult_words(
    state,
    limit=3
):

    vocabulary_memory = get_vocabulary_memory(
        state
    )

    difficult_words = []

    for word, memory in vocabulary_memory.items():

        mistakes = memory.get(
            "mistakes",
            0
        )

        correct = memory.get(
            "correct",
            0
        )

        if mistakes <= 0:
            continue

        difficult_words.append(
            (
                word,
                mistakes,
                correct
            )
        )

    difficult_words.sort(
        key=lambda item: (
            item[1],
            -item[2]
        ),
        reverse=True
    )

    return [
        item[0]
        for item in difficult_words[
            :limit
        ]
    ]


# ==========================================
# OSTATNIE ĆWICZONE SŁOWA
# ==========================================

def get_recent_vocabulary_words(
    state,
    limit=3
):

    topics = get_recent_learning_topics(
        state,
        limit=10
    )

    words = []

    for topic in topics:

        if not topic.startswith(
            "Wortschatz:"
        ):
            continue

        word = topic.split(
            ":",
            1
        )[1].strip()

        if word:

            words.append(
                word
            )

    words = unique_items(
        words
    )

    return words[
        :limit
    ]


# ==========================================
# PLAN – SŁOWA DO POWTÓRKI
# ==========================================

def get_review_plan(
    state
):

    review_words = get_words_for_review(
        state
    )

    review_words = unique_items(
        review_words
    )

    difficult_words = get_difficult_words(
        state,
        limit=5
    )

    extra_difficult = []

    review_keys = {
        word.lower()
        for word in review_words
    }

    for word in difficult_words:

        if word.lower() in review_keys:
            continue

        extra_difficult.append(
            word
        )

    main_words = (
        review_words
        + extra_difficult
    )

    main_words = unique_items(
        main_words
    )

    return main_words[
        :3
    ]


# ==========================================
# NASTĘPNY KROK – POWTÓRKA / ĆWICZENIE
# ==========================================

def get_next_learning_step(
    state
):
    """
    Decyduje, co uczeń powinien
    POWTÓRZYĆ lub ĆWICZYĆ.

    Przykład:
    "Was soll ich heute üben?"
    """

    if state is None:

        return {
            "type": "start",
            "words": [],
            "topic": None,
            "message":
                "Lass uns mit einer kleinen Übung anfangen."
        }


    # ======================================
    # 1. SŁOWA DO POWTÓRKI
    # ======================================

    review_words = get_review_plan(
        state
    )

    if review_words:

        word_list = format_word_list(
            review_words
        )

        return {
            "type": "vocabulary_review",
            "words": review_words,
            "topic": "Wortschatz",

            "message": (
                "Heute sollten wir zuerst "
                f"{word_list} wiederholen."
            )
        }


    # ======================================
    # 2. TRUDNE SŁOWA
    # ======================================

    difficult_words = get_difficult_words(
        state,
        limit=3
    )

    difficult_words = unique_items(
        difficult_words
    )

    if difficult_words:

        word_list = format_word_list(
            difficult_words
        )

        return {
            "type": "difficult_vocabulary",
            "words": difficult_words,
            "topic": "Wortschatz",

            "message": (
                "Diese Wörter waren zuletzt "
                "etwas schwieriger für dich: "
                f"{word_list}. "
                "Lass sie uns kurz üben."
            )
        }


    # ======================================
    # 3. OSTATNIE SŁOWO
    # ======================================

    recent_words = get_recent_vocabulary_words(
        state,
        limit=2
    )

    if recent_words:

        last_word = display_word(
            recent_words[0]
        )

        return {
            "type": "continue_vocabulary",

            "words": [
                recent_words[0]
            ],

            "topic": "Wortschatz",

            "message": (
                "Zuletzt hast du das Wort "
                f"„{last_word}“ geübt. "
                "Möchtest du damit weitermachen?"
            )
        }


    # ======================================
    # 4. OSTATNI TEMAT
    # ======================================

    recent_topics = get_recent_learning_topics(
        state,
        limit=1
    )

    if recent_topics:

        topic = recent_topics[0]

        if "hotel" in topic.lower():

            return {
                "type": "continue_topic",
                "words": [],
                "topic": topic,

                "message": (
                    "Zuletzt hast du das Thema "
                    f"„{topic}“ geübt. "
                    "Heute können wir damit "
                    "weitermachen und danach "
                    "einen kurzen Hotel-Dialog machen."
                )
            }

        return {
            "type": "continue_topic",
            "words": [],
            "topic": topic,

            "message": (
                "Zuletzt hast du "
                f"„{topic}“ geübt. "
                "Möchtest du damit weitermachen?"
            )
        }


    # ======================================
    # 5. JESZCZE BRAK HISTORII
    # ======================================

    return {
        "type": "start",
        "words": [],
        "topic": None,

        "message": (
            "Wir haben noch keinen "
            "Lernschwerpunkt gespeichert. "
            "Lass uns mit einer kleinen "
            "Übung anfangen."
        )
    }


# ==========================================
# STRUKTURA PRAWDZIWEJ LEKCJI
# ==========================================

def sync_lesson_structure(
    state,
    level,
    lesson
):
    """
    Pobiera prawdziwą strukturę kursu
    z brain/knowledge/... i zapisuje ją
    w pamięci postępu lekcji.

    Nie usuwa ukończonych części.
    """

    level = str(
        level or ""
    ).strip().upper()


    # ======================================
    # A1
    # ======================================

    if level == "A1":

        if not a1_lesson_exists(
            lesson
        ):
            return []

        sections = get_a1_lesson_sections(
            lesson
        )

        if sections:

            set_lesson_sections(
                state,
                level,
                lesson,
                sections
            )

        return sections


    # ======================================
    # INNE POZIOMY
    # PÓŹNIEJ PODŁĄCZYMY A2/B1...
    # ======================================

    return []


# ==========================================
# NASTĘPNA PRAWDZIWA LEKCJA
# ==========================================

def get_next_course_lesson(
    level,
    lesson
):

    level = str(
        level or ""
    ).strip().upper()


    if level == "A1":

        return get_next_a1_lesson_number(
            lesson
        )


    return None


# ==========================================
# NASTĘPNY NOWY MATERIAŁ
# ==========================================

def get_next_new_learning_step(
    state
):
    """
    Decyduje, czego NOWEGO uczeń
    powinien uczyć się dalej.

    Przykład:
    "Was soll ich heute lernen?"

    Korzysta z prawdziwej struktury
    kursu, jeśli jest dostępna.
    """

    if state is None:

        return {
            "type": "new_learning",
            "level": "A1",
            "lesson": 1,
            "section": None,
            "topic": None,

            "message": (
                "Lass uns mit A1, "
                "Lektion 1 anfangen."
            )
        }


    # ======================================
    # AKTUALNY POZIOM
    # ======================================

    level = get_current_level(
        state
    )


    # ======================================
    # AKTUALNA LEKCJA
    # ======================================

    current_lesson = get_current_lesson(
        state
    )


    # ======================================
    # PODŁĄCZENIE PRAWDZIWEJ
    # STRUKTURY LEKCJI
    # ======================================

    sync_lesson_structure(
        state,
        level,
        current_lesson
    )


    # ======================================
    # POSTĘP WEWNĄTRZ LEKCJI
    # ======================================

    lesson_progress = get_lesson_progress(
        state,
        level,
        current_lesson
    )


    sections = lesson_progress.get(
        "sections",
        []
    )


    # ======================================
    # JEŻELI LEKCJA MA CZĘŚCI
    # ======================================

    if sections:

        next_section = (
            get_next_incomplete_section(
                state,
                level,
                current_lesson
            )
        )


        # ==================================
        # NASTĘPNA NIEUKOŃCZONA CZĘŚĆ
        # ==================================

        if next_section:

            completion_percent = (
                get_lesson_completion_percent(
                    state,
                    level,
                    current_lesson
                )
            )

            return {
                "type": "new_section",
                "level": level,
                "lesson": current_lesson,
                "section": next_section,
                "topic": next_section,

                "completion_percent":
                    completion_percent,

                "message": (
                    f"Du bist bei {level}, "
                    f"Lektion {current_lesson}. "
                    "Als Nächstes ist "
                    f"„{next_section}“ dran."
                )
            }


        # ==================================
        # CAŁA LEKCJA UKOŃCZONA
        # ==================================

        if is_lesson_fully_completed(
            state,
            level,
            current_lesson
        ):

            next_lesson = get_next_course_lesson(
                level,
                current_lesson
            )


            # =================================
            # MAMY PRAWDZIWĄ NASTĘPNĄ LEKCJĘ
            # =================================

            if next_lesson is not None:

                return {
                    "type": "new_lesson",
                    "level": level,
                    "lesson": next_lesson,
                    "section": None,
                    "topic": None,
                    "completion_percent": 100,

                    "message": (
                        f"Du hast {level}, "
                        f"Lektion {current_lesson} "
                        "abgeschlossen. "
                        "Als Nächstes können wir "
                        f"mit {level}, Lektion "
                        f"{next_lesson} anfangen."
                    )
                }


            # =================================
            # NASTĘPNA LEKCJA NIE JEST JESZCZE
            # W STRUKTURZE BACKENDU
            # =================================

            return {
                "type": "lesson_completed",
                "level": level,
                "lesson": current_lesson,
                "section": None,
                "topic": None,
                "completion_percent": 100,

                "message": (
                    f"Du hast {level}, "
                    f"Lektion {current_lesson} "
                    "vollständig abgeschlossen."
                )
            }


    # ======================================
    # STARSZY SYSTEM:
    # CAŁA LEKCJA OZNACZONA JAKO UKOŃCZONA
    # ======================================

    if is_lesson_completed(
        state,
        current_lesson
    ):

        next_lesson = get_next_course_lesson(
            level,
            current_lesson
        )


        if next_lesson is not None:

            return {
                "type": "new_lesson",
                "level": level,
                "lesson": next_lesson,
                "section": None,
                "topic": None,

                "message": (
                    f"Du hast {level}, "
                    f"Lektion {current_lesson} "
                    "schon abgeschlossen. "
                    "Als Nächstes können wir mit "
                    f"{level}, Lektion {next_lesson} "
                    "weitermachen."
                )
            }


    # ======================================
    # BRAK STRUKTURY LEKCJI
    # ======================================

    return {
        "type": "continue_lesson",
        "level": level,
        "lesson": current_lesson,
        "section": None,
        "topic": None,

        "message": (
            f"Du bist gerade bei "
            f"{level}, Lektion {current_lesson}. "
            "Als Nächstes können wir dort "
            "mit neuem Stoff weitermachen."
        )
    }


# ==========================================
# WIADOMOŚĆ – POWTÓRKA
# ==========================================

def get_next_learning_message(
    state
):

    plan = get_next_learning_step(
        state
    )

    return plan.get(
        "message"
    )


# ==========================================
# WIADOMOŚĆ – NOWY MATERIAŁ
# ==========================================

def get_next_new_learning_message(
    state
):

    plan = get_next_new_learning_step(
        state
    )

    return plan.get(
        "message"
)
