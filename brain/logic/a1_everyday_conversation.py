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
    }
    if low in direct: return direct[low]

    # Content-led entry points. A learner may introduce a fact before Nele has
    # asked the matching question. These anchors let the new A1 bank take over
    # naturally instead of falling through to unrelated legacy topics.
    name_match=re.search(r"\\b(?:ich heiße|ich heisse|mein name ist)\\s+([A-Za-zÄÖÜäöüß-]+)", raw, re.I)
    if name_match:
        facts["name"]=name_match.group(1)
        return f"Freut mich, {name_match.group(1)}! Woher kommst du?"

    origin_match=re.search(r"\\bich komme aus\\s+(.+)$", raw, re.I)
    if origin_match:
        facts["origin"]=origin_match.group(1).strip(" .")
        return "Wo wohnst du jetzt?"

    if re.search(r"\\bich wohne (?:in|im|bei|mit)\\b", low):
        if any(x in low for x in ("wohnung", "haus")):
            facts["home_type"]="Wohnung" if "wohnung" in low else "Haus"
            return "Ist dein Zuhause groß oder klein?"
        if "famil" in low:
            return "Hast du Kinder?"
        return "Wohnst du in einem Haus oder in einer Wohnung?"

    if re.search(r"\\bich habe\\b.*\\b(?:wohnzimmer|schlafzimmer|küche|kueche|bad|zimmer)\\b", low):
        return "Hast du ein Sofa im Wohnzimmer?"
    if re.search(r"\\bich habe (?:ein|einen) sofa\\b", low):
        return "Wo steht dein Tisch?"
    if re.search(r"\\b(?:der )?tisch steht\\b", low):
        return "Wohnst du allein oder mit deiner Familie?"

    if re.search(r"\\bich habe (?:eine )?tochter\\b|\\bich habe (?:einen )?sohn\\b|\\bich habe kinder\\b", low):
        return "Wie heißen deine Kinder?"
    if re.search(r"\\bich habe (?:einen )?bruder\\b|\\bich habe (?:eine )?schwester\\b|\\bich habe geschwister\\b", low):
        return "Wo wohnen deine Geschwister?"
    if re.search(r"\\bmeine eltern wohnen\\b", low):
        return "Besuchst du sie oft?"

    if re.search(r"\\bich arbeite\\b", low):
        return "Arbeitest du heute?"
    if re.search(r"\\bich trinke morgens\\b", low):
        return "Was isst du zum Frühstück?"
    if re.search(r"\\bich esse\\b", low) and any(x in low for x in ("brot","käse","kaese","frühstück","fruehstueck")):
        return "Magst du Obst?"
    if any(x in low for x in ("äpfel","aepfel","bananen")) and not low.startswith("ich kaufe"):
        return "Was trinkst du gern?"

    if re.search(r"\\bich kaufe (?:nach der arbeit )?ein\\b", low):
        return "Wo kaufst du ein?"
    if low in {"im supermarkt","in der bäckerei","in der baeckerei"}:
        return "Was kaufst du heute?" if "supermarkt" in low else "Wie viel kostet ein Brot?"
    if re.search(r"\\bich gehe nach hause\\b", low):
        return "Lernst du heute Deutsch?"
    if re.search(r"\\bich lerne deutsch\\b", low):
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
