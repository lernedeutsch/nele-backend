"""Practical A1/A2 content added without replacing Nele 1's original course."""

DIALOGUES = [
    {
        "id": "bakery",
        "title": "In der Bäckerei",
        "level": "A1",
        "prompt": "Ich bin die Verkäuferin: Guten Morgen. Was möchten Sie?",
        "keywords": ["ich möchte", "bitte"],
        "model_answer": "Ich möchte zwei Brötchen, bitte.",
    },
    {
        "id": "supermarket",
        "title": "Im Supermarkt",
        "level": "A1",
        "prompt": "Ich arbeite hier. Kann ich Ihnen helfen?",
        "keywords": ["wo", "finde"],
        "model_answer": "Ja, bitte. Wo finde ich die Milch?",
    },
    {
        "id": "appointment",
        "title": "Einen Termin vereinbaren",
        "level": "A2",
        "prompt": "Praxis Berger, guten Tag. Was kann ich für Sie tun?",
        "keywords": ["termin", "möchte"],
        "model_answer": "Guten Tag. Ich möchte gern einen Termin vereinbaren.",
    },
    {
        "id": "hotel_guest",
        "title": "Gast auf dem Flur",
        "level": "A2",
        "prompt": "Entschuldigung, könnten Sie mir bitte ein zusätzliches Handtuch bringen?",
        "keywords": ["natürlich", "sofort", "bringe"],
        "model_answer": "Natürlich, sehr gerne. Ich bringe Ihnen sofort ein Handtuch.",
    },
]

LISTENING_TASKS = [
    {
        "id": "train_time",
        "title": "Am Bahnhof",
        "level": "A1",
        "text": "Der Zug nach Mannheim fährt heute um acht Uhr zwanzig von Gleis drei.",
        "question": "Um wie viel Uhr fährt der Zug?",
        "answers": ["acht uhr zwanzig", "8:20", "acht zwanzig"],
    },
    {
        "id": "shop_hours",
        "title": "Öffnungszeiten",
        "level": "A1",
        "text": "Der Laden ist von Montag bis Freitag von neun bis achtzehn Uhr geöffnet.",
        "question": "Bis wann ist der Laden geöffnet?",
        "answers": ["achtzehn uhr", "18 uhr", "18:00"],
    },
    {
        "id": "hotel_request",
        "title": "Zimmer 204",
        "level": "A2",
        "text": "Zimmer zweihundertvier braucht zwei frische Handtücher und eine Flasche Wasser.",
        "question": "Was braucht Zimmer 204?",
        "answers": ["zwei handtücher und wasser", "handtücher und wasser", "zwei frische handtücher und eine flasche wasser"],
    },
    {
        "id": "work_schedule",
        "title": "Frühschicht",
        "level": "A2",
        "text": "Morgen beginnt die Frühschicht um sieben Uhr. Bitte seien Sie zehn Minuten früher da.",
        "question": "Wann sollst du morgen da sein?",
        "answers": ["sechs uhr fünfzig", "6:50", "zehn minuten vor sieben"],
    },
]

WRITING_TASKS = [
    {
        "id": "short_message",
        "title": "Verspätung melden",
        "level": "A1",
        "prompt": "Schreib zwei kurze Sätze: Du kommst heute zehn Minuten später zur Arbeit.",
        "keywords": ["komme", "später"],
        "required": ["ich"],
        "min_words": 6,
        "min_sentences": 2,
        "model_answer": "Guten Morgen. Ich komme heute etwa zehn Minuten später. Entschuldigung.",
    },
    {
        "id": "appointment_email",
        "title": "Neuer Termin",
        "level": "A2",
        "prompt": "Schreib eine kurze Nachricht: Du möchtest einen neuen Termin am Vormittag.",
        "keywords": ["termin", "vormittag"],
        "min_words": 8,
        "model_answer": "Guten Tag. Ich möchte gern einen neuen Termin am Vormittag vereinbaren. Vielen Dank.",
    },
    {
        "id": "work_defect",
        "title": "Defekt melden",
        "level": "A2",
        "prompt": "Schreib eine kurze Meldung an die Hausdame: Im Zimmer 315 ist die Lampe kaputt.",
        "keywords": ["zimmer", "lampe", "kaputt"],
        "min_words": 7,
        "model_answer": "Im Zimmer 315 ist die Lampe kaputt. Bitte geben Sie der Technik Bescheid.",
    },
]

WORK_GERMAN = [
    {
        "id": "towel",
        "title": "Handtuch bringen",
        "level": "A1",
        "prompt": "Gast: Entschuldigung, ich brauche noch ein Handtuch.",
        "keywords": ["natürlich", "handtuch"],
        "model_answer": "Natürlich. Ich bringe Ihnen sofort ein frisches Handtuch.",
    },
    {
        "id": "shower_gel",
        "title": "Duschgel nachfüllen",
        "level": "A1",
        "prompt": "Gast: Das Duschgel ist leer.",
        "keywords": ["duschgel", "sofort"],
        "model_answer": "Oh, Entschuldigung. Ich bringe Ihnen sofort neues Duschgel.",
    },
    {
        "id": "room_later",
        "title": "Zimmer später reinigen",
        "level": "A2",
        "prompt": "Gast: Können Sie mein Zimmer bitte erst später reinigen?",
        "keywords": ["natürlich", "später"],
        "model_answer": "Natürlich. Ich komme später noch einmal. Wann passt es Ihnen?",
    },
    {
        "id": "defect",
        "title": "Defekt im Zimmer",
        "level": "A2",
        "prompt": "Gast: Die Lampe neben dem Bett funktioniert nicht.",
        "keywords": ["tut mir leid", "kümmere", "technik"],
        "model_answer": "Das tut mir leid. Ich kümmere mich sofort darum und gebe der Technik Bescheid.",
    },
    {
        "id": "unknown_answer",
        "title": "Kurz nachfragen",
        "level": "A2",
        "prompt": "Gast: Wissen Sie, ob das Restaurant heute bis 23 Uhr geöffnet ist?",
        "keywords": ["moment", "frage", "bescheid"],
        "model_answer": "Einen Moment bitte. Ich frage kurz nach und gebe Ihnen Bescheid.",
    },
]

PRONUNCIATION_TARGETS = [
    {"title": "Handtuch", "target": "Handtuch"},
    {"title": "Duschgel", "target": "Duschgel"},
    {"title": "Natürlich", "target": "Natürlich, sehr gerne."},
    {"title": "Ich kümmere mich darum", "target": "Ich kümmere mich sofort darum."},
    {"title": "Einen Moment bitte", "target": "Einen Moment bitte. Ich frage kurz nach."},
    {"title": "Termin vereinbaren", "target": "Ich möchte gern einen Termin vereinbaren."},
]

COURSE_TASKS = {
    "A1": [
        {
            "id": "a1_greeting",
            "title": "Sich vorstellen",
            "type": "speaking",
            "prompt": "Stell dich in zwei Sätzen vor: Name und Wohnort.",
            "keywords": ["ich heiße", "ich wohne"],
        },
        {
            "id": "a1_day",
            "title": "Mein Tag",
            "type": "speaking",
            "prompt": "Erzähl in zwei kurzen Sätzen, was du heute gemacht hast.",
            "keywords": ["ich"],
        },
        {
            "id": "a1_shop",
            "title": "Nach dem Preis fragen",
            "type": "dialogue",
            "prompt": "Du bist im Geschäft. Frag höflich nach dem Preis.",
            "keywords": ["wie viel", "kostet"],
        },
    ],
    "A2": [
        {
            "id": "a2_reason",
            "title": "Warum Deutsch?",
            "type": "speaking",
            "prompt": "Sag in zwei Sätzen, warum du Deutsch lernst.",
            "keywords": ["weil"],
        },
        {
            "id": "a2_problem",
            "title": "Problem bei der Arbeit",
            "type": "speaking",
            "prompt": "Beschreibe ein kleines Problem bei der Arbeit und sag, was du gemacht hast.",
            "keywords": ["habe"],
        },
        {
            "id": "a2_request",
            "title": "Kollegin um Hilfe bitten",
            "type": "dialogue",
            "prompt": "Bitte eine Kollegin höflich um Hilfe.",
            "keywords": ["könntest", "bitte"],
        },
    ],
}
