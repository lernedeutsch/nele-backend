import re


def normalize(text):

    text = (
        text
        .lower()
        .strip()
        .replace("?", "")
        .replace("!", "")
        .replace(".", "")
        .replace(",", "")
        .replace(":", "")
        .replace(";", "")
    )

    return " ".join(
        text.split()
    )


def clean_short_answer(text):

    return (
        text
        .strip()
        .strip(".!?")
        .strip()
    )


def capitalize_value(value):

    value = value.strip()

    if not value:
        return value

    return (
        value[0].upper()
        + value[1:]
    )


def pattern_matches(
    message,
    pattern
):

    message_normalized = normalize(
        message
    )

    pattern_normalized = normalize(
        pattern
    )

    if not pattern_normalized:
        return False

    regex = (
        r"(?<!\w)"
        + re.escape(
            pattern_normalized
        )
        + r"(?!\w)"
    )

    return bool(
        re.search(
            regex,
            message_normalized,
            flags=re.UNICODE
        )
    )
