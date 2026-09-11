# ==========================================
# NELE – NASTĘPNY KROK NAUKI
# STUDENT MEMORY 2.0
# ==========================================

from brain.memory.vocabulary_memory import (
    get_vocabulary_memory,
    get_words_for_review
)

from brain.memory.student_progress import (
    get_recent_learning_topics
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


    # ======================================
    # NAJWIĘCEJ BŁĘDÓW NA POCZĄTKU
    # ======================================

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


    # ======================================
    # TRUDNE SŁOWA, KTÓRYCH NIE MA JESZCZE
    # NA LIŚCIE POWTÓREK
    # ======================================

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


    # ======================================
    # MAKSYMALNIE 3 SŁOWA NA POCZĄTEK
    # ======================================

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
# NASTĘPNY KROK NAUKI
# ==========================================

def get_next_learning_step(
    state
):
    """
    Analizuje pamięć ucznia i zwraca
    propozycję następnego kroku nauki.

    Zwracany wynik jest słownikiem,
    żeby później mogły z niego korzystać:
    - welcome.py
    - review.py
    - lekcje
    - dialogi
    - przyszły avatar
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
    # 1. NAJPIERW POWTÓRKI
    # ======================================

    review_words = get_review_plan(
        state
    )


    if review_words:

        word_list = format_word_list(
            review_words
        )


        if len(review_words) == 1:

            message = (
                "Heute sollten wir zuerst "
                f"{word_list} wiederholen."
            )

        else:

            message = (
                "Heute sollten wir zuerst "
                f"{word_list} wiederholen."
            )


        return {
            "type": "vocabulary_review",
            "words": review_words,
            "topic": "Wortschatz",
            "message": message
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


        # ==================================
        # TEMAT HOTEL
        # ==================================

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
# TYLKO GOTOWA WIADOMOŚĆ DLA NELE
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
