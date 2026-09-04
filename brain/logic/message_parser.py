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
# DZIELENIE PYTANIA PO "UND"
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
        " und welche "
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
            " ?"
        ) + "?"

        second = second.rstrip(
            " ?"
        ) + "?"

        return [
            first,
            second
        ]

    return []


# ==========================================
# GŁÓWNE DZIELENIE WIADOMOŚCI
# ==========================================

def split_multiple_questions(
    user_message
):

    # Najpierw sprawdzamy kilka pytań
    # oddzielonych znakami zapytania.

    questions = split_by_question_mark(
        user_message
    )

    if questions:
        return questions


    # Jeżeli jest tylko jeden znak zapytania,
    # sprawdzamy pytanie złożone z "und".

    questions = split_compound_question(
        user_message
    )

    if questions:
        return questions


    return []
