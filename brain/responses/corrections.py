# ==========================================
# NELE – KOREKTA BŁĘDÓW
# ==========================================

CORRECTIONS = [

    # ======================================
    # LEKCJA A1/1 – PRZEDSTAWIANIE SIĘ
    # ======================================

    {
        "wrong": "ich heise ",
        "correct": "Ich heiße ",
        "explanation": (
            "Fast richtig. "
            "Man schreibt „heiße“ mit ß."
        )
    },

    {
        "wrong": "ich heisse ",
        "correct": "Ich heiße ",
        "explanation": (
            "Fast richtig. "
            "In Deutschland schreibt man „heiße“ mit ß."
        )
    },

    {
        "wrong": "mein name ist ",
        "correct": "Mein Name ist ",
        "explanation": (
            "Fast richtig. "
            "„Name“ ist ein Nomen und wird großgeschrieben."
        )
    },

    {
        "wrong": "wie heist du",
        "correct": "Wie heißt du?",
        "explanation": (
            "Fast richtig. "
            "Man schreibt „heißt“ mit ß."
        )
    },

    {
        "wrong": "wie heisst du",
        "correct": "Wie heißt du?",
        "explanation": (
            "Fast richtig. "
            "Man schreibt „heißt“ mit ß."
        )
    },

    {
        "wrong": "guten morgen",
        "correct": "Guten Morgen!",
        "explanation": (
            "„Morgen“ ist ein Nomen und wird großgeschrieben."
        )
    },

    {
        "wrong": "guten abend",
        "correct": "Guten Abend!",
        "explanation": (
            "„Abend“ ist ein Nomen und wird großgeschrieben."
        )
    }

]


# ==========================================
# SZUKANIE KOREKTY
# ==========================================

def find_correction(text):

    original = text.strip()

    if not original:
        return None

    lower_text = original.lower()


    for item in CORRECTIONS:

        wrong = item["wrong"]

        if lower_text.startswith(wrong):

            rest = original[len(wrong):].strip()

            correct = item["correct"]

            if rest:
                correct_sentence = correct + rest
            else:
                correct_sentence = correct

            return {
                "original": original,
                "correct": correct_sentence,
                "explanation": item["explanation"]
            }


    return None
