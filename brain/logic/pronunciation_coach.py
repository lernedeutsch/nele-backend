# ==========================================
# NELE – PRONUNCIATION COACH
# AUSSPRACHE-COACH
# STUDENT MEMORY 2.0
# ==========================================
#
# Ten moduł łączy:
#
# pronunciation_feedback.py
#        +
# pronunciation_memory.py
#
# Sam NIE analizuje audio.
#
# Dostaje wynik z przyszłego analizatora,
# zapisuje go w pamięci ucznia
# i tworzy odpowiedź Nele.
# ==========================================

from brain.logic.pronunciation_feedback import (
    create_pronunciation_result
)

from brain.memory.pronunciation_memory import (
    remember_word_pronunciation,
    remember_sound_pronunciation
)


# ==========================================
# BEZPIECZNY TEKST
# ==========================================

def clean_coach_text(
    text
):

    if text is None:
        return ""

    return str(
        text
    ).strip()


# ==========================================
# ZAPIS WYNIKU SŁOWA
# ==========================================

def save_word_pronunciation_result(
    state,
    word,
    score,
    feedback=None
):

    word = clean_coach_text(
        word
    )

    if not word:
        return False

    return remember_word_pronunciation(
        state,
        word,
        score=score,
        feedback=feedback
    )


# ==========================================
# ZAPIS WYNIKU DŹWIĘKU
# ==========================================

def save_sound_pronunciation_result(
    state,
    sound,
    score,
    feedback=None
):

    sound = clean_coach_text(
        sound
    )

    if not sound:
        return False

    return remember_sound_pronunciation(
        state,
        sound,
        score=score,
        feedback=feedback
    )


# ==========================================
# ANALIZA JEDNEGO SŁOWA
# ==========================================

def process_word_pronunciation(
    state,
    word,
    score,
    problem_sound=None,
    sound_score=None
):

    result = create_pronunciation_result(
        target_type="word",
        target=word,
        score=score,
        problem_sound=problem_sound
    )

    feedback = result.get(
        "feedback"
    )

    # ======================================
    # ZAPIS SŁOWA
    # ======================================

    save_word_pronunciation_result(
        state,
        word,
        score,
        feedback
    )


    # ======================================
    # ZAPIS PROBLEMATYCZNEGO DŹWIĘKU
    # ======================================

    if problem_sound:

        if sound_score is None:

            sound_score = score

        save_sound_pronunciation_result(
            state,
            problem_sound,
            sound_score,
            feedback
        )


    return result


# ==========================================
# ANALIZA SAMEGO DŹWIĘKU
# ==========================================

def process_sound_pronunciation(
    state,
    sound,
    score
):

    result = create_pronunciation_result(
        target_type="sound",
        target=sound,
        score=score
    )

    feedback = result.get(
        "feedback"
    )

    save_sound_pronunciation_result(
        state,
        sound,
        score,
        feedback
    )

    return result


# ==========================================
# ANALIZA CAŁEGO ZDANIA
# ==========================================
#
# Na razie pamięć zapisuje:
#
# - problematyczne słowo
# - problematyczny dźwięk
#
# Nie zapisujemy jeszcze całych zdań
# do pronunciation_memory.
# ==========================================

def process_sentence_pronunciation(
    state,
    sentence,
    score,
    problem_word=None,
    problem_word_score=None,
    problem_sound=None,
    problem_sound_score=None
):

    result = create_pronunciation_result(
        target_type="sentence",
        target=sentence,
        score=score,
        problem_word=problem_word,
        problem_sound=problem_sound
    )

    feedback = result.get(
        "feedback"
    )


    # ======================================
    # PROBLEMATYCZNE SŁOWO
    # ======================================

    if problem_word:

        word_score = problem_word_score

        if word_score is None:

            word_score = score

        save_word_pronunciation_result(
            state,
            problem_word,
            word_score,
            feedback
        )


    # ======================================
    # PROBLEMATYCZNY DŹWIĘK
    # ======================================

    if problem_sound:

        sound_score = problem_sound_score

        if sound_score is None:

            sound_score = (
                problem_word_score
                if problem_word_score
                is not None
                else score
            )

        save_sound_pronunciation_result(
            state,
            problem_sound,
            sound_score,
            feedback
        )


    return result


# ==========================================
# GŁÓWNA FUNKCJA COACHA
# ==========================================

def process_pronunciation_result(
    state,
    target_type,
    target,
    score,
    problem_word=None,
    problem_word_score=None,
    problem_sound=None,
    problem_sound_score=None
):

    target_type = clean_coach_text(
        target_type
    ).lower()


    # ======================================
    # SŁOWO
    # ======================================

    if target_type in {
        "word",
        "words"
    }:

        return process_word_pronunciation(
            state,
            target,
            score,
            problem_sound=problem_sound,
            sound_score=problem_sound_score
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

        return process_sound_pronunciation(
            state,
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

        return process_sentence_pronunciation(
            state,
            target,
            score,
            problem_word=problem_word,
            problem_word_score=problem_word_score,
            problem_sound=problem_sound,
            problem_sound_score=problem_sound_score
        )


    # ======================================
    # NIEZNANY TYP
    # ======================================

    return None


# ==========================================
# GOTOWA ODPOWIEDŹ NELE
# ==========================================

def get_pronunciation_coach_answer(
    state,
    target_type,
    target,
    score,
    problem_word=None,
    problem_word_score=None,
    problem_sound=None,
    problem_sound_score=None
):

    result = process_pronunciation_result(
        state,
        target_type,
        target,
        score,
        problem_word=problem_word,
        problem_word_score=problem_word_score,
        problem_sound=problem_sound,
        problem_sound_score=problem_sound_score
    )

    if not result:
        return None

    return result.get(
        "feedback"
  )
