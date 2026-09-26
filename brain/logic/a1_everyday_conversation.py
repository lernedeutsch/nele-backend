"""Reusable A1 everyday conversation bank for lessons 1-10.

This is not a script to recite. It provides natural reactions and follow-ups
from course vocabulary so free conversation can mix learned material.
"""
import re

def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip(" ?!.,")

def a1_everyday_reply(text, last_question, state=None):
    raw=str(text or "").strip()
    low=_norm(raw); last=_norm(last_question)
    facts=(state or {}).setdefault("a1_everyday_facts", {}) if state is not None else {}

    # A fresh learner question must never be consumed as an answer to the
    # previous A1 subthread. Direct question handlers below may still answer
    # known questions; otherwise stale last_question context is cleared.
    question_low = re.sub(r"^(?:(?:und|aber|also)\\s+)+", "", low)
    learner_question = "?" in raw and re.match(
        r"^(?:was|wie|wo|woher|wohin|wann|warum|wer|welcher|welche|welches|arbeitest|wohnst|isst|trinkst|magst|machst|hast|bist|kommst)\b",
        question_low,
    )

    # Learner-led questions: answer briefly and return the conversation.
    direct={
      "woher kommst du":"Ich bin Nele, deine Deutschtrainerin. Und woher kommst du?",
      "wo wohnst du":"Ich wohne nicht wirklich an einem Ort. Und wo wohnst du?",
      "wie alt bist du":"Ich habe kein echtes Alter. Und wie alt bist du?",
      "was machst du beruflich":"Ich bin deine Deutschtrainerin. Und was machst du beruflich?",
      "was isst du gern":"Ich mag keine echten Mahlzeiten, aber wir können darüber sprechen. Was isst du gern?",
      "was trinkst du gern":"Ich trinke nicht wirklich. Was trinkst du gern?",
      "hast du geschwister":"Ich habe keine Familie wie ein Mensch. Hast du Geschwister?",
      "wie spät ist es":"Das kann ich hier nicht zuverlässig sehen. Wie spät ist es bei dir?",
      "wann fängst du an":"Ich bin immer für dich da. Wann fängst du heute an?",
      "wann faengst du an":"Ich bin immer für dich da. Wann fängst du heute an?",
      "wann fängst du heute an":"Ich bin immer für dich da. Wann fängst du heute an?",
      "wann faengst du heute an":"Ich bin immer für dich da. Wann fängst du heute an?",
      "was machst du bei der arbeit":"Ich bin keine Person und arbeite nicht wirklich. Was machst du bei der Arbeit?",
      "was machst du auf der arbeit":"Ich bin keine Person und arbeite nicht wirklich. Was machst du bei der Arbeit?",
      "was kochst du gern":"Ich koche nicht wirklich. Was kochst du gern?",
      "was putzt du bei der arbeit":"Ich putze nicht wirklich. Was putzt du bei der Arbeit?",
      "was putzt du auf der arbeit":"Ich putze nicht wirklich. Was putzt du bei der Arbeit?",
      "was reinigst du bei der arbeit":"Ich reinige nicht wirklich. Was reinigst du bei der Arbeit?",
    }
    if low in direct: return direct[low]
    if learner_question:
        return None

    # Work-activity slot: keep common housekeeping activities anchored to the
    # active work question. This is a reusable slot, not a one-off phrase.
    work_activity_slots = {
        "putze": ("Ich putze.", "Was putzt du bei der Arbeit?"),
        "reinige": ("Ich reinige.", "Was reinigst du bei der Arbeit?"),
        "mache sauber": ("Ich mache sauber.", "Was machst du bei der Arbeit sauber?"),
        "koche": ("Ich koche.", "Was kochst du gern?"),
    }
    if re.fullmatch(r"(?:ich\s+)?(?:putze|reinige|koche)|ich\s+mache\s+sauber", low):
        key = "mache sauber" if "mache sauber" in low else low.replace("ich ", "")
        model, follow_up = work_activity_slots.get(key, (None, None))
        if model:
            facts["work_activity"] = key
            return f"Du kannst sagen: „{model}“ {follow_up}"

    if "was machst du bei der arbeit" in last or "was putzt du bei der arbeit" in last or "was putzt du auf der arbeit" in last:
        if low in {"zimmer", "zimmern", "die zimmer", "hotelzimmer", "hotelzimmern", "ich putze zimmer", "ich putze die zimmer", "ich putze hotelzimmer"}:
            facts["work_activity"] = "putze"
            facts["work_activity_detail"] = "Zimmer"
            return "Sehr gut. Du putzt Zimmer. Wie viele Zimmer putzt du normalerweise?"

    if "was reinigst du bei der arbeit" in last:
        if low in {"zimmer", "die zimmer", "hotelzimmer"}:
            facts["work_activity_detail"] = "Zimmer"
            return "Du kannst sagen: „Ich reinige Zimmer.“ Wie viele Zimmer reinigst du normalerweise?"

    # Learner-led intent/content has priority over stale last_question context.
    # Only genuinely short/dependent answers should continue the previous turn.
    if re.fullmatch(r"(?:und\s+)?hast du (?:eine )?familie", low):
        return "Ich habe keine Familie wie ein Mensch. Erzähl mir von deiner Familie."
    if re.fullmatch(r"(?:kannst|könntest|koenntest) du mir helfen", low):
        return "Ja, gern. Wobei brauchst du Hilfe?"
    if re.search(r"\b(?:meine tochter|mein sohn) (?:heißt|heisst)\s+", low):
        facts["child_type"] = "tochter" if "tochter" in low else "sohn"
        return "Wie alt ist dein Kind?"
    if re.search(r"\bheute ist das wetter\b|\bdas wetter ist heute\b", low):
        return "Schön! Was machst du bei diesem Wetter?"
    if re.search(r"\bich gehe (?:heute |später |spaeter )?einkaufen\b", low):
        return "Was möchtest du kaufen?"
    if re.search(r"\bich brauche\b", low) and any(x in low for x in ("milch","brot","äpfel","aepfel","gemüse","gemuese")):
        return "Wo kaufst du das?"
    if re.search(r"\b(?:nein[, ]+)?heute arbeite ich nicht\b|\bich arbeite heute nicht\b", low):
        return "Was machst du heute?"
    if re.search(r"\bmorgen arbeite ich\b", low):
        return "Wann fängst du morgen an?"

    # Work start time: a short time answer belongs to the active work question.
    # Acknowledge/model the learner's answer before moving the conversation on.
    # This handles arbitrary valid clock times, not one hard-coded example.
    if (
        any(q in last for q in ("wann fängst du an", "wann faengst du an", "wann fängst du heute an", "wann faengst du heute an"))
        and (m := re.fullmatch(r"(?:um\s+)?([01]?\d|2[0-3])(?:(?::|\.)([0-5]\d))?(?:\s*uhr)?", low))
    ):
        hour, minute = m.group(1), m.group(2)
        time_value = f"{hour}:{minute}" if minute else hour
        facts["work_start"] = time_value
        return f"Du kannst sagen: „Ich fange um {time_value} Uhr an.“ Was machst du bei der Arbeit?"
    if (
        ("wann fängst du morgen an" in last or "wann faengst du morgen an" in last)
        and re.fullmatch(r"(?:um\s+)?(?:[01]?\d|2[0-3])(?:(?::|\.)[0-5]\d)?(?:\s*uhr)?", low)
    ):
        return "Und wann bist du morgen fertig?"
    if re.search(r"\bdeutsch\b.*\b(?:schwierig|schwer)\b", low):
        return "Was ist für dich beim Deutschlernen schwierig?"
    if low in {"sprechen","das sprechen"} and "deutschlernen schwierig" in last:
        return "Dann üben wir Sprechen zusammen. Worüber möchtest du sprechen?"

    # Content-led entry points. A learner may introduce a fact before Nele has
    # asked the matching question. These anchors let the new A1 bank take over
    # naturally instead of falling through to unrelated legacy topics.
    name_match=re.search(r"\b(?:ich heiße|ich heisse|mein name ist)\s+([A-Za-zÄÖÜäöüß-]+)", raw, re.I)
    if name_match:
        facts["name"]=name_match.group(1)
        return f"Freut mich, {name_match.group(1)}! Woher kommst du?"

    origin_match=re.search(r"\bich komme aus\s+(.+)$", raw, re.I)
    if origin_match:
        facts["origin"]=origin_match.group(1).strip(" .")
        return "Wo wohnst du jetzt?"

    if re.search(r"\bich wohne (?:in|im|bei|mit)\b", low):
        if any(x in low for x in ("wohnung", "haus")):
            facts["home_type"]="Wohnung" if "wohnung" in low else "Haus"
            return "Ist dein Zuhause groß oder klein?"
        if "famil" in low:
            return "Hast du Kinder?"
        return "Wohnst du in einem Haus oder in einer Wohnung?"

    if re.search(r"\bich habe\b.*\b(?:wohnzimmer|schlafzimmer|küche|kueche|bad|zimmer)\b", low):
        return "Hast du ein Sofa im Wohnzimmer?"
    if re.search(r"\bich habe (?:ein|einen) sofa\b", low):
        return "Wo steht dein Tisch?"
    if re.search(r"\b(?:der )?tisch steht\b", low):
        return "Wohnst du allein oder mit deiner Familie?"

    if re.search(r"\bich habe (?:eine )?tochter\b", low):
        facts["child_type"] = "tochter"
        return "Wie heißt deine Tochter?"
    if re.search(r"\bich habe (?:einen )?sohn\b", low):
        facts["child_type"] = "sohn"
        return "Wie heißt dein Sohn?"
    if re.search(r"\bich habe kinder\b", low):
        facts["child_type"] = "kinder"
        return "Wie heißen deine Kinder?"
    if re.search(r"\bich habe (?:einen )?bruder\b|\bich habe (?:eine )?schwester\b|\bich habe geschwister\b", low):
        return "Wo wohnen deine Geschwister?"
    if re.search(r"\bmeine eltern wohnen\b", low):
        return "Besuchst du sie oft?"

    # Keep learner content anchored to the active A1 subthread. Short pronoun
    # answers such as "Sie heißt Lena" or "Sie ist zwölf Jahre alt" carry
    # meaning through the previous question; without that context they used to
    # fall through to unrelated generic topics.
    if ("groß oder klein" in last or "gross oder klein" in last) and re.search(
        r"\b(?:sie|es|mein(?:e)?\s+(?:wohnung|haus|zuhause))\b.*\b(?:klein|groß|gross)\b",
        low,
    ):
        return "Welche Zimmer hast du?"

    if any(q in last for q in ("wie heißen deine kinder", "wie heissen deine kinder", "wie heißt deine tochter", "wie heisst deine tochter", "wie heißt dein sohn", "wie heisst dein sohn")) and re.search(
        r"\b(?:sie|er|meine tochter|mein sohn)\s+(?:heißt|heisst)\b",
        low,
    ):
        if facts.get("child_type") == "tochter":
            return "Wie alt ist deine Tochter?"
        if facts.get("child_type") == "sohn":
            return "Wie alt ist dein Sohn?"
        return "Wie alt sind deine Kinder?"

    if (
        "wie alt ist dein kind" in last
        or "wie alt sind sie" in last
        or "wie alt ist deine tochter" in last
        or "wie alt ist dein sohn" in last
    ) and (
        re.search(r"\b(?:sie|er|mein(?:e)?\s+(?:tochter|sohn))\s+ist\b.*\bjahre?\s+alt\b", low)
        or re.search(r"\b\d{1,2}\s+jahre?\b", low)
    ):
        return "Hast du Geschwister?"

    if re.search(r"\bich arbeite\b", low):
        return "Arbeitest du heute?"
    if re.search(r"\bich trinke morgens\b", low):
        return "Was isst du zum Frühstück?"
    if re.search(r"\bich esse\b", low) and any(x in low for x in ("brot","käse","kaese","frühstück","fruehstueck")):
        return "Magst du Obst?"
    # Shopping context outranks generic food associations. A product list can
    # contain fruit, but after "Was kaufst du heute?" it is still a shopping
    # answer and must stay in the shopping subthread.
    if "was kaufst du heute" in last:
        return "Wo kaufst du Brot?"
    if any(x in low for x in ("äpfel","aepfel","bananen")) and not low.startswith("ich kaufe"):
        return "Was trinkst du gern?"

    if re.search(r"\bich kaufe (?:nach der arbeit )?ein\b", low):
        return "Wo kaufst du ein?"
    if low in {"im supermarkt","in der bäckerei","in der baeckerei"}:
        return "Was kaufst du heute?" if "supermarkt" in low else "Wie viel kostet ein Brot?"
    if re.search(r"\bich gehe nach hause\b", low):
        return "Lernst du heute Deutsch?"
    if re.search(r"\bich lerne deutsch\b", low):
        return "Um wie viel Uhr?"
    if "sprechen" in low and any(x in low for x in ("schwierig","schwer")):
        return "Dann üben wir Sprechen zusammen. Worüber möchtest du sprechen?"

    # Introduction -> origin -> home.
    if "wie heißt du" in last or "wie heisst du" in last:
        m=re.search(r"(?:ich heiße|ich heisse|mein name ist|ich bin)\s+([A-Za-zÄÖÜäöüß-]+)", raw, re.I)
        if m: facts["name"]=m.group(1)
        return "Freut mich! Woher kommst du?"
    if "woher kommst du" in last:
        m=re.search(r"aus\s+(.+)$", raw, re.I)
        if m: facts["origin"]=m.group(1).strip(" .")
        return "Wohnst du auch dort?"
    if "wohnst du auch dort" in last:
        return "Wo wohnst du jetzt?" if low.startswith("nein") else "Wohnst du in einem Haus oder in einer Wohnung?"
    if last in {"wo wohnst du jetzt","wo wohnst du"}:
        return "Wohnst du in einem Haus oder in einer Wohnung?"
    if "haus oder in einer wohnung" in last:
        return "Ist dein Zuhause groß oder klein?"
    if "groß oder klein" in last or "gross oder klein" in last:
        return "Welche Zimmer hast du?"
    if "welche zimmer hast du" in last:
        return "Hast du ein Sofa im Wohnzimmer?"
    if "sofa im wohnzimmer" in last:
        return "Wo steht dein Tisch?"

    # Home -> family.
    if "wo steht dein tisch" in last:
        return "Wohnst du allein oder mit deiner Familie?"
    if "allein oder mit deiner familie" in last:
        return "Hast du Kinder?" if "famil" in low or low.startswith("mit ") else "Hast du Geschwister?"
    if "hast du kinder" in last:
        return "Wie heißen deine Kinder?" if low.startswith("ja") else "Hast du Geschwister?"
    if "wie heißen deine kinder" in last or "wie heissen deine kinder" in last:
        return "Wie alt sind sie?"
    if "hast du geschwister" in last:
        return "Wo wohnen deine Geschwister?" if low.startswith("ja") else "Wo wohnen deine Eltern?"
    if "wo wohnen deine geschwister" in last:
        return "Und wo wohnen deine Eltern?"
    if "wo wohnen deine eltern" in last:
        return "Besuchst du sie oft?"
    if "besuchst du sie oft" in last:
        return "Was machst du beruflich?"

    # Work -> time -> breakfast.
    if "was machst du beruflich" in last:
        return "Wo arbeitest du?"
    if "wo arbeitest du" in last:
        return "Arbeitest du heute?"
    if "arbeitest du heute" in last:
        return "Wann fängst du an?" if low.startswith("ja") else "Was machst du heute?"
    if "wann fängst du an" in last or "wann faengst du an" in last:
        return "Und wann bist du fertig?"
    if "wann bist du fertig" in last:
        return "Trinkst du morgens Kaffee oder Tee?"
    if "kaffee oder tee" in last:
        return "Was isst du zum Frühstück?"
    if "was isst du zum frühstück" in last or "was isst du zum fruehstueck" in last:
        return "Magst du Obst?"
    if "magst du obst" in last:
        return "Welches Obst magst du?" if low.startswith("ja") else "Was isst du gern?"

    # Food -> shopping.
    if "welches obst magst du" in last or "was isst du gern" in last:
        return "Was trinkst du gern?"
    if "was trinkst du gern" in last:
        return "Was machst du nach der Arbeit?"
    if "was machst du nach der arbeit" in last:
        return "Wo kaufst du ein?" if any(x in low for x in ("kauf","supermarkt","bäck","baeck")) else "Lernst du heute Deutsch?"
    if "wo kaufst du ein" in last:
        return "Was kaufst du heute?"
    if "was kaufst du heute" in last:
        return "Kaufst du Brot im Supermarkt oder in der Bäckerei?"
    if "brot im supermarkt oder in der bäckerei" in last or "brot im supermarkt oder in der baeckerei" in last:
        return "Wie viel kostet ein Brot?"

    # Shopping -> learning -> time.
    if "wie viel kostet ein brot" in last:
        return "Was machst du danach?"
    if "was machst du danach" in last:
        return "Lernst du heute Deutsch?"
    if "lernst du heute deutsch" in last:
        return "Um wie viel Uhr?" if low.startswith("ja") else "Wann lernst du normalerweise Deutsch?"
    if "um wie viel uhr" in last:
        return "Lernst du lieber morgens oder abends?"
    if "morgens oder abends" in last:
        return "Was ist für dich beim Deutschlernen schwierig?"
    if "beim deutschlernen schwierig" in last:
        return "Dann üben wir das zusammen. Was möchtest du jetzt sagen?"

    return None
