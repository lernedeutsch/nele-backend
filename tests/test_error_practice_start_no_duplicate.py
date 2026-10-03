from brain.logic.conversation_memory import handle_error_memory_request
from brain.memory.error_memory import remember_error


def test_starting_error_practice_does_not_append_duplicate_resume_prompt():
    state = {}
    context = "Frag höflich nach dem Alter."
    remember_error(
        state,
        "grammar",
        "Ich bin zweiunddreißig Jahre alt.",
        "Wie alt sind Sie?",
        context=context,
    )

    handled, answer = handle_error_memory_request(
        "meine Fehler üben",
        state,
    )

    assert handled is True
    assert state.get("error_practice_active") is True
    assert answer.count("Welche Antwort passt hier?") == 1
    assert "Jetzt machen wir weiter. Welcher Satz ist richtig?" not in answer
    assert answer.count("1. Ich bin zweiunddreißig Jahre alt.") == 1
    assert answer.count("2. Wie alt sind Sie?") == 1
