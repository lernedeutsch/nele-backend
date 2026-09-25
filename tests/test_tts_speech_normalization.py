from speech.speaker import Speaker


def test_tts_removes_single_and_repeated_underscores():
    assert Speaker.normalize_text_for_speech("Ich ___ aus Deutschland.") == "Ich aus Deutschland."
    assert Speaker.normalize_text_for_speech("Ich _ aus Polen.") == "Ich aus Polen."
    assert Speaker.normalize_text_for_speech("Du ____ in Berlin.") == "Du in Berlin."


def test_tts_blank_normalization_is_not_sentence_specific():
    cases = {
        "Ich ___ Monika.": "Ich Monika.",
        "Wir ___ Pizza.": "Wir Pizza.",
        "Er ___ um 8 Uhr.": "Er um 8 Uhr.",
        "Heute ist es ___.": "Heute ist es.",
        "___ kommst du?": "kommst du?",
    }
    for visible_text, expected_speech in cases.items():
        assert Speaker.normalize_text_for_speech(visible_text) == expected_speech


def test_tts_keeps_normal_german_text_and_punctuation():
    text = "Hallo! Wie geht's dir? Ich arbeite heute von 8 bis 14 Uhr."
    assert Speaker.normalize_text_for_speech(text) == text


def test_tts_does_not_join_words_around_a_blank():
    assert Speaker.normalize_text_for_speech("Ich___komme.") == "Ich komme."
