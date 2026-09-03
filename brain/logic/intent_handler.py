# ==========================================
# NELE – OBSŁUGA INTENCJI
# ==========================================

from brain.logic.intents import detect_intent
from brain.logic.memory import get_conversation_state

from brain.knowledge.A1.meanings import MEANINGS
from brain.knowledge.A1.usage import USAGE
from brain.knowledge.A1.differences import DIFFERENCES
from brain.knowledge.A1.examples import EXAMPLES
from brain.knowledge.A1.explanations import EXPLANATIONS
from brain.knowledge.A1.formality import FORMALITY


# ==========================================
# GŁÓWNA OBSŁUGA INTENCJI
# ==========================================

def handle_intent(
    user_message,
    session_id="default"
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
    # PAMIĘĆ TEMATU
    # ======================================

    state = get_conversation_state(
        session_id
    )

    current_topic = state.get(
        "current_topic"
    )


    # ======================================
    # "DAS" = AKTUALNY TEMAT
    # ======================================

    if content == "das":

        if current_topic:

            content = current_topic

        else:

            return None


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
    # PYTANIE O RÓŻNICĘ
    # ======================================

    if intent_type == "difference":

        answer = DIFFERENCES.get(
            content
        )

        if answer:
            return answer


    # ======================================
    # PROŚBA O PRZYKŁAD
    # ======================================

    if intent_type == "example":

        answer = EXAMPLES.get(
            content
        )

        if answer:
            return answer


    # ======================================
    # PROŚBA O WYJAŚNIENIE
    # ======================================

    if intent_type == "explanation":

        answer = EXPLANATIONS.get(
            content
        )

        if answer:
            return answer


    # ======================================
    # FORMELL / INFORMELL
    # ======================================

    if intent_type == "formality":

        answer = FORMALITY.get(
            content
        )

        if answer:
            return answer


    # ======================================
    # BRAK GOTOWEJ ODPOWIEDZI
    # ======================================

    return None
