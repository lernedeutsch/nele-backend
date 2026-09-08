# ==========================================
# NELE – WORTSCHATZMODUL: VERWENDUNG
# ==========================================

from brain.logic.matcher import normalize
from brain.knowledge.A1.vocabulary import VOCABULARY

from brain.logic.vocabulary_modules.helpers import (
    clean_vocabulary_word,
    remember_vocabulary_word
)


# ==========================================
# VERWENDUNG – WORT ERKENNEN
# ==========================================

def extract_usage_word(
    user_message
):

    message = normalize(
        user_message
    )

    patterns = [

        # ==================================
        # WANN ...
        # ==================================

        "wann benutzt man das wort ",
        "wann verwendet man das wort ",
        "wann sagt man das wort ",
        "wann benutze ich das wort ",
        "wann verwende ich das wort ",

        "wann benutzt man ",
        "wann verwendet man ",
        "wann sagt man ",
        "wann benutze ich ",
        "wann verwende ich ",

        # ==================================
        # WIE ...
        # ==================================

        "wie benutzt man das wort ",
        "wie verwendet man das wort ",
        "wie benutze ich das wort ",
        "wie verwende ich das wort ",

        "wie benutzt man ",
        "wie verwendet man ",
        "wie benutze ich ",
        "wie verwende ich "
    ]

    patterns.sort(
        key=len,
        reverse=True
    )

    for pattern in patterns:

        if message.startswith(
            pattern
        ):

            word = message[
                len(pattern):
            ]

            word = clean_vocabulary_word(
                word
            )

            if word:
                return word

    return None


# ==========================================
# VERWENDUNG – KONTEXTFRAGE
# ==========================================

def is_vocabulary_usage_follow_up(
    user_message
):

    message = normalize(
        user_message
    )

    usage_follow_ups = [

        # ==================================
        # WANN BENUTZT ...
        # ==================================

        "wann benutzt man das",
        "und wann benutzt man das",

        "wann benutzt man dieses wort",
        "und wann benutzt man dieses wort",

        "wann benutzt man das wort",
        "und wann benutzt man das wort",

        # ==================================
        # WANN VERWENDET ...
        # ==================================

        "wann verwendet man das",
        "und wann verwendet man das",

        "wann verwendet man dieses wort",
        "und wann verwendet man dieses wort",

        "wann verwendet man das wort",
        "und wann verwendet man das wort",

        # ==================================
        # WANN SAGT ...
        # ==================================

        "wann sagt man das",
        "und wann sagt man das",

        "wann sagt man dieses wort",
        "und wann sagt man dieses wort",

        "wann sagt man das wort",
        "und wann sagt man das wort",

        # ==================================
        # WANN BENUTZE ICH ...
        # ==================================

        "wann benutze ich das",
        "und wann benutze ich das",

        "wann benutze ich dieses wort",
        "und wann benutze ich dieses wort",

        # ==================================
        # WANN VERWENDE ICH ...
        # ==================================

        "wann verwende ich das",
        "und wann verwende ich das",

        "wann verwende ich dieses wort",
        "und wann verwende ich dieses wort",

        # ==================================
        # WIE BENUTZT ...
        # ==================================

        "wie benutzt man das",
        "und wie benutzt man das",

        "wie benutzt man dieses wort",
        "und wie benutzt man dieses wort",

        "wie benutzt man das wort",
        "und wie benutzt man das wort",

        # ==================================
        # WIE VERWENDET ...
        # ==================================

        "wie verwendet man das",
        "und wie verwendet man das",

        "wie verwendet man dieses wort",
        "und wie verwendet man dieses wort",

        "wie verwendet man das wort",
        "und wie verwendet man das wort",

        # ==================================
        # WIE BENUTZE ICH ...
        # ==================================

        "wie benutze ich das",
        "und wie benutze ich das",

        "wie benutze ich dieses wort",
        "und wie benutze ich dieses wort",

        # ==================================
        # WIE VERWENDE ICH ...
        # ==================================

        "wie verwende ich das",
        "und wie verwende ich das",

        "wie verwende ich dieses wort",
        "und wie verwende ich dieses wort"
    ]

    return message in usage_follow_ups


# ==========================================
# VERWENDUNG – ANTWORT
# ==========================================

def answer_vocabulary_usage(
    user_message,
    state=None
):

    # ======================================
    # KONTEXTFRAGE
    #
    # Beispiel:
    #
    # Groß
    # → ähnliches Wort: Riesig
    # → Was ist der Unterschied?
    # → Wann benutzt man das?
    #
    # "das" soll sich auf Riesig beziehen.
    # ======================================

    if is_vocabulary_usage_follow_up(
        user_message
    ):

        if state is None:
            return None

        related_word = state.get(
            "current_vocabulary_related_word"
        )

        current_word = state.get(
            "current_vocabulary_word"
        )

        # Zuerst das zuletzt erwähnte
        # verwandte Wort verwenden.
        if (
            related_word
            and related_word in VOCABULARY
        ):
            word = related_word

        else:
            word = current_word

    # ======================================
    # DIREKTE FRAGE MIT KONKRETEM WORT
    # ======================================

    else:

        word = extract_usage_word(
            user_message
        )


    if not word:
        return None


    # ======================================
    # WORTSCHATZEINTRAG
    # ======================================

    vocabulary_entry = VOCABULARY.get(
        word
    )

    if not vocabulary_entry:
        return None


    # ======================================
    # VERWENDUNG
    # ======================================

    usage = vocabulary_entry.get(
        "usage"
    )

    if not usage:
        return None


    # ======================================
    # WORT IM KONTEXT SPEICHERN
    # ======================================

    if state is not None:

        remember_vocabulary_word(
            state,
            word
        )

        # Wenn das verwandte Wort jetzt
        # zum aktuellen Wort geworden ist,
        # wird die alte Beziehung gelöscht.
        if state.get(
            "current_vocabulary_related_word"
        ) == word:

            state[
                "current_vocabulary_related_word"
            ] = None


    return usage
