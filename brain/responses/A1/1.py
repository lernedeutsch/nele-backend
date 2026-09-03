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
# 3. VORSTELLUNG – INFORMELL
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
# 4. VORSTELLUNG – FORMELL
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
            "wie gehts dir",
            "wie geht es",
            "wie geht's",
            "wie gehts"
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
            "mir gehts gut",
            "sehr gut",
            "gut"
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
            "mir geht es nicht gut",
            "mir geht's nicht gut",
            "mir gehts nicht gut",
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
# 7. KIEDY UŻYWAMY POWITAŃ
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
# 8. DU / SIE – INFORMELL UND FORMELL
# ==========================================

DU_SIE = [

    # --------------------------------------
    # Różnica DU / SIE
    # --------------------------------------

    {
        "patterns": [
            "was ist der unterschied zwischen du und sie",
            "was ist der unterschied zwischen sie und du",
            "unterschied zwischen du und sie",
            "unterschied du sie",
            "du oder sie"
        ],

        "intent": "du_sie_difference",

        "responses": [
            "„Du“ ist informell. „Sie“ ist formell. Mit Freunden, Familie und Personen, die man gut kennt, sagt man meistens „du“. In formellen Situationen sagt man „Sie“."
        ]
    },


    # --------------------------------------
    # DU
    # --------------------------------------

    {
        "patterns": [
            "wann sagt man du",
            "wann benutzt man du",
            "wann verwende ich du"
        ],

        "intent": "when_use_du",

        "responses": [
            "„Du“ benutzt man informell, zum Beispiel mit Freunden, Familie, Kindern oder Personen, mit denen man per Du ist."
        ]
    },

    {
        "patterns": [
            "was bedeutet du"
        ],

        "intent": "meaning_du",

        "responses": [
            "„Du“ ist die informelle Anrede für eine Person."
        ]
    },


    # --------------------------------------
    # SIE
    # --------------------------------------

    {
        "patterns": [
            "wann sagt man sie",
            "wann benutzt man sie",
            "wann verwende ich sie"
        ],

        "intent": "when_use_sie",

        "responses": [
            "„Sie“ benutzt man formell, zum Beispiel bei unbekannten Erwachsenen, im beruflichen Kontakt oder in anderen formellen Situationen."
        ]
    },

    {
        "patterns": [
            "was bedeutet sie"
        ],

        "intent": "meaning_sie",

        "responses": [
            "„Sie“ mit großem S ist die formelle Anrede für eine oder mehrere Personen."
        ]
    },


    # --------------------------------------
    # WIE HEISST DU / WIE HEISSEN SIE
    # --------------------------------------

    {
        "patterns": [
            "unterschied wie heißt du und wie heißen sie",
            "unterschied zwischen wie heißt du und wie heißen sie",
            "wie heißt du oder wie heißen sie"
        ],

        "intent": "difference_name_question",

        "responses": [
            "„Wie heißt du?“ ist informell. „Wie heißen Sie?“ ist formell. Beide Fragen bedeuten, dass man nach dem Namen fragt."
        ]
    },


    # --------------------------------------
    # PRZYKŁAD INFORMALNY
    # --------------------------------------

    {
        "patterns": [
            "beispiel mit du",
            "beispiel informell",
            "informelles beispiel"
        ],

        "intent": "informal_example",

        "responses": [
            "Ein informelles Beispiel ist: „Hallo! Wie heißt du?“ – „Ich heiße Anna.“"
        ]
    },


    # --------------------------------------
    # PRZYKŁAD FORMALNY
    # --------------------------------------

    {
        "patterns": [
            "beispiel mit sie",
            "beispiel formell",
            "formelles beispiel"
        ],

        "intent": "formal_example",

        "responses": [
            "Ein formelles Beispiel ist: „Guten Tag. Wie heißen Sie?“ – „Ich heiße Thomas.“"
        ]
    },


    # --------------------------------------
    # INFORMELL
    # Ważne: jest przed FORMELL
    # --------------------------------------

    {
        "patterns": [
            "was bedeutet informell",
            "was heißt informell",
            "was heisst informell",
            "informell"
        ],

        "intent": "informal_explanation",

        "responses": [
            "Informell spricht man zum Beispiel mit Freunden oder Familie. Man sagt „du“. Beispiele sind: „Hallo“, „Wie heißt du?“ und „Tschüss“."
        ]
    },


    # --------------------------------------
    # FORMELL
    # --------------------------------------

    {
        "patterns": [
            "was bedeutet formell",
            "was heißt formell",
            "was heisst formell",
            "formell",
            "formal"
        ],

        "intent": "formal_explanation",

        "responses": [
            "Formell spricht man höflich und mit etwas mehr Distanz. Man sagt „Sie“. Beispiele sind: „Guten Tag“, „Wie heißen Sie?“ und „Auf Wiedersehen“."
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
            "das deutsche alphabet",
            "deutsches alphabet",
            "alphabet"
        ],

        "intent": "alphabet_general",

        "responses": [
            "Das deutsche Alphabet hat die Buchstaben A bis Z. Dazu gibt es Ä, Ö, Ü und ß."
        ]
    },

    {
        "patterns": [
            "die umlaute",
            "umlaute"
        ],

        "intent": "umlaute",

        "responses": [
            "Die deutschen Umlaute sind Ä, Ö und Ü. Dazu gibt es das ß, das Eszett."
        ]
    },

    {
        "patterns": [
            "was ist eszett",
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
            "informeller dialog",
            "üben wir informell"
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
            "formeller dialog",
            "üben wir formell"
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
            "vielen dank",
            "danke schön",
            "dankeschön",
            "danke"
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
    + DU_SIE
    + ALPHABET_RESPONSES
    + DIALOGUES
    + THANKS
)
