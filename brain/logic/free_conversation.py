"""Natural adaptive free conversation for Nele.

The free mode follows the learner's last answer instead of running a quiz.
It keeps short conversational memory, avoids repeated questions, recasts only
clear A1 errors, and records recurring errors in shared learner state.
"""
import re

OPENERS = [
    "Hallo! Wie geht's dir heute?",
    "Hallo! Wie war dein Tag?",
    "Schön, dass du da bist. Was machst du gerade?",
    "Hallo! Was machst du heute?",
]

# Course level controls what free conversation may actively introduce.
# New lessons can be added here without creating a separate free mode.
LEVEL_ORDER = ["A1.1", "A1.2", "A1.3", "A1.4", "A2.1", "A2.2", "B1.1"]
LEVEL_SKILLS = {
    "A1.1": {"today", "place", "work", "shopping", "hobby", "weather", "holiday"},
    "A1.2": {"yesterday"},
}

FALLBACKS = {
    "today": ["Was machst du heute?", "Was möchtest du heute noch machen?", "Wie ist dein Tag heute?"],
    "work": ["Arbeitest du heute?", "Wann fängst du an?", "Was machst du bei der Arbeit?"],
    "hobby": ["Was machst du gern in deiner Freizeit?", "Hörst du gern Musik?", "Machst du gern Sport?"],
    "weather": ["Wie ist das Wetter bei dir?", "Ist es warm oder kalt?", "Magst du das Wetter heute?"],
    "holiday": ["Wo machst du gern Urlaub?", "Meer oder Berge – was magst du lieber?", "Was machst du gern im Urlaub?"],
    "yesterday": ["Was hast du gestern gemacht?", "Wie war dein Tag gestern?"],
}

YES = {"ja", "ja ja", "ja gern", "ja, gern", "klar", "genau"}
NO = {"nein", "nein nein", "nein danke", "nein, danke"}
NORMAL_SHORT = YES | NO | {
    "gut", "sehr gut", "prima", "super", "okay", "ok", "gern",
    "müde", "arbeit", "zu hause", "zuhause",
}

def _words(text):
    return re.findall(r"[A-Za-zÄÖÜäöüß]+", str(text or ""))

def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower())

def _difficulty_signal(text):
    value = _norm(text)
    explicit = any(x in value for x in (
        "weiß nicht", "weiss nicht", "keine ahnung", "ich verstehe nicht",
        "verstehe nicht",
    )) or value in {"?", "..."}
    # A short correct answer is normal in a real conversation, not failure.
    struggle = explicit and value not in NORMAL_SHORT
    return struggle, len(_words(value)) >= 7

def _allowed_skills(level):
    skills = set()
    try:
        upto = LEVEL_ORDER.index(level)
    except ValueError:
        upto = 0
    for item in LEVEL_ORDER[:upto + 1]:
        skills.update(LEVEL_SKILLS.get(item, set()))
    return skills or set(LEVEL_SKILLS["A1.1"])

def _extract_facts(text):
    """Extract only facts that are clear enough to reuse naturally."""
    value = str(text or "").strip()
    low = value.lower()
    facts = {}

    # Places: "Ich bin heute in Heidelberg", "Ich bin in Mannheim".
    m = re.search(r"\bich\s+bin(?:\s+heute)?\s+in\s+([A-ZÄÖÜ][A-Za-zÄÖÜäöüß-]+)", value)
    if m:
        facts["place"] = m.group(1)

    # Shopping and object.
    if re.search(r"\b(?:ich\s+)?(?:kaufe|kaufen|kauf)\b", low):
        facts["activity"] = "shopping"
        if "schuh" in low:
            facts["shopping_item"] = "Schuhe"
    if "sportschuh" in low:
        facts["shopping_item"] = "Sportschuhe"

    if re.search(r"\bmein\s+tag\b", low):
        facts["topic"] = "today"
        facts["day_statement"] = True

    # Simple colors useful for shopping follow-ups.
    for color in ("schwarz", "blau", "rot", "grün", "grau", "rosa", "weiß", "braun"):
        if re.search(rf"\b{color}\w*\b", low):
            facts["color"] = color.capitalize()
            break

    if re.search(r"\b(?:ich\s+)?(?:fahren|fahre|fährst|faehrst)\s+rad\b", low):
        facts["activity"] = "cycling"
        facts["topic"] = "hobby"
    elif re.search(r"\b(?:shwimmen|schwimmen|schwime?n|schwim+en)\b", low):
        facts["activity"] = "swimming"
        facts["topic"] = "hobby"
    elif re.search(r"\b(?:ich\s+)?(?:machen\s+)?(?:lesen|lese)\b", low):
        facts["activity"] = "reading"
        facts["topic"] = "hobby"
    elif re.search(r"\b(?:ich\s+)?(?:horen|hören|höre|hoere)\b", low):
        facts["activity"] = "music"
        facts["topic"] = "hobby"
        for genre in ("pop", "rock", "jazz", "techno", "rap", "klassik"):
            if re.search(rf"\b{genre}\b", low):
                facts["music_genre"] = genre.capitalize()
                break

    if any(x in low for x in ("arbeit", "job", "hotel")):
        facts["topic"] = "work"
    elif any(x in low for x in ("hobby", "freizeit", "musik", "sport", "lesen", "buch")):
        facts["topic"] = "hobby"
    elif any(x in low for x in ("wetter", "sonne", "regen", "kalt", "warm")):
        facts["topic"] = "weather"
    elif any(x in low for x in ("urlaub", "reise", "ferien", "meer", "berge")):
        facts["topic"] = "holiday"
    elif "gestern" in low:
        facts["topic"] = "yesterday"
    return facts

def _error_and_recast(text):
    """Return (natural recast, error key). Never interrupt with grammar theory."""
    value = str(text or "").strip()
    low = value.lower()
    patterns = [
        (r"^ich\s+machen\s+lesen$", "ich_machen_lesen", lambda m: "Ah, du liest gern."),
        (r"^ich\s+lesen\s+gern$", "ich_lesen", lambda m: "Ah, du liest gern."),
        (r"^ich\s+lesen$", "ich_lesen", lambda m: "Ah, du liest."),
        (r"^ich\s+fahren\s+rad$", "ich_fahren_rad", lambda m: "Ah, du fährst gern Rad."),
        (r"^ich\s+(?:horen|hören|hoere)\s+(.+)$", "ich_hoeren", lambda m: f"Ah, du hörst {m.group(1).capitalize()}."),
        (r"^ich\s+(?:shwimmen|schwimmen|schwimen)$", "ich_schwimmen", lambda m: "Ah, du schwimmst gern."),
        (r"^ich\s+kaufen\s+(.+)$", "ich_kaufen", lambda m: f"Ah, du kaufst {m.group(1)}."),
        (r"^ich\s+gehen\s+(.+)$", "ich_gehen", lambda m: f"Ah, du gehst {m.group(1)}."),
        (r"^ich\s+arbeiten(?:\s+(.+))?$", "ich_arbeiten", lambda m: "Ah, du arbeitest" + (f" {m.group(1)}." if m.group(1) else ".")),
        (r"^ich\s+lesen\s+gern(?:\s+(.+))?$", "ich_lesen", lambda m: "Ah, du liest gern" + (f" {m.group(1)}." if m.group(1) else ".")),
        (r"^ich\s+wohnen\s+(.+)$", "ich_wohnen", lambda m: f"Ah, du wohnst {m.group(1)}."),
    ]
    for pattern, key, build in patterns:
        match = re.match(pattern, low, re.I)
        if match:
            return build(match), key
    return None, None

def _record_error(state, free, key, original):
    if not key:
        return
    counts = free.setdefault("error_counts", {})
    counts[key] = int(counts.get(key, 0) or 0) + 1
    if counts[key] < 2:
        return

    # Shared memory: course mode can consume these recurring errors later.
    shared = state.setdefault("learner_memory", {})
    recurring = shared.setdefault("recurring_errors", [])
    existing = next((x for x in recurring if isinstance(x, dict) and x.get("key") == key), None)
    if existing:
        existing["count"] = counts[key]
        existing["last_example"] = str(original or "").strip()
    else:
        recurring.append({
            "key": key,
            "count": counts[key],
            "last_example": str(original or "").strip(),
            "source": "free_conversation",
        })
    del recurring[:-12]

def _remember_question(free, question):
    if not question:
        return
    free["last_question"] = question
    history = free.setdefault("recent_questions", [])
    if not history or history[-1] != question:
        history.append(question)
    del history[:-8]

def _not_recent(free, candidates):
    recent = set(free.get("recent_questions", [])[-5:])
    available = [q for q in candidates if q not in recent]
    return available or candidates

def _yes_no_followup(text, last_question, facts):
    low = _norm(text)
    yes, no = low in YES, low in NO
    if not (yes or no):
        return None

    q = _norm(last_question)
    if "suchst du sportschuhe" in q:
        return "Welche Farbe möchtest du?" if yes else "Welche Schuhe suchst du?"
    if "arbeitest du heute" in q:
        return "Wann fängst du an?" if yes else "Heute hast du also frei. Was machst du heute?"
    if "bist du heute zu hause" in q:
        return "Was machst du zu Hause?" if yes else "Ah, du bist unterwegs. Wo bist du gerade?"
    if "hast du heute viel zu tun" in q:
        return "Was musst du noch machen?" if yes else "Das ist schön. Was möchtest du heute machen?"
    if "hörst du gern musik" in q:
        return "Welche Musik hörst du gern?" if yes else "Was machst du lieber in deiner Freizeit?"
    if "machst du gern sport" in q:
        return "Welchen Sport machst du gern?" if yes else "Was machst du gern in deiner Freizeit?"
    if "fährst du oft rad" in q:
        return "Wo fährst du gern Rad?" if yes else "Was machst du sonst gern in deiner Freizeit?"
    if "fährst du dort oft rad" in q:
        return "Schön! Fährst du lieber allein oder mit jemandem?" if yes else "Wo fährst du lieber Rad?"
    if "schwimmst du dort im sommer" in q:
        return "Schön! Gehst du auch im Winter schwimmen?" if yes else "Wann schwimmst du dort gern?"
    if "schwimmst du oft" in q:
        return "Wo schwimmst du gern?" if yes else "Welchen Sport machst du sonst gern?"
    if "hörst du oft" in q and "musik" in q:
        return "Wann hörst du gern Musik?" if yes else "Welche Musik hörst du lieber?"
    if "spielst du oft fußball" in q:
        return "Wo spielst du gern Fußball?" if yes else "Welchen Sport machst du sonst gern?"
    if "hast du schon schöne schuhe" in q:
        if yes:
            facts["shopping_complete"] = True
            return "Super! Gefallen dir die Schuhe?"
        return "Welche Schuhe suchst du?"
    if "gefallen dir die schuhe" in q:
        facts["shopping_complete"] = True
        return "Schön! Und wie ist dein Tag heute?" if yes else "Oh, schade. Suchst du noch weiter?"
    if "magst du das wetter heute" in q:
        return "Schön! Was machst du bei diesem Wetter gern?" if yes else "Was machst du bei diesem Wetter lieber?"
    if "magst du das wetter" in q:
        return "Schön! Was machst du bei diesem Wetter gern?" if yes else "Was machst du bei diesem Wetter lieber?"
    return None

def _social_a1_reply(text, free, state):
    """Core A1 greetings, wellbeing and introductions with gentle modelling."""
    raw = str(text or "").strip()
    low = _norm(raw)
    last = _norm(free.get("last_question", ""))

    # ---- Questions the learner can ask Nele at any moment ----
    # Names: informal and polite variants.
    if low.strip(" ?!.") in {
        "wie heißt du", "wie heisst du", "wie ist dein name",
        "wer bist du", "wie heißen sie", "wie heissen sie",
        "wie ist ihr name"
    }:
        return "Ich heiße Nele. Und wie heißt du?"

    # Gentle correction for very common A1 name-question mistakes.
    if low.strip(" ?!.") in {
        "wie heißen du", "wie heissen du", "wie heißt sie",
        "wie heisst sie", "wie du heißt", "wie du heisst"
    }:
        _record_error(state, free, "wie_heisst_du", raw)
        return "Fast. Richtig: „Wie heißt du?“ Ich heiße Nele. Und du?"

    # Wellbeing: the learner may ask first, not only answer Nele.
    if low.strip(" ?!.") in {
        "wie geht's", "wie gehts", "wie geht es dir", "wie geht's dir",
        "wie gehts dir", "wie geht es ihnen", "wie geht's ihnen",
        "wie gehts ihnen", "alles gut", "alles klar"
    }:
        return "Mir geht es gut, danke. Und dir?"

    if low.strip(" ?!.") in {
        "wie geht du", "wie geht dir", "wie geht es du",
        "wie geht ihnen", "wie geht sie"
    }:
        _record_error(state, free, "wie_geht_es_dir", raw)
        return "Fast. Richtig: „Wie geht es dir?“ Mir geht es gut, danke. Und dir?"

    # Weather questions. Free conversation uses a conversational answer rather
    # than pretending to know the learner's live local weather.
    weather_questions = {
        "wie ist das wetter", "wie ist das wetter heute",
        "wie ist heute das wetter", "was macht das wetter",
        "wie ist das wetter bei dir", "ist es warm",
        "ist es kalt", "regnet es", "regnet es heute",
        "scheint die sonne", "ist es sonnig", "ist es windig",
        "schneit es", "ist es bewölkt", "ist es bewoelkt"
    }
    if low.strip(" ?!.") in weather_questions:
        return "Bei mir gibt es kein echtes Wetter. Wie ist das Wetter bei dir?"

    if low.strip(" ?!.") in {
        "wie wetter heute", "wie ist wetter", "was ist das wetter",
        "wie das wetter ist"
    }:
        _record_error(state, free, "wie_ist_das_wetter", raw)
        return "Fast. Richtig: „Wie ist das Wetter heute?“ Wie ist es bei dir?"

    # ---- Weather statements and natural reactions ----
    weather_patterns = [
        (("sonnig", "die sonne scheint", "sonne"), "Sonne", "Schön! Magst du sonniges Wetter?"),
        (("warm", "heiß", "heiss"), "warm", "Schön! Was machst du gern, wenn es warm ist?"),
        (("kalt", "kühl", "kuehl"), "kalt", "Oh, es ist kalt. Magst du kaltes Wetter?"),
        (("regen", "regnet", "regnerisch"), "Regen", "Oh, es regnet. Hast du einen Regenschirm?"),
        (("schnee", "schneit", "verschneit"), "Schnee", "Oh, es schneit. Magst du Schnee?"),
        (("windig", "wind"), "windig", "Es ist windig. Ist es auch kalt?"),
        (("bewölkt", "bewoelkt", "wolken", "wolkig"), "bewölkt", "Es ist bewölkt. Ist es trotzdem warm?"),
        (("nebel", "neblig"), "neblig", "Es ist neblig. Ist es auch kalt?"),
        (("gewitter", "donner", "blitz"), "Gewitter", "Oh, ein Gewitter. Regnet es stark?"),
    ]
    weather_context = any(x in last for x in (
        "wetter", "warm", "kalt", "sonnig", "regnet", "schnee",
        "windig", "bewölkt", "bewoelkt"
    ))
    explicit_weather = any(x in low for x in (
        "wetter", "sonne", "sonnig", "regen", "regnet", "schnee", "schneit",
        "wind", "windig", "bewölkt", "bewoelkt", "wolken", "wolkig",
        "nebel", "neblig", "gewitter"
    ))
    if weather_context or explicit_weather:
        # Common keyboard/ASR typo from beginner input.
        if low in {"sonn8g", "sonnlg", "sonig"}:
            _record_error(state, free, "sonnig_spelling", raw)
            free.setdefault("conversation_facts", {})["weather"] = "Sonne"
            return "Fast richtig 😊 Du meinst „sonnig“. Du kannst sagen: „Es ist sonnig.“ Ist es auch warm?"

        # Common A1 errors: "es ist regen", "es regnen", "es sonnig".
        if re.fullmatch(r"es\s+ist\s+regen", low):
            _record_error(state, free, "es_regnet", raw)
            return "Fast. Richtig: „Es regnet.“ Magst du Regen?"
        if re.fullmatch(r"es\s+(?:regnen|regen)", low):
            _record_error(state, free, "es_regnet", raw)
            return "Fast. Richtig: „Es regnet.“ Hast du einen Regenschirm?"
        m = re.fullmatch(r"es\s+(sonnig|warm|kalt|windig|bewölkt|bewoelkt)", low)
        if m:
            word = m.group(1)
            correct = "bewölkt" if word == "bewoelkt" else word
            _record_error(state, free, "wetter_es_ist", raw)
            return f"Fast. Richtig: „Es ist {correct}.“ Magst du dieses Wetter?"

        # Accept short answers such as "sonnig" after a weather question.
        for variants, remembered, reaction in weather_patterns:
            if any(v == low or v in low for v in variants):
                free.setdefault("conversation_facts", {})["weather"] = remembered
                return reaction

        if low in {"gut", "schön", "schoen", "schlecht", "wechselhaft"}:
            return f"Das Wetter ist also {low}. Magst du das Wetter heute?"

    # ---- Everyday A1: today, hobby, work, shopping and holiday ----
    # Clear learner questions can start these topics at any moment.
    everyday_questions = {
        "was machst du heute": "Heute spreche ich mit dir. Und was machst du heute?",
        "was machst du gern": "Ich spreche gern mit dir. Was machst du gern?",
        "was machst du gern in deiner freizeit": "Ich spreche gern mit dir. Und du? Was machst du gern in deiner Freizeit?",
        "hast du ein hobby": "Ja, ich mag Sprachen. Und du? Was ist dein Hobby?",
        "arbeitest du": "Ich bin deine Deutschtrainerin. Arbeitest du heute?",
        "gehst du arbeiten": "Ich arbeite hier mit dir. Und du? Arbeitest du heute?",
        "gehst du gern einkaufen": "Ich kann mit dir über Einkaufen sprechen. Was kaufst du gern?",
        "was kaufst du gern": "Ich mag Wörter und Gespräche. Was kaufst du gern?",
        "machst du gern urlaub": "Ich kann mit dir über Urlaub sprechen. Wo machst du gern Urlaub?",
        "wo machst du urlaub": "Ich reise nicht wirklich. Und du? Wo machst du gern Urlaub?",
    }
    everyday_key = low.strip(" ?!.")
    if everyday_key in everyday_questions:
        return everyday_questions[everyday_key]

    # Common A1 verb/conjugation errors in the five everyday topics.
    everyday_errors = [
        (r"^ich\s+arbeiten(?:\s+(.+))?$", "ich_arbeite",
         lambda m: "Ich arbeite" + (f" {m.group(1)}." if m.group(1) else ".")),
        (r"^ich\s+kaufen(?:\s+(.+))?$", "ich_kaufe",
         lambda m: "Ich kaufe" + (f" {m.group(1)}." if m.group(1) else ".")),
        (r"^ich\s+fahren\s+rad$", "ich_fahre_rad",
         lambda m: "Ich fahre Rad."),
        (r"^ich\s+machen\s+sport$", "ich_mache_sport",
         lambda m: "Ich mache Sport."),
        (r"^ich\s+machen\s+urlaub(?:\s+(.+))?$", "ich_mache_urlaub",
         lambda m: "Ich mache Urlaub" + (f" {m.group(1)}." if m.group(1) else ".")),
        (r"^ich\s+gehen\s+einkaufen$", "ich_gehe_einkaufen",
         lambda m: "Ich gehe einkaufen."),
    ]
    for pattern, key, build in everyday_errors:
        match = re.match(pattern, low, re.I)
        if match:
            correct = build(match)
            _record_error(state, free, key, raw)
            if key == "ich_arbeite":
                return f"Fast. Richtig: „{correct}“ Wann arbeitest du heute?"
            if key in {"ich_kaufe", "ich_gehe_einkaufen"}:
                return f"Fast. Richtig: „{correct}“ Was möchtest du kaufen?"
            if key in {"ich_fahre_rad", "ich_mache_sport"}:
                return f"Fast. Richtig: „{correct}“ Machst du das oft?"
            return f"Fast. Richtig: „{correct}“ Wo machst du gern Urlaub?"

    # Natural short answers keep the current everyday topic alive and model
    # a complete A1 sentence instead of abruptly changing the subject.
    if any(x in last for x in ("was machst du gerade", "was machst du heute", "wie ist dein tag", "viel zu tun")):
        if low in {"lernen", "deutsch lernen"}:
            return "Du kannst sagen: „Ich lerne gerade Deutsch.“ Was lernst du gerade?"
        if low in {"arbeiten", "arbeit"}:
            return "Du arbeitest heute. Wann fängst du an?"
        if low in {"einkaufen", "shoppen"}:
            return "Du gehst einkaufen. Was möchtest du kaufen?"
        if low in {"zu hause", "zuhause"}:
            return "Du bist zu Hause. Was machst du dort?"
        if low in {"frei", "ich habe frei"}:
            return "Schön, du hast heute frei. Was möchtest du machen?"

    if any(x in last for x in ("bei diesem wetter", "wenn es warm ist")):
        if low in {"radfahren", "rad fahren", "fahrrad fahren"}:
            return "Du kannst sagen: „Ich fahre gern Rad.“ Fährst du lieber allein oder mit jemandem?"
        if low in {"spazieren", "spazieren gehen", "spaziergang"}:
            return "Du kannst sagen: „Ich gehe gern spazieren.“ Wo gehst du gern spazieren?"
        if low in {"schwimmen", "baden"}:
            return "Du kannst sagen: „Ich gehe gern schwimmen.“ Wo schwimmst du gern?"

    if any(x in last for x in ("freizeit", "hobby", "was machst du gern")):
        if low in {"lesen", "bücher lesen", "buch lesen"}:
            return "Du liest gern. Was liest du gern?"
        if low in {"musik", "musik hören", "musik hoeren"}:
            return "Du hörst gern Musik. Welche Musik magst du?"
        if low in {"sport", "sport machen"}:
            return "Du machst gern Sport. Welchen Sport machst du?"
        if low in {"rad fahren", "fahrrad fahren"}:
            return "Du fährst gern Rad. Wo fährst du gern Rad?"
        if low in {"schwimmen", "schwimmbad"}:
            return "Du schwimmst gern. Wo schwimmst du gern?"

    if any(x in last for x in ("arbeitest du", "arbeit", "wann fängst du", "wann faengst du")):
        if low in {"ja", "ja gern", "ja, gern"}:
            return "Wann fängst du heute an?"
        if low in {"nein", "nein heute nicht", "heute nicht"}:
            return "Dann hast du heute frei. Was machst du heute?"
        if re.fullmatch(r"(?:um\s+)?\d{1,2}(?::\d{2})?(?:\s+uhr)?", low):
            return f"Du fängst {raw.strip()} an. Was machst du bei der Arbeit?"

    if any(x in last for x in ("kaufen", "einkaufen", "welche schuhe", "was möchtest du kaufen")):
        if low in {"schuhe", "sportschuhe", "kleidung", "lebensmittel", "essen"}:
            return f"Du möchtest {raw.strip()} kaufen. Wo kaufst du gern ein?"

    if any(x in last for x in ("urlaub", "meer oder berge", "wohin reist")):
        if low in {"meer", "ans meer"}:
            return "Du magst das Meer. Was machst du dort gern?"
        if low in {"berge", "in die berge"}:
            return "Du magst die Berge. Wanderst du gern?"
        if re.fullmatch(r"(?:in|nach)\s+[a-zäöüß-]+", low):
            return f"Schön! Du machst Urlaub {raw.strip()}. Was machst du dort gern?"

    # ---- Greetings: common variants and gentle correction ----
    greeting_mistakes = {
        "gute morgen": "Guten Morgen",
        "gut morgen": "Guten Morgen",
        "guten morg": "Guten Morgen",
        "gute tag": "Guten Tag",
        "gut tag": "Guten Tag",
        "gute abend": "Guten Abend",
        "gut abend": "Guten Abend",
        "guten nacht": "Gute Nacht",
    }
    clean_social = low.strip("!., ")
    if clean_social in greeting_mistakes:
        correct = greeting_mistakes[clean_social]
        _record_error(state, free, "greeting", raw)
        return f"Fast. Richtig: „{correct}!“ Sag es bitte noch einmal."

    # ---- Wie geht's? / Wie geht es dir/Ihnen? ----
    wellbeing_question = any(x in last for x in (
        "wie geht's dir", "wie geht es dir", "wie geht es ihnen", "wie geht's ihnen"
    ))
    if wellbeing_question:
        # Accept short everyday answers but model the complete A1 sentence.
        wellbeing = {
            "prima": ("Mir geht es prima.", "Prima!"),
            "super": ("Mir geht es super.", "Super!"),
            "sehr gut": ("Mir geht es sehr gut.", "Das freut mich!"),
            "gut": ("Mir geht es gut.", "Das freut mich!"),
            "ganz gut": ("Mir geht es ganz gut.", "Schön!"),
            "nicht schlecht": ("Mir geht es nicht schlecht.", "Schön!"),
            "so lala": ("Mir geht es so lala.", "Verstehe."),
            "es geht": ("Es geht.", "Verstehe."),
            "geht so": ("Es geht so.", "Verstehe."),
            "nicht so gut": ("Mir geht es nicht so gut.", "Oh, das tut mir leid."),
            "schlecht": ("Mir geht es schlecht.", "Oh, das tut mir leid."),
            "sehr schlecht": ("Mir geht es sehr schlecht.", "Oh, das tut mir leid."),
            "müde": ("Ich bin müde.", "Oh, du bist müde."),
        }
        if low in wellbeing:
            model, reaction = wellbeing[low]
            free.setdefault("conversation_facts", {})["wellbeing"] = low
            if low in {"schlecht", "sehr schlecht", "nicht so gut"}:
                return f"{reaction} Du kannst sagen: „{model}“ Warum geht es dir nicht gut?"
            if low == "müde":
                return f"{reaction} Du kannst sagen: „{model}“ War dein Tag anstrengend?"
            return f"{reaction} Du kannst auch sagen: „{model}“ Was machst du heute?"

        # Common malformed answers: ich gut / mir geht gut / ich bin gut.
        if re.fullmatch(r"ich\s+(?:gut|prima|schlecht)", low):
            word = low.split()[-1]
            model = f"Mir geht es {word}."
            return f"Fast richtig. Sag: „{model}“ Und was machst du heute?"
        m = re.fullmatch(r"mir\s+geht(?:\s+es)?\s+(gut|prima|schlecht|super)", low)
        if m:
            word = m.group(1)
            model = f"Mir geht es {word}."
            if low == model.lower().rstrip("."):
                return f"Sehr gut! Was machst du heute?"
            return f"Fast richtig. Sag: „{model}“ Was machst du heute?"

    # ---- Introductions / names ----
    # Correct variants.
    m = re.match(r"^ich\s+heiße\s+(.+)$", raw, re.I)
    if m:
        name = m.group(1).strip(" .")
        free.setdefault("conversation_facts", {})["name"] = name
        return f"Hallo {name}! Schön, dich kennenzulernen. Woher kommst du?"

    m = re.match(r"^mein\s+name\s+ist\s+(.+)$", raw, re.I)
    if m:
        name = m.group(1).strip(" .")
        free.setdefault("conversation_facts", {})["name"] = name
        return f"Hallo {name}! Schön, dich kennenzulernen. Woher kommst du?"

    # "Ich bin Moni" is valid as an informal self-introduction when a name follows.
    m = re.match(r"^ich\s+bin\s+([A-ZÄÖÜ][A-Za-zÄÖÜäöüß-]{1,30})[.!]?$", raw)
    if m:
        name = m.group(1)
        free.setdefault("conversation_facts", {})["name"] = name
        return f"Hallo {name}! Schön, dich kennenzulernen. Woher kommst du?"

    # Common conjugation mistakes when giving a name.
    m = re.match(r"^ich\s+(?:heißen|heissen|heißt|heisst)\s+(.+)$", raw, re.I)
    if m:
        name = m.group(1).strip(" .")
        free.setdefault("conversation_facts", {})["name"] = name
        _record_error(state, free, "ich_heisse", raw)
        return f"Fast richtig. Sag: „Ich heiße {name}.“ Hallo {name}! Woher kommst du?"

    m = re.match(r"^mein\s+name\s+(?:sein|sind)\s+(.+)$", raw, re.I)
    if m:
        name = m.group(1).strip(" .")
        _record_error(state, free, "mein_name_ist", raw)
        return f"Fast richtig. Sag: „Mein Name ist {name}.“ Woher kommst du?"

    # ---- Greetings: formal and informal ----
    greetings = {
        "hallo": ("Hallo!", "informell"),
        "hi": ("Hi!", "informell"),
        "hey": ("Hallo!", "informell"),
        "guten morgen": ("Guten Morgen!", "neutral"),
        "guten tag": ("Guten Tag!", "formal"),
        "guten abend": ("Guten Abend!", "neutral"),
        "moin": ("Moin!", "informell"),
        "servus": ("Servus!", "informell"),
        "grüß gott": ("Grüß Gott!", "regional"),
        "gruss gott": ("Grüß Gott!", "regional"),
        "grüß dich": ("Grüß dich!", "informell"),
        "gruss dich": ("Grüß dich!", "informell"),
        "gute nacht": ("Gute Nacht!", "neutral"),
        "tschüss": ("Tschüss!", "informell"),
        "tschuss": ("Tschüss!", "informell"),
        "ciao": ("Ciao!", "informell"),
        "bis bald": ("Bis bald!", "neutral"),
        "bis später": ("Bis später!", "informell"),
        "bis spaeter": ("Bis später!", "informell"),
        "auf wiedersehen": ("Auf Wiedersehen!", "formal"),
    }
    clean = low.strip("!., ")
    if clean in greetings:
        answer, register = greetings[clean]
        free.setdefault("conversation_facts", {})["greeting_register"] = register
        if clean in {
            "gute nacht", "tschüss", "tschuss", "ciao",
            "bis bald", "bis später", "bis spaeter", "auf wiedersehen"
        }:
            return answer
        return f"{answer} Wie geht es dir heute?"

    return None


def _content_followup(text, facts, memory, free, level):
    """Choose a question from the learner's content before any generic pool."""
    low = _norm(text)
    place = facts.get("place") or memory.get("place")
    item = facts.get("shopping_item") or memory.get("shopping_item")
    color = facts.get("color") or memory.get("color")

    if facts.get("place"):
        return f"Schön! Was machst du in {facts['place']}?"

    if facts.get("activity") == "shopping" and item == "Schuhe":
        return "Suchst du Sportschuhe?"

    if facts.get("activity") == "shopping":
        return "Was möchtest du kaufen?"

    # A one-word color is meaningful after a shopping/color question.
    # Short noun answers get their meaning from the previous question.
    last_q = _norm(free.get("last_question", ""))
    if "wo schwimmst du gern" in last_q and low in {"see", "im see", "schwimmbad", "im schwimmbad", "pool", "im pool"}:
        place_word = "im See" if "see" in low else ("im Schwimmbad" if "schwimmbad" in low else "im Pool")
        memory["swimming_place"] = place_word
        return f"Ah, {place_word}. Schwimmst du dort im Sommer?"
    if "wo fährst du gern rad" in last_q and low in {"park", "im park", "wald", "im wald", "stadt", "in der stadt"}:
        place_word = "im Park" if "park" in low else ("im Wald" if "wald" in low else "in der Stadt")
        memory["cycling_place"] = place_word
        return f"Ah, {place_word}. Fährst du dort oft Rad?"
    if "welchen sport machst du gern" in last_q and low in {"fuzball", "fußball", "fussball"}:
        memory["sport"] = "Fußball"
        return "Fußball? Spielst du oft Fußball?"

    # Keep very short weather answers attached to the weather question.
    if "warm oder kalt" in last_q:
        if low in {"warm", "waren", "war"}:
            memory["weather"] = "warm"
            return "Ah, es ist warm. Ist es auch sonnig?"
        if low == "kalt":
            memory["weather"] = "kalt"
            return "Oh, es ist kalt. Bleibst du heute lieber drinnen?"

    if "es regnet" in low or low == "regen":
        memory["weather"] = "Regen"
        return "Oh, es regnet. Magst du das Wetter heute?"

    if facts.get("day_statement"):
        # "schon" is a very common keyboard/ASR spelling for "schön" here.
        if re.search(r"\b(?:schon|schön)\b", low):
            return "Das freut mich! Was war heute schön?"
        if "gut" in low:
            return "Das freut mich! Was war heute gut?"
        return "Erzähl mir ein bisschen von deinem Tag."

    if color and (
        "farbe" in _norm(free.get("last_question", ""))
        or (item and not memory.get("shopping_complete"))
    ):
        if place:
            return f"{color} passt gut. Hast du schon schöne Schuhe in {place} gefunden?"
        return f"{color} passt gut. Hast du schon schöne Schuhe gefunden?"

    if "ich bin müde" in low or low == "müde":
        return "Oh, du bist müde. War dein Tag anstrengend?"

    activity = facts.get("activity")
    if activity == "reading":
        if _norm(text) in {"ich lesen", "ich lese"}:
            return "Was liest du gerade?"
        return "Was liest du gern?"
    if activity == "music":
        genre = facts.get("music_genre")
        return f"Hörst du oft {genre}musik?" if genre else "Welche Musik hörst du gern?"
    if activity == "cycling":
        return "Fährst du oft Rad?"
    if activity == "swimming":
        return "Schwimmen? Schön! Schwimmst du oft?"

    if re.search(r"\bich\s+arbeite\b", low):
        return "Wann fängst du an?"
    if re.search(r"\bich\s+(?:höre|mag)\b.*musik", low):
        return "Welche Musik hörst du gern?"
    if re.search(r"\bich\s+lese\b", low):
        return "Was liest du gern?"

    return None

def _generic_followup(topic, free, support, independent, level):
    allowed = _allowed_skills(level)
    if topic == "yesterday" and "yesterday" not in allowed:
        topic = "today"
    pool = FALLBACKS.get(topic, FALLBACKS["today"])
    pool = _not_recent(free, pool)
    # More independent learners get the more open end of the same A1 material.
    index = -1 if independent >= 3 and support == 0 else 0
    return pool[index]

def generate_free_welcome(state, session_id=None):
    free = state.setdefault("free_conversation", {})
    index = int(free.get("welcome_index", 0) or 0)
    free["welcome_index"] = (index + 1) % len(OPENERS)
    free["last_question"] = OPENERS[index]
    free["recent_questions"] = [OPENERS[index]]
    free["turn_count"] = 0
    free["support_level"] = 1
    free["independent_turns"] = 0
    free["struggle_turns"] = 0
    free["topic_turns"] = 0
    free["conversation_facts"] = {}
    free.setdefault("error_counts", {})
    state.setdefault("student_progress", {}).setdefault("current_level", "A1.1")
    return OPENERS[index]

def generate_free_conversation_reply(user_message, state, session_id=None):
    free = state.setdefault("free_conversation", {})
    progress = state.setdefault("student_progress", {})
    level = str(progress.get("current_level", "A1.1") or "A1.1")

    struggle, strong = _difficulty_signal(user_message)
    independent = int(free.get("independent_turns", 0) or 0)
    struggles = int(free.get("struggle_turns", 0) or 0)
    support = int(free.get("support_level", 1) or 1)

    if struggle:
        struggles += 1
        independent = 0
        support = min(3, support + 1)
    else:
        independent += 1
        struggles = max(0, struggles - 1)
        if strong or independent >= 3:
            support = max(0, support - 1)

    facts = _extract_facts(user_message)
    memory = free.setdefault("conversation_facts", {})
    memory.update({k: v for k, v in facts.items() if k not in {"topic", "day_statement"}})

    # A clear new everyday topic closes the active shopping branch. Keep the
    # useful facts (place/color) in memory, but do not let them hijack replies.
    if facts.get("day_statement"):
        memory["shopping_complete"] = True

    previous_topic = free.get("last_topic", "today")
    topic = facts.get("topic", previous_topic)
    if facts.get("activity") == "shopping":
        topic = "shopping"
    elif facts.get("place"):
        topic = "place"

    last_question = free.get("last_question", "")
    recast, error_key = _error_and_recast(user_message)
    _record_error(state, free, error_key, user_message)

    # Priority 0: core A1 social language (greetings, wellbeing, introductions).
    social_reply = _social_a1_reply(user_message, free, state)
    if social_reply:
        # Store its final question as conversational context for the next turn.
        parts = re.findall(r"[^.!?]*[?]", social_reply)
        next_question = parts[-1].strip() if parts else ""
        if next_question:
            _remember_question(free, next_question)
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        return social_reply, {
            "conversation_mode": "free",
            "support_level": support,
            "topic": free.get("last_topic", "today"),
            "independent_turns": independent,
            "course_level": level,
            "conversation_facts": dict(free.get("conversation_facts", {})),
            "recurring_errors": list((state.get("learner_memory") or {}).get("recurring_errors", [])),
        }

    # Priority: answer context -> learner content -> safe course-level fallback.
    question = _yes_no_followup(user_message, last_question, memory)
    if not question:
        question = _content_followup(user_message, facts, memory, free, level)
    if not question:
        question = _generic_followup(topic, free, support, independent, level)

    # Do not repeat the same question. Compare normalized text so punctuation
    # and capitalization cannot bypass the loop guard.
    recent_norm = {_norm(q).strip(" ?!.") for q in free.get("recent_questions", [])[-8:]}
    question_norm = _norm(question).strip(" ?!.")
    if question_norm in recent_norm:
        question = _generic_followup("today", free, support, independent, level)
        if question == last_question:
            question = _not_recent(free, FALLBACKS["today"])[0]

    if struggle:
        reply = f"Kein Problem. {question}"
    elif recast:
        reply = f"{recast} {question}"
    elif _norm(user_message) in {"gut", "sehr gut", "prima", "super"}:
        reply = f"Schön! {question}"
    elif _norm(user_message) in YES | NO:
        reply = question
    else:
        reply = question

    turn = int(free.get("turn_count", 0) or 0) + 1
    free.update({
        "independent_turns": independent,
        "struggle_turns": struggles,
        "support_level": support,
        "last_topic": topic,
        "topic_turns": int(free.get("topic_turns", 0) or 0) + 1,
        "turn_count": turn,
        "last_user_message": str(user_message or "").strip(),
    })
    _remember_question(free, question)

    return reply, {
        "conversation_mode": "free",
        "support_level": support,
        "topic": topic,
        "independent_turns": independent,
        "course_level": level,
        "conversation_facts": dict(memory),
        "recurring_errors": list((state.get("learner_memory") or {}).get("recurring_errors", [])),
    }
