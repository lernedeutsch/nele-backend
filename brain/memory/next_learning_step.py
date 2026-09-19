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

from brain.memory.lesson_review import (
    get_due_lesson_reviews
)

from brain.memory.error_memory import (
    get_error_summary
)

from brain.memory.error_review import (
    refresh_error_reviews,
    get_due_error_reviews
)

from brain.knowledge.A1.lessons import (
    lesson_exists as a1_lesson_exists,
    get_lesson_sections as get_a1_lesson_sections,
    get_next_lesson_number as get_next_a1_lesson_number
)


from brain.logic.lesson_loader import (
    lesson_module_exists,
    get_lesson_sections_from_module,
    get_next_lesson_number_from_modules
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
# ŁADNE NAZWY TYPÓW BŁĘDÓW
# ==========================================

def display_error_type(
    error_type
):

    error_type = str(
        error_type or ""
    ).strip().lower()


    names = {

        "word_order":
            "Wortstellung",

        "wortstellung":
            "Wortstellung",

        "article":
            "Artikel",

        "articles":
            "Artikel",

        "artikel":
            "Artikel",

        "case":
            "Kasus",

        "kasus":
            "Kasus",

        "verb":
            "Verbformen",

        "verb_form":
            "Verbformen",

        "verb_forms":
            "Verbformen",

        "verb_conjugation":
            "Verbformen",

        "conjugation":
            "Verbformen",

        "grammar":
            "Grammatik",

        "grammatik":
            "Grammatik",

        "vocabulary":
            "Wortschatz",

        "wortschatz":
            "Wortschatz",

        "spelling":
            "Rechtschreibung",

        "rechtschreibung":
            "Rechtschreibung",

        "preposition":
            "Präpositionen",

        "prepositions":
            "Präpositionen",

        "pronoun":
            "Pronomen",

        "pronouns":
            "Pronomen",

        "sentence_structure":
            "Satzbau",

        "sentence_order":
            "Wortstellung"
    }


    if error_type in names:

        return names[
            error_type
        ]


    if not error_type:

        return "Grammatik"


    value = error_type.replace(
        "_",
        " "
    ).strip()


    return display_word(
        value
    )


# ==========================================
# LICZBA Z PAMIĘCI BŁĘDU
# ==========================================

def get_error_number(
    memory,
    keys
):

    if not isinstance(
        memory,
        dict
    ):

        return 0


    for key in keys:

        value = memory.get(
            key
        )

        try:

            value = int(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            continue


        if value > 0:

            return value


    return 0


# ==========================================
# CZY BŁĄD WYMAGA POWTÓRKI
# ==========================================

def error_needs_review(
    memory
):

    if not isinstance(
        memory,
        dict
    ):

        return False


    if memory.get(
        "mastered"
    ) is True:

        return False


    if memory.get(
        "resolved"
    ) is True:

        return False


    if memory.get(
        "completed"
    ) is True:

        return False


    if memory.get(
        "needs_practice"
    ) is True:

        return True


    if memory.get(
        "needs_review"
    ) is True:

        return True


    if memory.get(
        "review_due"
    ) is True:

        return True


    if memory.get(
        "due_for_review"
    ) is True:

        return True


    if memory.get(
        "should_review"
    ) is True:

        return True


    return False


# ==========================================
# BŁĘDY DO POWTÓRKI
# ADAPTIVE REVIEW 2.0
# ==========================================

def get_errors_for_review(
    state,
    limit=3
):

    if state is None:
        return []


    try:

        refresh_error_reviews(
            state
        )

    except Exception as error:

        print(
            f"Teacher error review refresh: {error}"
        )


    try:

        due_error_types = get_due_error_reviews(
            state
        )

    except Exception as error:

        print(
            f"Teacher due error review: {error}"
        )

        due_error_types = []


    if not due_error_types:

        return []


    result = []
    seen = set()


    for error_type in due_error_types:

        error_type = str(
            error_type or ""
        ).strip()


        if not error_type:
            continue


        key = error_type.lower()


        if key in seen:
            continue


        seen.add(
            key
        )


        summary = get_error_summary(
            state,
            error_type
        )


        if not isinstance(
            summary,
            dict
        ):

            summary = {}


        mistakes = get_error_number(
            summary,
            (
                "count",
                "mistakes",
                "occurrences",
                "wrong",
                "errors"
            )
        )


        result.append({

            "error_type":
                error_type,

            "label":
                display_error_type(
                    error_type
                ),

            "mistakes":
                mistakes

        })


    result.sort(
        key=lambda item:
            item.get(
                "mistakes",
                0
            ),
        reverse=True
    )


    return result[
        :limit
    ]


# ==========================================
# LEKCJE DO POWTÓRKI
# SPACED REPETITION
# ==========================================

def get_lessons_for_review(
    state,
    limit=1
):

    if state is None:
        return []


    try:

        due_reviews = get_due_lesson_reviews(
            state
        )

    except Exception as error:

        print(
            f"Teacher lesson review error: {error}"
        )

        due_reviews = []


    if not isinstance(
        due_reviews,
        list
    ):

        return []


    result = []
    seen = set()


    for item in due_reviews:

        if not isinstance(
            item,
            dict
        ):

            continue


        level = str(
            item.get(
                "level",
                "A1"
            )
            or
            "A1"
        ).strip().upper()


        try:

            lesson = int(
                item.get(
                    "lesson",
                    1
                )
            )

        except (
            TypeError,
            ValueError
        ):

            lesson = 1


        key = (
            level,
            lesson
        )


        if key in seen:
            continue


        seen.add(
            key
        )


        result.append({

            "level":
                level,

            "lesson":
                lesson,

            "review":
                item.get(
                    "review",
                    {}
                )

        })


    return result[
        :limit
    ]


# ==========================================
# OPIS LEKCJI DO POWTÓRKI
# ==========================================

def get_lesson_review_description(
    lesson_review
):

    if not isinstance(
        lesson_review,
        dict
    ):

        return ""


    level = str(
        lesson_review.get(
            "level",
            "A1"
        )
        or
        "A1"
    ).strip().upper()


    try:

        lesson = int(
            lesson_review.get(
                "lesson",
                1
            )
        )

    except (
        TypeError,
        ValueError
    ):

        lesson = 1


    return (
        f"{level}, Lektion {lesson}"
    )


# ==========================================
# FORMATOWANIE BŁĘDÓW
# ==========================================

def format_error_list(
    errors
):

    labels = unique_items([
        item.get(
            "label"
        )
        for item in errors
        if isinstance(
            item,
            dict
        )
    ])


    if not labels:
        return ""


    if len(labels) == 1:

        return labels[0]


    if len(labels) == 2:

        return (
            labels[0]
            + " und "
            + labels[1]
        )


    return (
        ", ".join(
            labels[:-1]
        )
        + " und "
        + labels[-1]
    )


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
#
# Funkcja służy do INFORMACJI
# o historii ucznia.
#
# Nie oznacza automatycznie,
# że słowo trzeba powtarzać TERAZ.
# ==========================================

def get_difficult_words(
    state,
    limit=3
):

    vocabulary_memory = (
        get_vocabulary_memory(
            state
        )
    )

    difficult_words = []


    for word, memory in (
        vocabulary_memory.items()
    ):

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
# SPACED REPETITION
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


    return review_words[
        :3
    ]


# ==========================================
# NASTĘPNY KROK – POWTÓRKA / ĆWICZENIE
#
# PRIORYTET:
#
# 1. błędy należne
# 2. słowa należne
# 3. lekcja należna do powtórki
# 4. trudne słowa informacyjnie
# 5. ostatnie słowa
# 6. ostatni temat
# ==========================================

def get_next_learning_step(
    state
):

    if state is None:

        return {
            "type":
                "start",

            "words":
                [],

            "errors":
                [],

            "lesson_reviews":
                [],

            "topic":
                None,

            "message":
                (
                    "Lass uns mit einer "
                    "kleinen Übung anfangen."
                )
        }


    # ======================================
    # 1. BŁĘDY NALEŻNE TERAZ
    # ======================================

    errors = get_errors_for_review(
        state,
        limit=2
    )


    if errors:

        error_list = format_error_list(
            errors
        )


        return {
            "type":
                "error_review",

            "words":
                [],

            "errors":
                errors,

            "lesson_reviews":
                [],

            "topic":
                "Fehlertraining",

            "message":
                (
                    "Heute sollten wir zuerst "
                    f"kurz {error_list} üben."
                )
        }


    # ======================================
    # 2. SŁOWA NALEŻNE TERAZ
    # ======================================

    review_words = get_review_plan(
        state
    )


    if review_words:

        word_list = format_word_list(
            review_words
        )


        return {
            "type":
                "vocabulary_review",

            "words":
                review_words,

            "errors":
                [],

            "lesson_reviews":
                [],

            "topic":
                "Wortschatz",

            "message":
                (
                    "Heute sollten wir zuerst "
                    f"{word_list} wiederholen."
                )
        }


    # ======================================
    # 3. LEKCJA NALEŻNA DO POWTÓRKI
    # ======================================

    lesson_reviews = get_lessons_for_review(
        state,
        limit=1
    )


    if lesson_reviews:

        lesson_review = lesson_reviews[0]

        lesson_description = (
            get_lesson_review_description(
                lesson_review
            )
        )


        return {
            "type":
                "lesson_review",

            "words":
                [],

            "errors":
                [],

            "lesson_reviews":
                lesson_reviews,

            "level":
                lesson_review.get(
                    "level"
                ),

            "lesson":
                lesson_review.get(
                    "lesson"
                ),

            "topic":
                "Lektionswiederholung",

            "message":
                (
                    "Heute sollten wir zuerst "
                    f"{lesson_description} "
                    "wiederholen."
                )
        }


    # ======================================
    # 4. TRUDNE SŁOWA – INFORMACYJNIE
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
            "type":
                "difficult_vocabulary",

            "words":
                difficult_words,

            "errors":
                [],

            "lesson_reviews":
                [],

            "topic":
                "Wortschatz",

            "message":
                (
                    "Diese Wörter waren zuletzt "
                    "etwas schwieriger für dich: "
                    f"{word_list}."
                )
        }


    # ======================================
    # 5. OSTATNIE SŁOWO – INFORMACYJNIE
    # ======================================

    recent_words = (
        get_recent_vocabulary_words(
            state,
            limit=2
        )
    )


    if recent_words:

        last_word = display_word(
            recent_words[0]
        )


        return {
            "type":
                "continue_vocabulary",

            "words":
                [
                    recent_words[0]
                ],

            "errors":
                [],

            "lesson_reviews":
                [],

            "topic":
                "Wortschatz",

            "message":
                (
                    "Zuletzt hast du das Wort "
                    f"„{last_word}“ geübt."
                )
        }


    # ======================================
    # 6. OSTATNI TEMAT
    # ======================================

    recent_topics = (
        get_recent_learning_topics(
            state,
            limit=1
        )
    )


    if recent_topics:

        topic = recent_topics[0]


        if "hotel" in topic.lower():

            return {
                "type":
                    "continue_topic",

                "words":
                    [],

                "errors":
                    [],

                "lesson_reviews":
                    [],

                "topic":
                    topic,

                "message":
                    (
                        "Zuletzt hast du das Thema "
                        f"„{topic}“ geübt."
                    )
            }


        return {
            "type":
                "continue_topic",

            "words":
                [],

            "errors":
                [],

            "lesson_reviews":
                [],

            "topic":
                topic,

            "message":
                (
                    "Zuletzt hast du "
                    f"„{topic}“ geübt."
                )
        }


    return {
        "type":
            "start",

        "words":
            [],

        "errors":
            [],

        "lesson_reviews":
            [],

        "topic":
            None,

        "message":
            (
                "Wir haben noch keinen "
                "Lernschwerpunkt gespeichert."
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

    level = str(
        level or ""
    ).strip().upper()


    if level == "A1":

        sections = []


        if a1_lesson_exists(
            lesson
        ):

            sections = (
                get_a1_lesson_sections(
                    lesson
                )
            )


        if (
            not sections
            and
            lesson_module_exists(
                level,
                lesson
            )
        ):

            sections = (
                get_lesson_sections_from_module(
                    level,
                    lesson
                )
            )


        if sections:

            set_lesson_sections(
                state,
                level,
                lesson,
                sections
            )


        return sections


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

        static_next = get_next_a1_lesson_number(
            lesson
        )


        dynamic_next = (
            get_next_lesson_number_from_modules(
                level,
                lesson
            )
        )


        candidates = [
            value
            for value in (
                static_next,
                dynamic_next
            )
            if value is not None
        ]


        if candidates:

            return min(
                candidates
            )


        return None


    return get_next_lesson_number_from_modules(
        level,
        lesson
    )


# ==========================================
# NASTĘPNY NOWY MATERIAŁ
# ==========================================

def get_next_new_learning_step(
    state
):

    if state is None:

        return {
            "type":
                "new_learning",

            "level":
                "A1",

            "lesson":
                1,

            "section":
                None,

            "topic":
                None,

            "message":
                (
                    "Lass uns mit A1, "
                    "Lektion 1 anfangen."
                )
        }


    level = get_current_level(
        state
    )


    current_lesson = get_current_lesson(
        state
    )


    sync_lesson_structure(
        state,
        level,
        current_lesson
    )


    lesson_progress = (
        get_lesson_progress(
            state,
            level,
            current_lesson
        )
    )


    sections = lesson_progress.get(
        "sections",
        []
    )


    if sections:

        next_section = (
            get_next_incomplete_section(
                state,
                level,
                current_lesson
            )
        )


        if next_section:

            completion_percent = (
                get_lesson_completion_percent(
                    state,
                    level,
                    current_lesson
                )
            )


            return {
                "type":
                    "new_section",

                "level":
                    level,

                "lesson":
                    current_lesson,

                "section":
                    next_section,

                "topic":
                    next_section,

                "completion_percent":
                    completion_percent,

                "message":
                    (
                        f"Du bist bei {level}, "
                        f"Lektion {current_lesson}. "
                        "Als Nächstes ist "
                        f"„{next_section}“ dran."
                    )
            }


        if is_lesson_fully_completed(
            state,
            level,
            current_lesson
        ):

            next_lesson = (
                get_next_course_lesson(
                    level,
                    current_lesson
                )
            )


            if next_lesson is not None:

                next_sections = sync_lesson_structure(
                    state,
                    level,
                    next_lesson
                )


                first_section = (
                    next_sections[0]
                    if next_sections
                    else None
                )


                return {
                    "type":
                        "new_lesson",

                    "level":
                        level,

                    "lesson":
                        next_lesson,

                    "section":
                        first_section,

                    "topic":
                        first_section,

                    "completion_percent":
                        100,

                    "message":
                        (
                            f"Lektion {current_lesson} ist fertig. "
                            f"Jetzt kommt Lektion {next_lesson}."
                        )
                }


            return {
                "type":
                    "lesson_completed",

                "level":
                    level,

                "lesson":
                    current_lesson,

                "section":
                    None,

                "topic":
                    None,

                "completion_percent":
                    100,

                "message":
                    (
                        f"Du hast {level}, "
                        f"Lektion {current_lesson} "
                        "vollständig abgeschlossen."
                    )
            }


    if is_lesson_completed(
        state,
        current_lesson
    ):

        next_lesson = (
            get_next_course_lesson(
                level,
                current_lesson
            )
        )


        if next_lesson is not None:

            return {
                "type":
                    "new_lesson",

                "level":
                    level,

                "lesson":
                    next_lesson,

                "section":
                    None,

                "topic":
                    None,

                "message":
                    (
                        f"Lektion {current_lesson} ist fertig. "
                        f"Jetzt kommt Lektion {next_lesson}."
                    )
            }


    return {
        "type":
            "continue_lesson",

        "level":
            level,

        "lesson":
            current_lesson,

        "section":
            None,

        "topic":
            None,

        "message":
            (
                "Du bist gerade bei "
                f"{level}, Lektion "
                f"{current_lesson}. "
                "Als Nächstes können wir dort "
                "mit neuem Stoff weitermachen."
            )
    }


# ==========================================
# KRÓTKI OPIS NOWEGO KROKU
# ==========================================

def get_new_learning_short_description(
    plan
):

    if not isinstance(
        plan,
        dict
    ):

        return ""


    section = plan.get(
        "section"
    )


    if section:

        return (
            f"„{section}“"
        )


    level = plan.get(
        "level"
    )

    lesson = plan.get(
        "lesson"
    )


    if (
        level
        and
        lesson
    ):

        return (
            f"{level}, Lektion {lesson}"
        )


    topic = plan.get(
        "topic"
    )


    if topic:

        return (
            f"„{topic}“"
        )


    return ""


# ==========================================
# MÓZG NAUCZYCIELA
#
# PRIORYTET:
#
# 1. błędy
# 2. słownictwo
# 3. powtórka całej lekcji
# 4. nowy materiał
# ==========================================

def get_teacher_learning_plan(
    state
):

    if state is None:

        return {
            "type":
                "new_learning",

            "level":
                "A1",

            "lesson":
                1,

            "section":
                None,

            "topic":
                None,

            "priority":
                "start",

            "message":
                (
                    "Lass uns mit A1, "
                    "Lektion 1 anfangen."
                )
        }


    new_learning_plan = (
        get_next_new_learning_step(
            state
        )
    )


    new_description = (
        get_new_learning_short_description(
            new_learning_plan
        )
    )


    # ======================================
    # 1. BŁĘDY NALEŻNE TERAZ
    # ======================================

    errors = get_errors_for_review(
        state,
        limit=2
    )


    if errors:

        error_list = format_error_list(
            errors
        )


        if new_description:

            message = (
                "Du hattest zuletzt noch "
                f"Probleme mit {error_list}. "
                "Wir üben das kurz und machen "
                "danach mit "
                f"{new_description} weiter."
            )

        else:

            message = (
                "Du hattest zuletzt noch "
                f"Probleme mit {error_list}. "
                "Wir üben das zuerst kurz."
            )


        return {
            "type":
                "teacher_plan",

            "priority":
                "error_review",

            "errors":
                errors,

            "words":
                [],

            "lesson_reviews":
                [],

            "next":
                new_learning_plan,

            "message":
                message
        }


    # ======================================
    # 2. SŁOWNICTWO NALEŻNE TERAZ
    # ======================================

    review_words = get_review_plan(
        state
    )


    if review_words:

        word_list = format_word_list(
            review_words
        )


        if new_description:

            message = (
                "Wir wiederholen zuerst kurz "
                f"{word_list}. "
                "Danach machen wir mit "
                f"{new_description} weiter."
            )

        else:

            message = (
                "Wir wiederholen zuerst kurz "
                f"{word_list}."
            )


        return {
            "type":
                "teacher_plan",

            "priority":
                "vocabulary_review",

            "errors":
                [],

            "words":
                review_words,

            "lesson_reviews":
                [],

            "next":
                new_learning_plan,

            "message":
                message
        }


    # ======================================
    # 3. POWTÓRKA CAŁEJ LEKCJI
    # ======================================

    lesson_reviews = get_lessons_for_review(
        state,
        limit=1
    )


    if lesson_reviews:

        lesson_review = lesson_reviews[0]

        lesson_description = (
            get_lesson_review_description(
                lesson_review
            )
        )


        if new_description:

            message = (
                "Heute wiederholen wir zuerst "
                f"{lesson_description}. "
                "Danach machen wir mit "
                f"{new_description} weiter."
            )

        else:

            message = (
                "Heute wiederholen wir zuerst "
                f"{lesson_description}."
            )


        return {
            "type":
                "teacher_plan",

            "priority":
                "lesson_review",

            "errors":
                [],

            "words":
                [],

            "lesson_reviews":
                lesson_reviews,

            "level":
                lesson_review.get(
                    "level"
                ),

            "lesson":
                lesson_review.get(
                    "lesson"
                ),

            "next":
                new_learning_plan,

            "message":
                message
        }


    # ======================================
    # 4. BRAK NALEŻNYCH POWTÓREK
    # -> OD RAZU LEKCJA / NOWY MATERIAŁ
    # ======================================

    return new_learning_plan


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


# ==========================================
# WIADOMOŚĆ – DECYZJA NAUCZYCIELA
# ==========================================

def get_teacher_learning_message(
    state
):

    plan = get_teacher_learning_plan(
        state
    )

    return plan.get(
        "message"
)
