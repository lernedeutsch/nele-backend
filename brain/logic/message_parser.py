# ==========================================
# NELE – ANALIZA WIADOMOŚCI UŻYTKOWNIKA
# ==========================================

from brain.logic.matcher import normalize


# ==========================================
# CZYSZCZENIE CZĘŚCI WIADOMOŚCI
# ==========================================

def clean_part(
    text
):

    if not text:
        return ""

    text = text.strip()

    text = text.strip(
        " ,;.?!"
    )

    return text


# ==========================================
# DZIELENIE PO ZNAKACH ZAPYTANIA
# ==========================================

def split_by_question_mark(
    user_message
):

    if not user_message:
        return []

    parts = user_message.split("?")

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
# ROZPOZNAWANIE:
# WAS BEDEUTET X, GIB MIR EIN BEISPIEL
# UND SAG MIR, WANN MAN DAS WORT BENUTZT
# ==========================================

def split_vocabulary_commands(
    user_message
):

    if not user_message:
        return []

    message = normalize(
        user_message
    )

    # ======================================
    # ZNACZENIE + PRZYKŁAD + UŻYCIE
    # ======================================

    start_patterns = [
        "was bedeutet das wort ",
        "was heißt das wort ",
        "was heisst das wort ",
        "was bedeutet ",
        "was heißt ",
        "was heisst "
    ]

    example_markers = [
        ", gib mir ein beispiel",
        ", nenn mir ein beispiel",
        ", zeig mir ein beispiel"
    ]

    usage_markers = [
        " und sag mir, wann man das wort benutzt",
        " und sag mir wann man das wort benutzt",
        " und wann benutzt man das wort",
        " und wann verwendet man das wort"
    ]

    start_pattern = None

    for pattern in start_patterns:

        if message.startswith(
            pattern
        ):

            start_pattern = pattern
            break

    if not start_pattern:
        return []


    example_marker = None
    example_position = -1

    for marker in example_markers:

        position = message.find(
            marker
        )

        if position != -1:

            example_marker = marker
            example_position = position
            break


    if example_marker is not None:

        word = message[
            len(start_pattern):
            example_position
        ]

        word = clean_part(
            word
        )

        if not word:
            return []

        rest = message[
            example_position
            + len(example_marker):
        ]

        has_usage = False

        for marker in usage_markers:

            if marker in (
                example_marker + rest
            ):
                has_usage = True
                break

        # W praktyce po usunięciu frazy
        # ", gib mir ein Beispiel"
        # pozostaje np.
        # " und sag mir, wann man das Wort benutzt"
        if not has_usage:

            for marker in usage_markers:

                marker_without_leading_space = (
                    marker.strip()
                )

                if marker_without_leading_space in rest:
                    has_usage = True
                    break

        if has_usage:

            return [
                f"Was bedeutet {word}?",
                "Gib mir ein Beispiel?",
                "Wann benutzt man das Wort?"
            ]

        return [
            f"Was bedeutet {word}?",
            "Gib mir ein Beispiel?"
        ]


    # ======================================
    # ZNACZENIE + UŻYCIE
    # ======================================

    for marker in usage_markers:

        position = message.find(
            marker
        )

        if position == -1:
            continue

        word = message[
            len(start_pattern):
            position
        ]

        word = clean_part(
            word
        )

        if not word:
            return []

        return [
            f"Was bedeutet {word}?",
            "Wann benutzt man das Wort?"
        ]


    return []


# ==========================================
# DWA PYTANIA PO "UND"
# ==========================================

def split_compound_question(
    user_message
):

    if not user_message:
        return []

    message = normalize(
        user_message
    )

    patterns = [
        " und gibt es ",
        " und was ist ",
        " und wann ",
        " und wie ",
        " und warum ",
        " und welches ",
        " und welcher ",
        " und welche ",
        " und gib mir ",
        " und nenn mir ",
        " und zeig mir "
    ]

    for pattern in patterns:

        position = message.find(
            pattern
        )

        if position == -1:
            continue

        first = clean_part(
            user_message[
                :position
            ]
        )

        # +1 zostawia słowo "und"
        second = clean_part(
            user_message[
                position + 1:
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
# GŁÓWNY PARSER
# ==========================================

def split_multiple_questions(
    user_message
):

    if not user_message:
        return []


    # ======================================
    # 1. KILKA ODDZIELNYCH PYTAŃ
    # ======================================

    questions = split_by_question_mark(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 2. ZŁOŻONE POLECENIA SŁOWNICTWA
    # ======================================

    questions = split_vocabulary_commands(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 3. PROSTE PYTANIE Z "UND"
    # ======================================

    questions = split_compound_question(
        user_message
    )

    if questions:
        return questions


    return []
