# ==========================================
# NELE – ANALIZA WIADOMOŚCI UŻYTKOWNIKA
# ==========================================

from brain.logic.matcher import normalize


# ==========================================
# DZIELENIE WIADOMOŚCI PO ZNAKU ?
# ==========================================

def split_by_question_mark(
    user_message
):

    if not user_message:
        return []

    parts = user_message.split("?")

    questions = []

    for part in parts:

        part = part.strip()

        if not part:
            continue

        questions.append(
            part + "?"
        )

    if len(questions) < 2:
        return []

    return questions


# ==========================================
# DZIELENIE PYTANIA ZŁOŻONEGO PO "UND"
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
        " und zeig mir ",
        " und sag mir "
    ]

    for pattern in patterns:

        if pattern not in message:
            continue

        position = message.find(
            pattern
        )

        first = user_message[
            :position
        ].strip()

        second_start = position + 1

        second = user_message[
            second_start:
        ].strip()

        if not first or not second:
            continue

        first = first.rstrip(
            " ?."
        ) + "?"

        second = second.rstrip(
            " ?."
        ) + "?"

        return [
            first,
            second
        ]

    return []


# ==========================================
# DZIELENIE KILKU POLECEŃ
# ==========================================

def split_multiple_commands(
    user_message
):

    if not user_message:
        return []

    message = normalize(
        user_message
    )

    # --------------------------------------
    # PRZYPADEK:
    #
    # Was bedeutet Zimmer,
    # gib mir ein Beispiel
    # und sag mir, wann man das Wort benutzt.
    # --------------------------------------

    command_patterns = [
        ", gib mir ",
        ", nenn mir ",
        ", zeig mir ",
        ", sag mir "
    ]

    for pattern in command_patterns:

        if pattern not in message:
            continue

        position = message.find(
            pattern
        )

        first = user_message[
            :position
        ].strip()

        rest_start = (
            position
            + len(pattern)
            - len(pattern.lstrip())
        )

        rest = user_message[
            rest_start:
        ].strip()

        if not first or not rest:
            continue

        # Pierwsza część
        first = first.rstrip(
            " ?."
        ) + "?"

        # Teraz próbujemy podzielić pozostałą
        # część jeszcze raz po "und".
        rest_parts = split_compound_question(
            rest
        )

        if rest_parts:

            return [
                first,
                rest_parts[0],
                rest_parts[1]
            ]

        rest = rest.rstrip(
            " ?."
        ) + "?"

        return [
            first,
            rest
        ]

    return []


# ==========================================
# GŁÓWNE DZIELENIE WIADOMOŚCI
# ==========================================

def split_multiple_questions(
    user_message
):

    # ======================================
    # 1. KILKA PYTAŃ Z ?
    # ======================================

    questions = split_by_question_mark(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 2. KILKA POLECEŃ W JEDNYM ZDANIU
    # ======================================

    questions = split_multiple_commands(
        user_message
    )

    if questions:
        return questions


    # ======================================
    # 3. DWA PYTANIA / POLECENIA Z "UND"
    # ======================================

    questions = split_compound_question(
        user_message
    )

    if questions:
        return questions


    return []
