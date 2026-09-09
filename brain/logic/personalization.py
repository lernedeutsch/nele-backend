# ==========================================
# NELE – PERSONALIZACJA NAUKI
# ==========================================

from brain.memory.user_facts import (
    get_user_fact
)

from brain.logic.matcher import (
    normalize
)


# ==========================================
# PODSTAWOWE CZASOWNIKI DO WALIDACJI ZDANIA
# ==========================================

BASIC_GERMAN_VERBS = {
    "bin",
    "bist",
    "ist",
    "sind",
    "seid",

    "habe",
    "hast",
    "hat",
    "haben",

    "mache",
    "machst",
    "macht",
    "machen",

    "fahre",
    "fährst",
    "fahrt",
    "fahren",

    "gehe",
    "gehst",
    "geht",
    "gehen",

    "komme",
    "kommst",
    "kommt",
    "kommen",

    "wohne",
    "wohnst",
    "wohnt",
    "wohnen",

    "lebe",
    "lebst",
    "lebt",
    "leben",

    "spiele",
    "spielst",
    "spielt",
    "spielen",

    "lese",
    "liest",
    "lest",
    "lesen",

    "höre",
    "hörst",
    "hört",
    "hören",

    "lerne",
    "lernst",
    "lernt",
    "lernen",

    "mag",
    "magst",
    "mögen",

    "liebe",
    "liebst",
    "liebt",
    "lieben",

    "sehe",
    "siehst",
    "sieht",
    "sehen",

    "esse",
    "isst",
    "esst",
    "essen",

    "trinke",
    "trinkst",
    "trinkt",
    "trinken"
}


# ==========================================
# SŁOWA POWIĄZANE Z WYBRANYMI TEMATAMI
# ==========================================

PERSONALIZATION_KEYWORDS = {

    "radfahren": {
        "radfahren",
        "rad",
        "fahrrad",
        "fahre",
        "fährst",
        "fahren"
    }

}


# ==========================================
# OKREŚLENIA CZASU
# ==========================================

TIME_KEYWORDS = {
    "heute",
    "morgen",
    "morgens",
    "mittags",
    "nachmittags",
    "abends",

    "montag",
    "dienstag",
    "mittwoch",
    "donnerstag",
    "freitag",
    "samstag",
    "sonntag",

    "montags",
    "dienstags",
    "mittwochs",
    "donnerstags",
    "freitags",
    "samstags",
    "sonntags",

    "wochenende",
    "wochentags",

    "oft",
    "manchmal",
    "selten",
    "immer",

    "früh",
    "spät"
}


# ==========================================
# POBRANIE PROFILU DO PERSONALIZACJI
# ==========================================

def get_learning_profile(
    state
):

    return {
        "name": get_user_fact(
            state,
            "name"
        ),

        "origin": get_user_fact(
            state,
            "origin"
        ),

        "residence": get_user_fact(
            state,
            "residence"
        ),

        "favorite_word": get_user_fact(
            state,
            "favorite_word"
        ),

        "favorite_color": get_user_fact(
            state,
            "favorite_color"
        ),

        "hobby": get_user_fact(
            state,
            "hobby"
        ),

        "learning_goal": get_user_fact(
            state,
            "learning_goal"
        )
    }


# ==========================================
# ZAPIS AKTYWNEGO ĆWICZENIA
# ==========================================

def remember_personalized_exercise(
    state,
    exercise_type,
    topic,
    value,
    step=1
):

    state[
        "personalization_exercise"
    ] = {
        "type": exercise_type,
        "topic": topic,
        "value": value,
        "step": step
    }


# ==========================================
# WYCZYSZCZENIE AKTYWNEGO ĆWICZENIA
# ==========================================

def clear_personalized_exercise(
    state
):

    state[
        "personalization_exercise"
    ] = None


# ==========================================
# POBRANIE AKTYWNEGO ĆWICZENIA
# ==========================================

def get_personalized_exercise(
    state
):

    exercise = state.get(
        "personalization_exercise"
    )

    if not isinstance(
        exercise,
        dict
    ):
        return None

    if "step" not in exercise:
        exercise["step"] = 1

    return exercise


# ==========================================
# USTAWIENIE ETAPU ĆWICZENIA
# ==========================================

def set_personalized_exercise_step(
    state,
    step
):

    exercise = get_personalized_exercise(
        state
    )

    if not exercise:
        return False

    exercise[
        "step"
    ] = step

    return True


# ==========================================
# SPRAWDZENIE, CZY ZDANIE MA CZASOWNIK
# ==========================================

def sentence_has_verb(
    words
):

    for word in words:

        if word in BASIC_GERMAN_VERBS:
            return True

    return False


# ==========================================
# SŁOWA POWIĄZANE Z TEMATEM
# ==========================================

def get_topic_keywords(
    topic,
    value
):

    normalized_value = normalize(
        value or ""
    )

    keywords = set()

    if normalized_value:

        keywords.add(
            normalized_value
        )

        for word in normalized_value.split():

            if word:
                keywords.add(
                    word
                )

    additional_keywords = (
        PERSONALIZATION_KEYWORDS.get(
            normalized_value,
            set()
        )
    )

    keywords.update(
        additional_keywords
    )

    if topic == "favorite_color":

        keywords.add(
            normalized_value
        )

    if topic == "favorite_word":

        keywords.add(
            normalized_value
        )

    return keywords


# ==========================================
# SPRAWDZENIE ZWIĄZKU Z TEMATEM
# ==========================================

def answer_matches_topic(
    words,
    topic,
    value
):

    keywords = get_topic_keywords(
        topic,
        value
    )

    if not keywords:
        return True

    word_set = set(
        words
    )

    for keyword in keywords:

        if keyword in word_set:
            return True

        if " " in keyword:

            joined_answer = " ".join(
                words
            )

            if keyword in joined_answer:
                return True

    return False


# ==========================================
# SPRAWDZENIE ODPOWIEDZI CZASOWEJ
# ==========================================

def answer_contains_time(
    words
):

    for word in words:

        if word in TIME_KEYWORDS:
            return True

    return False


# ==========================================
# WALIDACJA PIERWSZEGO ETAPU
# ==========================================

def validate_sentence_step(
    user_message,
    topic,
    value
):

    message = normalize(
        user_message
    )

    words = message.split()

    if not words:

        return {
            "status": "retry",
            "answer": (
                "Ich habe noch keine Antwort "
                "gehört. Versuch es bitte "
                "noch einmal."
            )
        }

    if len(
        words
    ) < 3:

        return {
            "status": "retry",
            "answer": (
                "Das ist noch kein ganzer "
                "Satz. Bilde bitte einen "
                "vollständigen Satz."
            )
        }

    if not sentence_has_verb(
        words
    ):

        return {
            "status": "retry",
            "answer": (
                "Noch nicht ganz. "
                "Ich erkenne noch keinen "
                "passenden vollständigen Satz. "
                "Versuch es noch einmal."
            )
        }

    if not answer_matches_topic(
        words,
        topic,
        value
    ):

        return {
            "status": "retry",
            "answer": (
                "Der Satz ist noch nicht "
                "klar mit dem Thema verbunden. "
                "Versuch bitte einen Satz "
                f"zum Thema „{value}“."
            )
        }

    return {
        "status": "step_1_accepted",
        "answer": user_message.strip(),
        "topic": topic,
        "value": value
    }


# ==========================================
# WALIDACJA DRUGIEGO ETAPU – CZAS
# ==========================================

def validate_time_step(
    user_message,
    topic,
    value
):

    message = normalize(
        user_message
    )

    words = message.split()

    if not words:

        return {
            "status": "retry",
            "answer": (
                "Ich habe noch keine Antwort "
                "gehört. Wann machst du das?"
            )
        }

    if not answer_contains_time(
        words
    ):

        return {
            "status": "retry",
            "answer": (
                "Sag bitte, wann du das machst. "
                "Zum Beispiel: "
                "„Am Wochenende.“"
            )
        }

    return {
        "status": "step_2_accepted",
        "answer": user_message.strip(),
        "topic": topic,
        "value": value
    }


# ==========================================
# WALIDACJA ODPOWIEDZI UCZNIA
# ==========================================

def validate_personalized_answer(
    user_message,
    state
):

    exercise = get_personalized_exercise(
        state
    )

    if not exercise:
        return None

    exercise_type = exercise.get(
        "type"
    )

    topic = exercise.get(
        "topic"
    )

    value = exercise.get(
        "value"
    )

    step = exercise.get(
        "step",
        1
    )


    # ======================================
    # ĆWICZENIE ZDANIOWE
    # ======================================

    if exercise_type == "sentence":

        if step == 1:

            return validate_sentence_step(
                user_message,
                topic,
                value
            )

        if step == 2:

            return validate_time_step(
                user_message,
                topic,
                value
            )


    # ======================================
    # INNY TYP ĆWICZENIA
    # ======================================

    return {
        "status": "accepted",
        "answer": user_message.strip(),
        "topic": topic,
        "value": value
    }


# ==========================================
# PYTANIE DRUGIEGO ETAPU
# ==========================================

def get_personalized_follow_up(
    state
):

    exercise = get_personalized_exercise(
        state
    )

    if not exercise:
        return None

    topic = exercise.get(
        "topic"
    )

    value = exercise.get(
        "value"
    )


    # ======================================
    # HOBBY
    # ======================================

    if topic == "hobby":

        if normalize(
            value or ""
        ) == "radfahren":

            return (
                "Sehr gut! "
                "Wann fährst du normalerweise Rad?"
            )

        return (
            "Sehr gut! "
            "Wann machst du dein Hobby "
            "normalerweise?"
        )


    # ======================================
    # INNY TEMAT
    # ======================================

    return (
        "Sehr gut! "
        "Wann machst du das normalerweise?"
    )


# ==========================================
# PERSONALIZOWANE ĆWICZENIE
# ==========================================

def create_personalized_exercise(
    state
):

    hobby = get_user_fact(
        state,
        "hobby"
    )

    favorite_color = get_user_fact(
        state,
        "favorite_color"
    )

    favorite_word = get_user_fact(
        state,
        "favorite_word"
    )

    learning_goal = get_user_fact(
        state,
        "learning_goal"
    )


    # ======================================
    # HOBBY
    # ======================================

    if hobby:

        remember_personalized_exercise(
            state,
            "sentence",
            "hobby",
            hobby,
            step=1
        )

        return (
            f"Du hast mir erzählt, dass "
            f"dein Hobby {hobby} ist. "
            f"Bilde einen Satz über "
            f"dein Hobby."
        )


    # ======================================
    # ULUBIONY KOLOR
    # ======================================

    if favorite_color:

        remember_personalized_exercise(
            state,
            "sentence",
            "favorite_color",
            favorite_color,
            step=1
        )

        return (
            f"Deine Lieblingsfarbe ist "
            f"{favorite_color}. "
            f"Bilde einen Satz über "
            f"deine Lieblingsfarbe."
        )


    # ======================================
    # ULUBIONE SŁOWO
    # ======================================

    if favorite_word:

        remember_personalized_exercise(
            state,
            "sentence",
            "favorite_word",
            favorite_word,
            step=1
        )

        return (
            f"Dein Lieblingswort ist "
            f"„{favorite_word}“. "
            f"Bilde einen Satz mit "
            f"diesem Wort."
        )


    # ======================================
    # CEL NAUKI
    # ======================================

    if learning_goal:

        remember_personalized_exercise(
            state,
            "learning",
            "learning_goal",
            learning_goal,
            step=1
        )

        return (
            f"Dein Lernziel ist "
            f"{learning_goal}. "
            f"Lass uns dafür Deutsch üben."
        )


    # ======================================
    # BRAK DANYCH DO PERSONALIZACJI
    # ======================================

    clear_personalized_exercise(
        state
    )

    return (
        "Erzähl mir etwas über dich, "
        "damit ich die Übungen besser "
        "an dich anpassen kann."
        )
