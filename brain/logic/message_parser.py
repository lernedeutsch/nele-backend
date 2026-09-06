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

    text = text.strip(
        " \t\r\n,;.?!"
    )

    # ======================================
    # NIEMIECKIE ŁĄCZNIKI MIĘDZY PYTANIAMI
    # ======================================

    connectors = [
        "und dann ",
        "dann ",
        "danach ",
        "anschließend ",
        "anschliessend "
    ]

    lowered = text.lower()

    for connector in connectors:

        if lowered.startswith(
            connector
        ):

            text = text[
                len(connector):
            ].strip()

            break

    return text


# ==========================================
# ROZPOZNANIE POCZĄTKU NOWEGO PYTANIA
# LUB POLECENIA
# ==========================================

def is_new_question_start(
    text
):

    if not text:
        return False

    text = text.strip()

    pattern = (
        r"^(?:und\s+)?"
        r"(?:"
        r"was|"
        r"wann|"
        r"wie|"
        r"warum|"
        r"welcher|"
        r"welche|"
        r"welches|"
        r"welchen|"
        r"gibt|"
        r"gib|"
        r"nenn|"
        r"zeig|"
        r"hast|"
        r"kannst|"
        r"kennst|"
        r"noch|"
        r"ein\s+weiteres|"
        r"erklär|"
        r"erkläre|"
        r"erklaere|"
        r"erläutere|"
        r"erlaeutere"
        r")\b"
    )

    return bool(
        re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )
    )


# ==========================================
# FRAGEN UND BEFEHLE NACH . ? !
# TRENNEN
# ==========================================

def split_by_sentence_marks(
    user_message
):

    if not user_message:
        return []

    raw_parts = re.split(
        r"([.?!]+)",
        user_message
    )

    parts = []

    current = ""

    index = 0

    while index < len(
        raw_parts
    ):

        text = raw_parts[
            index
        ].strip()

        punctuation = ""

        if (
            index + 1
            < len(raw_parts)
        ):

            possible_punctuation = raw_parts[
                index + 1
            ]

            if re.fullmatch(
                r"[.?!]+",
                possible_punctuation
            ):

                punctuation = possible_punctuation
                index += 1

        if text:

            if current:

                if is_new_question_start(
                    text
                ):

                    cleaned = clean_part(
                        current
                    )

                    if cleaned:

                        parts.append(
                            cleaned + "?"
                        )

                    current = text

                else:

                    current += " " + text

            else:

                current = text

        if punctuation:

            next_text = ""

            next_index = (
                index + 1
            )

            if next_index < len(
                raw_parts
            ):

                next_text = raw_parts[
                    next_index
                ].strip()

            if (
                current
                and (
                    punctuation.find(
                        "?"
                    ) != -1
                    or punctuation.find(
                        "!"
                    ) != -1
                    or is_new_question_start(
                        next_text
                    )
                )
            ):

                cleaned = clean_part(
                    current
                )

                if cleaned:

                    parts.append(
                        cleaned + "?"
                    )

                current = ""

        index += 1

    if current:

        cleaned = clean_part(
            current
        )

        if cleaned:

            parts.append(
                cleaned + "?"
            )

    if len(parts) < 2:
        return []

    return parts


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

        # ==================================
        # DODATKOWY PODZIAŁ PO KROPCE
        # ==================================
        #
        # Beispiele:
        #
        # Gib mir ein Beispiel.
        # Noch ein Beispiel.
        # Wann benutzt man das?
        #
        # ==================================

        subparts = re.split(
            (
                r"\.\s+"
                r"(?="
                r"(?:und\s+)?"
                r"(?:"
                r"was|"
                r"wann|"
                r"wie|"
                r"warum|"
                r"welcher|"
                r"welche|"
                r"welches|"
                r"welchen|"
                r"gibt|"
                r"gib|"
                r"nenn|"
                r"zeig|"
                r"hast|"
                r"kannst|"
                r"kennst|"
                r"noch|"
                r"ein\s+weiteres|"
                r"erklär|"
                r"erkläre|"
                r"erklaere|"
                r"erläutere|"
                r"erlaeutere"
                r")\b"
                r")"
            ),
            part,
            flags=re.IGNORECASE
        )

        for subpart in subparts:

            subpart = clean_part(
                subpart
            )

            if not subpart:
                continue

            questions.append(
                subpart + "?"
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
        r"\s+und\s+(?=welche\s+)",
        r"\s+und\s+(?=welchen\s+)"
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
# DWA PYTANIA Z NIEMIECKIM ŁĄCZNIKIEM
# ==========================================

def split_with_german_connector(
    user_message
):

    if not user_message:
        return []

    pattern = (
        r"\?\s*"
        r"(?:"
        r"und\s+dann"
        r"|dann"
        r"|danach"
        r"|anschließend"
        r"|anschliessend"
        r")"
        r"\s*[:,\-]?\s*"
    )

    match = re.search(
        pattern,
        user_message,
        flags=re.IGNORECASE
    )

    if not match:
        return []

    first = clean_part(
        user_message[
            :match.start()
        ]
    )

    second = clean_part(
        user_message[
            match.end():
        ]
    )

    if not first or not second:
        return []

    return [
        first + "?",
        second + "?"
    ]


# ==========================================
# GŁÓWNE DZIELENIE WIADOMOŚCI
# ==========================================

def split_multiple_questions(
    user_message
):

    if not user_message:
        return []


    # ======================================
    # 1. NIEMIECKIE ŁĄCZNIKI
    # ======================================

    questions = split_with_german_connector(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 2. MIESZANE . ? !
    # ======================================

    questions = split_by_sentence_marks(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 3. KILKA PYTAŃ Z ?
    # ======================================

    questions = split_by_question_mark(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 4. ZNACZENIE + PRZYKŁAD + UŻYCIE
    # ======================================

    questions = split_meaning_example_usage(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 5. ZNACZENIE + PODOBNE SŁOWO
    # ======================================

    questions = split_meaning_similar(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 6. ZNACZENIE + PRZYKŁAD
    # ======================================

    questions = split_meaning_example(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 7. ZNACZENIE + UŻYCIE
    # ======================================

    questions = split_meaning_usage(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 8. INNE DWA PYTANIA Z "UND"
    # ======================================

    questions = split_compound_question(
        user_message
    )

    if questions:
        return questions


    return []
