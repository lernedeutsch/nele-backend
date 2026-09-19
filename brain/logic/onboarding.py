# ==========================================
# NELE – PIERWSZE SPOTKANIE Z UŻYTKOWNIKIEM
# ==========================================

import re

from brain.memory.user_facts import (
    get_user_fact,
    remember_user_fact
)


# ==========================================
# SPRAWDZENIE, CZY ONBOARDING JEST GOTOWY
# ==========================================

def is_onboarding_completed(
    state
):

    return bool(
        state.get(
            "onboarding_completed",
            False
        )
    )


# ==========================================
# POBRANIE AKTUALNEGO ETAPU
# ==========================================

def get_onboarding_step(
    state
):

    return state.get(
        "onboarding_step",
        0
    )


# ==========================================
# USTAWIENIE ETAPU
# ==========================================

def set_onboarding_step(
    state,
    step
):

    state[
        "onboarding_step"
    ] = step


# ==========================================
# ZAKOŃCZENIE ONBOARDINGU
# ==========================================

def complete_onboarding(
    state
):

    state[
        "onboarding_completed"
    ] = True

    state[
        "onboarding_step"
    ] = 0


# ==========================================
# CZY UŻYTKOWNIK JEST NOWY
# ==========================================

def is_new_user(
    state
):

    if is_onboarding_completed(
        state
    ):
        return False

    name = get_user_fact(
        state,
        "name"
    )

    origin = get_user_fact(
        state,
        "origin"
    )

    residence = get_user_fact(
        state,
        "residence"
    )

    hobby = get_user_fact(
        state,
        "hobby"
    )

    learning_goal = get_user_fact(
        state,
        "learning_goal"
    )

    return not any([
        name,
        origin,
        residence,
        hobby,
        learning_goal
    ])


# ==========================================
# POMOCNICZE CZYSZCZENIE TEKSTU
# ==========================================

def clean_value(
    value
):

    if not value:
        return ""

    value = str(
        value
    ).strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    value = value.strip(
        " .,!?:;„“\"'"
    )

    if not value:
        return ""

    return (
        value[:1].upper()
        + value[1:]
    )


# ==========================================
# NORMALIZACJA DO SPRAWDZANIA
# ==========================================

def normalize_answer(
    text
):

    text = str(
        text or ""
    ).strip().lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip(
        " .,!?:;„“\"'"
    )


# ==========================================
# ZAPAMIĘTANIE FAKTU
# ==========================================

def save_onboarding_fact(
    state,
    key,
    value
):

    if not value:
        return

    remember_user_fact(
        state,
        key,
        value
    )


    # ======================================
    # ZGODNOŚĆ ZE STARSZĄ PAMIĘCIĄ
    # ======================================

    if key in {
        "name",
        "origin",
        "residence"
    }:

        state[
            key
        ] = value


# ==========================================
# WYSZUKANIE WARTOŚCI W PEŁNYM ZDANIU
# ==========================================

def extract_pattern_value(
    user_message,
    patterns
):

    text = str(
        user_message or ""
    ).strip()

    for pattern in patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            return clean_value(
                match.group(1)
            )

    return ""


# ==========================================
# IMIĘ
# ==========================================
#
# WAŻNE:
#
# Akceptujemy tylko bezpieczne formy:
#
# Ich heiße Moni.
# Mein Name ist Moni.
#
# NIE używamy już:
#
# Ich bin ...
#
# ponieważ:
#
# Ich bin müde.
# Ich bin Anfängerin.
# Ich bin bei A1.
#
# nie są imieniem.
# ==========================================

def extract_name_sentence(
    user_message
):

    return extract_pattern_value(
        user_message,
        [
            r"^\s*ich\s+hei(?:ß|ss)e\s+(.+?)\s*[.!?]*\s*$",
            r"^\s*mein\s+name\s+ist\s+(.+?)\s*[.!?]*\s*$"
        ]
    )


# ==========================================
# POCHODZENIE
# ==========================================

def extract_origin_sentence(
    user_message
):

    return extract_pattern_value(
        user_message,
        [
            r"^\s*ich\s+komme\s+aus\s+(.+?)\s*[.!?]*\s*$",
            r"^\s*ich\s+bin\s+aus\s+(.+?)\s*[.!?]*\s*$"
        ]
    )


# ==========================================
# MIEJSCE ZAMIESZKANIA
# ==========================================

def extract_residence_sentence(
    user_message
):

    return extract_pattern_value(
        user_message,
        [
            r"^\s*ich\s+wohne\s+in\s+(.+?)\s*[.!?]*\s*$",
            r"^\s*ich\s+lebe\s+in\s+(.+?)\s*[.!?]*\s*$"
        ]
    )


# ==========================================
# HOBBY – NATURALNE ZDANIA
# ==========================================

def extract_hobby_sentence(
    user_message
):

    normalized = normalize_answer(
        user_message
    )


    # ======================================
    # CZĘSTE NATURALNE ODPOWIEDZI
    # ======================================

    hobby_patterns = [

        (
            (
                "fahre gern rad" in normalized
                or
                "fahre gerne rad" in normalized
            ),
            "Radfahren"
        ),

        (
            (
                "lese gern" in normalized
                or
                "lese gerne" in normalized
            ),
            "Lesen"
        ),

        (
            (
                "koche gern" in normalized
                or
                "koche gerne" in normalized
            ),
            "Kochen"
        ),

        (
            (
                "schwimme gern" in normalized
                or
                "schwimme gerne" in normalized
            ),
            "Schwimmen"
        ),

        (
            (
                "wandere gern" in normalized
                or
                "wandere gerne" in normalized
            ),
            "Wandern"
        ),

        (
            (
                "reise gern" in normalized
                or
                "reise gerne" in normalized
            ),
            "Reisen"
        ),

        (
            (
                "tanze gern" in normalized
                or
                "tanze gerne" in normalized
            ),
            "Tanzen"
        ),

        (
            (
                "jogge gern" in normalized
                or
                "jogge gerne" in normalized
            ),
            "Joggen"
        ),

        (
            (
                "fotografiere gern" in normalized
                or
                "fotografiere gerne" in normalized
            ),
            "Fotografieren"
        ),

        (
            (
                "höre gern musik" in normalized
                or
                "höre gerne musik" in normalized
            ),
            "Musik hören"
        ),

        (
            (
                "gehe gern spazieren" in normalized
                or
                "gehe gerne spazieren" in normalized
            ),
            "Spazierengehen"
        )
    ]


    for condition, hobby in hobby_patterns:

        if condition:

            return hobby


    # ======================================
    # "MEIN HOBBY IST ..."
    # NADAL POPRAWNE I AKCEPTOWANE
    # ======================================

    hobby = extract_pattern_value(
        user_message,
        [
            r"^\s*mein\s+hobby\s+ist\s+(.+?)\s*[.!?]*\s*$"
        ]
    )

    if hobby:

        return hobby


    # ======================================
    # INNA NATURALNA ODPOWIEDŹ Z "GERN"
    #
    # Akceptujemy prosty szyk A1:
    # "Ich spiele gern Tennis."
    # "Ich lese sehr gerne."
    #
    # Nie akceptujemy przypadkowych ciągów typu:
    # "Ich schreibe gerade gerne fahre."
    # ======================================

    natural_hobby_patterns = [
        r"^ich\s+[a-zäöüß]+\s+(?:sehr\s+)?gern(?:e)?(?:\s+.+)?$",
        r"^in\s+meiner\s+freizeit\s+[a-zäöüß]+\s+ich\s+(?:sehr\s+)?gern(?:e)?(?:\s+.+)?$",
        r"^in\s+meiner\s+freizeit\s+[a-zäöüß]+\s+(?:sehr\s+)?gern(?:e)?(?:\s+.+)?$"
    ]


    for pattern in natural_hobby_patterns:

        if re.match(
            pattern,
            normalized,
            flags=re.IGNORECASE
        ):

            return clean_value(
                user_message
            )


    return ""


# ==========================================
# POZIOM CEFR – TAKŻE TYPOWE WARIANTY ASR
# ==========================================

def extract_learning_level(
    text
):

    normalized = normalize_answer(
        text
    )

    if not normalized:
        return ""


    # Zapis standardowy: A1, B1, B2...
    direct = re.search(
        r"\b(a1|a2|b1|b2|c1|c2)\b",
        normalized,
        flags=re.IGNORECASE
    )

    if direct:

        return (
            direct
            .group(1)
            .upper()
        )


    # Typowe wyniki rozpoznawania mowy:
    # "B eins" -> "b eins"
    # "B1" -> "bei eins"
    # podobnie dla A/C i 1/2.
    spoken_patterns = [
        (r"\b(?:a|ah)\s*eins\b", "A1"),
        (r"\b(?:a|ah)\s*zwei\b", "A2"),
        (r"\b(?:b|be|bei)\s*eins\b", "B1"),
        (r"\b(?:b|be|bei)\s*zwei\b", "B2"),
        (r"\b(?:c|ce|cee|ze)\s*eins\b", "C1"),
        (r"\b(?:c|ce|cee|ze)\s*zwei\b", "C2"),
    ]


    for pattern, level in spoken_patterns:

        if re.search(
            pattern,
            normalized,
            flags=re.IGNORECASE
        ):

            return level


    return ""


# ==========================================
# CEL NAUKI
# ==========================================

def extract_learning_goal_sentence(
    user_message
):

    normalized = normalize_answer(
        user_message
    )


    # ======================================
    # MUSI TO BYĆ PEŁNE ZDANIE
    # ======================================

    valid_start = (
        normalized.startswith(
            "ich möchte "
        )
        or
        normalized.startswith(
            "ich will "
        )
        or
        normalized.startswith(
            "mein ziel ist "
        )
        or
        normalized.startswith(
            "mein lernziel ist "
        )
    )


    if not valid_start:

        return ""


    # ======================================
    # JEŻELI PODANO POZIOM
    # ======================================

    level = extract_learning_level(
        normalized
    )


    if level:

        return (
            f"Deutsch {level}"
        )


    # ======================================
    # INNY CEL
    # ======================================

    goal = extract_pattern_value(
        user_message,
        [
            r"^\s*ich\s+möchte\s+(.+?)\s*[.!?]*\s*$",
            r"^\s*ich\s+will\s+(.+?)\s*[.!?]*\s*$",
            r"^\s*mein\s+ziel\s+ist\s+(.+?)\s*[.!?]*\s*$",
            r"^\s*mein\s+lernziel\s+ist\s+(.+?)\s*[.!?]*\s*$"
        ]
    )

    return goal


# ==========================================
# KRÓTKA ODPOWIEDŹ
# ==========================================

def get_short_answer_value(
    user_message,
    step
):

    normalized = normalize_answer(
        user_message
    )

    if not normalized:
        return ""


    # ======================================
    # NIE TRAKTUJEMY BŁĘDNEGO ZDANIA
    # JAKO KRÓTKIEJ ODPOWIEDZI
    # ======================================

    if normalized.startswith(
        (
            "ich ",
            "mein ",
            "meine "
        )
    ):

        return ""


    # ======================================
    # POCHODZENIE:
    # "AUS POLEN"
    # ======================================

    if (
        step == 2
        and
        normalized.startswith(
            "aus "
        )
    ):

        return clean_value(
            normalized[4:]
        )


    # ======================================
    # MIEJSCE:
    # "IN HEIDELBERG"
    # ======================================

    if (
        step == 3
        and
        normalized.startswith(
            "in "
        )
    ):

        return clean_value(
            normalized[3:]
        )


    words = normalized.split()


    if len(words) > 4:

        return ""


    return clean_value(
        normalized
    )


# ==========================================
# POZIOM Z KRÓTKIEJ ODPOWIEDZI
# ==========================================

def get_short_learning_level(
    user_message
):

    return extract_learning_level(
        user_message
    )


# ==========================================
# ROZPOCZĘCIE PIERWSZEGO SPOTKANIA
# ==========================================

def start_onboarding(
    state
):

    set_onboarding_step(
        state,
        1
    )

    return (
        "Hallo! Ich bin Nele, "
        "deine persönliche Deutschtrainerin. "
        "Schön, dich kennenzulernen! "
        "Wie heißt du?"
    )


# ==========================================
# PYTANIE DLA DANEGO ETAPU
# ==========================================

def get_onboarding_question(
    state
):

    step = get_onboarding_step(
        state
    )


    # ======================================
    # 1. IMIĘ
    # ======================================

    if step == 1:

        return (
            "Wie heißt du?"
        )


    # ======================================
    # 2. POCHODZENIE
    # ======================================

    if step == 2:

        name = get_user_fact(
            state,
            "name"
        )

        if name:

            return (
                f"Schön, dich kennenzulernen, "
                f"{name}! Woher kommst du?"
            )

        return (
            "Schön, dich kennenzulernen! "
            "Woher kommst du?"
        )


    # ======================================
    # 3. MIEJSCE ZAMIESZKANIA
    # ======================================

    if step == 3:

        return (
            "Und wo wohnst du jetzt?"
        )


    # ======================================
    # 4. CZAS WOLNY / HOBBY
    # ======================================

    if step == 4:

        return (
            "Was machst du gern "
            "in deiner Freizeit?"
        )


    # ======================================
    # 5. CEL NAUKI
    # ======================================

    if step == 5:

        return (
            "Was ist dein Ziel "
            "beim Deutschlernen?"
        )


    return None


# ==========================================
# PRZEJŚCIE DO NASTĘPNEGO PYTANIA
# ==========================================

def advance_onboarding(
    state
):

    step = get_onboarding_step(
        state
    )

    next_step = step + 1

    set_onboarding_step(
        state,
        next_step
    )

    return get_onboarding_question(
        state
    )


# ==========================================
# ODPOWIEDŹ TRENINGOWA
# ==========================================

def get_onboarding_retry(
    step,
    user_message=""
):

    short_value = get_short_answer_value(
        user_message,
        step
    )


    # ======================================
    # 1. IMIĘ
    # ======================================

    if step == 1:

        if short_value:

            return (
                "Genau! "
                "Sag es bitte als ganzen Satz: "
                f"„Ich heiße {short_value}.“"
            )

        return (
            "Sag bitte als ganzen Satz, "
            "zum Beispiel: "
            "„Ich heiße Anna.“"
        )


    # ======================================
    # 2. POCHODZENIE
    # ======================================

    if step == 2:

        if short_value:

            return (
                "Genau! "
                "Sag es bitte als ganzen Satz: "
                f"„Ich komme aus {short_value}.“"
            )

        return (
            "Sag bitte als ganzen Satz, "
            "zum Beispiel: "
            "„Ich komme aus Polen.“"
        )


    # ======================================
    # 3. MIEJSCE ZAMIESZKANIA
    # ======================================

    if step == 3:

        if short_value:

            return (
                "Genau! "
                "Sag es bitte als ganzen Satz: "
                f"„Ich wohne in {short_value}.“"
            )

        return (
            "Sag bitte als ganzen Satz, "
            "zum Beispiel: "
            "„Ich wohne in Heidelberg.“"
        )


    # ======================================
    # 4. HOBBY
    # ======================================

    if step == 4:

        normalized = normalize_answer(
            user_message
        )

        if normalized in {
            "radfahren",
            "fahrradfahren",
            "rad fahren",
            "fahrrad fahren"
        }:

            return (
                "Genau! "
                "Sag es bitte als ganzen Satz: "
                "„Ich fahre gern Rad.“"
            )

        return (
            "Sag bitte als ganzen Satz, "
            "zum Beispiel: "
            "„Ich fahre gern Rad.“"
        )


    # ======================================
    # 5. CEL NAUKI
    # ======================================

    if step == 5:

        level = get_short_learning_level(
            user_message
        )

        if level:

            return (
                "Genau! "
                "Sag es bitte als ganzen Satz: "
                f"„Ich möchte {level} erreichen.“"
            )

        return (
            "Sag bitte als ganzen Satz, "
            "zum Beispiel: "
            "„Ich möchte B1 erreichen.“"
        )


    return (
        "Versuch es bitte noch einmal."
    )


# ==========================================
# ZAKOŃCZENIE PIERWSZEGO SPOTKANIA
# ==========================================

def finish_onboarding(
    state
):

    name = get_user_fact(
        state,
        "name"
    )

    complete_onboarding(
        state
    )

    # Po pierwszym poznaniu ucznia Nele czeka
    # na naturalne "ja" / "nein" i dopiero wtedy
    # uruchamia pierwszy krok nauki.
    state[
        "last_question"
    ] = "start_after_onboarding"

    if name:

        return (
            f"Super, {name}! "
            "Jetzt kenne ich dich schon "
            "ein bisschen besser. "
            "Ich passe die Übungen an dich an. "
            "Möchtest du gleich anfangen?"
        )

    return (
        "Super! "
        "Jetzt kenne ich dich schon "
        "ein bisschen besser. "
        "Ich passe die Übungen an dich an. "
        "Möchtest du gleich anfangen?"
    )


# ==========================================
# OBSŁUGA ODPOWIEDZI PODCZAS ONBOARDINGU
# ==========================================

def handle_onboarding_answer(
    user_message,
    state,
    session_id="default"
):

    if is_onboarding_completed(
        state
    ):
        return None

    step = get_onboarding_step(
        state
    )

    if step == 0:
        return None


    # ======================================
    # ETAP 1 – IMIĘ
    # ======================================

    if step == 1:

        name = extract_name_sentence(
            user_message
        )

        if not name:

            return get_onboarding_retry(
                step,
                user_message
            )

        save_onboarding_fact(
            state,
            "name",
            name
        )

        set_onboarding_step(
            state,
            2
        )

        return (
            f"Schön, dich kennenzulernen, "
            f"{name}! Woher kommst du?"
        )


    # ======================================
    # ETAP 2 – POCHODZENIE
    # ======================================

    if step == 2:

        origin = extract_origin_sentence(
            user_message
        )

        if not origin:

            return get_onboarding_retry(
                step,
                user_message
            )

        save_onboarding_fact(
            state,
            "origin",
            origin
        )

        set_onboarding_step(
            state,
            3
        )

        return (
            "Und wo wohnst du jetzt?"
        )


    # ======================================
    # ETAP 3 – MIEJSCE ZAMIESZKANIA
    # ======================================

    if step == 3:

        residence = (
            extract_residence_sentence(
                user_message
            )
        )

        if not residence:

            return get_onboarding_retry(
                step,
                user_message
            )

        save_onboarding_fact(
            state,
            "residence",
            residence
        )

        set_onboarding_step(
            state,
            4
        )

        return (
            "Was machst du gern "
            "in deiner Freizeit?"
        )


    # ======================================
    # ETAP 4 – HOBBY / CZAS WOLNY
    # ======================================

    if step == 4:

        hobby = extract_hobby_sentence(
            user_message
        )

        if not hobby:

            return get_onboarding_retry(
                step,
                user_message
            )

        save_onboarding_fact(
            state,
            "hobby",
            hobby
        )

        set_onboarding_step(
            state,
            5
        )

        return (
            "Schön! "
            "Und was ist dein Ziel "
            "beim Deutschlernen?"
        )


    # ======================================
    # ETAP 5 – CEL NAUKI
    # ======================================

    if step == 5:

        learning_goal = (
            extract_learning_goal_sentence(
                user_message
            )
        )

        if not learning_goal:

            return get_onboarding_retry(
                step,
                user_message
            )

        save_onboarding_fact(
            state,
            "learning_goal",
            learning_goal
        )

        return finish_onboarding(
            state
        )


    return None
