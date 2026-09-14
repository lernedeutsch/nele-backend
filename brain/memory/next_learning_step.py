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


    review_flags = (
        "needs_review",
        "review_due",
        "due_for_review",
        "should_review"
    )


    for flag in review_flags:

        if memory.get(
            flag
        ) is True:

            return True


    status = str(
        memory.get(
            "status",
            ""
        )
    ).strip().lower()


    if status in {
        "review",
        "due",
        "needs_review",
        "open",
        "active"
    }:

        return True


    mistakes = get_error_number(
        memory,
        (
            "mistakes",
            "count",
            "occurrences",
            "wrong",
            "errors"
        )
    )


    return mistakes > 0


# ==========================================
# POBRANIE REKORDÓW BŁĘDÓW
# ==========================================

def collect_error_records(
    state
):

    if not isinstance(
        state,
        dict
    ):

        return []


    result = []


    containers = [

        state.get(
            "error_memory"
        ),

        state.get(
            "student_errors"
        ),

        state.get(
            "errors"
        )

    ]


    for container in containers:

        if not container:
            continue


        if isinstance(
            container,
            list
        ):

            for item in container:

                if isinstance(
                    item,
                    dict
                ):

                    result.append(
                        item
                    )

            continue


        if not isinstance(
            container,
            dict
        ):

            continue


        nested_errors = container.get(
            "errors"
        )


        if isinstance(
            nested_errors,
            list
        ):

            for item in nested_errors:

                if isinstance(
                    item,
                    dict
                ):

                    result.append(
                        item
                    )


        elif isinstance(
            nested_errors,
            dict
        ):

            for key, value in (
                nested_errors.items()
            ):

                if not isinstance(
                    value,
                    dict
                ):

                    continue

                record = dict(
                    value
                )

                record.setdefault(
                    "error_type",
                    key
                )

                result.append(
                    record
                )


        for key, value in (
            container.items()
        ):

            if key == "errors":
                continue

            if not isinstance(
                value,
                dict
            ):
                continue

            record = dict(
                value
            )

            record.setdefault(
                "error_type",
                key
            )

            result.append(
                record
            )


    return result


# ==========================================
# BŁĘDY DO POWTÓRKI
# ==========================================

def get_errors_for_review(
    state,
    limit=3
):

    records = collect_error_records(
        state
    )

    review_items = []


    for record in records:

        if not error_needs_review(
            record
        ):

            continue


        error_type = (
            record.get(
                "error_type"
            )
            or
            record.get(
                "type"
            )
            or
            record.get(
                "category"
            )
        )


        if not error_type:

            continue


        mistakes = get_error_number(
            record,
            (
                "mistakes",
                "count",
                "occurrences",
                "wrong",
                "errors"
            )
        )


        review_items.append({

            "error_type":
                str(
                    error_type
                ).strip(),

            "label":
                display_error_type(
                    error_type
                ),

            "mistakes":
                mistakes

        })


    review_items.sort(
        key=lambda item:
            item.get(
                "mistakes",
                0
            ),
        reverse=True
    )


    result = []
    seen = set()


    for item in review_items:

        key = str(
            item.get(
                "error_type",
                ""
            )
        ).lower()


        if not key:
            continue


        if key in seen:
            continue


        seen.add(
            key
        )

        result.append(
            item
        )


        if len(
            result
        ) >= limit:

            break


    return result


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

    if state is None:

        return {
            "type":
                "start",

            "words":
                [],

            "errors":
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
    # 1. BŁĘDY
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

            "topic":
                "Fehlertraining",

            "message":
                (
                    "Heute sollten wir zuerst "
                    f"kurz {error_list} üben."
                )
        }


    # ======================================
    # 2. SŁOWA DO POWTÓRKI
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

            "topic":
                "Wortschatz",

            "message":
                (
                    "Heute sollten wir zuerst "
                    f"{word_list} wiederholen."
                )
        }


    # ======================================
    # 3. TRUDNE SŁOWA
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

            "topic":
                "Wortschatz",

            "message":
                (
                    "Diese Wörter waren zuletzt "
                    "etwas schwieriger für dich: "
                    f"{word_list}. "
                    "Lass sie uns kurz üben."
                )
        }


    # ======================================
    # 4. OSTATNIE SŁOWO
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

            "topic":
                "Wortschatz",

            "message":
                (
                    "Zuletzt hast du das Wort "
                    f"„{last_word}“ geübt. "
                    "Möchtest du damit "
                    "weitermachen?"
                )
        }


    # ======================================
    # 5. OSTATNI TEMAT
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

                "topic":
                    topic,

                "message":
                    (
                        "Zuletzt hast du das Thema "
                        f"„{topic}“ geübt. "
                        "Heute können wir damit "
                        "weitermachen und danach "
                        "einen kurzen Hotel-Dialog "
                        "machen."
                    )
            }


        return {
            "type":
                "continue_topic",

            "words":
                [],

            "errors":
                [],

            "topic":
                topic,

            "message":
                (
                    "Zuletzt hast du "
                    f"„{topic}“ geübt. "
                    "Möchtest du damit "
                    "weitermachen?"
                )
        }


    return {
        "type":
            "start",

        "words":
            [],

        "errors":
            [],

        "topic":
            None,

        "message":
            (
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

    level = str(
        level or ""
    ).strip().upper()


    if level == "A1":

        if not a1_lesson_exists(
            lesson
        ):

            return []


        sections = (
            get_a1_lesson_sections(
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

                    "completion_percent":
                        100,

                    "message":
                        (
                            f"Du hast {level}, "
                            f"Lektion {current_lesson} "
                            "abgeschlossen. "
                            "Als Nächstes können wir "
                            f"mit {level}, Lektion "
                            f"{next_lesson} anfangen."
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
                        f"Du hast {level}, "
                        f"Lektion {current_lesson} "
                        "schon abgeschlossen. "
                        "Als Nächstes können wir mit "
                        f"{level}, Lektion "
                        f"{next_lesson} "
                        "weitermachen."
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
    # 1. BŁĘDY
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

            "next":
                new_learning_plan,

            "message":
                message
        }


    # ======================================
    # 2. SŁOWNICTWO
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

            "next":
                new_learning_plan,

            "message":
                message
        }


    # ======================================
    # 3. LEKCJA / NOWY MATERIAŁ
    #
    # WAŻNE:
    #
    # Zwracamy prawdziwy plan nowej nauki,
    # np.:
    #
    # type = new_section
    # section = Wir begrüßen uns
    #
    # Dzięki temu review.py może zapisać
    # pending_new_learning, a późniejsze
    # "Ja" uruchomi lesson_teaching.py.
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
