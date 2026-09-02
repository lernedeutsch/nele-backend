# ==========================================
# NELE – A1 / LEKTION 1
# Guten Tag! – Begrüßung und Vorstellung
# ==========================================

LESSON = {
    "level": "A1",
    "lesson": 1,
    "title": "Guten Tag! – Begrüßung und Vorstellung"
}


# ==========================================
# 1. BEGRÜSSUNG
# ==========================================

GREETINGS = [

    {
        "patterns": [
            "guten morgen",
            "morgen"
        ],

        "intent": "greeting_morning",

        "responses": [
            "Guten Morgen!",
            "Guten Morgen! Schön, dass du da bist.",
            "Guten Morgen! Wie geht es dir?"
        ],

        "follow_up": [
            "Wie geht es dir?",
            "Wie heißt du?"
        ]
    },

    {
        "patterns": [
            "guten tag"
        ],

        "intent": "greeting_day",

        "responses": [
            "Guten Tag!",
            "Guten Tag! Schön, dich zu sehen.",
            "Guten Tag! Wie geht es dir?"
        ],

        "follow_up": [
            "Wie geht es dir?",
            "Wie heißt du?"
        ]
    },

    {
        "patterns": [
            "guten abend"
        ],

        "intent": "greeting_evening",

        "responses": [
            "Guten Abend!",
            "Guten Abend! Schön, dass du da bist.",
            "Guten Abend! Wie geht es dir?"
        ],

        "follow_up": [
            "Wie geht es dir?",
            "Wie heißt du?"
        ]
    },

    {
        "patterns": [
            "hallo",
            "hi"
        ],

        "intent": "greeting_informal",

        "responses": [
            "Hallo!",
            "Hallo! Schön, dass du da bist.",
            "Hallo! Schön, dich zu sehen."
        ],

        "follow_up": [
            "Wie geht es dir?",
            "Wie heißt du?"
        ]
    }

]


# ==========================================
# 2. ABSCHIED
# ==========================================

GOODBYES = [

    {
        "patterns": [
            "tschüss",
            "tschüs"
        ],

        "intent": "goodbye_informal",

        "responses": [
            "Tschüss!",
            "Tschüss! Bis bald!",
            "Tschüss! Viel Erfolg beim Deutschlernen!"
        ]
    },

    {
        "patterns": [
            "auf wiedersehen"
        ],

        "intent": "goodbye_formal",

        "responses": [
            "Auf Wiedersehen!",
            "Auf Wiedersehen! Bis bald!"
        ]
    }

]


# ==========================================
# 3. VORSTELLUNG – WIE HEISST DU?
# ==========================================

INTRODUCTIONS_INFORMAL = [

    {
        "patterns": [
            "wie heißt du",
            "wie heisst du"
        ],

        "intent": "ask_nele_name_informal",

        "responses": [
            "Ich heiße Nele.",
            "Mein Name ist Nele.",
            "Ich bin Nele."
        ],

        "follow_up": [
            "Und du?",
            "Wie heißt du?"
        ]
    },

    {
        "patterns": [
            "und du"
        ],

        "intent": "and_you_informal",

        "responses": [
            "Ich heiße Nele.",
            "Mein Name ist Nele.",
            "Ich bin Nele."
        ]
    }

]


# ==========================================
# 4. VORSTELLUNG – WIE HEISSEN SIE?
# ==========================================

INTRODUCTIONS_FORMAL = [

    {
        "patterns": [
            "wie heißen sie",
            "wie heissen sie"
        ],

        "intent": "ask_nele_name_formal",

        "responses": [
            "Ich heiße Nele.",
            "Mein Name ist Nele."
        ],

        "follow_up": [
            "Und Sie?",
            "Wie heißen Sie?"
        ]
    },

    {
        "patterns": [
            "und sie"
        ],

        "intent": "and_you_formal",

        "responses": [
            "Ich heiße Nele.",
            "Mein Name ist Nele."
        ]
    }

]


# ==========================================
# 5. UŻYTKOWNIK PODAJE IMIĘ
# ==========================================

USER_NAME = [

    {
        "patterns": [
            "ich heiße ",
            "ich heisse "
        ],

        "intent": "user_name_ich_heisse",

        "responses": [
            "Freut mich!",
            "Schön, dich kennenzulernen.",
            "Freut mich, dich kennenzulernen."
        ],

        "follow_up": [
            "Wie geht es dir?",
            "Möchtest du weiter üben?"
        ]
    },

    {
        "patterns": [
            "mein name ist "
        ],

        "intent": "user_name_mein_name",

        "responses": [
            "Freut mich!",
            "Schön, dich kennenzulernen.",
            "Freut mich, dich kennenzulernen."
        ],

        "follow_up": [
            "Wie geht es dir?",
            "Möchtest du weiter üben?"
        ]
    },

    {
        "patterns": [
            "ich bin "
        ],

        "intent": "user_name_ich_bin",

        "responses": [
            "Freut mich!",
            "Schön, dich kennenzulernen."
        ],

        "follow_up": [
            "Wie geht es dir?"
        ]
    }

]


# ==========================================
# 6. SAMOPOCZUCIE
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
            "gut",
            "sehr gut",
            "mir geht es gut",
            "mir geht's gut",
            "mir gehts gut"
        ],

        "intent": "user_wellbeing_good",

        "responses": [
            "Das freut mich!",
            "Sehr schön!",
            "Schön zu hören!"
        ]
    },

    {
        "patterns": [
            "nicht gut",
            "schlecht",
            "mir geht es nicht gut",
            "mir geht's nicht gut",
            "mir gehts nicht gut"
        ],

        "intent": "user_wellbeing_bad",

        "responses": [
            "Das tut mir leid.",
            "Oh, das tut mir leid."
        ]
    }

]


# ==========================================
# 7. WYJAŚNIENIA: KIEDY JAKIE POWITANIE
# ==========================================

GREETING_EXPLANATIONS = [

    {
        "patterns": [
            "wann sagt man guten morgen",
            "wann guten morgen"
        ],

        "intent": "explain_guten_morgen",

        "responses": [
            "„Guten Morgen“ sagt man morgens, ungefähr von 5 oder 6 Uhr bis 10 oder 11 Uhr."
        ]
    },

    {
        "patterns": [
            "wann sagt man guten tag",
            "wann guten tag"
        ],

        "intent": "explain_guten_tag",

        "responses": [
            "„Guten Tag“ sagt man tagsüber, ungefähr von 10 oder 11 Uhr bis 17 oder 18 Uhr."
        ]
    },

    {
        "patterns": [
            "wann sagt man guten abend",
            "wann guten abend"
        ],

        "intent": "explain_guten_abend",

        "responses": [
            "„Guten Abend“ sagt man ungefähr ab 17 oder 18 Uhr."
        ]
    },

    {
        "patterns": [
            "wann sagt man hallo",
            "wann hallo"
        ],

        "intent": "explain_hallo",

        "responses": [
            "„Hallo“ ist informell und kann zu jeder Tageszeit verwendet werden."
        ]
    },

    {
        "patterns": [
            "wann sagt man tschüss",
            "wann tschüss"
        ],

        "intent": "explain_tschuess",

        "responses": [
            "„Tschüss“ sagt man informell beim Abschied."
        ]
    },

    {
        "patterns": [
            "wann sagt man auf wiedersehen",
            "wann auf wiedersehen"
        ],

        "intent": "explain_auf_wiedersehen",

        "responses": [
            "„Auf Wiedersehen“ ist eine formelle Verabschiedung."
        ]
    }

]


# ==========================================
# 8. FORMELL / INFORMELL
# ==========================================

FORMAL_INFORMAL = [

    {
        "patterns": [
            "formell",
            "formal"
        ],

        "intent": "formal_explanation",

        "responses": [
            "Formell sagt man zum Beispiel: „Guten Tag“, „Wie heißen Sie?“ und „Auf Wiedersehen“."
        ]
    },

    {
        "patterns": [
            "informell"
        ],

        "intent": "informal_explanation",

        "responses": [
            "Informell sagt man zum Beispiel: „Hallo“, „Wie heißt du?“ und „Tschüss“."
        ]
    },

    {
        "patterns": [
            "was ist der unterschied zwischen du und sie",
            "unterschied du sie",
            "du oder sie"
        ],

        "intent": "du_sie_explanation",

        "responses": [
            "„Du“ ist informell. „Sie“ ist formell."
        ]
    }

]


# ==========================================
# 9. ALPHABET
# ==========================================

ALPHABET = {

    "a": "a",
    "b": "be",
    "c": "ce",
    "d": "de",
    "e": "e",
    "f": "ef",
    "g": "ge",
    "h": "ha",
    "i": "i",
    "j": "jot",
    "k": "ka",
    "l": "el",
    "m": "em",
    "n": "en",
    "o": "o",
    "p": "pe",
    "q": "ku",
    "r": "er",
    "s": "es",
    "t": "te",
    "u": "u",
    "v": "vau",
    "w": "we",
    "x": "ix",
    "y": "Ypsilon",
    "z": "zet",
    "ä": "ä",
    "ö": "ö",
    "ü": "ü",
    "ß": "Eszett"

}


ALPHABET_RESPONSES = [

    {
        "patterns": [
            "alphabet",
            "deutsches alphabet",
            "das deutsche alphabet"
        ],

        "intent": "alphabet_general",

        "responses": [
            "Das deutsche Alphabet hat die Buchstaben A bis Z. Dazu gibt es Ä, Ö, Ü und ß."
        ]
    },

    {
        "patterns": [
            "umlaute",
            "die umlaute"
        ],

        "intent": "umlaute",

        "responses": [
            "Die deutschen Umlaute sind Ä, Ö und Ü. Dazu gibt es das ß, das Eszett."
        ]
    },

    {
        "patterns": [
            "eszett",
            "ß"
        ],

        "intent": "eszett",

        "responses": [
            "Das Zeichen ß heißt Eszett."
        ]
    }

]


# ==========================================
# 10. MINI-DIALOGI
# ==========================================

DIALOGUES = [

    {
        "patterns": [
            "dialog informell",
            "informeller dialog"
        ],

        "intent": "dialog_informal",

        "responses": [
            "Gerne. Ich beginne: Hallo! Wie heißt du?"
        ],

        "follow_up": [
            "Wie heißt du?"
        ]
    },

    {
        "patterns": [
            "dialog formell",
            "formeller dialog"
        ],

        "intent": "dialog_formal",

        "responses": [
            "Gerne. Ich beginne: Guten Tag. Wie heißen Sie?"
        ],

        "follow_up": [
            "Wie heißen Sie?"
        ]
    }

]


# ==========================================
# 11. PODZIĘKOWANIA
# ==========================================

THANKS = [

    {
        "patterns": [
            "danke",
            "danke schön",
            "dankeschön",
            "vielen dank"
        ],

        "intent": "thanks",

        "responses": [
            "Gern geschehen!",
            "Sehr gerne!"
        ]
    }

]


# ==========================================
# CAŁA WIEDZA LEKCJI 1
# ==========================================

LESSON_RESPONSES = (
    GREETINGS
    + GOODBYES
    + INTRODUCTIONS_INFORMAL
    + INTRODUCTIONS_FORMAL
    + USER_NAME
    + WELLBEING
    + GREETING_EXPLANATIONS
    + FORMAL_INFORMAL
    + ALPHABET_RESPONSES
    + DIALOGUES
    + THANKS
)
