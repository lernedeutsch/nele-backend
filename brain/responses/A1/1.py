# ==========================================
# NELE – A1 / LEKTION 1
# Begrüßung und Vorstellung
# ==========================================

LESSON = {
    "level": "A1",
    "lesson": 1,
    "title": "Begrüßung und Vorstellung"
}


# ==========================================
# POWITANIA
# ==========================================

GREETINGS = [

    {
        "patterns": [
            "hallo",
            "hi",
            "guten tag",
            "guten morgen",
            "guten abend"
        ],

        "responses": [
            "Hallo! Schön, dass du da bist.",
            "Hallo! Wie geht es dir?",
            "Guten Tag! Schön, dich zu sehen."
        ],

        "follow_up": [
            "Wie geht es dir?",
            "Wie heißt du?",
            "Was möchtest du heute üben?"
        ]
    }

]


# ==========================================
# PRZEDSTAWIANIE SIĘ
# ==========================================

INTRODUCTIONS = [

    {
        "patterns": [
            "ich heiße",
            "ich heisse",
            "mein name ist"
        ],

        "intent": "user_name",

        "responses": [
            "Freut mich, dich kennenzulernen.",
            "Schön, dich kennenzulernen.",
            "Freut mich!"
        ],

        "follow_up": [
            "Woher kommst du?",
            "Wo wohnst du?"
        ]
    },

    {
        "patterns": [
            "wie heißt du",
            "wie heisst du",
            "wie ist dein name",
            "wer bist du"
        ],

        "intent": "ask_nele_name",

        "responses": [
            "Ich heiße Nele.",
            "Mein Name ist Nele.",
            "Ich bin Nele, deine Deutschtrainerin."
        ]
    }

]


# ==========================================
# POCHODZENIE
# ==========================================

ORIGIN = [

    {
        "patterns": [
            "ich komme aus"
        ],

        "intent": "user_origin",

        "responses": [
            "Schön!",
            "Interessant!",
            "Das ist schön."
        ],

        "follow_up": [
            "Wo wohnst du jetzt?",
            "Seit wann lernst du Deutsch?"
        ]
    },

    {
        "patterns": [
            "woher kommst du"
        ],

        "intent": "ask_nele_origin",

        "responses": [
            "Ich bin Nele, deine virtuelle Deutschtrainerin."
        ],

        "follow_up": [
            "Und woher kommst du?"
        ]
    }

]


# ==========================================
# MIEJSCE ZAMIESZKANIA
# ==========================================

RESIDENCE = [

    {
        "patterns": [
            "ich wohne in",
            "ich lebe in"
        ],

        "intent": "user_residence",

        "responses": [
            "Ah, schön!",
            "Interessant.",
            "Das klingt gut."
        ],

        "follow_up": [
            "Gefällt es dir dort?",
            "Wohnst du schon lange dort?"
        ]
    },

    {
        "patterns": [
            "wo wohnst du",
            "wo lebst du"
        ],

        "intent": "ask_nele_residence",

        "responses": [
            "Ich lebe hier in deinem Deutschkurs."
        ]
    }

]


# ==========================================
# SAMOPOCZUCIE
# ==========================================

WELLBEING = [

    {
        "patterns": [
            "wie geht es dir",
            "wie geht's dir",
            "wie gehts dir"
        ],

        "intent": "ask_nele_wellbeing",

        "responses": [
            "Mir geht es gut, danke!",
            "Sehr gut, danke!"
        ],

        "follow_up": [
            "Und wie geht es dir?"
        ]
    },

    {
        "patterns": [
            "mir geht es gut",
            "mir geht's gut",
            "sehr gut",
            "gut"
        ],

        "intent": "user_wellbeing_good",

        "responses": [
            "Das freut mich!",
            "Schön zu hören!",
            "Das ist schön."
        ]
    },

    {
        "patterns": [
            "mir geht es nicht gut",
            "mir geht's nicht gut",
            "nicht gut",
            "schlecht"
        ],

        "intent": "user_wellbeing_bad",

        "responses": [
            "Das tut mir leid.",
            "Oh, das tut mir leid."
        ]
    }

]


# ==========================================
# POŻEGNANIA
# ==========================================

GOODBYES = [

    {
        "patterns": [
            "tschüss",
            "tschüs",
            "auf wiedersehen",
            "bis bald",
            "bis später",
            "bis morgen"
        ],

        "responses": [
            "Tschüss! Bis bald!",
            "Auf Wiedersehen!",
            "Bis bald! Viel Erfolg beim Deutschlernen!",
            "Bis morgen!"
        ]
    }

]


# ==========================================
# PODZIĘKOWANIA
# ==========================================

THANKS = [

    {
        "patterns": [
            "danke",
            "danke schön",
            "dankeschön",
            "vielen dank"
        ],

        "responses": [
            "Gern geschehen!",
            "Sehr gerne!",
            "Kein Problem!"
        ]
    }

]


# ==========================================
# CAŁA WIEDZA LEKCJI 1
# ==========================================

LESSON_RESPONSES = (
    GREETINGS
    + INTRODUCTIONS
    + ORIGIN
    + RESIDENCE
    + WELLBEING
    + GOODBYES
    + THANKS
)
