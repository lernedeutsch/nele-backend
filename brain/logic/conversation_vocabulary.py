# ==========================================
# NELE – PYTANIA O SŁOWNICTWO W ROZMOWIE
# TEACHER MODE
# ==========================================

import re

from brain.logic.vocabulary_router import (
    handle_vocabulary
)

from brain.logic.vocabulary_modules.practice import (
    is_vocabulary_practice_active
)

from brain.memory.error_memory import (
    remember_error
)


# ==========================================
# ZAPAMIĘTANIE BŁĘDU JĘZYKOWEGO
# ==========================================

def remember_vocabulary_language_error(
    state,
    wrong_text,
    correct_text,
    error_type="grammar"
):

    if state is None:
        return

    wrong_text = str(
        wrong_text or ""
    ).strip()

    correct_text = str(
        correct_text or ""
    ).strip()

    if (
        not wrong_text
        or
        not correct_text
    ):

        return

    try:

        remember_error(
            state,
            error_type,
            wrong_text,
            correct_text
        )

    except Exception as error:

        print(
            f"Vocabulary language error memory: {error}"
        )


# ==========================================
# CZYSZCZENIE SŁOWA
# ==========================================

def clean_vocabulary_target(
    target
):

    target = str(
        target or ""
    ).strip()

    target = target.strip(
        " .?!„“\"'"
    )

    target = re.sub(
        r"\s+",
        " ",
        target
    )

    if target.lower().startswith(
        "das wort "
    ):

        target = target[
            len("das wort "):
        ].strip()

    return target


# ==========================================
# ŁADNA FORMA SŁOWA
# ==========================================

def display_target_word(
    target
):

    target = clean_vocabulary_target(
        target
    )

    if not target:
        return ""

    return (
        target[:1].upper()
        + target[1:]
    )


# ==========================================
# BUDOWANIE WYNIKU ANALIZY
# ==========================================

def build_vocabulary_analysis(
    target,
    feedback=None,
    corrected=None,
    error_type=None
):

    target = clean_vocabulary_target(
        target
    )

    if not target:

        return {
            "recognized": False
        }

    return {
        "recognized":
            True,

        "target":
            target,

        "canonical":
            (
                "Was bedeutet das Wort "
                f"{target}?"
            ),

        "feedback":
            feedback,

        "corrected":
            corrected,

        "error_type":
            error_type
    }


# ==========================================
# ROZPOZNANIE PYTANIA O SŁOWO
# ==========================================

def analyze_vocabulary_explanation_request(
    user_message
):

    text = str(
        user_message or ""
    ).strip()

    if not text:

        return {
            "recognized": False
        }


    # ======================================
    # Was bedeutet Zimmer?
    # Was bedeutet das Wort Zimmer?
    # ======================================

    match = re.match(
        (
            r"^\s*was\s+bedeutet\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        return build_vocabulary_analysis(
            match.group(1)
        )


    # ======================================
    # Was heißt Zimmer?
    # Was heißt das Wort Zimmer?
    # ======================================

    match = re.match(
        (
            r"^\s*was\s+heißt\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        return build_vocabulary_analysis(
            match.group(1)
        )


    # ======================================
    # Was heisst Zimmer?
    # ======================================

    match = re.match(
        (
            r"^\s*was\s+heisst\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        corrected = (
            "Was heißt "
            f"{display_target_word(target)}?"
        )

        return build_vocabulary_analysis(
            target,
            (
                "Fast! Richtig schreibt man: "
                f"„{corrected}“"
            ),
            corrected,
            "spelling"
        )


    # ======================================
    # Was bedeuten Zimmer?
    # ======================================

    match = re.match(
        (
            r"^\s*was\s+bedeuten\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        corrected = (
            "Was bedeutet "
            f"{display_target_word(target)}?"
        )

        return build_vocabulary_analysis(
            target,
            (
                "Fast! Richtig sagt man: "
                f"„{corrected}“"
            ),
            corrected,
            "grammar"
        )


    # ======================================
    # Was ist bedeutet Zimmer?
    # ======================================

    match = re.match(
        (
            r"^\s*was\s+ist\s+bedeutet\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        corrected = (
            "Was bedeutet "
            f"{display_target_word(target)}?"
        )

        return build_vocabulary_analysis(
            target,
            (
                "Fast! Richtig sagt man: "
                f"„{corrected}“"
            ),
            corrected,
            "grammar"
        )


    # ======================================
    # Kannst du mir Zimmer erklären?
    # ======================================

    match = re.match(
        (
            r"^\s*kannst\s+du\s+mir\s+"
            r"(?:bitte\s+)?"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s+erklären\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        return build_vocabulary_analysis(
            match.group(1)
        )


    # ======================================
    # Kannst du bitte Zimmer erklären?
    # Kannst du bitte mir Zimmer erklären?
    # ======================================

    match = re.match(
        (
            r"^\s*kannst\s+du\s+bitte\s+"
            r"(?:mir\s+)?"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s+erklären\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        return build_vocabulary_analysis(
            match.group(1)
        )


    # ======================================
    # Kannst du mir Zimmer bitte erklären?
    # ======================================

    match = re.match(
        (
            r"^\s*kannst\s+du\s+mir\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s+bitte\s+erklären"
            r"\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        return build_vocabulary_analysis(
            match.group(1)
        )


    # ======================================
    # Kannst du mir Zimmer erkläre?
    # ======================================

    match = re.match(
        (
            r"^\s*kannst\s+du\s+"
            r"(?:mir\s+|bitte\s+mir\s+|bitte\s+)?"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s+erkläre\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        corrected = (
            "Kannst du mir "
            f"{display_target_word(target)} "
            "erklären?"
        )

        return build_vocabulary_analysis(
            target,
            (
                "Fast! Nach „kannst“ "
                "steht der Infinitiv: "
                f"„{corrected}“"
            ),
            corrected,
            "grammar"
        )


    # ======================================
    # Kannst du mir erklären Zimmer?
    # ======================================

    match = re.match(
        (
            r"^\s*kannst\s+du\s+mir\s+"
            r"erklären\s+"
            r"(?:das\s+wort\s+)?"
            r"(.+?)\s*[?.!]*\s*$"
        ),
        text,
        re.IGNORECASE
    )

    if match:

        target = clean_vocabulary_target(
            match.group(1)
        )

        corrected = (
            "Kannst du mir "
            f"{display_target_word(target)} "
            "erklären?"
        )

        return build_vocabulary_analysis(
            target,
            (
                "Fast! Natürlicher sagt man: "
                f"„{corrected}“"
            ),
            corrected,
            "word_order"
        )


    return {
        "recognized": False
    }


# ==========================================
# OBSŁUGA PYTANIA O SŁOWO
# ==========================================

def handle_vocabulary_explanation_request(
    user_message,
    state
):

    analysis = (
        analyze_vocabulary_explanation_request(
            user_message
        )
    )

    if not analysis.get(
        "recognized",
        False
    ):

        return (
            False,
            None,
            None
        )


    canonical = analysis.get(
        "canonical"
    )

    feedback = analysis.get(
        "feedback"
    )

    corrected = analysis.get(
        "corrected"
    )

    error_type = analysis.get(
        "error_type"
    )


    # ======================================
    # ZAPAMIĘTANIE BŁĘDU UCZNIA
    # ======================================

    if (
        corrected
        and
        error_type
    ):

        remember_vocabulary_language_error(
            state,
            user_message,
            corrected,
            error_type
        )


    # ======================================
    # JEŻELI TRWA TRENING SŁOWA,
    # NIE CHCEMY GO STRACIĆ PRZEZ
    # PYTANIE POBOCZNE
    # ======================================

    vocabulary_active = (
        is_vocabulary_practice_active(
            state
        )
    )

    saved_vocabulary_state = None


    if vocabulary_active:

        saved_vocabulary_state = {

            "vocabulary_practice_active":
                state.get(
                    "vocabulary_practice_active"
                ),

            "vocabulary_practice_word":
                state.get(
                    "vocabulary_practice_word"
                ),

            "vocabulary_practice_type":
                state.get(
                    "vocabulary_practice_type"
                ),

            "last_activity":
                state.get(
                    "last_activity"
                ),

            "last_activity_detail":
                state.get(
                    "last_activity_detail"
                )
        }


        state[
            "vocabulary_practice_active"
        ] = False


    # ======================================
    # NORMALNA ODPOWIEDŹ MODUŁU
    # SŁOWNICTWA
    # ======================================

    answer = handle_vocabulary(
        canonical,
        state
    )


    # ======================================
    # PRZYWRACAMY PRZERWANY TRENING
    # ======================================

    if saved_vocabulary_state is not None:

        for (
            key,
            value
        ) in saved_vocabulary_state.items():

            state[
                key
            ] = value


    if not answer:

        return (
            False,
            None,
            feedback
        )


    return (
        True,
        answer,
        feedback
  )
