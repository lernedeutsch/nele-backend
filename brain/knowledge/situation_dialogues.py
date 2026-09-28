"""Reusable real-life situation dialogues for the shared Nele Dialogue Engine.

Content only: conversation control stays in brain.logic.dialogue_engine.
These scenarios deliberately accept several natural A1/A2 answers instead of
advancing on arbitrary text.
"""

SITUATION_DIALOGUES = [
    {
        "id": "a1-situation-begruessung",
        "level": "A1", "lesson": 1, "title": "Begrüßung", "topic": "Begrüßung",
        "situation": "Sich begrüßen und kurz kennenlernen", "register": "informal",
        "knowledge_status": "active", "max_turns": 8, "max_variations": 2,
        "entry_triggers": ["Guten Morgen! Wie geht es dir?", "Hallo! Wie geht es dir?"],
        "next_allowed_topics": ["Begrüßung", "Herkunft", "Arbeit"],
        "turns": [
            {"role":"nele","text":"Guten Morgen! Wie geht es dir?","intent":"ask_wellbeing"},
            {"role":"student","expected_intent":"give_wellbeing","expected":"Mir geht es gut, danke.","accepted_patterns":["Mir geht es gut, danke.","Gut, danke.","Sehr gut.","Ich bin müde.","Es geht."]},
            {"role":"nele","text":"Woher kommst du?","intent":"ask_origin"},
            {"role":"student","expected_intent":"give_origin","expected":"Ich komme aus Polen.","accepted_patterns":["Ich komme aus Polen.","Aus Polen.","Ich komme aus Deutschland.","Aus Deutschland."]},
            {"role":"nele","text":"Was machst du beruflich?","intent":"ask_job"},
            {"role":"student","expected_intent":"give_job","expected":"Ich arbeite im Hotel.","accepted_patterns":["Ich arbeite im Hotel.","Ich arbeite als Reinigungskraft.","Ich bin Studentin.","Ich bin Student.","Ich lerne Deutsch."]},
            {"role":"nele","text":"Wie lange lernst du schon Deutsch?","intent":"ask_learning_duration"},
            {"role":"student","expected_intent":"give_learning_duration","expected":"Ich lerne seit einem Jahr Deutsch.","accepted_patterns":["Ich lerne seit einem Jahr Deutsch.","Seit einem Jahr.","Seit sechs Monaten.","Seit zwei Jahren."]}
        ],
        "complete": "Sehr gut! Schön, dich kennenzulernen."
    },
    {
        "id": "a2-situation-baeckerei",
        "level": "A2", "lesson": 1, "title": "Beim Bäcker", "topic": "Bäckerei",
        "situation": "In einer Bäckerei etwas kaufen", "register": "formal",
        "knowledge_status": "active", "max_turns": 8, "max_variations": 2,
        "entry_triggers": ["Guten Morgen! Was darf es sein?", "Ich möchte ein Brötchen kaufen."],
        "next_allowed_topics": ["Bäckerei", "Einkaufen", "Bezahlen"],
        "turns": [
            {"role":"nele","text":"Guten Morgen! Was darf es sein?","intent":"ask_order"},
            {"role":"student","expected_intent":"order_food","expected":"Ich hätte gern ein Brötchen, bitte.","accepted_patterns":["Ich hätte gern ein Brötchen, bitte.","Ich möchte ein Brot, bitte.","Ein Brötchen, bitte.","Ich nehme ein Brötchen.","Haben Sie Vollkornbrot?"]},
            {"role":"nele","text":"Möchten Sie noch etwas dazu?","intent":"ask_extra"},
            {"role":"student","expected_intent":"choose_extra","expected":"Nein, danke. Das ist alles.","accepted_patterns":["Nein, danke. Das ist alles.","Nein, danke.","Ja, ein Stück Käse, bitte.","Nur Käse, bitte."]},
            {"role":"nele","text":"Das macht 3 Euro 50.","intent":"give_price"},
            {"role":"student","expected_intent":"pay","expected":"Ich zahle mit Karte.","accepted_patterns":["Ich zahle mit Karte.","Mit Karte, bitte.","Hier bitte.","Stimmt so."]},
            {"role":"nele","text":"Vielen Dank. Einen schönen Tag noch!","intent":"close_purchase"},
            {"role":"student","expected_intent":"close","expected":"Danke, Ihnen auch!","accepted_patterns":["Danke, Ihnen auch!","Danke, gleichfalls!","Auf Wiedersehen!","Tschüss!"]}
        ],
        "complete": "Sehr gut! Der Einkauf ist erledigt."
    },
    {
        "id": "a2-situation-bahnhof",
        "level": "A2", "lesson": 1, "title": "Am Bahnhof", "topic": "Bahnhof",
        "situation": "Am Bahnhof eine Verbindung und Fahrkarte erfragen", "register": "formal",
        "knowledge_status": "active", "max_turns": 8, "max_variations": 2,
        "entry_triggers": ["Ich brauche eine Fahrkarte nach Frankfurt.", "Wann fährt der nächste Zug nach Frankfurt?"],
        "next_allowed_topics": ["Bahnhof", "Reisen", "Fahrkarte"],
        "turns": [
            {"role":"nele","text":"Guten Tag! Wohin möchten Sie fahren?","intent":"ask_destination"},
            {"role":"student","expected_intent":"give_destination","expected":"Ich möchte nach Frankfurt fahren.","accepted_patterns":["Ich möchte nach Frankfurt fahren.","Nach Frankfurt, bitte.","Ich brauche eine Fahrkarte nach Frankfurt."]},
            {"role":"nele","text":"Möchten Sie nur hin oder hin und zurück?","intent":"ask_ticket_type"},
            {"role":"student","expected_intent":"give_ticket_type","expected":"Nur hin, bitte.","accepted_patterns":["Nur hin, bitte.","Nur hin.","Hin und zurück, bitte.","Hin und zurück."]},
            {"role":"nele","text":"Möchten Sie mit Karte oder bar bezahlen?","intent":"ask_payment"},
            {"role":"student","expected_intent":"give_payment","expected":"Mit Karte, bitte.","accepted_patterns":["Mit Karte, bitte.","Ich zahle mit Karte.","Bar, bitte.","Ich zahle bar."]},
            {"role":"nele","text":"Hier ist Ihre Fahrkarte. Gute Reise!","intent":"close_ticket"},
            {"role":"student","expected_intent":"close","expected":"Vielen Dank!","accepted_patterns":["Vielen Dank!","Danke!","Auf Wiedersehen!"]}
        ],
        "complete": "Sehr gut! Du hast die Situation am Bahnhof geschafft."
    },
]


def get_situation_dialogues(level=None, lesson=None):
    wanted_level = str(level or "").upper()
    result = []
    for dialogue in SITUATION_DIALOGUES:
        if wanted_level and str(dialogue.get("level") or "").upper() != wanted_level:
            continue
        if lesson is not None and dialogue.get("lesson") not in (None, lesson):
            continue
        if dialogue.get("knowledge_status", "active") == "active":
            result.append(dialogue)
    return result
