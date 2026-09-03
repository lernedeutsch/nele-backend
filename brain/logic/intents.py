# ==========================================
# NELE – ROZPOZNAWANIE INTENCJI
# ==========================================

from brain.logic.matcher import normalize


# ==========================================
# POMOCNICZA FUNKCJA
# ==========================================

def match_prefix(
    message,
    patterns
):

    for pattern in patterns:

        if message.startswith(
            pattern
        ):

            content = message[
                len(pattern):
            ].strip()

            return content

    return None


# ==========================================
# ROZPOZNAWANIE TYPU PYTANIA
# ==========================================

def detect_intent(
    user_message
):

    message = normalize(
        user_message
    )

    if not message:
        return None


    # ======================================
    # PYTANIE O ZNACZENIE
    # Dłuższe wzorce są przed krótszymi.
    # ======================================

    meaning_patterns = [
        "was bedeutet das wort ",
        "was bedeutet der ausdruck ",
        "was heißt das wort ",
        "was heisst das wort ",
        "kannst du mir erklären ",
        "kannst du erklären ",
        "was bedeutet ",
        "was heißt ",
        "was heisst ",
        "erklär mir ",
        "erkläre mir "
    ]

    content = match_prefix(
        message,
        meaning_patterns
    )

    if content:

        return {
            "intent": "meaning",
            "content": content
        }


    # ======================================
    # PYTANIE: JAK TO SIĘ MÓWI?
    # ======================================

    speaking_patterns = [
        "wie sagt man auf deutsch ",
        "wie kann man sagen ",
        "wie sage ich ",
        "wie sagt man "
    ]

    content = match_prefix(
        message,
        speaking_patterns
    )

    if content:

        return {
            "intent": "how_to_say",
            "content": content
        }


    # ======================================
    # PYTANIE O UŻYCIE
    # ======================================

    usage_patterns = [
        "wann verwendet man ",
        "wann benutzt man ",
        "wann sagt man ",
        "wie verwendet man ",
        "wie benutzt man "
    ]

    content = match_prefix(
        message,
        usage_patterns
    )

    if content:

        return {
            "intent": "usage",
            "content": content
        }


    # ======================================
    # PYTANIE O RÓŻNICĘ
    # ======================================

    difference_patterns = [
        "was ist der unterschied zwischen ",
        "wo ist der unterschied zwischen ",
        "was ist der unterschied von ",
        "was unterscheidet "
    ]

    content = match_prefix(
        message,
        difference_patterns
    )

    if content:

        return {
            "intent": "difference",
            "content": content
        }


    # ======================================
    # PROŚBA O PRZYKŁAD
    # ======================================

    example_patterns = [
        "gib mir ein beispiel für ",
        "nenn mir ein beispiel für ",
        "zeig mir ein beispiel für ",
        "gib mir ein beispiel",
        "nenn mir ein beispiel",
        "zeig mir ein beispiel"
    ]

    for pattern in example_patterns:

        if message.startswith(
            pattern
        ):

            content = message[
                len(pattern):
            ].strip()

            return {
                "intent": "example",
                "content": content
            }


    # ======================================
    # PROŚBA O WYJAŚNIENIE
    # ======================================

    explanation_patterns = [
        "warum heißt es ",
        "warum heisst es ",
        "warum sagt man ",
        "warum ist das ",
        "erkläre das",
        "erklär das"
    ]

    for pattern in explanation_patterns:

        if message.startswith(
            pattern
        ):

            content = message[
                len(pattern):
            ].strip()

            return {
                "intent": "explanation",
                "content": content
            }


    # ======================================
    # NIE ROZPOZNANO INTENCJI
    # ======================================

    return None
