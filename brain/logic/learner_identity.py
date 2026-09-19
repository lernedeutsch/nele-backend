"""Canonical learner identity rules for production Nele."""

MAX_LEARNER_ID_LENGTH = 100
RESERVED_LEARNER_IDS = {"default"}


def normalize_learner_id(value):
    """Return a safe learner id or None when the public id is invalid."""

    text = str(value or "").strip()

    if not text:
        return None

    if text.lower() in RESERVED_LEARNER_IDS:
        return None

    return text[:MAX_LEARNER_ID_LENGTH]
