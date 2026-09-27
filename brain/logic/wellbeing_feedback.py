# ==========================================
# NELE – REAKCJA NA SAMOPOCZUCIE UCZNIA
# WELLBEING FEEDBACK
# STUDENT MEMORY 2.0
# ==========================================

from brain.logic.matcher import normalize


# ==========================================
# CZYSZCZENIE ODPOWIEDZI
# ==========================================

def clean_wellbeing_message(
    text
):

    if not text:
        return ""

    text = normalize(
        text
    )

    return text.strip(
        " .?!„“\"'"
    )


# ==========================================
# TYPOWE BŁĘDY UCZNIA
#
# corrected_message:
# poprawna wersja
#
# feedback:
# krótka poprawka Nele
#
# meaning:
# rzeczywiste samopoczucie użytkownika
# ==========================================

WELLBEING_CORRECTIONS = {

    "mir geht gut": {
        "corrected_message":
            "Mir geht es gut.",

        "feedback":
            "Fast! Richtig sagt man: "
            "„Mir geht es gut.“",

        "meaning":
            "good",

        "error_type":
            "grammar"
    },

    "ich geht gut": {
        "corrected_message":
            "Mir geht es gut.",

        "feedback":
            "Fast! Auf die Frage "
            "„Wie geht es dir?“ sagt man: "
            "„Mir geht es gut.“",

        "meaning":
            "good",

        "error_type":
            "grammar"
    },

    "ich gehe gut": {
        "corrected_message":
            "Mir geht es gut.",

        "feedback":
            "Fast! Auf die Frage "
            "„Wie geht es dir?“ sagt man: "
            "„Mir geht es gut.“",

        "meaning":
            "good",

        "error_type":
            "grammar"
    },

    "mir geht es gute": {
        "corrected_message":
            "Mir geht es gut.",

        "feedback":
            "Fast! Richtig heißt es: "
            "„Mir geht es gut.“",

        "meaning":
            "good",

        "error_type":
            "grammar"
    },

    "mir ist gut": {
        "corrected_message":
            "Mir geht es gut.",

        "feedback":
            "Fast! Natürlicher sagt man hier: "
            "„Mir geht es gut.“",

        "meaning":
            "good",

        "error_type":
            "grammar"
    },

    "ich habe gut": {
        "corrected_message":
            "Mir geht es gut.",

        "feedback":
            "Fast! Auf die Frage "
            "„Wie geht es dir?“ antwortest du: "
            "„Mir geht es gut.“",

        "meaning":
            "good",

        "error_type":
            "grammar"
    },

    "gut mir geht es": {
        "corrected_message":
            "Mir geht es gut.",

        "feedback":
            "Fast! Die richtige Wortstellung ist: "
            "„Mir geht es gut.“",

        "meaning":
            "good",

        "error_type":
            "word_order"
    },

    "es mir geht gut": {
        "corrected_message":
            "Mir geht es gut.",

        "feedback":
            "Fast! Die richtige Wortstellung ist: "
            "„Mir geht es gut.“",

        "meaning":
            "good",

        "error_type":
            "word_order"
    },

    "ich fühle gut": {
        "corrected_message":
            "Ich fühle mich gut.",

        "feedback":
            "Fast! Richtig sagt man: "
            "„Ich fühle mich gut.“",

        "meaning":
            "good",

        "error_type":
            "grammar"
    },

    "ich fühle mich gute": {
        "corrected_message":
            "Ich fühle mich gut.",

        "feedback":
            "Fast! Richtig heißt es: "
            "„Ich fühle mich gut.“",

        "meaning":
            "good",

        "error_type":
            "grammar"
    },

    "gutt": {
        "corrected_message":
            "Gut.",

        "feedback":
            "Fast! Richtig schreibt man: "
            "„gut“.",

        "meaning":
            "good",

        "error_type":
            "spelling"
    },


    "git": {
        "corrected_message":
            "Gut.",

        "feedback":
            "Fast! Richtig schreibt man: "
            "„gut“.",

        "meaning":
            "good",

        "error_type":
            "spelling"
    },

    "sehr gutt": {
        "corrected_message":
            "Sehr gut.",

        "feedback":
            "Fast! Richtig schreibt man: "
            "„sehr gut“.",

        "meaning":
            "very_good",

        "error_type":
            "spelling"
    },

    "nich schlecht": {
        "corrected_message":
            "Nicht schlecht.",

        "feedback":
            "Fast! Richtig schreibt man: "
            "„nicht schlecht“.",

        "meaning":
            "quite_good",

        "error_type":
            "spelling"
    },

    "ich bin mude": {
        "corrected_message":
            "Ich bin müde.",

        "feedback":
            "Fast! Richtig schreibt man: "
            "„Ich bin müde.“",

        "meaning":
            "tired",

        "error_type":
            "spelling"
    }
}


# ==========================================
# BARDZO DOBRZE
# ==========================================

VERY_GOOD_ANSWERS = {

    "sehr gut",
    "super",
    "prima",
    "wunderbar",
    "toll",
    "bestens",
    "ausgezeichnet",
    "fantastisch",
    "sehr gut danke",
    "sehr gut danke und dir",
    "super danke",
    "prima danke"
}


# ==========================================
# DOBRZE
# ==========================================

GOOD_ANSWERS = {

    "gut",
    "mir geht es gut",
    "mir geht's gut",
    "mir gehts gut",
    "es geht mir gut",
    "ich fühle mich gut",
    "gut danke",
    "danke gut",
    "gut danke und dir",
    "gut und dir",
    "mir geht es gut danke",
    "mir geht es gut danke und dir"
}


# ==========================================
# CAŁKIEM DOBRZE
#
# WAŻNE:
# "nicht schlecht" NIE jest złą odpowiedzią.
# ==========================================

QUITE_GOOD_ANSWERS = {

    "nicht schlecht",
    "ganz gut",
    "ziemlich gut",
    "eigentlich ganz gut",
    "recht gut",
    "ganz okay",
    "ganz ok",
    "alles gut"
}


# ==========================================
# NEUTRALNIE / TAK SOBIE
# ==========================================

NEUTRAL_ANSWERS = {

    "okay",
    "ok",
    "es geht",
    "geht so",
    "so lala",
    "na ja",
    "naja",
    "könnte besser sein",
    "es könnte besser sein",
    "mittelmäßig"
}


# ==========================================
# ŹLE
# ==========================================

BAD_ANSWERS = {

    "nicht gut",
    "nicht so gut",
    "schlecht",
    "sehr schlecht",
    "mir geht es nicht gut",
    "mir geht es nicht so gut",
    "mir geht es schlecht",
    "mir geht's nicht gut",
    "mir gehts nicht gut"
}


# ==========================================
# ZMĘCZENIE
# ==========================================

TIRED_ANSWERS = {

    "müde",
    "sehr müde",
    "ich bin müde",
    "ich bin sehr müde",
    "total müde"
}


# ==========================================
# STRES
# ==========================================

STRESSED_ANSWERS = {

    "gestresst",
    "ich bin gestresst",
    "sehr gestresst",
    "ich bin sehr gestresst",
    "ich habe stress",
    "viel stress"
}


# ==========================================
# SMUTEK
# ==========================================

SAD_ANSWERS = {

    "traurig",
    "ich bin traurig",
    "sehr traurig",
    "ich bin sehr traurig"
}


# ==========================================
# CHOROBA / ZŁE SAMOPOCZUCIE FIZYCZNE
# ==========================================

SICK_ANSWERS = {

    "krank",
    "ich bin krank",
    "ich fühle mich krank",
    "mir ist nicht gut",
    "mir geht es gesundheitlich nicht gut"
}


# ==========================================
# WSPÓLNE MODELE A1 DLA SAMOPOCZUCIA
#
# Rozpoznanie znaczenia jest wspólne dla
# Kursu i Frei sprechen. Każdy tryb może
# dobrać własną dalszą reakcję/pytanie.
# ==========================================

WELLBEING_MODEL_SENTENCES = {
    "very_good": "Mir geht es sehr gut.",
    "good": "Mir geht es gut.",
    "quite_good": "Mir geht es ganz gut.",
    "neutral": "Es geht.",
    "bad": "Mir geht es nicht so gut.",
    "tired": "Ich bin müde.",
    "stressed": "Ich bin gestresst.",
    "sad": "Ich bin traurig.",
    "sick": "Ich bin krank.",
}


def get_wellbeing_model_sentence(wellbeing_type, user_message=""):
    message = clean_wellbeing_message(user_message)
    everyday_models = {
        "prima": "Mir geht es prima.",
        "super": "Mir geht es super.",
        "sehr gut": "Mir geht es sehr gut.",
        "gut": "Mir geht es gut.",
        "ganz gut": "Mir geht es ganz gut.",
        "nicht schlecht": "Mir geht es nicht schlecht.",
        "so lala": "Mir geht es so lala.",
        "es geht": "Es geht.",
        "geht so": "Es geht so.",
        "nicht so gut": "Mir geht es nicht so gut.",
        "schlecht": "Mir geht es schlecht.",
        "sehr schlecht": "Mir geht es sehr schlecht.",
        "müde": "Ich bin müde.",
    }
    return everyday_models.get(
        message,
        WELLBEING_MODEL_SENTENCES.get(wellbeing_type),
    )


# ==========================================
# CZY UŻYTKOWNIK PYTA TEŻ:
# "UND DIR?"
# ==========================================

def asks_back_how_are_you(
    user_message
):

    message = clean_wellbeing_message(
        user_message
    )


    endings = {

        "und dir",
        "wie geht es dir",
        "und wie geht es dir"
    }


    for ending in endings:

        if message.endswith(
            ending
        ):

            return True


    return False


# ==========================================
# POPRAWKA JĘZYKOWA
# ==========================================

def get_wellbeing_correction(
    user_message
):

    message = clean_wellbeing_message(
        user_message
    )


    correction = WELLBEING_CORRECTIONS.get(
        message
    )


    if not correction:

        return None


    return {
        "original_message":
            user_message,

        "corrected_message":
            correction.get(
                "corrected_message"
            ),

        "feedback":
            correction.get(
                "feedback"
            ),

        "meaning":
            correction.get(
                "meaning"
            ),

        "error_type":
            correction.get(
                "error_type"
            )
    }


# ==========================================
# ROZPOZNANIE SAMOPOCZUCIA
# ==========================================

def detect_wellbeing_type(
    user_message
):

    message = clean_wellbeing_message(
        user_message
    )


    # ======================================
    # NAJPIERW BŁĘDY
    # ======================================

    correction = get_wellbeing_correction(
        user_message
    )


    if correction:

        return correction.get(
            "meaning"
        )


    # ======================================
    # BARDZO DOBRZE
    # ======================================

    if message in VERY_GOOD_ANSWERS:

        return "very_good"


    # ======================================
    # DOBRZE
    # ======================================

    if message in GOOD_ANSWERS:

        return "good"


    # ======================================
    # CAŁKIEM DOBRZE
    # ======================================

    if message in QUITE_GOOD_ANSWERS:

        return "quite_good"


    # ======================================
    # NEUTRALNIE
    # ======================================

    if message in NEUTRAL_ANSWERS:

        return "neutral"


    # ======================================
    # ŹLE
    # ======================================

    if message in BAD_ANSWERS:

        return "bad"


    # ======================================
    # ZMĘCZONY
    # ======================================

    if message in TIRED_ANSWERS:

        return "tired"


    # ======================================
    # STRES
    # ======================================

    if message in STRESSED_ANSWERS:

        return "stressed"


    # ======================================
    # SMUTEK
    # ======================================

    if message in SAD_ANSWERS:

        return "sad"


    # ======================================
    # CHOROBA
    # ======================================

    if message in SICK_ANSWERS:

        return "sick"


    return None


# ==========================================
# KRÓTKA REAKCJA NELE
# ==========================================

def get_wellbeing_reaction(
    wellbeing_type,
    user_message=""
):

    asks_back = asks_back_how_are_you(
        user_message
    )


    # ======================================
    # BARDZO DOBRZE
    # ======================================

    if wellbeing_type == "very_good":

        if asks_back:

            return (
                "Mir geht es gut, danke! "
                "Super, das freut mich."
            )

        return (
            "Super, das freut mich!"
        )


    # ======================================
    # DOBRZE
    # ======================================

    if wellbeing_type == "good":

        if asks_back:

            return (
                "Mir geht es gut, danke! "
                "Das freut mich."
            )

        return (
            "Das freut mich!"
        )


    # ======================================
    # CAŁKIEM DOBRZE
    # ======================================

    if wellbeing_type == "quite_good":

        if asks_back:

            return (
                "Mir geht es gut, danke! "
                "Schön zu hören."
            )

        return (
            "Schön zu hören!"
        )


    # ======================================
    # NEUTRALNIE
    # ======================================

    if wellbeing_type == "neutral":

        return (
            "Okay. Dann machen wir es "
            "heute ganz entspannt."
        )


    # ======================================
    # ŹLE
    # ======================================

    if wellbeing_type == "bad":

        return (
            "Das tut mir leid. "
            "Dann machen wir es heute "
            "lieber etwas leichter."
        )


    # ======================================
    # ZMĘCZENIE
    # ======================================

    if wellbeing_type == "tired":

        return (
            "Verstehe. Dann machen wir "
            "heute etwas Kurzes und Leichtes."
        )


    # ======================================
    # STRES
    # ======================================

    if wellbeing_type == "stressed":

        return (
            "Verstehe. Dann machen wir es "
            "heute ganz ruhig und entspannt."
        )


    # ======================================
    # SMUTEK
    # ======================================

    if wellbeing_type == "sad":

        return (
            "Das tut mir leid. "
            "Wir können heute etwas "
            "Leichtes machen."
        )


    # ======================================
    # CHOROBA
    # ======================================

    if wellbeing_type == "sick":

        return (
            "Oh, dann ruh dich gut aus. "
            "Wenn du möchtest, machen wir "
            "heute nur etwas Leichtes."
        )


    return None


# ==========================================
# PEŁNA ANALIZA ODPOWIEDZI
# ==========================================

def analyze_wellbeing_response(
    user_message
):
    """Analyze a wellbeing reply.

    Return contract: recognized, type, reaction, feedback, corrected_message,
    error_type, and model_sentence are always present. model_sentence is the
    natural A1 model for the recognized meaning, or None when unrecognized.
    """

    wellbeing_type = detect_wellbeing_type(
        user_message
    )


    if not wellbeing_type:

        return {
            "recognized":
                False,

            "type":
                None,

            "reaction":
                None,

            "feedback":
                None,

            "corrected_message":
                None,

            "error_type":
                None,

            "model_sentence":
                None
        }


    correction = get_wellbeing_correction(
        user_message
    )


    reaction = get_wellbeing_reaction(
        wellbeing_type,
        user_message
    )

    model_sentence = get_wellbeing_model_sentence(
        wellbeing_type,
        user_message
    )


    return {
        "recognized":
            True,

        "type":
            wellbeing_type,

        "reaction":
            reaction,

        "feedback":
            (
                correction.get(
                    "feedback"
                )
                if correction
                else None
            ),

        "corrected_message":
            (
                correction.get(
                    "corrected_message"
                )
                if correction
                else None
            ),

        "error_type":
            (
                correction.get(
                    "error_type"
                )
                if correction
                else None
            ),

        "model_sentence":
            model_sentence
}
