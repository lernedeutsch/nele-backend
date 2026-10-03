# ==========================================
# NELE – A1 / LEKTION 3
# Wie alt sind Sie?
# Quelle: deutschsprechen/lessons/a1/lektion-3.html
# ==========================================

LESSON = {
    "level": "A1",
    "lesson": 3,
    "title": "Wie alt sind Sie?",
}

LESSON_RESPONSES = [
    {
        "patterns": ["wie alt sind sie", "wie alt bist du"],
        "intent": "age_question",
        "responses": ["Zum Beispiel: „Ich bin 32 Jahre alt.“ Kurz kann man auch sagen: „Ich bin 32.“"],
    },
    {
        "patterns": ["sein konjugation", "verb sein"],
        "intent": "sein_conjugation",
        "responses": ["sein: ich bin, du bist, er/sie/es ist, wir sind, ihr seid, sie/Sie sind."],
    },
    {
        "patterns": ["zahlen 11 bis 100", "zahlen 11-100"],
        "intent": "numbers_11_100",
        "responses": ["11 elf, 12 zwölf, 20 zwanzig, 30 dreißig, 40 vierzig, 50 fünfzig, 60 sechzig, 70 siebzig, 80 achtzig, 90 neunzig, 100 hundert."],
    },
]

LESSON_FLOW = {
    "sections": {
        "Wie alt sind Sie?": {
            "intro": "Jetzt sprechen wir über das Alter. Du lernst, höflich und informell zu fragen und natürlich zu antworten.",
            "steps": [
                {
                    "prompt": "Frag höflich nach dem Alter.",
                    "accepted": ["Wie alt sind Sie?"],
                    "correct_answer": "Wie alt sind Sie?",
                    "error_type": "grammar",
                    "retry": "Formell mit „Sie“: „Wie alt sind Sie?“",
                    "success": "Richtig.",
                },
                {
                    "prompt": "Jetzt frag einen Freund nach dem Alter.",
                    "accepted": ["Wie alt bist du?"],
                    "correct_answer": "Wie alt bist du?",
                    "error_type": "grammar",
                    "retry": "Informell mit „du“: „Wie alt bist du?“",
                    "success": "Sehr gut.",
                },
                {
                    "prompt": "Du bist 32 Jahre alt. Antworte natürlich auf „Wie alt bist du?“",
                    "accepted": ["Ich bin 32 Jahre alt.", "Ich bin 32.", "32"],
                    "correct_answer": "Ich bin 32 Jahre alt.",
                    "error_type": "grammar",
                    "retry": "Du kannst sagen: „Ich bin 32 Jahre alt.“ oder kurz „Ich bin 32.“",
                    "success": "Genau.",
                },
            ],
            "complete": "Du kannst jetzt nach dem Alter fragen und dein Alter sagen.",
        },

        "Zahlen 11–100": {
            "intro": "Jetzt üben wir wichtige Zahlen von 11 bis 100 und danach zusammengesetzte Zahlen.",
            "steps": [
                {
                    "prompt": "Sag die Zahlen 11 bis 15 auf Deutsch.",
                    "accepted": ["elf, zwölf, dreizehn, vierzehn, fünfzehn", "elf zwölf dreizehn vierzehn fünfzehn"],
                    "correct_answer": "elf, zwölf, dreizehn, vierzehn, fünfzehn",
                    "error_type": "vocabulary",
                    "retry": "Hör zu: elf, zwölf, dreizehn, vierzehn, fünfzehn. Sag sie noch einmal.",
                    "success": "Sehr gut.",
                },
                {
                    "prompt": "Jetzt 16 bis 20.",
                    "accepted": ["sechzehn, siebzehn, achtzehn, neunzehn, zwanzig", "sechzehn siebzehn achtzehn neunzehn zwanzig"],
                    "correct_answer": "sechzehn, siebzehn, achtzehn, neunzehn, zwanzig",
                    "error_type": "vocabulary",
                    "retry": "Hör zu: sechzehn, siebzehn, achtzehn, neunzehn, zwanzig. Sag sie noch einmal.",
                    "success": "Richtig.",
                },
                {
                    "prompt": "Sag die Zehner 30, 40, 50, 60, 70, 80, 90 und 100 auf Deutsch.",
                    "accepted": ["dreißig, vierzig, fünfzig, sechzig, siebzig, achtzig, neunzig, hundert", "dreißig vierzig fünfzig sechzig siebzig achtzig neunzig hundert"],
                    "correct_answer": "dreißig, vierzig, fünfzig, sechzig, siebzig, achtzig, neunzig, hundert",
                    "error_type": "vocabulary",
                    "retry": "Sag: „dreißig, vierzig, fünfzig, sechzig, siebzig, achtzig, neunzig, hundert“.",
                    "success": "Sehr gut.",
                },
                {
                    "prompt": "Wie heißt die Zahl 35 auf Deutsch?",
                    "accepted": ["fünfunddreißig"],
                    "correct_answer": "fünfunddreißig",
                    "error_type": "vocabulary",
                    "retry": "5 + und + 30: „fünfunddreißig“.",
                    "success": "Genau.",
                },
                {
                    "prompt": "Und 48 auf Deutsch?",
                    "accepted": ["achtundvierzig"],
                    "correct_answer": "achtundvierzig",
                    "error_type": "vocabulary",
                    "retry": "8 + und + 40: „achtundvierzig“.",
                    "success": "Perfekt.",
                },
            ],
            "complete": "Du kannst wichtige Zahlen von 11 bis 100 bilden und sagen.",
        },

        "Das Verb sein": {
            "intro": "Jetzt üben wir „sein“. Wir beginnen mit „ich“.",
            "steps": [
                {
                    "prompt": "Ergänze: „Ich ___ 30 Jahre alt.“",
                    "accepted": ["Ich bin 30 Jahre alt.", "bin"],
                    "correct_answer": "Ich bin 30 Jahre alt.",
                    "error_type": "grammar",
                    "retry": "Bei „ich“ heißt es „bin“.",
                    "success": "Richtig: ich bin.",
                },
                {
                    "prompt": "Ergänze: „Du ___ Paul.“",
                    "accepted": ["Du bist Paul.", "bist"],
                    "correct_answer": "Du bist Paul.",
                    "error_type": "grammar",
                    "retry": "Bei „du“ heißt es „bist“.",
                    "success": "Richtig: du bist.",
                },
                {
                    "prompt": "Ergänze: „Anna ___ Lehrerin.“",
                    "accepted": ["Anna ist Lehrerin.", "ist"],
                    "correct_answer": "Anna ist Lehrerin.",
                    "error_type": "grammar",
                    "retry": "Bei „er/sie/es“ heißt es „ist“.",
                    "success": "Richtig: sie ist.",
                },
                {
                    "prompt": "Ergänze: „Wir ___ hier.“",
                    "accepted": ["Wir sind hier.", "sind"],
                    "correct_answer": "Wir sind hier.",
                    "error_type": "grammar",
                    "retry": "Bei „wir“ heißt es „sind“.",
                    "success": "Richtig: wir sind.",
                },
                {
                    "prompt": "Ergänze: „Ihr ___ hier.“",
                    "accepted": ["Ihr seid hier.", "seid"],
                    "correct_answer": "Ihr seid hier.",
                    "error_type": "grammar",
                    "retry": "Bei „ihr“ heißt es „seid“.",
                    "success": "Richtig: ihr seid.",
                },
                {
                    "prompt": "Zum Schluss höflich: Ergänze „Sie ___ hier.“",
                    "accepted": ["Sie sind hier.", "sind"],
                    "correct_answer": "Sie sind hier.",
                    "error_type": "grammar",
                    "retry": "Bei „Sie“ heißt es „sind“.",
                    "success": "Genau.",
                },
            ],
            "complete": "Du kannst „sein“ jetzt mit den wichtigsten Personalpronomen benutzen.",
        },

        "Persönliche Daten": {
            "intro": "Jetzt üben wir persönliche Daten. Wir benutzen nur Beispieldaten.",
            "steps": [
                {
                    "prompt": "Frag höflich nach dem Namen.",
                    "accepted": ["Wie ist Ihr Name?", "Wie heißen Sie?"],
                    "correct_answer": "Wie ist Ihr Name?",
                    "error_type": "grammar",
                    "retry": "Formell: „Wie ist Ihr Name?“",
                    "success": "Richtig.",
                },
                {
                    "prompt": "Antworte mit dem Beispielnamen Becker.",
                    "accepted": ["Mein Name ist Becker.", "Becker"],
                    "correct_answer": "Mein Name ist Becker.",
                    "error_type": "grammar",
                    "retry": "Sag: „Mein Name ist Becker.“",
                    "success": "Sehr gut.",
                },
                {
                    "prompt": "Frag höflich nach dem Wohnort.",
                    "accepted": ["Wo wohnen Sie?"],
                    "correct_answer": "Wo wohnen Sie?",
                    "error_type": "grammar",
                    "retry": "Formell: „Wo wohnen Sie?“",
                    "success": "Richtig.",
                },
                {
                    "prompt": "Antworte mit dem Beispiel Heidelberg.",
                    "accepted": ["Ich wohne in Heidelberg.", "Heidelberg", "in Heidelberg"],
                    "correct_answer": "Ich wohne in Heidelberg.",
                    "error_type": "grammar",
                    "retry": "Sag: „Ich wohne in Heidelberg.“",
                    "success": "Sehr gut.",
                },
                {
                    "prompt": "Wie fragst du höflich nach der Telefonnummer?",
                    "accepted": ["Wie ist Ihre Telefonnummer?"],
                    "correct_answer": "Wie ist Ihre Telefonnummer?",
                    "error_type": "grammar",
                    "retry": "Formell: „Wie ist Ihre Telefonnummer?“",
                    "success": "Genau.",
                },
            ],
            "complete": "Du kannst jetzt einfache Fragen zu persönlichen Daten stellen und beantworten.",
        },
    }
}

LESSON_DIALOGUES = [
    {
        "id": "persoenliche-daten",
        "title": "Persönliche Daten",
        "section": "Dialog – Persönliche Daten",
        "aliases": ["Dialog persönliche Daten", "Name und Alter"],
        "level": "A1",
        "lesson": 3,
        "topic": "Persönliche Daten",
        "situation": "Formelles Kennenlernen",
        "register": "formal",
        "learning_goals": ["nach dem Namen fragen", "nach dem Alter fragen", "Alter nennen"],
        "mastery_scope": "practice",
        "grammar": ["sein", "Sie"],
        "vocabulary": ["Name", "Vorname", "Alter"],
        "slots": {},
        "slot_values": {},
        "allowed_variations": [],
        "forbidden_variations": ["mix_formal_and_informal"],
        "next_allowed_topics": ["Wohnort"],
        "max_turns": 6,
        "max_variations": 0,
        "intro": "Wir machen einen kurzen formellen Dialog mit Beispieldaten.",
        "turns": [
            {"role": "nele", "speaker": "Anna", "text": "Guten Tag. Wie ist Ihr Name?", "intent": "ask_name"},
            {
                "role": "student",
                "prompt": "Antworte mit dem Beispielnamen Becker.",
                "expected_intent": "give_name",
                "expected": "Mein Name ist Becker.",
                "accepted_patterns": ["Mein Name ist Becker", "Becker"],
                "retry": "Sag: „Mein Name ist Becker.“",
            },
            {"role": "nele", "speaker": "Anna", "text": "Wie alt sind Sie?", "intent": "ask_age"},
            {
                "role": "student",
                "prompt": "Antworte mit dem Beispielalter 28.",
                "expected_intent": "give_age",
                "expected": "Ich bin 28 Jahre alt.",
                "accepted_patterns": ["Ich bin 28 Jahre alt", "Ich bin 28", "28"],
                "retry": "Du kannst sagen: „Ich bin 28 Jahre alt.“",
            },
        ],
        "complete": "Sehr gut! Du kannst Name und Alter in einem formellen Dialog angeben.",
    }
]
