# ==========================================
# NELE – ADAPTIVE REVIEW 2.0
# INTELIGENTNE PLANOWANIE POWTÓREK
# ==========================================

from datetime import datetime, timezone, timedelta


# ==========================================
# JAKOŚĆ ODPOWIEDZI
# ==========================================
#
# 0 = błędnie
#     użytkownik jeszcze nie potrafi
#
# 1 = poprawnie dopiero po dużej pomocy
#
# 2 = poprawnie po kilku trudnościach
#
# 3 = poprawnie po jednej dodatkowej próbie
#
# 4 = poprawnie samodzielnie
#     bez dodatkowej pomocy
# ==========================================

QUALITY_WRONG = 0
QUALITY_WITH_HELP = 1
QUALITY_DIFFICULT = 2
QUALITY_GOOD = 3
QUALITY_EASY = 4


# ==========================================
# NAZWY WYNIKÓW
# ==========================================

QUALITY_NAMES = {

    QUALITY_WRONG:
        "wrong",

    QUALITY_WITH_HELP:
        "correct_with_help",

    QUALITY_DIFFICULT:
        "correct_with_difficulty",

    QUALITY_GOOD:
        "correct",

    QUALITY_EASY:
        "correct_easy"
}


# ==========================================
# AKTUALNY CZAS
# ==========================================

def get_adaptive_review_now():

    return datetime.now(
        timezone.utc
    )


# ==========================================
# OGRANICZENIE WARTOŚCI
# ==========================================

def clamp(
    value,
    minimum,
    maximum
):

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


# ==========================================
# JAKOŚĆ NA PODSTAWIE LICZBY PRÓB
# ==========================================
#
# attempts = liczba wcześniejszych
# błędnych odpowiedzi podczas ćwiczenia.
#
# 0 błędów -> bardzo dobrze
# 1 błąd   -> dobrze
# 2 błędy  -> z trudnością
# 3+       -> potrzebna była większa pomoc
# ==========================================

def calculate_answer_quality(
    attempts=0,
    used_hint=False
):

    try:

        attempts = int(
            attempts
        )

    except (
        TypeError,
        ValueError
    ):

        attempts = 0


    attempts = max(
        0,
        attempts
    )


    # ======================================
    # UŻYTKOWNIK POTRZEBOWAŁ PODPOWIEDZI
    # ======================================

    if used_hint:

        if attempts >= 2:

            return QUALITY_WITH_HELP

        return QUALITY_DIFFICULT


    # ======================================
    # BEZ PODPOWIEDZI
    # ======================================

    if attempts == 0:

        return QUALITY_EASY


    if attempts == 1:

        return QUALITY_GOOD


    if attempts == 2:

        return QUALITY_DIFFICULT


    return QUALITY_WITH_HELP


# ==========================================
# NAZWA JAKOŚCI
# ==========================================

def get_quality_name(
    quality
):

    return QUALITY_NAMES.get(
        quality,
        "unknown"
    )


# ==========================================
# PODSTAWOWY ODSTĘP POWTÓRKI
# ==========================================
#
# Wynik zależy od:
#
# quality
# correct_streak
#
# Nie wystarczy więc samo:
#
# 1 dzień -> 3 dni -> 7 dni
#
# Jeżeli uczeń miał problemy,
# odstęp będzie krótszy.
# ==========================================

def get_base_review_interval_hours(
    quality,
    correct_streak
):

    try:

        quality = int(
            quality
        )

    except (
        TypeError,
        ValueError
    ):

        quality = QUALITY_WRONG


    try:

        correct_streak = int(
            correct_streak
        )

    except (
        TypeError,
        ValueError
    ):

        correct_streak = 0


    correct_streak = max(
        0,
        correct_streak
    )


    # ======================================
    # BŁĘDNA ODPOWIEDŹ
    #
    # Nie czekamy do następnego dnia.
    # Trzeba wrócić do problemu
    # jeszcze podczas nauki.
    # ======================================

    if quality <= QUALITY_WRONG:

        return 0


    # ======================================
    # POPRAWNIE DOPIERO PO DUŻEJ POMOCY
    # ======================================

    if quality == QUALITY_WITH_HELP:

        return 6


    # ======================================
    # POPRAWNIE, ALE Z TRUDNOŚCIĄ
    # ======================================

    if quality == QUALITY_DIFFICULT:

        if correct_streak <= 1:

            return 12

        if correct_streak == 2:

            return 24

        return 48


    # ======================================
    # DOBRA ODPOWIEDŹ
    # ======================================

    if quality == QUALITY_GOOD:

        if correct_streak <= 1:

            return 24

        if correct_streak == 2:

            return 48

        if correct_streak == 3:

            return 96

        if correct_streak == 4:

            return 168

        return 336


    # ======================================
    # SAMODZIELNA, PEWNA ODPOWIEDŹ
    # ======================================

    if correct_streak <= 1:

        # 1 dzień

        return 24


    if correct_streak == 2:

        # 3 dni

        return 72


    if correct_streak == 3:

        # 7 dni

        return 168


    if correct_streak == 4:

        # 14 dni

        return 336


    # 30 dni

    return 720


# ==========================================
# WPŁYW TRUDNOŚCI
# ==========================================
#
# difficulty:
#
# 0.0 = bardzo łatwe
# 0.5 = normalne
# 1.0 = bardzo trudne
#
# Trudniejszy materiał wraca szybciej.
# ==========================================

def get_difficulty_multiplier(
    difficulty
):

    try:

        difficulty = float(
            difficulty
        )

    except (
        TypeError,
        ValueError
    ):

        difficulty = 0.5


    difficulty = clamp(
        difficulty,
        0.0,
        1.0
    )


    # ======================================
    # PRZYKŁADOWO:
    #
    # difficulty 0.0 -> 1.25
    # difficulty 0.5 -> 0.875
    # difficulty 1.0 -> 0.50
    # ======================================

    return (
        1.25
        -
        (
            difficulty
            *
            0.75
        )
    )


# ==========================================
# ADAPTACYJNY ODSTĘP
# ==========================================

def calculate_review_interval_hours(
    quality,
    correct_streak,
    difficulty=0.5
):

    base_hours = (
        get_base_review_interval_hours(
            quality,
            correct_streak
        )
    )


    # ======================================
    # BŁĄD = POWTÓRKA W TEJ SAMEJ SESJI
    # ======================================

    if base_hours <= 0:

        return 0


    multiplier = (
        get_difficulty_multiplier(
            difficulty
        )
    )


    interval = (
        base_hours
        *
        multiplier
    )


    # ======================================
    # MINIMUM 1 GODZINA,
    # JEŻELI NIE JEST TO POWTÓRKA
    # W TEJ SAMEJ SESJI
    # ======================================

    interval = max(
        1,
        interval
    )


    return int(
        round(
            interval
        )
    )


# ==========================================
# DATA NASTĘPNEJ POWTÓRKI
# ==========================================

def calculate_next_review_at(
    quality,
    correct_streak,
    difficulty=0.5,
    now=None
):

    if now is None:

        now = get_adaptive_review_now()


    if now.tzinfo is None:

        now = now.replace(
            tzinfo=timezone.utc
        )


    interval_hours = (
        calculate_review_interval_hours(
            quality,
            correct_streak,
            difficulty
        )
    )


    return (
        now
        +
        timedelta(
            hours=interval_hours
        )
    )


# ==========================================
# DATA NASTĘPNEJ POWTÓRKI – ISO
# ==========================================

def calculate_next_review_timestamp(
    quality,
    correct_streak,
    difficulty=0.5,
    now=None
):

    next_review = (
        calculate_next_review_at(
            quality,
            correct_streak,
            difficulty,
            now
        )
    )


    return next_review.isoformat()


# ==========================================
# CZY POWTÓRKA JEST JUŻ POTRZEBNA
# ==========================================

def is_review_due(
    next_review_at,
    now=None
):

    if not next_review_at:

        return True


    try:

        review_time = datetime.fromisoformat(
            str(
                next_review_at
            ).replace(
                "Z",
                "+00:00"
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return True


    if review_time.tzinfo is None:

        review_time = review_time.replace(
            tzinfo=timezone.utc
        )


    if now is None:

        now = get_adaptive_review_now()


    if now.tzinfo is None:

        now = now.replace(
            tzinfo=timezone.utc
        )


    return now >= review_time


# ==========================================
# PEŁNY PLAN POWTÓRKI
# ==========================================

def build_adaptive_review_plan(
    attempts=0,
    used_hint=False,
    correct_streak=0,
    difficulty=0.5,
    now=None
):

    quality = calculate_answer_quality(
        attempts,
        used_hint
    )


    # ======================================
    # POPRAWNA ODPOWIEDŹ
    # ZWIĘKSZA SERIĘ
    # ======================================

    if quality > QUALITY_WRONG:

        next_streak = (
            correct_streak
            +
            1
        )

    else:

        next_streak = 0


    interval_hours = (
        calculate_review_interval_hours(
            quality,
            next_streak,
            difficulty
        )
    )


    next_review_at = (
        calculate_next_review_timestamp(
            quality,
            next_streak,
            difficulty,
            now
        )
    )


    return {

        "quality":
            quality,

        "quality_name":
            get_quality_name(
                quality
            ),

        "correct_streak":
            next_streak,

        "difficulty":
            difficulty,

        "interval_hours":
            interval_hours,

        "next_review_at":
            next_review_at
  }
