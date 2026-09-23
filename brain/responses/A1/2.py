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
            "intro": "Wir üben jetzt die Herkunft. Eine Frage und eine Antwort nach der anderen.",
            "steps": [
                {
                    "prompt": "Frag mich informell: Woher …?",
                    "accepted": ["Woher kommst du?"],
                    "correct_answer": "Woher kommst du?",
                    "error_type": "grammar",
                    "retry": "Fast. Informell sagt man: „Woher kommst du?“ Sag es bitte noch einmal.",
                    "success": "Sehr gut."
                },
                {
                    "prompt": "Jetzt höflich: Frag mich mit „Sie“.",
                    "accepted": ["Woher kommen Sie?"],
                    "correct_answer": "Woher kommen Sie?",
                    "error_type": "grammar",
                    "retry": "Fast. Formell sagt man: „Woher kommen Sie?“ Sag es bitte noch einmal.",
                    "success": "Genau."
                },
                {
                    "prompt": "Antworte mit Polen: Ich …",
                    "accepted": ["Ich komme aus Polen."],
                    "correct_answer": "Ich komme aus Polen.",
                    "error_type": "grammar",
                    "retry": "Fast. Richtig: „Ich komme aus Polen.“ Sag es bitte noch einmal.",
                    "success": "Richtig."
                },
                {
                    "prompt": "Und mit der Schweiz?",
                    "accepted": ["Ich komme aus der Schweiz."],
                    "correct_answer": "Ich komme aus der Schweiz.",
                    "error_type": "grammar",
                    "retry": "Achtung: die Schweiz → „aus der Schweiz“. Sag: „Ich komme aus der Schweiz.“",
                    "success": "Sehr gut."
                },
                {
                    "prompt": "Und mit den USA?",
                    "accepted": ["Ich komme aus den USA."],
                    "correct_answer": "Ich komme aus den USA.",
                    "error_type": "grammar",
                    "retry": "Achtung: die USA → „aus den USA“. Sag: „Ich komme aus den USA.“",
                    "success": "Perfekt."
                }
            ],
            "complete": "Du kannst jetzt nach der Herkunft fragen und mit „Ich komme aus …“ antworten."
        },

        "Länder und Nationalitäten": {
            "intro": "Jetzt üben wir Länder und Nationalitäten.",
            "steps": [
                {
                    "prompt": "Eine Frau kommt aus Polen. Ergänze: „Ich bin …“",
                    "accepted": ["Ich bin Polin."],
                    "correct_answer": "Ich bin Polin.",
                    "error_type": "vocabulary",
                    "retry": "Richtig ist: „Ich bin Polin.“ Sag es bitte noch einmal.",
                    "success": "Genau."
                },
                {
                    "prompt": "Ein Mann kommt aus Polen. Ergänze: „Ich bin …“",
                    "accepted": ["Ich bin Pole."],
                    "correct_answer": "Ich bin Pole.",
                    "error_type": "vocabulary",
                    "retry": "Richtig ist: „Ich bin Pole.“ Sag es bitte noch einmal.",
                    "success": "Sehr gut."
                },
                {
                    "prompt": "Ein Mann kommt aus Deutschland. Ergänze: „Er ist …“",
                    "accepted": ["Er ist Deutscher."],
                    "correct_answer": "Er ist Deutscher.",
                    "error_type": "vocabulary",
                    "retry": "Richtig ist: „Er ist Deutscher.“ Sag es bitte noch einmal.",
                    "success": "Richtig."
                },
                {
                    "prompt": "Eine Frau kommt aus Österreich. Ergänze: „Sie ist …“",
                    "accepted": ["Sie ist Österreicherin."],
                    "correct_answer": "Sie ist Österreicherin.",
                    "error_type": "vocabulary",
                    "retry": "Richtig ist: „Sie ist Österreicherin.“ Sag es bitte noch einmal.",
                    "success": "Sehr gut. Bei Frauen endet die Nationalität oft auf „-in“."
                }
            ],
            "complete": "Du kennst jetzt wichtige Länder und Nationalitäten."
        },

        "Das Verb kommen": {
            "intro": "Jetzt üben wir das Verb „kommen“. Der Stamm ist „komm-“.",
            "steps": [
                {
                    "prompt": "Ich … aus Spanien.",
                    "accepted": ["Ich komme aus Spanien."],
                    "correct_answer": "Ich komme aus Spanien.",
                    "error_type": "grammar",
                    "retry": "Bei „ich“: komm + e. Sag: „Ich komme aus Spanien.“",
                    "success": "Richtig: ich komme."
                },
                {
                    "prompt": "Du … aus Frankreich.",
                    "accepted": ["Du kommst aus Frankreich."],
                    "correct_answer": "Du kommst aus Frankreich.",
                    "error_type": "grammar",
                    "retry": "Bei „du“: komm + st. Sag: „Du kommst aus Frankreich.“",
                    "success": "Richtig: du kommst."
                },
                {
                    "prompt": "Anna … aus Österreich.",
                    "accepted": ["Anna kommt aus Österreich."],
                    "correct_answer": "Anna kommt aus Österreich.",
                    "error_type": "grammar",
                    "retry": "Bei „er/sie/es“: komm + t. Sag: „Anna kommt aus Österreich.“",
                    "success": "Richtig: sie kommt."
                },
                {
                    "prompt": "Wir … aus der Schweiz.",
                    "accepted": ["Wir kommen aus der Schweiz."],
                    "correct_answer": "Wir kommen aus der Schweiz.",
                    "error_type": "grammar",
                    "retry": "Bei „wir“: kommen. Sag: „Wir kommen aus der Schweiz.“",
                    "success": "Richtig: wir kommen."
                },
                {
                    "prompt": "Ihr … aus Italien.",
                    "accepted": ["Ihr kommt aus Italien."],
                    "correct_answer": "Ihr kommt aus Italien.",
                    "error_type": "grammar",
                    "retry": "Bei „ihr“: komm + t. Sag: „Ihr kommt aus Italien.“",
                    "success": "Richtig: ihr kommt."
                },
                {
                    "prompt": "Sie … aus Deutschland.",
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
            "intro": "Zum Schluss üben wir die Zahlen von 1 bis 20.",
            "steps": [
                {
                    "prompt": "Sag die Zahlen 1 bis 5.",
                    "accepted": ["eins, zwei, drei, vier, fünf", "eins zwei drei vier fünf"],
                    "correct_answer": "eins, zwei, drei, vier, fünf",
                    "error_type": "vocabulary",
                    "retry": "Hör zu: eins, zwei, drei, vier, fünf. Sag sie bitte noch einmal.",
                    "success": "Sehr gut."
                },
                {
                    "prompt": "Jetzt 6 bis 10.",
                    "accepted": ["sechs, sieben, acht, neun, zehn", "sechs sieben acht neun zehn"],
                    "correct_answer": "sechs, sieben, acht, neun, zehn",
                    "error_type": "vocabulary",
                    "retry": "Hör zu: sechs, sieben, acht, neun, zehn. Sag sie bitte noch einmal.",
                    "success": "Richtig."
                },
                {
                    "prompt": "Jetzt 11 bis 15.",
                    "accepted": ["elf, zwölf, dreizehn, vierzehn, fünfzehn", "elf zwölf dreizehn vierzehn fünfzehn"],
                    "correct_answer": "elf, zwölf, dreizehn, vierzehn, fünfzehn",
                    "error_type": "vocabulary",
                    "retry": "Hör zu: elf, zwölf, dreizehn, vierzehn, fünfzehn. Sag sie bitte noch einmal.",
                    "success": "Sehr gut."
                },
                {
                    "prompt": "Und 16 bis 20.",
                    "accepted": ["sechzehn, siebzehn, achtzehn, neunzehn, zwanzig", "sechzehn siebzehn achtzehn neunzehn zwanzig"],
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
