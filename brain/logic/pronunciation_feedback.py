# ==========================================
# NELE – PRONUNCIATION FEEDBACK
# AUSSPRACHE-COACH
# ==========================================
#
# Ten moduł NIE analizuje jeszcze audio.
#
# Dostaje gotowy wynik wymowy
# i zamienia go na naturalny feedback
# dla użytkownika.
#
# Przykład:
#
# score = 72
# word = "ich"
# problem = "ch"
#
# ->
#
# "Gut verständlich. Bei „ich“ kannst du
# den ch-Laut noch etwas weicher sprechen."
#
# ==========================================


# ==========================================
# PROGI OCENY
# ==========================================

SCORE_EXCELLENT = 90
SCORE_GOOD = 80
SCORE_UNDERSTANDABLE = 65
SCORE_NEEDS_WORK = 45


# ==========================================
# STATUSY
# ==========================================

STATUS_EXCELLENT = "excellent"
STATUS_GOOD = "good"
STATUS_UNDERSTANDABLE = "understandable"
STATUS_NEEDS_WORK = "needs_work"
STATUS_DIFFICULT = "difficult"


# ==========================================
# WSKAZÓWKI DLA DŹWIĘKÓW
# ==========================================

SOUND_TIPS = {

    "ch": (
        "Sprich den ch-Laut etwas weicher."
    ),

    "r": (
        "Das r kann noch etwas natürlicher klingen."
    ),

    "ü": (
        "Achte noch etwas auf das ü."
    ),

    "ö": (
        "Achte noch etwas auf das ö."
    ),

    "ä": (
        "Achte noch etwas auf das ä."
    ),

    "sch": (
        "Sprich das sch etwas deutlicher."
    ),

    "z": (
        "Das z klingt im Deutschen wie „ts“."
    ),

    "w": (
        "Das deutsche w klingt wie ein weiches v."
    ),

    "v": (
        "Achte auf die Aussprache von v."
    )
}


# ==========================================
# SCORE 0–100
# ==========================================

def normalize_pronunciation_score(
    score
):

    if score is None:
        return None


    try:

        score = float(
            score
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    score = max(
        0.0,
        min(
            100.0,
            score
        )
    )


    return round(
        score,
        2
    )


# ==========================================
# TEKST CELU
# ==========================================

def clean_pronunciation_target(
    target
):

    if target is None:
        return ""


    return str(
        target
    ).strip()


# ==========================================
# STATUS NA PODSTAWIE WYNIKU
# ==========================================

def get_pronunciation_status(
    score
):

    score = normalize_pronunciation_score(
        score
    )


    if score is None:
        return None


    if score >= SCORE_EXCELLENT:

        return STATUS_EXCELLENT


    if score >= SCORE_GOOD:

        return STATUS_GOOD


    if score >= SCORE_UNDERSTANDABLE:

        return STATUS_UNDERSTANDABLE


    if score >= SCORE_NEEDS_WORK:

        return STATUS_NEEDS_WORK


    return STATUS_DIFFICULT


# ==========================================
# CZY WYMOWA JEST WYSTARCZAJĄCO DOBRA
# ==========================================

def is_pronunciation_good(
    score
):

    status = get_pronunciation_status(
        score
    )


    return status in {
        STATUS_EXCELLENT,
        STATUS_GOOD
    }


# ==========================================
# CZY WYMOWA WYMAGA POWTÓRKI
# ==========================================

def pronunciation_needs_review(
    score
):

    status = get_pronunciation_status(
        score
    )


    return status in {
        STATUS_UNDERSTANDABLE,
        STATUS_NEEDS_WORK,
        STATUS_DIFFICULT
    }


# ==========================================
# PODSTAWOWY FEEDBACK
# ==========================================

def get_basic_pronunciation_feedback(
    score
):

    status = get_pronunciation_status(
        score
    )


    if status == STATUS_EXCELLENT:

        return (
            "Sehr gut! Das klingt klar "
            "und natürlich."
        )


    if status == STATUS_GOOD:

        return (
            "Gut! Das ist klar und "
            "gut verständlich."
        )


    if status == STATUS_UNDERSTANDABLE:

        return (
            "Gut verständlich. "
            "Ein Detail können wir "
            "noch verbessern."
        )


    if status == STATUS_NEEDS_WORK:

        return (
            "Fast. Man versteht dich, "
            "aber die Aussprache können "
            "wir noch verbessern."
        )


    if status == STATUS_DIFFICULT:

        return (
            "Versuch es noch einmal. "
            "Wir machen es langsam."
        )


    return (
        "Ich kann die Aussprache "
        "noch nicht sicher bewerten."
    )


# ==========================================
# WSKAZÓWKA DLA KONKRETNEGO DŹWIĘKU
# ==========================================

def get_sound_tip(
    sound
):

    sound = clean_pronunciation_target(
        sound
    ).lower()


    if not sound:
        return None


    return SOUND_TIPS.get(
        sound
    )


# ==========================================
# FEEDBACK DLA SŁOWA
# ==========================================

def build_word_pronunciation_feedback(
    word,
    score,
    problem_sound=None
):

    word = clean_pronunciation_target(
        word
    )


    base_feedback = (
        get_basic_pronunciation_feedback(
            score
        )
    )


    if not word:

        return base_feedback


    status = get_pronunciation_status(
        score
    )


    # ======================================
    # BARDZO DOBRZE
    # ======================================

    if status == STATUS_EXCELLENT:

        return (
            f"Sehr gut! „{word}“ klingt "
            "klar und natürlich."
        )


    # ======================================
    # DOBRZE
    # ======================================

    if status == STATUS_GOOD:

        return (
            f"Gut! „{word}“ ist klar "
            "und gut verständlich."
        )


    # ======================================
    # KONKRETNY PROBLEM DŹWIĘKOWY
    # ======================================

    sound_tip = get_sound_tip(
        problem_sound
    )


    if sound_tip:

        return (
            f"„{word}“ ist schon "
            f"gut verständlich. "
            f"{sound_tip}"
        )


    # ======================================
    # BRAK KONKRETNEGO PROBLEMU
    # ======================================

    if status == STATUS_UNDERSTANDABLE:

        return (
            f"„{word}“ ist gut verständlich. "
            "Sprich es noch einmal ganz ruhig."
        )


    if status == STATUS_NEEDS_WORK:

        return (
            f"Bei „{word}“ können wir "
            "die Aussprache noch verbessern. "
            "Sag das Wort bitte noch einmal."
        )


    return (
        f"Versuch „{word}“ noch einmal. "
        "Wir machen es langsam."
    )


# ==========================================
# FEEDBACK DLA DŹWIĘKU
# ==========================================

def build_sound_pronunciation_feedback(
    sound,
    score
):

    sound = clean_pronunciation_target(
        sound
    )


    status = get_pronunciation_status(
        score
    )


    if not sound:

        return get_basic_pronunciation_feedback(
            score
        )


    if status == STATUS_EXCELLENT:

        return (
            f"Sehr gut! Der Laut „{sound}“ "
            "klingt schon sehr natürlich."
        )


    if status == STATUS_GOOD:

        return (
            f"Gut! Der Laut „{sound}“ "
            "ist klar."
        )


    tip = get_sound_tip(
        sound
    )


    if tip:

        return tip


    return (
        f"Den Laut „{sound}“ üben "
        "wir noch ein bisschen."
    )


# ==========================================
# FEEDBACK DLA CAŁEGO ZDANIA
# ==========================================

def build_sentence_pronunciation_feedback(
    sentence,
    score,
    problem_word=None,
    problem_sound=None
):

    sentence = clean_pronunciation_target(
        sentence
    )

    problem_word = clean_pronunciation_target(
        problem_word
    )


    status = get_pronunciation_status(
        score
    )


    # ======================================
    # BARDZO DOBRA WYPOWIEDŹ
    # ======================================

    if status == STATUS_EXCELLENT:

        return (
            "Sehr gut! Der ganze Satz klingt "
            "klar und natürlich."
        )


    # ======================================
    # DOBRA WYPOWIEDŹ
    # ======================================

    if status == STATUS_GOOD:

        return (
            "Gut! Der Satz ist klar "
            "und gut verständlich."
        )


    # ======================================
    # PROBLEM W KONKRETNYM SŁOWIE
    # ======================================

    if problem_word:

        sound_tip = get_sound_tip(
            problem_sound
        )


        if sound_tip:

            return (
                "Der Satz ist gut verständlich. "
                f"Bei „{problem_word}“ kannst du "
                f"noch etwas aufpassen. "
                f"{sound_tip}"
            )


        return (
            "Der Satz ist gut verständlich. "
            f"„{problem_word}“ üben wir "
            "noch einmal."
        )


    # ======================================
    # OGÓLNY FEEDBACK
    # ======================================

    if status == STATUS_UNDERSTANDABLE:

        return (
            "Der Satz ist gut verständlich. "
            "Ein kleines Detail können wir "
            "noch verbessern."
        )


    if status == STATUS_NEEDS_WORK:

        return (
            "Man versteht den Satz schon. "
            "Wir sprechen ihn noch einmal "
            "etwas langsamer."
        )


    return (
        "Versuch den Satz noch einmal. "
        "Sprich langsam und deutlich."
    )


# ==========================================
# GŁÓWNA FUNKCJA FEEDBACKU
# ==========================================

def build_pronunciation_feedback(
    target_type,
    target,
    score,
    problem_word=None,
    problem_sound=None
):

    target_type = str(
        target_type or ""
    ).strip().lower()


    # ======================================
    # SŁOWO
    # ======================================

    if target_type in {
        "word",
        "words"
    }:

        return build_word_pronunciation_feedback(
            target,
            score,
            problem_sound
        )


    # ======================================
    # DŹWIĘK
    # ======================================

    if target_type in {
        "sound",
        "sounds",
        "phoneme",
        "phonemes"
    }:

        return build_sound_pronunciation_feedback(
            target,
            score
        )


    # ======================================
    # ZDANIE
    # ======================================

    if target_type in {
        "sentence",
        "sentences"
    }:

        return build_sentence_pronunciation_feedback(
            target,
            score,
            problem_word,
            problem_sound
        )


    # ======================================
    # NIEZNANY TYP
    # ======================================

    return get_basic_pronunciation_feedback(
        score
    )


# ==========================================
# PEŁNA OCENA DO DALSZEGO SYSTEMU
# ==========================================

def create_pronunciation_result(
    target_type,
    target,
    score,
    problem_word=None,
    problem_sound=None
):

    normalized_score = (
        normalize_pronunciation_score(
            score
        )
    )


    status = get_pronunciation_status(
        normalized_score
    )


    feedback = build_pronunciation_feedback(
        target_type,
        target,
        normalized_score,
        problem_word,
        problem_sound
    )


    return {
        "target_type":
            target_type,

        "target":
            target,

        "score":
            normalized_score,

        "status":
            status,

        "good":
            is_pronunciation_good(
                normalized_score
            ),

        "needs_review":
            pronunciation_needs_review(
                normalized_score
            ),

        "problem_word":
            problem_word,

        "problem_sound":
            problem_sound,

        "feedback":
            feedback
      }
