# ==========================================
# NELE – PAMIĘĆ SŁOWNICTWA UCZNIA
# ==========================================


# ==========================================
# POBIERANIE PAMIĘCI SŁOWNICTWA
# ==========================================

def get_vocabulary_memory(
    state
):

    if state is None:
        return {}

    if "vocabulary_memory" not in state:
        state["vocabulary_memory"] = {}

    return state["vocabulary_memory"]


# ==========================================
# POBIERANIE PAMIĘCI JEDNEGO SŁOWA
# ==========================================

def get_word_memory(
    word,
    state
):

    if not word or state is None:
        return None

    vocabulary_memory = get_vocabulary_memory(
        state
    )

    if word not in vocabulary_memory:

        vocabulary_memory[word] = {
            "seen": 0,
            "correct": 0,
            "mistakes": 0,
            "correct_streak": 0,
            "needs_review": False
        }

    else:

        word_memory = vocabulary_memory[
            word
        ]

        if "seen" not in word_memory:
            word_memory["seen"] = 0

        if "correct" not in word_memory:
            word_memory["correct"] = 0

        if "mistakes" not in word_memory:
            word_memory["mistakes"] = 0

        if "correct_streak" not in word_memory:
            word_memory["correct_streak"] = 0

        if "needs_review" not in word_memory:
            word_memory["needs_review"] = False

    return vocabulary_memory[
        word
    ]


# ==========================================
# ZAPISANIE ĆWICZONEGO SŁOWA
# ==========================================

def remember_practiced_word(
    word,
    state
):

    word_memory = get_word_memory(
        word,
        state
    )

    if word_memory is None:
        return

    word_memory[
        "seen"
    ] += 1


# ==========================================
# ZAPISANIE POPRAWNEJ ODPOWIEDZI
# ==========================================

def remember_correct_answer(
    word,
    state
):

    word_memory = get_word_memory(
        word,
        state
    )

    if word_memory is None:
        return

    word_memory[
        "correct"
    ] += 1

    word_memory[
        "correct_streak"
    ] += 1

    if word_memory[
        "correct_streak"
    ] >= 3:

        word_memory[
            "needs_review"
        ] = False


# ==========================================
# ZAPISANIE BŁĘDU
# ==========================================

def remember_mistake(
    word,
    state
):

    word_memory = get_word_memory(
        word,
        state
    )

    if word_memory is None:
        return

    word_memory[
        "mistakes"
    ] += 1

    word_memory[
        "correct_streak"
    ] = 0

    word_memory[
        "needs_review"
    ] = True


# ==========================================
# CZY SŁOWO WYMAGA POWTÓRKI
# ==========================================

def word_needs_review(
    word,
    state
):

    word_memory = get_word_memory(
        word,
        state
    )

    if word_memory is None:
        return False

    return word_memory[
        "needs_review"
    ]


# ==========================================
# SŁOWA DO POWTÓRKI
# ==========================================

def get_words_for_review(
    state
):

    vocabulary_memory = get_vocabulary_memory(
        state
    )

    words = []

    for word, word_memory in vocabulary_memory.items():

        if word_memory.get(
            "needs_review",
            False
        ):

            words.append(
                word
            )

    return words
