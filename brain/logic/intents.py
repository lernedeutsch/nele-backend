# ==========================================
# NELE – ROZPOZNAWANIE INTENCJI
# ==========================================

from brain.logic.matcher import normalize


# ==========================================
# ROZPOZNAWANIE TYPU PYTANIA
# ==========================================

def detect_intent(user_message):

    message = normalize(
        user_message
    )

    if not message:
        return None


    # ======================================
    # PYTANIE O ZNACZENIE
    # ======================================

    meaning_patterns = [
        "was bedeutet ",
        "was heißt ",
        "was heisst ",
        "was bedeutet das wort ",
        "was bedeutet der ausdruck ",
        "was heißt das wort ",
        "was heisst das wort ",
        "erklär mir ",
        "erkläre mir ",
        "kannst du mir erklären ",
        "kannst du erklären "
    ]

    for pattern in meaning_patterns:

        if message.startswith(pattern):

            content = message[
                len(pattern):
            ].strip()

            if content:

                return {
                    "intent": "meaning",
                    "content": content
                }


    # ======================================
    # PYTANIE: JAK TO SIĘ MÓWI?
    # ======================================

    speaking_patterns = [
        "wie sagt man ",
        "wie kann man sagen ",
        "wie sage ich ",
        "wie sagt man auf deutsch "
    ]

    for pattern in speaking_patterns:

        if message.startswith(pattern):

            content = message[
                len(pattern):
            ].strip()

            if content:

                return {
                    "intent": "how_to_say",
                    "content": content
                }


    # ======================================
    # PYTANIE O UŻYCIE
    # ======================================

    usage_patterns = [
        "wann sagt man ",
        "wann benutzt man ",
        "wann verwendet man ",
        "wie benutzt man ",
        "wie verwendet man "
    ]

    for pattern in usage_patterns:

        if message.startswith(pattern):

            content = message[
                len(pattern):
            ].strip()

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
        "was ist der unterschied von ",
        "wo ist der unterschied zwischen ",
        "was unterscheidet "
    ]

    for pattern in difference_patterns:

        if message.startswith(pattern):

            content = message[
                len(pattern):
            ].strip()

            if content:

                return {
                    "intent": "difference",
                    "content": content
                }


    # ======================================
    # PROŚBA O PRZYKŁAD
    # ======================================

    example_patterns = [
        "gib mir ein beispiel",
        "gib mir ein beispiel für ",
        "nenn mir ein beispiel",
        "nenn mir ein beispiel für ",
        "zeig mir ein beispiel",
        "zeig mir ein beispiel für "
    ]

    for pattern in example_patterns:

        if message.startswith(pattern):

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
        "warum sagt man ",
        "warum heißt es ",
        "warum heisst es ",
        "warum ist das ",
        "erklär das",
        "erkläre das"
    ]

    for pattern in explanation_patterns:

        if message.startswith(pattern):

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
