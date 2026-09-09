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
# PODSTAWOWE CZASOWNIKI
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
# SŁOWA POWIĄZANE Z TEMATAMI
# ==========================================

PERSONALIZATION_KEYWORDS = {

    "radfahren": {
        "radfahren",
        "rad",
        "fahrrad",
        "fahre",
        "fährst",
        "fahrt",
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
# POBRANIE PROFILU
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
# WYCZYSZCZENIE ĆWICZENIA
# ==========================================

def clear_personalized_exercise(
    state
):

    state[
        "personalization_exercise"
    ] = None


# ==========================================
# POBRANIE ĆWICZENIA
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
# USTAWIENIE ETAPU
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
# CZY ZDANIE MA CZASOWNIK
# ==========================================

def sentence_has_verb(
    words
):

    for word in words:

        if word in BASIC_GERMAN_VERBS:
            return True

    return False


# ==========================================
# SŁOWA TEMATYCZNE
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
# CZY ODPOWIEDŹ PASUJE DO TEMATU
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

    joined_answer = " ".join(
        words
    )

    for keyword in keywords:

        if keyword in word_set:
            return True

        if " " in keyword:

            if keyword in joined_answer:
                return True

    return False


# ==========================================
# CZY ODPOWIEDŹ ZAWIERA CZAS
# ==========================================

def answer_contains_time(
    words
):

    for word in words:

        if word in TIME_KEYWORDS:
            return True

    return False


# ==========================================
# ETAP 1 – JAKIE MASZ HOBBY?
# ==========================================

def validate_hobby_step(
    user_message,
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
                "gehört. Was ist dein Hobby?"
            )
        }

    expected_hobby = normalize(
        value or ""
    )

    topic_keywords = get_topic_keywords(
        "hobby",
        value
    )

    word_set = set(
        words
    )

    hobby_found = False

    if expected_hobby in message:
        hobby_found = True

    if not hobby_found:

        for keyword in topic_keywords:

            if keyword in word_set:
                hobby_found = True
                break

    if not hobby_found:

        return {
            "status": "retry",
            "answer": (
                "Versuch es noch einmal. "
                "Antworte zum Beispiel: "
                "„Mein Hobby ist ...“"
            )
        }

    return {
        "status": "step_1_accepted",
        "answer": user_message.strip(),
        "topic": "hobby",
        "value": value
    }


# ==========================================
# ETAP 2 – CO LUBISZ ROBIĆ?
# ==========================================

def validate_activity_step(
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
                "gehört. Was machst du gern "
                "in deiner Freizeit?"
            )
        }

    if len(
        words
    ) < 3:

        return {
            "status": "retry",
            "answer": (
                "Antworte bitte mit einem "
                "ganzen Satz."
            )
        }

    if not sentence_has_verb(
        words
    ):

        return {
            "status": "retry",
            "answer": (
                "Noch nicht ganz. "
                "Bilde bitte einen "
                "vollständigen Satz."
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
                "Das passt noch nicht ganz "
                "zu deinem Hobby. "
                "Versuch es noch einmal."
            )
        }

    return {
        "status": "step_2_accepted",
        "answer": user_message.strip(),
        "topic": topic,
        "value": value
    }


# ==========================================
# ETAP 3 – KIEDY?
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
        "status": "step_3_accepted",
        "answer": user_message.strip(),
        "topic": topic,
        "value": value
    }


# ==========================================
# WALIDACJA ODPOWIEDZI
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
    # ROZMOWA O HOBBY
    # ======================================

    if (
        exercise_type == "conversation"
        and topic == "hobby"
    ):

        if step == 1:

            return validate_hobby_step(
                user_message,
                value
            )

        if step == 2:

            return validate_activity_step(
                user_message,
                topic,
                value
            )

        if step == 3:

            return validate_time_step(
                user_message,
                topic,
                value
            )


    # ======================================
    # STARSZY TYP ĆWICZENIA ZDANIOWEGO
    # ======================================

    if exercise_type == "sentence":

        return validate_activity_step(
            user_message,
            topic,
            value
        )


    # ======================================
    # INNY TYP
    # ======================================

    return {
        "status": "accepted",
        "answer": user_message.strip(),
        "topic": topic,
        "value": value
    }


# ==========================================
# KOLEJNE PYTANIE
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

    step = exercise.get(
        "step",
        1
    )


    # ======================================
    # HOBBY
    # ======================================

    if topic == "hobby":


        # ==================================
        # ETAP 2
        # ==================================

        if step == 2:

            return (
                "Sehr gut! "
                "Was machst du gern "
                "in deiner Freizeit?"
            )


        # ==================================
        # ETAP 3
        # ==================================

        if step == 3:

            if normalize(
                value or ""
            ) == "radfahren":

                return (
                    "Super! "
                    "Wann fährst du "
                    "normalerweise Rad?"
                )

            return (
                "Super! "
                "Wann machst du dein Hobby "
                "normalerweise?"
            )


    return None


# ==========================================
# NOWE PERSONALIZOWANE ĆWICZENIE
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
    # HOBBY – NATURALNA ROZMOWA
    # ======================================

    if hobby:

        remember_personalized_exercise(
            state,
            "conversation",
            "hobby",
            hobby,
            step=1
        )

        return (
            "Was ist dein Hobby?"
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
            "Was ist deine Lieblingsfarbe?"
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
            "Was ist dein Lieblingswort?"
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
            "Was ist dein Lernziel?"
        )


    # ======================================
    # BRAK DANYCH
    # ======================================

    clear_personalized_exercise(
        state
    )

    return (
        "Erzähl mir etwas über dich, "
        "damit ich die Übungen besser "
        "an dich anpassen kann."
        )
