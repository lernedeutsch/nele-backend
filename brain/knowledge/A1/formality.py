# ==========================================
# NELE – A1 – FORMELL / INFORMELL
# ==========================================


# ==========================================
# OPISY FORMALNOŚCI
# ==========================================

FORMALITY = {

    # ======================================
    # POWITANIA
    # ======================================

    "guten morgen": (
        "„Guten Morgen“ ist höflich und neutral. "
        "Man kann es sowohl in formellen als auch "
        "in weniger formellen Situationen benutzen."
    ),

    "guten tag": (
        "„Guten Tag“ ist höflich und eher formell. "
        "Man benutzt es häufig bei unbekannten Personen "
        "oder in beruflichen Situationen."
    ),

    "guten abend": (
        "„Guten Abend“ ist höflich und neutral. "
        "Es kann auch in formellen Situationen "
        "benutzt werden."
    ),

    "hallo": (
        "„Hallo“ ist freundlich und eher informell. "
        "Man benutzt es häufig mit Freunden, Bekannten "
        "oder Personen, mit denen man per Du ist."
    ),

    "hi": (
        "„Hi“ ist informell. "
        "Man benutzt es besonders mit Freunden "
        "und Bekannten."
    ),


    # ======================================
    # POŻEGNANIA
    # ======================================

    "tschüss": (
        "„Tschüss“ ist informell. "
        "Man benutzt es besonders mit Freunden, "
        "Bekannten oder Personen, mit denen man per Du ist."
    ),

    "auf wiedersehen": (
        "„Auf Wiedersehen“ ist höflich und eher formell. "
        "Man kann es zum Beispiel bei unbekannten Personen "
        "oder im beruflichen Kontakt benutzen."
    ),


    # ======================================
    # DU / SIE
    # ======================================

    "du": (
        "„Du“ ist informell. "
        "Man benutzt „du“ normalerweise mit Freunden, "
        "Familie und Personen, die man gut kennt."
    ),

    "sie": (
        "„Sie“ ist formell und höflich. "
        "Man benutzt „Sie“ zum Beispiel bei unbekannten "
        "Erwachsenen oder in formellen Situationen."
    ),


    # ======================================
    # PYTANIE O IMIĘ
    # ======================================

    "wie heißt du": (
        "„Wie heißt du?“ ist informell, "
        "weil man die Person mit „du“ anspricht."
    ),

    "wie heißen sie": (
        "„Wie heißen Sie?“ ist formell und höflich, "
        "weil man die Person mit „Sie“ anspricht."
    )
}


# ==========================================
# POZIOM FORMALNOŚCI
# ==========================================
#
# 1 = bardzo nieformalnie
# 2 = nieformalnie
# 3 = neutralnie
# 4 = raczej formalnie
# 5 = formalnie
#
# Te wartości pozwalają Nele porównywać
# dwa zwroty, zamiast przechowywać osobną
# odpowiedź dla każdej możliwej pary.
# ==========================================

FORMALITY_LEVELS = {

    # POWITANIA

    "hi": 1,

    "hallo": 2,

    "guten morgen": 3,

    "guten abend": 3,

    "guten tag": 4,


    # POŻEGNANIA

    "tschüss": 2,

    "auf wiedersehen": 4,


    # DU / SIE

    "du": 2,

    "sie": 5,


    # PYTANIE O IMIĘ

    "wie heißt du": 2,

    "wie heißen sie": 5
}
