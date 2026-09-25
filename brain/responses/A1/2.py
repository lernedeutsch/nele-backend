# ==========================================
# NELE – A1 / LEKTION 2
# Woher kommen Sie?
# Quelle: deutschsprechen/lessons/a1/lektion-2.html
# ==========================================

LESSON = {
    "level": "A1",
    "lesson": 2,
    "title": "Woher kommen Sie?"
}

# Kurze Wissensantworten, wenn der Lernende außerhalb
# des aktiven Lektionsflows nach dem Stoff fragt.
LESSON_RESPONSES = [
    {
        "patterns": ["woher kommst du", "woher kommen sie"],
        "intent": "origin_question",
        "responses": ["Ich komme aus Deutschland. Und du?"]
    },
    {
        "patterns": ["kommen konjugation", "verb kommen"],
        "intent": "kommen_conjugation",
        "responses": [
            "kommen: ich komme, du kommst, er/sie/es kommt, wir kommen, ihr kommt, sie/Sie kommen."
        ]
    },
    {
        "patterns": ["zahlen 1 bis 20", "zahlen 1-20"],
        "intent": "numbers_1_20",
        "responses": [
            "eins, zwei, drei, vier, fünf, sechs, sieben, acht, neun, zehn, elf, zwölf, dreizehn, vierzehn, fünfzehn, sechzehn, siebzehn, achtzehn, neunzehn, zwanzig."
        ]
    },
    {
        "patterns": ["schweiz aus", "aus schweiz"],
        "intent": "origin_switzerland",
        "responses": ["Man sagt: „Ich komme aus der Schweiz.“"]
    },
    {
        "patterns": ["usa aus", "aus usa"],
        "intent": "origin_usa",
        "responses": ["Man sagt: „Ich komme aus den USA.“"]
    }
]


LESSON_FLOW = {
    "sections": {
        "Woher kommen Sie?": {
            "intro": "Jetzt sprechen wir über Länder. Ich frage dich, du antwortest. Beispiel: „Woher kommst du?“ – „Ich komme aus Polen.“",
            "steps": [
                {
                    "prompt": "{name}, woher kommst du? Antworte: „Ich komme aus …“",
                    "accepted": ["Ich komme aus Polen.", "Polen", "aus Polen"],
                    "correct_answer": "Ich komme aus Polen.",
                    "error_type": "grammar",
                    "retry": "Fast. Sag den ganzen Satz: „Ich komme aus Polen.“ Sprich ihn bitte nach.",
                    "success": "Sehr gut. Jetzt fragst du mich."
                },
                {
                    "prompt": "Jetzt fragst du mich. Zu Freunden sagen wir „du“. Frag: „Woher kommst du?“",
                    "accepted": ["Woher kommst du?"],
                    "correct_answer": "Woher kommst du?",
                    "error_type": "grammar",
                    "retry": "Fast. Informell sagt man: „Woher kommst du?“ Sag es bitte noch einmal.",
                    "success": "Sehr gut."
                },
                {
                    "prompt": "Jetzt höflich mit „Sie“. Frag: „Woher kommen Sie?“",
                    "accepted": ["Woher kommen Sie?"],
                    "correct_answer": "Woher kommen Sie?",
                    "error_type": "grammar",
                    "retry": "Fast. Formell sagt man: „Woher kommen Sie?“ Sag es bitte noch einmal.",
                    "success": "Genau."
                },
                {
                    "prompt": "Jetzt antworte mit einem ganzen Satz. Land: Polen. „Ich komme …“",
                    "accepted": ["Ich komme aus Polen."],
                    "correct_answer": "Ich komme aus Polen.",
                    "error_type": "grammar",
                    "retry": "Fast. Richtig: „Ich komme aus Polen.“ Sag es bitte noch einmal.",
                    "success": "Richtig."
                },
                {
                    "prompt": "Land: die Schweiz. Sag den ganzen Satz: „Ich komme aus …“",
                    "accepted": ["Ich komme aus der Schweiz."],
                    "correct_answer": "Ich komme aus der Schweiz.",
                    "error_type": "grammar",
                    "retry": "Achtung: die Schweiz → „aus der Schweiz“. Sag: „Ich komme aus der Schweiz.“",
                    "success": "Sehr gut."
                },
                {
                    "prompt": "Land: die USA. Sag den ganzen Satz: „Ich komme aus …“",
                    "accepted": ["Ich komme aus den USA."],
                    "correct_answer": "Ich komme aus den USA.",
                    "error_type": "grammar",
                    "retry": "Achtung: die USA → „aus den USA“. Sag: „Ich komme aus den USA.“",
                    "success": "Perfekt."
                }
            ],
            "complete": "Du kannst jetzt nach der Herkunft fragen und mit „Ich komme aus …“ antworten."
        },

        "Das Verb kommen": {
            "intro": "Jetzt lernen wir „kommen“. Hör zuerst: ich komme, du kommst, er oder sie kommt, wir kommen, ihr kommt, sie kommen. Jetzt üben wir langsam.",
            "steps": [
                {
                    "prompt": "Zuerst „ich“. Ergänze: „Ich … aus Spanien.“",
                    "accepted": ["Ich komme aus Spanien."],
                    "correct_answer": "Ich komme aus Spanien.",
                    "error_type": "grammar",
                    "retry": "Bei „ich“: komm + e. Sag: „Ich komme aus Spanien.“",
                    "success": "Richtig: ich komme."
                },
                {
                    "prompt": "Jetzt „du“. Ergänze: „Du … aus Frankreich.“",
                    "accepted": ["Du kommst aus Frankreich."],
                    "correct_answer": "Du kommst aus Frankreich.",
                    "error_type": "grammar",
                    "retry": "Bei „du“: komm + st. Sag: „Du kommst aus Frankreich.“",
                    "success": "Richtig: du kommst."
                },
                {
                    "prompt": "Jetzt Anna, also „sie“. Ergänze: „Anna … aus Österreich.“",
                    "accepted": ["Anna kommt aus Österreich."],
                    "correct_answer": "Anna kommt aus Österreich.",
                    "error_type": "grammar",
                    "retry": "Bei „er/sie/es“: komm + t. Sag: „Anna kommt aus Österreich.“",
                    "success": "Richtig: sie kommt."
                },
                {
                    "prompt": "Jetzt „wir“. Ergänze: „Wir … aus der Schweiz.“",
                    "accepted": ["Wir kommen aus der Schweiz."],
                    "correct_answer": "Wir kommen aus der Schweiz.",
                    "error_type": "grammar",
                    "retry": "Bei „wir“: kommen. Sag: „Wir kommen aus der Schweiz.“",
                    "success": "Richtig: wir kommen."
                },
                {
                    "prompt": "Jetzt „ihr“. Ergänze: „Ihr … aus Italien.“",
                    "accepted": ["Ihr kommt aus Italien."],
                    "correct_answer": "Ihr kommt aus Italien.",
                    "error_type": "grammar",
                    "retry": "Bei „ihr“: komm + t. Sag: „Ihr kommt aus Italien.“",
                    "success": "Richtig: ihr kommt."
                },
                {
                    "prompt": "Zum Schluss „Sie“. Ergänze: „Sie … aus Deutschland.“",
                    "accepted": ["Sie kommen aus Deutschland."],
                    "correct_answer": "Sie kommen aus Deutschland.",
                    "error_type": "grammar",
                    "retry": "Bei „sie/Sie“: kommen. Sag: „Sie kommen aus Deutschland.“",
                    "success": "Genau. Die Endungen sind: -e, -st, -t, -en, -t, -en."
                }
            ],
            "complete": "Du kannst „kommen“ jetzt mit ich, du, er/sie/es, wir, ihr und sie/Sie benutzen."
        },

        "Zahlen 1–20": {
            "intro": "Zum Schluss üben wir die Zahlen von 1 bis 20. Du kannst sie sagen oder schreiben. Ich helfe dir, wenn du sie noch nicht kennst.",
            "steps": [
                {
                    "prompt": "Sag die Zahlen 1 bis 5 auf Deutsch. Wenn du sie noch nicht weißt, kannst du auch 1 2 3 4 5 schreiben.",
                    "accepted": ["eins, zwei, drei, vier, fünf", "eins zwei drei vier fünf", "1 2 3 4 5", "1, 2, 3, 4, 5"],
                    "correct_answer": "eins, zwei, drei, vier, fünf",
                    "error_type": "vocabulary",
                    "retry": "Hör zu: eins, zwei, drei, vier, fünf. Sag sie bitte noch einmal.",
                    "success": "Sehr gut."
                },
                {
                    "prompt": "Sehr gut. Jetzt 6 bis 10 auf Deutsch. Du kannst auch die Ziffern schreiben.",
                    "accepted": ["sechs, sieben, acht, neun, zehn", "sechs sieben acht neun zehn", "6 7 8 9 10", "6, 7, 8, 9, 10"],
                    "correct_answer": "sechs, sieben, acht, neun, zehn",
                    "error_type": "vocabulary",
                    "retry": "Hör zu: sechs, sieben, acht, neun, zehn. Sag sie bitte noch einmal.",
                    "success": "Richtig."
                },
                {
                    "prompt": "Jetzt 11 bis 15 auf Deutsch. Du kannst auch die Ziffern schreiben.",
                    "accepted": ["elf, zwölf, dreizehn, vierzehn, fünfzehn", "elf zwölf dreizehn vierzehn fünfzehn", "11 12 13 14 15", "11, 12, 13, 14, 15"],
                    "correct_answer": "elf, zwölf, dreizehn, vierzehn, fünfzehn",
                    "error_type": "vocabulary",
                    "retry": "Hör zu: elf, zwölf, dreizehn, vierzehn, fünfzehn. Sag sie bitte noch einmal.",
                    "success": "Sehr gut."
                },
                {
                    "prompt": "Und jetzt 16 bis 20 auf Deutsch. Du kannst auch die Ziffern schreiben.",
                    "accepted": ["sechzehn, siebzehn, achtzehn, neunzehn, zwanzig", "sechzehn siebzehn achtzehn neunzehn zwanzig", "16 17 18 19 20", "16, 17, 18, 19, 20"],
                    "correct_answer": "sechzehn, siebzehn, achtzehn, neunzehn, zwanzig",
                    "error_type": "vocabulary",
                    "retry": "Hör zu: sechzehn, siebzehn, achtzehn, neunzehn, zwanzig. Sag sie bitte noch einmal.",
                    "success": "Perfekt."
                }
            ],
            "complete": "Du kannst jetzt die Zahlen von 1 bis 20 sagen."
        }
    }
}


# Dialoge sind reine Lerninhalte. Die Ablauf-Logik liegt global in dialogue_engine.py.
LESSON_DIALOGUES = [
    {
        "id": "woher-kommst-du",
        "title": "Woher kommst du?",
        "section": "Woher kommen Sie?",
        "aliases": ["Herkunft", "Dialog Herkunft"],
        "intro": "Wir machen einen kurzen Dialog über Herkunft.",
        "turns": [
            {"role": "nele", "speaker": "Mia", "text": "Hallo! Woher kommst du?"},
            {
                "role": "student",
                "prompt": "Du bist dran.",
                "expected": "Ich komme aus Polen.",
                "accepted": ["Ich komme aus Polen", "aus Polen", "Polen"],
                "retry": "Fast. Antworte mit einem ganzen Satz: „Ich komme aus Polen.“"
            },
            {"role": "nele", "speaker": "Mia", "text": "Kommst du aus Polen?"},
            {
                "role": "student",
                "prompt": "Antworte Mia.",
                "expected": "Ja, ich komme aus Polen.",
                "accepted": ["Ja", "Ja, ich komme aus Polen", "Ich komme aus Polen"],
                "retry": "Du kannst sagen: „Ja, ich komme aus Polen.“"
            },
            {"role": "nele", "speaker": "Mia", "text": "Und woher kommt Anna? Anna kommt aus Österreich."},
            {
                "role": "student",
                "prompt": "Antworte mit einem ganzen Satz.",
                "expected": "Anna kommt aus Österreich.",
                "accepted": ["Anna kommt aus Österreich"],
                "retry": "Sag bitte: „Anna kommt aus Österreich.“"
            }
        ],
        "complete": "Sehr gut! Du hast den Herkunftsdialog geschafft."
    }
]
