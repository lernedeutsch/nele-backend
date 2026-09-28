"""Active semantic dialogue registry.

These 20 dialogues were promoted from the user-supplied A1 lessons 11-15
after normalization and semantic validation.  They are content only; runtime
behaviour remains in the shared Dialogue Engine.
"""

ACTIVE_DIALOGUES = [
    # L11
    {
        "id": "a1-l11-geburtstag",
        "level": "A1", "lesson": 11, "title": "Geburtstag",
        "section": "Wochentage und Daten", "topic": "Geburtstag",
        "situation": "Über den Geburtstag sprechen", "register": "informal",
        "knowledge_status": "active", "max_turns": 8, "max_variations": 2,
        "slots": {"date": "14. Februar", "month": "Mai", "season": "Sommer"},
        "allowed_variations": ["change_date", "change_month", "change_season"],
        "forbidden_variations": ["combine_unrelated_topics"],
        "next_allowed_topics": ["Geburtstag", "Jahreszeiten"],
        "turns": [
            {"role":"nele","text":"Wann hast du Geburtstag?","intent":"ask_birthday"},
            {"role":"student","expected_intent":"give_birthday","expected":"Ich habe am vierzehnten Februar Geburtstag.","accepted_patterns":["Ich habe am vierzehnten Februar Geburtstag.","Am vierzehnten Februar."]},
            {"role":"nele","text":"Und du?","intent":"ask_birthday"},
            {"role":"student","expected_intent":"give_birthday","expected":"Am zweiten Mai.","accepted_patterns":["Am zweiten Mai.","Ich habe am zweiten Mai Geburtstag."]},
            {"role":"nele","text":"Welche Jahreszeit gefällt dir am besten?","intent":"ask_season"},
            {"role":"student","expected_intent":"give_season","expected":"Der Sommer.","accepted_patterns":["Der Sommer.","Mir gefällt der Sommer am besten.","Sommer."]},
            {"role":"nele","text":"Warum?","intent":"ask_reason"},
            {"role":"student","expected_intent":"give_reason","expected":"Ich mag die bunten Blätter.","accepted_patterns":["Ich mag die bunten Blätter.","Weil ich die bunten Blätter mag."]}
        ]
    },
    {
        "id": "a1-l11-wochenende",
        "level":"A1","lesson":11,"title":"Wochenende","section":"Wochentage","topic":"Wochenende",
        "situation":"Über das Wochenende sprechen","register":"informal","knowledge_status":"active",
        "max_turns":6,"max_variations":2,"slots":{"day":"Samstag"},
        "allowed_variations":["change_day"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Wochenende","Wochentage"],
        "turns":[
            {"role":"nele","text":"Was machst du am Samstag?","intent":"ask_weekend_activity"},
            {"role":"student","expected_intent":"give_weekend_activity","expected":"Am Samstag treffe ich Freunde.","accepted_patterns":["Am Samstag treffe ich Freunde.","Ich treffe am Samstag Freunde."]},
            {"role":"nele","text":"Und du?","intent":"ask_weekend_activity"},
            {"role":"student","expected_intent":"give_weekend_activity","expected":"Ich bleibe am Samstag zu Hause.","accepted_patterns":["Ich bleibe am Samstag zu Hause.","Am Samstag bleibe ich zu Hause."]},
            {"role":"nele","text":"Und was machst du am Sonntag?","intent":"ask_sunday_activity"},
            {"role":"student","expected_intent":"give_sunday_activity","expected":"Am Sonntag gehe ich spazieren.","accepted_patterns":["Am Sonntag gehe ich spazieren.","Ich gehe am Sonntag spazieren."]},
            {"role":"nele","text":"Klingt gut!","intent":"close_weekend"}
        ]
    },
    {
        "id":"a1-l11-tage-monate","level":"A1","lesson":11,"title":"Tage und Monate","section":"Wochentage und Monate",
        "topic":"Tage und Monate","situation":"Nach Tag und Urlaubsmonat fragen","register":"informal",
        "knowledge_status":"active","max_turns":8,"max_variations":2,
        "slots":{"day":"Mittwoch","next_day":"Donnerstag","month":"August"},
        "allowed_variations":["change_day","change_month"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Wochentage","Monate"],
        "turns":[
            {"role":"nele","text":"Welcher Tag ist heute?","intent":"ask_today"},
            {"role":"student","expected_intent":"give_today","expected":"Heute ist Mittwoch.","accepted_patterns":["Heute ist Mittwoch.","Mittwoch."]},
            {"role":"nele","text":"Und welcher Tag ist morgen?","intent":"ask_tomorrow"},
            {"role":"student","expected_intent":"give_tomorrow","expected":"Morgen ist Donnerstag.","accepted_patterns":["Morgen ist Donnerstag.","Donnerstag."]},
            {"role":"nele","text":"In welchem Monat hast du Urlaub?","intent":"ask_holiday_month"},
            {"role":"student","expected_intent":"give_holiday_month","expected":"Ich habe im August Urlaub.","accepted_patterns":["Ich habe im August Urlaub.","Im August."]},
            {"role":"nele","text":"Schön!","intent":"close_month"}
        ]
    },
    # L12
    {
        "id":"a1-l12-hobbys","level":"A1","lesson":12,"title":"Hobbys","section":"Hobbys und Freizeit",
        "topic":"Hobbys","situation":"Über Hobbys sprechen","register":"informal","knowledge_status":"active",
        "max_turns":8,"max_variations":2,"slots":{"sport":"Fußball","activity":"kochen"},
        "allowed_variations":["change_hobby","change_activity"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Hobbys","Freizeit"],
        "turns":[
            {"role":"nele","text":"Was machst du gern in deiner Freizeit?","intent":"ask_hobbies"},
            {"role":"student","expected_intent":"give_hobbies","expected":"Ich spiele gern Fußball und höre gern Musik.","accepted_patterns":["Ich spiele gern Fußball und höre gern Musik.","Ich höre gern Musik.","Ich spiele gern Fußball."]},
            {"role":"nele","text":"Und du?","intent":"ask_hobbies"},
            {"role":"student","expected_intent":"give_hobbies","expected":"Ich lese gern und ich koche gern.","accepted_patterns":["Ich lese gern und ich koche gern.","Ich lese gern.","Ich koche gern."]},
            {"role":"nele","text":"Kochst du oft?","intent":"ask_frequency"},
            {"role":"student","expected_intent":"give_frequency","expected":"Ja, manchmal.","accepted_patterns":["Ja, manchmal.","Manchmal.","Ja."]},
            {"role":"nele","text":"Was kochst du gern?","intent":"ask_cooking"},
            {"role":"student","expected_intent":"give_cooking","expected":"Ich koche gern neue Rezepte.","accepted_patterns":["Ich koche gern neue Rezepte.","Neue Rezepte."]}
        ]
    },
    {
        "id":"a1-l12-lieblingshobby","level":"A1","lesson":12,"title":"Lieblingshobby","section":"Hobbys und Freizeit",
        "topic":"Lieblingshobby","situation":"Über das Lieblingshobby sprechen","register":"informal","knowledge_status":"active",
        "max_turns":7,"max_variations":2,"slots":{"hobby":"Reisen"},
        "allowed_variations":["change_hobby"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Hobbys","Freizeit"],
        "turns":[
            {"role":"nele","text":"Was ist dein Lieblingshobby?","intent":"ask_favorite_hobby"},
            {"role":"student","expected_intent":"give_favorite_hobby","expected":"Am liebsten reise ich.","accepted_patterns":["Am liebsten reise ich.","Reisen.","Ich reise am liebsten."]},
            {"role":"nele","text":"Und dein Lieblingshobby?","intent":"ask_favorite_hobby"},
            {"role":"student","expected_intent":"give_favorite_hobby","expected":"Am liebsten lese ich.","accepted_patterns":["Am liebsten lese ich.","Lesen.","Ich lese am liebsten."]},
            {"role":"nele","text":"Liest du jeden Tag?","intent":"ask_frequency"},
            {"role":"student","expected_intent":"give_frequency","expected":"Nein, aber ich lese oft abends.","accepted_patterns":["Nein, aber ich lese oft abends.","Ich lese oft abends.","Nein."]}
        ]
    },
    {
        "id":"a1-l12-freizeit-samstag","level":"A1","lesson":12,"title":"Freizeit am Samstag","section":"Freizeit",
        "topic":"Freizeit","situation":"Freizeitpläne machen","register":"informal","knowledge_status":"active",
        "max_turns":7,"max_variations":2,"slots":{"day":"Samstag","activity":"joggen"},
        "allowed_variations":["change_activity","change_day"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Freizeit","Wochenende"],
        "turns":[
            {"role":"nele","text":"Was machst du gern in deiner Freizeit am Samstag?","intent":"ask_plan"},
            {"role":"student","expected_intent":"give_plan","expected":"Ich gehe gern joggen.","accepted_patterns":["Ich gehe gern joggen.","Ich jogge gern.","Joggen."]},
            {"role":"nele","text":"Und du?","intent":"ask_plan"},
            {"role":"student","expected_intent":"give_plan","expected":"Ich spiele manchmal mit Freunden Karten.","accepted_patterns":["Ich spiele manchmal mit Freunden Karten.","Ich spiele Karten mit Freunden."]},
            {"role":"nele","text":"Gehst du auch gern ins Kino?","intent":"ask_cinema"},
            {"role":"student","expected_intent":"accept_cinema","expected":"Ja, sehr gern.","accepted_patterns":["Ja, sehr gern.","Ja, gern.","Sehr gern."]},
            {"role":"nele","text":"Dann können wir am Samstag ins Kino gehen.","intent":"suggest_plan"},
            {"role":"student","expected_intent":"accept_plan","expected":"Ja, gern!","accepted_patterns":["Ja, gern!","Gern!","Ja."]}
        ]
    },
    # L13
    {
        "id":"a1-l13-sport","level":"A1","lesson":13,"title":"Sport","section":"Sport und Bewegung",
        "topic":"Sport","situation":"Über Sport sprechen","register":"informal","knowledge_status":"active",
        "max_turns":8,"max_variations":2,"slots":{"sport":"Tennis","other_sport":"Volleyball"},
        "allowed_variations":["change_sport"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Sport","Fähigkeiten"],
        "turns":[
            {"role":"nele","text":"Treibst du Sport?","intent":"ask_sport"},
            {"role":"student","expected_intent":"give_sport","expected":"Ja, ich treibe viel Sport.","accepted_patterns":["Ja, ich treibe viel Sport.","Ja.","Ich treibe viel Sport."]},
            {"role":"nele","text":"Was machst du?","intent":"ask_sport_activity"},
            {"role":"student","expected_intent":"give_sport_activity","expected":"Ich spiele Tennis und ich gehe oft schwimmen.","accepted_patterns":["Ich spiele Tennis und ich gehe oft schwimmen.","Ich spiele Tennis.","Ich gehe oft schwimmen."]},
            {"role":"nele","text":"Kannst du auch Volleyball spielen?","intent":"ask_ability"},
            {"role":"student","expected_intent":"give_ability","expected":"Ja, ein bisschen.","accepted_patterns":["Ja, ein bisschen.","Ein bisschen.","Ja."]},
            {"role":"nele","text":"Und du?","intent":"ask_ability"},
            {"role":"student","expected_intent":"give_ability","expected":"Ich kann leider nicht so gut schwimmen.","accepted_patterns":["Ich kann leider nicht so gut schwimmen.","Ich kann nicht so gut schwimmen.","Nicht so gut."]},
            {"role":"nele","text":"Das kannst du lernen!","intent":"encourage"}
        ]
    },
    {
        "id":"a1-l13-faehigkeiten","level":"A1","lesson":13,"title":"Was kannst du?","section":"Fähigkeiten",
        "topic":"Fähigkeiten","situation":"Über sportliche Fähigkeiten sprechen","register":"informal","knowledge_status":"active",
        "entry_triggers":["Kannst du schwimmen?"],
        "max_turns":8,"max_variations":2,"slots":{"sport":"Fußball","other_sport":"Tennis"},
        "allowed_variations":["change_sport"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Sport","Fähigkeiten"],
        "turns":[
            {"role":"nele","text":"Kannst du Fußball spielen?","intent":"ask_ability"},
            {"role":"student","expected_intent":"give_ability","expected":"Ja, ich kann Fußball spielen.","accepted_patterns":["Ja, ich kann Fußball spielen.","Ja.","Fußball kann ich spielen."]},
            {"role":"nele","text":"Kannst du auch Tennis spielen?","intent":"ask_ability"},
            {"role":"student","expected_intent":"give_ability","expected":"Ja, aber nicht sehr gut.","accepted_patterns":["Ja, aber nicht sehr gut.","Nicht sehr gut.","Ja."]},
            {"role":"nele","text":"Kannst du schwimmen?","intent":"ask_ability"},
            {"role":"student","expected_intent":"give_ability","expected":"Nein, leider nicht.","accepted_patterns":["Nein, leider nicht.","Nein.","Leider nicht."]},
            {"role":"nele","text":"Ich kann sehr gut schwimmen.","intent":"share_ability"},
            {"role":"student","expected_intent":"react","expected":"Dann musst du mir das zeigen!","accepted_patterns":["Dann musst du mir das zeigen!","Zeig es mir!"]}
        ]
    },
    {
        "id":"a1-l13-sport-wochenende","level":"A1","lesson":13,"title":"Sport am Wochenende","section":"Sport und Bewegung",
        "topic":"Sport am Wochenende","situation":"Sportpläne am Wochenende","register":"informal","knowledge_status":"active",
        "max_turns":7,"max_variations":2,"slots":{"day":"Samstag","activity":"schwimmen"},
        "allowed_variations":["change_activity"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Sport","Wochenende"],
        "turns":[
            {"role":"nele","text":"Welchen Sport machst du am Samstag?","intent":"ask_weekend_plan"},
            {"role":"student","expected_intent":"give_plan","expected":"Ich gehe schwimmen.","accepted_patterns":["Ich gehe schwimmen.","Ich schwimme.","Schwimmen."]},
            {"role":"nele","text":"Und du?","intent":"ask_weekend_plan"},
            {"role":"student","expected_intent":"give_plan","expected":"Ich fahre gern Rad.","accepted_patterns":["Ich fahre gern Rad.","Ich fahre gern Fahrrad.","Rad fahren."]},
            {"role":"nele","text":"Kannst du auch joggen?","intent":"ask_ability"},
            {"role":"student","expected_intent":"give_ability","expected":"Ja, ich kann gut joggen.","accepted_patterns":["Ja, ich kann gut joggen.","Ich kann gut joggen.","Ja."]},
            {"role":"nele","text":"Wollen wir zusammen Sport machen?","intent":"invite_sport"},
            {"role":"student","expected_intent":"accept_invitation","expected":"Ja, gern!","accepted_patterns":["Ja, gern!","Gern!","Ja."]}
        ]
    },
    # L14
    {
        "id":"a1-l14-musik","level":"A1","lesson":14,"title":"Musik","section":"Musik und Kultur",
        "topic":"Musik","situation":"Über Musik und Instrumente sprechen","register":"informal","knowledge_status":"active",
        "max_turns":7,"max_variations":2,"slots":{"genre":"Popmusik","instrument":"Klavier"},
        "allowed_variations":["change_genre","change_instrument"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Musik","Instrumente"],
        "turns":[
            {"role":"nele","text":"Welche Musik hörst du gern?","intent":"ask_music"},
            {"role":"student","expected_intent":"give_music","expected":"Ich höre gern Popmusik.","accepted_patterns":["Ich höre gern Popmusik.","Popmusik.","Ich mag Popmusik."]},
            {"role":"nele","text":"Und du?","intent":"ask_music"},
            {"role":"student","expected_intent":"give_music","expected":"Ich mag Klassik.","accepted_patterns":["Ich mag Klassik.","Klassik."]},
            {"role":"nele","text":"Spielst du ein Instrument?","intent":"ask_instrument"},
            {"role":"student","expected_intent":"give_instrument","expected":"Ja, ich spiele Klavier.","accepted_patterns":["Ja, ich spiele Klavier.","Ich spiele Klavier.","Klavier."]},
            {"role":"nele","text":"Ich spiele Gitarre.","intent":"share_instrument"},
            {"role":"student","expected_intent":"react","expected":"Schön!","accepted_patterns":["Schön!","Cool!","Toll!"]}
        ]
    },
    {
        "id":"a1-l14-kino","level":"A1","lesson":14,"title":"Ins Kino oder ins Theater?","section":"Einladen",
        "topic":"Kino","situation":"Eine Einladung ins Kino","register":"informal","knowledge_status":"active",
        "max_turns":6,"max_variations":2,"slots":{"time":"sieben Uhr","place":"Kino"},
        "allowed_variations":["change_time","change_place"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Einladen","Kultur"],
        "turns":[
            {"role":"nele","text":"Hast du Lust, heute Abend ins Kino zu gehen?","intent":"invite_cinema"},
            {"role":"student","expected_intent":"accept_invitation","expected":"Ja, gern!","accepted_patterns":["Ja, gern!","Sehr gern!","Ja."]},
            {"role":"nele","text":"Was läuft denn im Kino?","intent":"ask_film"},
            {"role":"student","expected_intent":"ask_or_answer_film","expected":"Ein neuer Actionfilm.","accepted_patterns":["Ein neuer Actionfilm.","Ein Actionfilm.","Actionfilm."]},
            {"role":"nele","text":"Wann gehen wir?","intent":"ask_time"},
            {"role":"student","expected_intent":"give_time","expected":"Um sieben Uhr.","accepted_patterns":["Um sieben Uhr.","Sieben Uhr."]},
            {"role":"nele","text":"Perfekt. Bis heute Abend!","intent":"close_invitation"}
        ]
    },
    {
        "id":"a1-l14-einladung","level":"A1","lesson":14,"title":"Einladung","section":"Einladen",
        "topic":"Einladung","situation":"Eine Einladung ins Museum und Konzert","register":"informal","knowledge_status":"active",
        "max_turns":7,"max_variations":2,"slots":{"place":"Museum","time":"sechs Uhr"},
        "allowed_variations":["change_place","change_time"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Einladen","Kultur"],
        "turns":[
            {"role":"nele","text":"Hast du Lust, morgen ins Museum zu gehen?","intent":"invite_museum"},
            {"role":"student","expected_intent":"accept_invitation","expected":"Ja, sehr gern!","accepted_patterns":["Ja, sehr gern!","Ja, gern!","Sehr gern!"]},
            {"role":"nele","text":"Danach können wir ins Konzert gehen.","intent":"suggest_concert"},
            {"role":"student","expected_intent":"accept_suggestion","expected":"Gute Idee!","accepted_patterns":["Gute Idee!","Ja, gern!","Klar!"]},
            {"role":"nele","text":"Um wie viel Uhr treffen wir uns?","intent":"ask_time"},
            {"role":"student","expected_intent":"give_time","expected":"Um sechs Uhr.","accepted_patterns":["Um sechs Uhr.","Sechs Uhr."]},
            {"role":"nele","text":"Ja, das passt.","intent":"confirm_plan"}
        ]
    },
    {
        "id":"a1-l14-keine-zeit","level":"A1","lesson":14,"title":"Keine Zeit","section":"Einladen",
        "topic":"Absagen","situation":"Eine Einladung ablehnen und einen neuen Termin vorschlagen","register":"informal","knowledge_status":"active",
        "max_turns":7,"max_variations":2,"slots":{"place":"Theater","day":"morgen"},
        "allowed_variations":["change_place","change_day"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Einladen","Freizeit"],
        "turns":[
            {"role":"nele","text":"Möchtest du heute mit mir ins Theater gehen?","intent":"invite_theater"},
            {"role":"student","expected_intent":"decline_invitation","expected":"Heute leider nicht. Ich muss arbeiten.","accepted_patterns":["Heute leider nicht. Ich muss arbeiten.","Leider nicht, ich muss arbeiten.","Ich muss arbeiten."]},
            {"role":"nele","text":"Schade. Hast du morgen Zeit?","intent":"ask_availability"},
            {"role":"student","expected_intent":"give_availability","expected":"Ja, morgen habe ich Zeit.","accepted_patterns":["Ja, morgen habe ich Zeit.","Ja, morgen.","Morgen habe ich Zeit."]},
            {"role":"nele","text":"Dann gehen wir morgen ins Theater.","intent":"suggest_new_plan"},
            {"role":"student","expected_intent":"accept_plan","expected":"Ja, gern!","accepted_patterns":["Ja, gern!","Gern!","Ja."]}
        ]
    },
    # L15
    {
        "id":"a1-l15-verkehrsmittel","level":"A1","lesson":15,"title":"Verkehrsmittel","section":"Reisen",
        "topic":"Verkehrsmittel","situation":"Über Verkehrsmittel sprechen","register":"informal","knowledge_status":"active",
        "max_turns":7,"max_variations":2,"slots":{"destination":"Berlin","transport":"Zug"},
        "allowed_variations":["change_destination","change_transport"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Reisen","Verkehrsmittel"],
        "turns":[
            {"role":"nele","text":"Wie fährst du nach Berlin?","intent":"ask_transport"},
            {"role":"student","expected_intent":"give_transport","expected":"Ich fahre mit dem Zug.","accepted_patterns":["Ich fahre mit dem Zug.","Mit dem Zug.","Zug."]},
            {"role":"nele","text":"Fährst du gern mit dem Zug?","intent":"ask_preference"},
            {"role":"student","expected_intent":"give_preference","expected":"Ja, sehr gern.","accepted_patterns":["Ja, sehr gern.","Ja, gern.","Sehr gern."]},
            {"role":"nele","text":"Und du?","intent":"ask_transport_preference"},
            {"role":"student","expected_intent":"give_transport_preference","expected":"Ich fahre lieber mit dem Auto.","accepted_patterns":["Ich fahre lieber mit dem Auto.","Lieber mit dem Auto.","Mit dem Auto."]},
            {"role":"nele","text":"Fliegst du auch manchmal?","intent":"ask_flying"},
            {"role":"student","expected_intent":"give_flying_frequency","expected":"Ja, manchmal fliege ich mit dem Flugzeug.","accepted_patterns":["Ja, manchmal fliege ich mit dem Flugzeug.","Manchmal.","Ja, manchmal."]}
        ]
    },
    {
        "id":"a1-l15-wohin","level":"A1","lesson":15,"title":"Wohin fährst du?","section":"Reisen","topic":"Reiseziele",
        "situation":"Über Reiseziele sprechen","register":"informal","knowledge_status":"active",
        "max_turns":7,"max_variations":2,"slots":{"city":"Berlin","country":"Polen","country_with_article":"die Schweiz"},
        "allowed_variations":["change_city","change_country"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Reisen","Reiseziele"],
        "turns":[
            {"role":"nele","text":"Wohin fährst du am Wochenende?","intent":"ask_destination"},
            {"role":"student","expected_intent":"give_destination","expected":"Ich fahre nach Berlin.","accepted_patterns":["Ich fahre nach Berlin.","Nach Berlin.","Berlin."]},
            {"role":"nele","text":"Und danach?","intent":"ask_next_destination"},
            {"role":"student","expected_intent":"give_destination","expected":"Danach fahre ich nach Polen.","accepted_patterns":["Danach fahre ich nach Polen.","Ich fahre nach Polen.","Nach Polen."]},
            {"role":"nele","text":"Fährst du auch in die Schweiz?","intent":"ask_destination"},
            {"role":"student","expected_intent":"give_destination","expected":"Ja, im Sommer.","accepted_patterns":["Ja, im Sommer.","Ja.","Im Sommer."]},
            {"role":"nele","text":"Schön!","intent":"close_travel"}
        ]
    },
    {
        "id":"a1-l15-weg-bahnhof","level":"A1","lesson":15,"title":"Nach dem Weg fragen","section":"Nach dem Weg fragen",
        "topic":"Wegbeschreibung","situation":"Nach dem Weg zum Bahnhof fragen","register":"formal",
        "knowledge_status":"active","max_turns":8,"max_variations":2,
        "slots":{"destination":"Bahnhof","distance":"300 Meter"},
        "allowed_variations":["change_destination","change_distance"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Wegbeschreibung","Stadt"],
        "turns":[
            {"role":"nele","text":"Entschuldigung, wo ist der Bahnhof?","intent":"ask_location"},
            {"role":"student","expected_intent":"give_location","expected":"Der Bahnhof ist nicht weit.","accepted_patterns":["Der Bahnhof ist nicht weit.","Nicht weit."]},
            {"role":"nele","text":"Wie komme ich zum Bahnhof?","intent":"ask_directions"},
            {"role":"student","expected_intent":"give_directions","expected":"Gehen Sie geradeaus und dann links.","accepted_patterns":["Gehen Sie geradeaus und dann links.","Geradeaus und dann links."]},
            {"role":"nele","text":"Wie weit ist es?","intent":"ask_distance"},
            {"role":"student","expected_intent":"give_distance","expected":"Ungefähr 300 Meter.","accepted_patterns":["Ungefähr 300 Meter.","Etwa 300 Meter.","300 Meter."]},
            {"role":"nele","text":"Vielen Dank!","intent":"thank"},
            {"role":"student","expected_intent":"respond_thanks","expected":"Gern geschehen.","accepted_patterns":["Gern geschehen.","Gerne.","Bitte schön."]}
        ]
    },
    {
        "id":"a1-l15-weg-museum","level":"A1","lesson":15,"title":"Zum Museum","section":"Nach dem Weg fragen",
        "topic":"Wegbeschreibung","situation":"Nach dem Weg zum Museum fragen","register":"formal",
        "knowledge_status":"active","max_turns":8,"max_variations":2,
        "slots":{"destination":"Museum","landmark":"Café"},
        "allowed_variations":["change_destination","change_landmark"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Wegbeschreibung","Stadt"],
        "turns":[
            {"role":"nele","text":"Entschuldigung, wie komme ich zum Museum?","intent":"ask_directions"},
            {"role":"student","expected_intent":"give_directions","expected":"Gehen Sie geradeaus, dann rechts.","accepted_patterns":["Gehen Sie geradeaus, dann rechts.","Geradeaus, dann rechts."]},
            {"role":"nele","text":"Ist das Museum weit?","intent":"ask_distance"},
            {"role":"student","expected_intent":"give_distance","expected":"Nein, es ist nicht weit.","accepted_patterns":["Nein, es ist nicht weit.","Nicht weit.","Nein."]},
            {"role":"nele","text":"Ist es neben dem Café?","intent":"ask_landmark"},
            {"role":"student","expected_intent":"confirm_landmark","expected":"Ja, genau. Das Museum ist auf der rechten Seite.","accepted_patterns":["Ja, genau. Das Museum ist auf der rechten Seite.","Ja, genau.","Ja, neben dem Café."]},
            {"role":"nele","text":"Danke schön!","intent":"thank"},
            {"role":"student","expected_intent":"respond_thanks","expected":"Bitte schön!","accepted_patterns":["Bitte schön!","Gern geschehen.","Gerne."]}
        ]
    },
    {
        "id":"a1-l15-schweiz","level":"A1","lesson":15,"title":"Reise in die Schweiz","section":"Reisen",
        "topic":"Reise in die Schweiz","situation":"Nach einer Zugverbindung fragen","register":"formal",
        "knowledge_status":"active","max_turns":8,"max_variations":2,
        "slots":{"country":"die Schweiz","city":"Zürich","time":"14 Uhr"},
        "allowed_variations":["change_city","change_time"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Reisen","Zug"],
        "turns":[
            {"role":"nele","text":"Wie fahre ich am besten in die Schweiz?","intent":"ask_travel_method"},
            {"role":"student","expected_intent":"suggest_transport","expected":"Sie können mit dem Zug fahren.","accepted_patterns":["Sie können mit dem Zug fahren.","Mit dem Zug.","Sie können mit dem Zug reisen."]},
            {"role":"nele","text":"Ist der Zug direkt?","intent":"ask_direct_train"},
            {"role":"student","expected_intent":"confirm_direct_train","expected":"Ja, es gibt einen direkten Zug nach Zürich.","accepted_patterns":["Ja, es gibt einen direkten Zug nach Zürich.","Ja, direkt nach Zürich.","Ja."]},
            {"role":"nele","text":"Wann fährt der Zug?","intent":"ask_train_time"},
            {"role":"student","expected_intent":"give_train_time","expected":"Er fährt um 14 Uhr.","accepted_patterns":["Er fährt um 14 Uhr.","Um 14 Uhr.","14 Uhr."]},
            {"role":"nele","text":"Perfekt. Vielen Dank!","intent":"thank"},
            {"role":"student","expected_intent":"respond_thanks","expected":"Gern geschehen.","accepted_patterns":["Gern geschehen.","Gerne.","Bitte schön."]}
        ]
    },
    {
        "id":"a1-l15-zug-flugzeug","level":"A1","lesson":15,"title":"Zug oder Flugzeug?","section":"Reisen",
        "topic":"Reisearten","situation":"Über bevorzugte Verkehrsmittel sprechen","register":"informal",
        "knowledge_status":"active","max_turns":7,"max_variations":2,"slots":{"transport":"Zug","other_transport":"Flugzeug"},
        "allowed_variations":["change_transport"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Reisen","Verkehrsmittel"],
        "turns":[
            {"role":"nele","text":"Wie reist du gern?","intent":"ask_travel_preference"},
            {"role":"student","expected_intent":"give_travel_preference","expected":"Ich reise gern mit dem Zug.","accepted_patterns":["Ich reise gern mit dem Zug.","Mit dem Zug.","Ich fahre gern mit dem Zug."]},
            {"role":"nele","text":"Warum?","intent":"ask_reason"},
            {"role":"student","expected_intent":"give_reason","expected":"Der Zug ist bequem.","accepted_patterns":["Der Zug ist bequem.","Weil der Zug bequem ist.","Bequem."]},
            {"role":"nele","text":"Ich fliege lieber mit dem Flugzeug.","intent":"share_preference"},
            {"role":"student","expected_intent":"ask_destination_preference","expected":"Wohin fliegst du gern?","accepted_patterns":["Wohin fliegst du gern?","Wohin fliegst du?"]},
            {"role":"nele","text":"Ich fliege gern nach Deutschland und in die Schweiz.","intent":"give_destination_preference"}
        ]
    },
    {
        "id":"a1-l15-bahnhof","level":"A1","lesson":15,"title":"Am Bahnhof","section":"Nach dem Weg fragen",
        "topic":"Bahnhof","situation":"Am Bahnhof nach dem Zug fragen","register":"formal",
        "knowledge_status":"active","max_turns":7,"max_variations":2,"slots":{"city":"Zürich","time":"14 Uhr"},
        "allowed_variations":["change_city","change_time"],"forbidden_variations":["combine_unrelated_topics"],
        "next_allowed_topics":["Bahnhof","Reisen"],
        "turns":[
            {"role":"nele","text":"Entschuldigung, wo ist der Bahnhof?","intent":"ask_location"},
            {"role":"student","expected_intent":"give_location","expected":"Gehen Sie geradeaus.","accepted_patterns":["Gehen Sie geradeaus.","Geradeaus."]},
            {"role":"nele","text":"Ist der Bahnhof weit?","intent":"ask_distance"},
            {"role":"student","expected_intent":"give_distance","expected":"Nein, er ist gleich da.","accepted_patterns":["Nein, er ist gleich da.","Gleich da.","Nein."]},
            {"role":"nele","text":"Fährt von hier ein Zug nach Zürich?","intent":"ask_train"},
            {"role":"student","expected_intent":"confirm_train","expected":"Ja. Der Zug fährt um 14 Uhr.","accepted_patterns":["Ja. Der Zug fährt um 14 Uhr.","Ja, um 14 Uhr.","Ja."]},
            {"role":"nele","text":"Vielen Dank!","intent":"thank"},
            {"role":"student","expected_intent":"respond_thanks","expected":"Bitte schön. Gute Reise!","accepted_patterns":["Bitte schön. Gute Reise!","Bitte schön.","Gute Reise!"]}
        ]
    }
,
    {
        "id":"a1-daily-post","level":"A1","lesson":16,"title":"Bei der Post","section":"Alltag",
        "topic":"Post","situation":"Bei der Post einen Brief verschicken","register":"formal",
        "knowledge_status":"active","max_turns":6,"max_variations":2,
        "slots":{"destination":"Polen"},"allowed_variations":["change_destination"],
        "forbidden_variations":["combine_unrelated_topics"],"next_allowed_topics":["Post","Einkaufen"],
        "entry_triggers":["Ich möchte einen Brief nach Polen schicken.","Was kostet ein Brief nach Polen?"],
        "turns":[
            {"role":"nele","text":"Guten Tag. Was möchten Sie?","intent":"ask_need"},
            {"role":"student","expected_intent":"give_need","expected":"Ich möchte einen Brief nach Polen schicken.","accepted_patterns":["Ich möchte einen Brief nach Polen schicken.","Einen Brief nach Polen, bitte.","Ich möchte einen Brief schicken."]},
            {"role":"nele","text":"Normal oder schnell?","intent":"ask_shipping"},
            {"role":"student","expected_intent":"choose_shipping","expected":"Normal, bitte.","accepted_patterns":["Normal, bitte.","Normal.","Ganz normal, bitte."]},
            {"role":"nele","text":"Gut. Sonst noch etwas?","intent":"ask_more"},
            {"role":"student","expected_intent":"finish","expected":"Nein, danke.","accepted_patterns":["Nein, danke.","Das ist alles, danke.","Nein."]}
        ]
    },
    {
        "id":"a1-daily-bus-ticket","level":"A1","lesson":16,"title":"Im Bus","section":"Unterwegs",
        "topic":"Bus","situation":"Im Bus nach einer Fahrkarte fragen","register":"formal",
        "knowledge_status":"active","max_turns":6,"max_variations":2,
        "slots":{"destination":"Bahnhof"},"allowed_variations":["change_destination"],
        "forbidden_variations":["combine_unrelated_topics"],"next_allowed_topics":["Bus","Verkehrsmittel"],
        "entry_triggers":["Fährt dieser Bus zum Bahnhof?","Eine Fahrkarte zum Bahnhof, bitte."],
        "turns":[
            {"role":"nele","text":"Guten Tag. Wohin möchten Sie?","intent":"ask_destination"},
            {"role":"student","expected_intent":"give_destination","expected":"Zum Bahnhof, bitte.","accepted_patterns":["Zum Bahnhof, bitte.","Zum Bahnhof.","Ich möchte zum Bahnhof."]},
            {"role":"nele","text":"Einfach oder hin und zurück?","intent":"ask_ticket_type"},
            {"role":"student","expected_intent":"choose_ticket","expected":"Einfach, bitte.","accepted_patterns":["Einfach, bitte.","Nur einfach.","Einfach."]},
            {"role":"nele","text":"Gut. Möchten Sie mit Karte zahlen?","intent":"ask_payment"},
            {"role":"student","expected_intent":"choose_payment","expected":"Ja, bitte.","accepted_patterns":["Ja, bitte.","Ja.","Nein, bar bitte."]}
        ]
    },
    {
        "id":"a2-daily-nachbar-paket","level":"A2","lesson":16,"title":"Paket beim Nachbarn","section":"Alltag",
        "topic":"Paket","situation":"Mit einem Nachbarn über ein angenommenes Paket sprechen","register":"informal",
        "knowledge_status":"active","max_turns":6,"max_variations":2,
        "slots":{"time":"gestern"},"allowed_variations":["change_time"],
        "forbidden_variations":["combine_unrelated_topics"],"next_allowed_topics":["Paket","Nachbarn"],
        "entry_triggers":["Hast du mein Paket angenommen?","Ist mein Paket bei dir?"],
        "turns":[
            {"role":"nele","text":"Hallo! Ich habe gestern ein Paket für dich angenommen.","intent":"inform_package"},
            {"role":"student","expected_intent":"thank_package","expected":"Danke! Ist es bei dir?","accepted_patterns":["Danke! Ist es bei dir?","Super, danke!","Danke dir!"]},
            {"role":"nele","text":"Ja. Möchtest du es jetzt holen?","intent":"ask_pickup"},
            {"role":"student","expected_intent":"arrange_pickup","expected":"Ja, ich komme gleich.","accepted_patterns":["Ja, ich komme gleich.","Gern, ich komme jetzt.","Ja, gern."]},
            {"role":"nele","text":"Okay, bis gleich!","intent":"close_package"}
        ]
    }
]


def get_active_dialogues(level=None, lesson=None):
    level = str(level or "").upper()
    result = []
    for dialogue in ACTIVE_DIALOGUES:
        if not isinstance(dialogue, dict):
            continue
        if level and str(dialogue.get("level") or "").upper() != level:
            continue
        if lesson is not None and dialogue.get("lesson") not in (None, lesson):
            continue
        if dialogue.get("knowledge_status", "active") != "active":
            continue
        result.append(dialogue)
    return result
