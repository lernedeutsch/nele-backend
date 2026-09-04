# ==========================================
# NELE – ANALIZA WIADOMOŚCI UŻYTKOWNIKA
# ==========================================

import re


# ==========================================
# CZYSZCZENIE TEKSTU
# ==========================================

def clean_part(
    text
):

    if not text:
        return ""

    return text.strip(
        " \t\r\n,;.?!"
    )


# ==========================================
# KILKA PYTAŃ ODDZIELONYCH ZNAKIEM ?
# ==========================================

def split_by_question_mark(
    user_message
):

    if not user_message:
        return []

    parts = user_message.split(
        "?"
    )

    questions = []

    for part in parts:

        part = clean_part(
            part
        )

        if not part:
            continue

        questions.append(
            part + "?"
        )

    if len(questions) < 2:
        return []

    return questions


# ==========================================
# POBIERANIE SŁOWA Z PYTANIA O ZNACZENIE
# ==========================================

def extract_meaning_word_from_compound(
    user_message
):

    pattern = (
        r"^\s*"
        r"was\s+"
        r"(?:bedeutet|heißt|heisst)\s+"
        r"(?:das\s+wort\s+)?"
        r"(.+?)"
        r"\s*(?:,|\s+und\s+)"
    )

    match = re.search(
        pattern,
        user_message,
        flags=re.IGNORECASE
    )

    if not match:
        return None

    word = clean_part(
        match.group(1)
    )

    if not word:
        return None

    return word


# ==========================================
# ZNACZENIE + PRZYKŁAD + UŻYCIE
# ==========================================

def split_meaning_example_usage(
    user_message
):

    if not user_message:
        return []

    pattern = (
        r"^\s*"
        r"was\s+"
        r"(?:bedeutet|heißt|heisst)\s+"
        r"(?:das\s+wort\s+)?"
        r"(.+?)"
        r"\s*,\s*"
        r"(?:gib|nenn|zeig)\s+mir\s+"
        r"ein\s+beispiel"
        r"\s+und\s+"
        r"sag\s+mir\s*,?\s*"
        r"wann\s+man\s+das\s+wort\s+"
        r"(?:benutzt|verwendet)"
        r"\s*[.?!]*\s*$"
    )

    match = re.match(
        pattern,
        user_message,
        flags=re.IGNORECASE
    )

    if not match:
        return []

    word = clean_part(
        match.group(1)
    )

    if not word:
        return []

    return [
        f"Was bedeutet {word}?",
        "Gib mir ein Beispiel?",
        "Wann benutzt man das Wort?"
    ]


# ==========================================
# ZNACZENIE + PRZYKŁAD
# ==========================================

def split_meaning_example(
    user_message
):

    if not user_message:
        return []

    pattern = (
        r"^\s*"
        r"was\s+"
        r"(?:bedeutet|heißt|heisst)\s+"
        r"(?:das\s+wort\s+)?"
        r"(.+?)"
        r"\s*(?:,|\s+und\s+)"
        r"(?:gib|nenn|zeig)\s+mir\s+"
        r"ein\s+beispiel"
        r"\s*[.?!]*\s*$"
    )

    match = re.match(
        pattern,
        user_message,
        flags=re.IGNORECASE
    )

    if not match:
        return []

    word = clean_part(
        match.group(1)
    )

    if not word:
        return []

    return [
        f"Was bedeutet {word}?",
        "Gib mir ein Beispiel?"
    ]


# ==========================================
# ZNACZENIE + UŻYCIE
# ==========================================

def split_meaning_usage(
    user_message
):

    if not user_message:
        return []

    pattern = (
        r"^\s*"
        r"was\s+"
        r"(?:bedeutet|heißt|heisst)\s+"
        r"(?:das\s+wort\s+)?"
        r"(.+?)"
        r"\s+und\s+"
        r"(?:"
        r"wann\s+(?:benutzt|verwendet)\s+man\s+das\s+wort"
        r"|"
        r"sag\s+mir\s*,?\s*wann\s+man\s+das\s+wort\s+"
        r"(?:benutzt|verwendet)"
        r")"
        r"\s*[.?!]*\s*$"
    )

    match = re.match(
        pattern,
        user_message,
        flags=re.IGNORECASE
    )

    if not match:
        return []

    word = clean_part(
        match.group(1)
    )

    if not word:
        return []

    return [
        f"Was bedeutet {word}?",
        "Wann benutzt man das Wort?"
    ]


# ==========================================
# ZNACZENIE + PODOBNE SŁOWO
# ==========================================

def split_meaning_similar(
    user_message
):

    if not user_message:
        return []

    pattern = (
        r"^\s*"
        r"was\s+"
        r"(?:bedeutet|heißt|heisst)\s+"
        r"(?:das\s+wort\s+)?"
        r"(.+?)"
        r"\s+und\s+"
        r"gibt\s+es\s+ein\s+ähnliches\s+wort"
        r"\s*[.?!]*\s*$"
    )

    match = re.match(
        pattern,
        user_message,
        flags=re.IGNORECASE
    )

    if not match:
        return []

    word = clean_part(
        match.group(1)
    )

    if not word:
        return []

    return [
        f"Was bedeutet {word}?",
        "Gibt es ein ähnliches Wort?"
    ]


# ==========================================
# PROSTE DWA PYTANIA PO "UND"
# ==========================================

def split_compound_question(
    user_message
):

    if not user_message:
        return []

    patterns = [
        r"\s+und\s+(?=gibt\s+es\s+)",
        r"\s+und\s+(?=was\s+ist\s+)",
        r"\s+und\s+(?=wann\s+)",
        r"\s+und\s+(?=wie\s+)",
        r"\s+und\s+(?=warum\s+)",
        r"\s+und\s+(?=welches\s+)",
        r"\s+und\s+(?=welcher\s+)",
        r"\s+und\s+(?=welche\s+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            user_message,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        first = clean_part(
            user_message[
                :match.start()
            ]
        )

        second = clean_part(
            user_message[
                match.end() - 4:
            ]
        )

        if not first or not second:
            continue

        return [
            first + "?",
            second + "?"
        ]

    return []


# ==========================================
# GŁÓWNE DZIELENIE WIADOMOŚCI
# ==========================================

def split_multiple_questions(
    user_message
):

    if not user_message:
        return []


    # ======================================
    # 1. KILKA PYTAŃ Z ?
    # ======================================

    questions = split_by_question_mark(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 2. ZNACZENIE + PRZYKŁAD + UŻYCIE
    # ======================================

    questions = split_meaning_example_usage(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 3. ZNACZENIE + PODOBNE SŁOWO
    # ======================================

    questions = split_meaning_similar(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 4. ZNACZENIE + PRZYKŁAD
    # ======================================

    questions = split_meaning_example(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 5. ZNACZENIE + UŻYCIE
    # ======================================

    questions = split_meaning_usage(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 6. INNE DWA PYTANIA Z "UND"
    # ======================================

    questions = split_compound_question(
        user_message
    )

    if questions:
        return questions


    return []
