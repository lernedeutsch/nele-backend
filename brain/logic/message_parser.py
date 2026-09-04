# ==========================================
# NELE – ANALIZA WIADOMOŚCI UŻYTKOWNIKA
# ==========================================


# ==========================================
# DZIELENIE WIADOMOŚCI NA KILKA PYTAŃ
# ==========================================

def split_multiple_questions(
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

    # Jedno pytanie nie wymaga dzielenia.
    if len(questions) < 2:
        return []

    return questions
