from brain.logic.vocabulary_engine import (
    get_entry,
    words_in_message,
    detect_topic,
    build_conversation_vocabulary,
)


def test_known_vocabulary_entry():
    entry = get_entry("Zimmer")
    assert entry is not None
    assert entry["word"] == "zimmer"
    assert entry["level"] == "A1"


def test_unknown_vocabulary_entry():
    assert get_entry("xyz-unbekannt") is None


def test_words_in_message():
    words = words_in_message("Ich bin im Hotel und habe ein Zimmer.")
    assert "hotel" in words
    assert "zimmer" in words


def test_detect_topic():
    assert detect_topic("Heute ist es sonnig und warm.") == "wetter"
    assert detect_topic("Ich arbeite heute in einer Firma.") == "arbeit"


def test_build_conversation_vocabulary():
    context = build_conversation_vocabulary("Das Zimmer im Hotel ist schön.")
    assert context["level"] == "A1"
    assert context["topic"] == "hotel"
    assert "zimmer" in context["used_words"]
    assert isinstance(context["suggestions"], list)
