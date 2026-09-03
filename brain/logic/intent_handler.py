# ==========================================
# NELE – OBSŁUGA INTENCJI
# ==========================================

from brain.logic.intents import detect_intent

from brain.knowledge.A1.meanings import MEANINGS
from brain.knowledge.A1.usage import USAGE


# ==========================================
# GŁÓWNA OBSŁUGA INTENCJI
# ==========================================

def handle_intent(
    user_message
):

    intent = detect_intent(
        user_message
    )

    if not intent:
        return None

    intent_type = intent.get(
        "intent"
    )

    content = intent.get(
        "content",
        ""
    )


    # ======================================
    # PYTANIE O ZNACZENIE
    # ======================================

    if intent_type == "meaning":

        answer = MEANINGS.get(
            content
        )

        if answer:
            return answer


    # ======================================
    # PYTANIE O UŻYCIE
    # ======================================

    if intent_type == "usage":

        answer = USAGE.get(
            content
        )

        if answer:
            return answer


    # ======================================
    # BRAK GOTOWEJ ODPOWIEDZI
    # ======================================

    return None
