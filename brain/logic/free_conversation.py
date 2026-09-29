"""Natural adaptive free conversation for Nele.

The free mode follows the learner's last answer instead of running a quiz.
It keeps short conversational memory, avoids repeated questions, recasts only
clear A1 errors, and records recurring errors in shared learner state.
"""
import re

from brain.logic.vocabulary_engine import build_personalized_conversation_vocabulary
from brain.logic.conversation_state import apply_response_to_conversation_state, reset_conversation_state, set_active_slot_from_question, sync_conversation_state
from brain.logic.topic_manager import choose_topic, update_topic_manager
from brain.logic.error_engine import process_error
from brain.logic.teacher_engine import choose_teacher_action, render_teacher_prefix
from brain.logic.learner_model import build_learner_model
from brain.logic.teacher_policy import choose_next_best_learning_action, policy_to_teacher_action
from brain.logic.learning_action_executor import execute_learning_action, resolve_learning_action
from brain.logic.learning_outcome_tracker import evaluate_learning_outcome
from brain.logic.question_simplifier import simplify_question
from brain.logic.response_understanding import understand_response
from brain.logic.conversation_coherence import choose_coherent_question, update_coherence_state
from brain.logic.conversation_goal_transition import decide_topic_transition
from brain.logic.conversation_personalization import remember_conversation_facts, choose_personalized_followup
from brain.logic.conversation_quality_controller import check_reply
from brain.logic.conversation_recovery import recover_reply
from brain.logic.conversation_orchestrator import build_turn_plan, build_orchestration_contract, enforce_orchestration, record_orchestration
from brain.logic.turn_plan_compliance import evaluate_turn_plan_compliance, record_turn_plan_compliance
from brain.logic.global_conversation_guard import record_answer, select_question, replace_final_question
from brain.logic.personal_sentences import handle_personal_sentence
from brain.logic.a1_everyday_conversation import a1_everyday_reply
from brain.logic.dialogue_engine import auto_start_dialogue_from_message, find_dialogue_for_message, is_dialogue_active, handle_dialogue, clear_dialogue
from brain.logic.wellbeing_feedback import analyze_wellbeing_response
from brain.logic.learner_turn import analyze_learner_turn, direct_nele_answer, question_slot
from brain.logic.knowledge_retriever import retrieve

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
    "A1.2": {"yesterday", "family", "friends", "food"},
    "A1.3": {"housing", "weekend"},
    "A2.1": {"transport", "technology", "health"},
}

FALLBACKS = {
    "today": ["Was machst du heute?", "Was möchtest du heute noch machen?", "Wie ist dein Tag heute?"],
    "place": ["Wo bist du gerade?", "Bist du gern dort?", "Was machst du dort gern?"],
    "shopping": ["Was möchtest du kaufen?", "Welche Farbe möchtest du?", "Wo kaufst du gern ein?"],
    "food": ["Was isst du gern?", "Was isst du heute?", "Was kochst du gern?", "Was isst du gern zum Frühstück?", "Kochst du gern, oder isst du lieber im Restaurant?", "Magst du deutsches Essen?"],
    "work": ["Arbeitest du heute?", "Wann fängst du an?", "Was machst du bei der Arbeit?"],
    "hobby": ["Was machst du gern in deiner Freizeit?", "Hörst du gern Musik?", "Machst du gern Sport?"],
    "weather": ["Wie ist das Wetter bei dir?", "Ist es warm oder kalt?", "Magst du das Wetter heute?"],
    "holiday": ["Wo machst du gern Urlaub?", "Meer oder Berge – was magst du lieber?", "Was machst du gern im Urlaub?"],
    "yesterday": ["Was hast du gestern gemacht?", "Wie war dein Tag gestern?"],
    "family": ["Hast du Geschwister?", "Wie oft siehst du deine Familie?", "Wohnt deine Familie in der Nähe?"],
    "friends": ["Hast du viele Freunde hier?", "Wie oft triffst du deine Freunde?", "Was macht ihr zusammen?"],
    "housing": ["Wohnst du in einer Wohnung oder in einem Haus?", "Wohnst du allein oder mit anderen?", "Gefällt dir deine Wohnung?"],
    "weekend": ["Was machst du am Wochenende?", "Schläfst du am Wochenende länger?", "Triffst du am Wochenende Freunde?"],
    "transport": ["Wie kommst du zur Arbeit?", "Fährst du gern mit dem Fahrrad?", "Ist der Bus bei dir meistens pünktlich?"],
    "technology": ["Wie viele Stunden bist du am Handy?", "Nutzt du WhatsApp oder Instagram?", "Schaust du lieber Serien, oder liest du lieber?"],
    "health": ["Wie fühlst du dich heute körperlich?", "Machst du regelmäßig Sport für die Gesundheit?", "Warst du dieses Jahr schon beim Arzt?"],
}

TOPIC_TRANSITION_BRIDGES = {
    "today": "Und jetzt zu deinem Tag:",
    "place": "Und wo wir gerade über deinen Alltag sprechen:",
    "shopping": "Noch etwas aus dem Alltag:",
    "food": "Und noch etwas Alltägliches:",
    "work": "Und wie ist es bei der Arbeit?",
    "hobby": "Und nach dem Alltag etwas Schönes:",
    "weather": "Und noch etwas von heute:",
    "holiday": "Und wenn du frei hast:",
    "yesterday": "Und noch kurz zu gestern:",
    "family": "Und noch etwas Persönliches:",
    "friends": "Und wie ist es mit deinen Freunden?",
    "housing": "Und zu deinem Zuhause:",
    "weekend": "Und wenn Wochenende ist:",
    "transport": "Und unterwegs im Alltag:",
    "technology": "Und im Alltag mit Technik:",
    "health": "Und noch zu deinem Wohlbefinden:",
}

def _smooth_topic_transition(question, topic):
    bridge = TOPIC_TRANSITION_BRIDGES.get(topic)
    if not bridge or not question:
        return question
    return f"{bridge} {question}"

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
    elif any(x in low for x in ("hobby", "freizeit", "musik", "sport", "lesen", "buch", "krimi")):
        facts["topic"] = "hobby"
    elif any(x in low for x in ("wetter", "sonne", "regen", "kalt", "warm")):
        facts["topic"] = "weather"
    elif any(x in low for x in ("urlaub", "reise", "ferien", "meer", "berge")):
        facts["topic"] = "holiday"
    elif "gestern" in low:
        facts["topic"] = "yesterday"
    elif low.startswith("ich komme aus ") or low.startswith("ich wohne in "):
        # Origin/residence is an explicit place branch and must expire stale
        # sticky topics such as food.
        facts["topic"] = "place"
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

def _question_key(question):
    return re.sub(r"[^a-zäöüß0-9]+", " ", _norm(question)).strip()

def _remember_question(free, question):
    if not question:
        return
    # Replies may contain an A1 model sentence followed by the actual question.
    # Store only the final question so Conversation State can infer the expected
    # answer type and the next turn can route against the real prompt.
    parts = re.findall(r"[^.!?]*[?]", str(question))
    actual_question = parts[-1].strip() if parts else str(question).strip()
    actual_question = actual_question.lstrip("„“”\"' ").strip()
    free["last_question"] = actual_question
    semantic_slot = question_slot(actual_question)
    free["last_question_context"] = {"slot": semantic_slot, "topic": free.get("last_topic")}
    asked = free.setdefault("asked", [])
    key = _question_key(actual_question)
    if key and key not in asked:
        asked.append(key)
    history = free.setdefault("recent_questions", [])
    if not history or history[-1] != actual_question:
        history.append(actual_question)
    del history[:-8]

SUBTOPIC_QUESTIONS = {
    ("hobby", "reading"): [
        ("reading_genre", "Was liest du gern?"),
        ("reading_detail", "Was gefällt dir daran?"),
        ("reading_frequency", "Liest du oft?"),
    ],
    ("hobby", "music"): [
        ("music_genre", "Welche Musik hörst du gern?"),
        ("music_artist", "Wer ist dein Lieblingssänger?"),
        ("music_frequency", "Hörst du oft Musik?"),
    ],
    ("hobby", "sport"): [
        ("sport_kind", "Welchen Sport machst du gern?"),
        ("sport_companion", "Mit wem machst du Sport?"),
        ("sport_frequency", "Wie oft machst du das?"),
    ],
    ("food", "essen"): [
        ("food", "Was isst du gern?"),
        ("food_detail", "Wie isst du das gern?"),
        ("food_frequency", "Wie oft isst du das?"),
    ],
    ("personal", "birthday"): [
        ("birthday", "Wann hast du Geburtstag?"),
        ("birthday_company", "Mit wem feierst du deinen Geburtstag?"),
        ("birthday_activity", "Was machst du an deinem Geburtstag gern?"),
    ],
}

# Once a semantic mini-thread has collected its core slots, do not silently
# fall back to a broad topic opener. Use one explicit bridge that stays related
# to what the learner just said, then let normal topic-transition policy decide.
SUBTOPIC_COMPLETION = {
    ("hobby", "reading"): ("reading_place", "Interessant. Liest du lieber zu Hause oder unterwegs?"),
    ("hobby", "music"): ("music_place", "Schön. Hörst du Musik lieber zu Hause oder unterwegs?"),
    ("hobby", "sport"): ("sport_environment", "Schön. Machst du diesen Sport lieber draußen oder drinnen?"),
    ("food", "essen"): ("food_place", "Verstehe. Isst du das lieber zu Hause oder im Restaurant?"),
    ("personal", "birthday"): ("birthday_preference", "Schön. Magst du Geburtstage?"),
}


def _subtopic_followup(topic, subtopic, free, memory, state=None):
    """Continue an established semantic subtopic without keyword hardcoding."""
    pool = SUBTOPIC_QUESTIONS.get((topic, subtopic))
    if not pool:
        return None
    asked = {_norm(q).strip(" ?!.") for q in free.get("recent_questions", [])}
    slots = memory.setdefault("subtopic_slots", {})
    key = f"{topic}/{subtopic}"
    filled = int(slots.get(key, 0) or 0)

    # Canonical semantic_slots is the primary owner of completed semantic
    # answers. Legacy reading memory remains only as a compatibility hint for
    # older routes; it must not decide progression ahead of canonical state.
    semantic_slots = (((state or {}).get("conversation_state_v2") or {}).get("semantic_slots") or {})
    canonical_filled = 0
    for slot_name, _question in pool:
        if slot_name in semantic_slots:
            canonical_filled += 1
        else:
            break
    # Once canonical semantic state exists, it alone determines progression.
    # The legacy numeric cursor is only a bootstrap fallback for conversations
    # that have not produced any canonical slot yet. Combining both owners can
    # skip unanswered slots and rewind reading threads.
    if canonical_filled:
        filled = canonical_filled
    elif key == "hobby/reading":
        if memory.get("reading_kind"):
            filled = max(filled, 1)
        if memory.get("reading_detail"):
            filled = max(filled, 2)
    slots[key] = filled

    for i, (_slot, question) in enumerate(pool):
        if _slot in semantic_slots:
            continue
        if canonical_filled == 0 and i < filled:
            continue
        if _norm(question).strip(" ?!.") in asked:
            continue
        slots[key] = i + 1
        if state is not None:
            set_active_slot_from_question(state, _slot)
        return question

    completion = SUBTOPIC_COMPLETION.get((topic, subtopic))
    completion_key = f"{key}/completion"
    if completion:
        bridge_slot, bridge_question = completion
    else:
        bridge_slot, bridge_question = None, None
    if bridge_question and not slots.get(completion_key) and _norm(bridge_question).strip(" ?!.") not in asked:
        slots[completion_key] = 1
        if state is not None:
            set_active_slot_from_question(state, bridge_slot)
            (state.get("conversation_state_v2") or {})["subtopic_status"] = "bridging"
        return bridge_question
    return None


def _not_recent(free, candidates):
    asked = set(free.get("asked", []))
    return [q for q in candidates if _question_key(q) not in asked]

def _content_question_repair(text, last_question):
    """Keep the topic when a yes/no answer cannot answer an open content question."""
    low = _norm(text).strip(" ?!.,")
    if low not in YES | NO:
        return None
    q = _norm(last_question).strip(" ?!.,")
    prompts = (
        ("welche musik", "Ich meine: Welche Musik? Zum Beispiel Pop, Rock oder Klassik."),
        ("welchen sport", "Ich meine: Welchen Sport? Zum Beispiel Fußball, Schwimmen oder Radfahren."),
        ("was ", "Ich meine: Was genau? Sag mir bitte ein Beispiel."),
        ("wo ", "Ich meine: Wo genau? Sag mir bitte einen Ort."),
        ("wann ", "Ich meine: Wann genau? Zum Beispiel morgens, abends oder um 8 Uhr."),
        ("wie viel", "Ich meine: Wie viel genau? Sag mir bitte eine Zahl."),
        ("wie viele", "Ich meine: Wie viele genau? Sag mir bitte eine Zahl."),
    )
    for prefix, repair in prompts:
        if q.startswith(prefix):
            return repair
    return None

def _yes_no_followup(text, last_question, facts):
    low = _norm(text).strip(" ?!.,")
    affirmative = re.sub(r"[^a-zäöüß ]+", "", low).strip()
    yes = low in YES or affirmative in {"ja sehr gern", "ja gern", "sehr gern"}
    no = low in NO
    if not (yes or no):
        return None

    q = _norm(last_question)
    if "suchst du sportschuhe" in q:
        return "Welche Farbe möchtest du?" if yes else "Welche Schuhe suchst du?"
    if "arbeitest du heute" in q:
        return "Wann fängst du an?" if yes else "Heute hast du also frei. Was machst du heute?"
    if "kochst du jeden tag bei der arbeit" in q:
        return "Was kochst du gern bei der Arbeit?" if yes else "Was machst du sonst bei der Arbeit?"
    if "kochst du auch gern etwas anderes" in q:
        return "Was kochst du noch gern?" if yes else "Was kochst du am liebsten?"
    if "kochst du sie oft" in q or "kochst du das oft" in q:
        return "Was kochst du noch gern?" if yes else "Was kochst du lieber?"
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
        return "Fährst du lieber allein oder mit jemandem?" if yes else "Wo fährst du lieber Rad?"
    if "schwimmst du dort im sommer" in q:
        return "Gehst du auch im Winter schwimmen?" if yes else "Wann schwimmst du dort gern?"
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
        return "Das klingt gut. Und wie ist dein Tag heute?" if yes else "Oh, schade. Suchst du noch weiter?"
    if "magst du das wetter heute" in q:
        return "Was machst du bei diesem Wetter gern?" if yes else "Was machst du bei diesem Wetter lieber?"
    if "magst du das wetter" in q:
        return "Was machst du bei diesem Wetter gern?" if yes else "Was machst du bei diesem Wetter lieber?"
    return None

def _social_a1_reply(text, free, state):
    """Core A1 greetings, wellbeing and introductions with gentle modelling."""
    raw = str(text or "").strip()
    low = _norm(raw)
    last = _norm(free.get("last_question", ""))

    # A1 lessons 1-10: reusable natural conversation, not a fixed script.
    everyday_reply = a1_everyday_reply(raw, free.get("last_question", ""), state)
    if everyday_reply:
        return everyday_reply

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

    # Wellbeing: a clear learner-led question must outrank stale topic context.
    wellbeing_ask = low.strip(" ?!.")
    if any(phrase in wellbeing_ask for phrase in (
        "wie geht es dir", "wie geht's dir", "wie gehts dir",
        "wie geht es ihnen", "wie geht's ihnen", "wie gehts ihnen",
    )):
        return "Mir geht es gut, danke. Und dir?"

    if wellbeing_ask in {"wie geht's", "wie gehts", "alles gut", "alles klar"}:
        return "Mir geht es gut, danke. Und dir?"

    # A clear tiredness statement is a learner-led topic change too.
    if re.search(r"\b(?:ich\s+bin(?:\s+heute)?|heute\s+bin\s+ich)\s+müde\b", low):
        free.setdefault("conversation_facts", {})["wellbeing"] = "müde"
        return "Oh, du bist heute müde. War dein Tag anstrengend?"

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
    # Previous weather context may interpret an ANSWER, but it must never
    # capture a new learner-led question about another topic.
    if explicit_weather or (weather_context and not _is_explicit_learner_question(raw)):
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
        "was machst du gern": "Ich spreche gern mit dir. Ich höre auch gern, was du erzählst. Was kochst du zum Beispiel gern?",
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

    # Learner-led free-time questions outrank stale conversation context.
    # Match natural variants instead of hard-coding one exact sentence.
    if re.fullmatch(
        r"was\s+machst\s+du\s+gern(?:e)?(?:\s+(?:am|an)\s+(?:wochenende|wochenenden))?",
        everyday_key,
    ):
        if "wochenend" in everyday_key:
            return "Am Wochenende höre ich gern Musik und spreche mit dir. Und du?"
        return "Ich spreche gern mit dir. Und du?"

    # A clear learner statement with "gern" is meaningful new content. React
    # to that content before generic teacher/fallback logic can revive an old
    # topic and produce an unrelated "Kein Problem" response.
    gern_statement = re.fullmatch(r"ich\s+(.+?)\s+gern(?:e)?(?:\s+(.+))?", everyday_key)
    if gern_statement:
        activity = gern_statement.group(1).strip()
        detail = (gern_statement.group(2) or "").strip()
        if activity in {"lerne", "lern"} and ("deutsch" in detail or not detail):
            free.setdefault("conversation_facts", {})["learning"] = "Deutsch"
            return "Schön! Lernst du jeden Tag Deutsch?"
        if activity in {"höre", "hoere"} and "musik" in detail:
            return "Schön! Welche Musik hörst du gern?"
        if activity in {"lese", "les"}:
            return "Schön! Was liest du gern?"
        if activity in {"koche", "koch"}:
            return "Schön! Was kochst du gern?"
        if activity in {"schwimme", "schwimm"}:
            return "Schön! Wo schwimmst du gern?"
        return "Schön! Was machst du sonst noch gern?"

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

    # Cooking subthread must win over the broad "Arbeit" context.
    # These are contextual yes/no answers, not a new answer to "Arbeitest du?".
    if "kochst du auch gern etwas anderes" in last:
        if low in {"ja", "ja gern", "ja, gern"}:
            return "Was kochst du noch gern?"
        if low in {"nein", "nein heute nicht", "heute nicht"}:
            return "Was kochst du am liebsten?"

    # A specific work question must win over the broad "Arbeit" context.
    # Otherwise "ja" after cooking restarts the work-start questions.
    if "kochst du jeden tag bei der arbeit" in last:
        if low in {"ja", "ja gern", "ja, gern"}:
            return "Was kochst du gern bei der Arbeit?"
        if low in {"nein", "nein heute nicht", "heute nicht"}:
            return "Was machst du sonst bei der Arbeit?"

    if any(x in last for x in ("arbeitest du", "arbeit", "wann fängst du", "wann faengst du")):
        if low in {"ja", "ja gern", "ja, gern"}:
            return "Wann fängst du heute an?"
        if low in {"nein", "nein heute nicht", "heute nicht"}:
            return "Dann hast du heute frei. Was machst du heute?"
        match = re.fullmatch(r"(?:um\s+)?(\d{1,2})(?::(\d{2}))?(?:\s+uhr)?", low)
        if match:
            hour = match.group(1)
            minute = match.group(2)
            time_value = f"{hour}:{minute}" if minute else hour
            free.setdefault("conversation_facts", {})["work_start"] = time_value
            return f"Du kannst sagen: „Ich fange um {time_value} Uhr an.“ Was machst du bei der Arbeit?"

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
        # Shared engine: recognition, corrections and canonical A1 model
        # sentences live in wellbeing_feedback.py. Free mode owns only the
        # conversational policy that follows the recognized meaning.
        analysis = analyze_wellbeing_response(raw)
        if analysis.get("recognized"):
            wellbeing_type = analysis.get("type")
            model = analysis.get("model_sentence")
            feedback = analysis.get("feedback")
            reaction = analysis.get("reaction") or ""

            free.setdefault("conversation_facts", {})["wellbeing"] = wellbeing_type

            if wellbeing_type == "bad":
                follow_up = "Warum geht es dir nicht gut?"
            elif wellbeing_type == "tired":
                follow_up = "War dein Tag anstrengend?"
            elif wellbeing_type == "stressed":
                follow_up = "Möchtest du kurz und ruhig weitermachen?"
            elif wellbeing_type == "sad":
                follow_up = "Möchtest du ein bisschen reden?"
            elif wellbeing_type == "sick":
                follow_up = "Möchtest du heute nur etwas Leichtes machen?"
            else:
                follow_up = "Was machst du heute?"

            if feedback:
                return f"{feedback} {reaction} {follow_up}".strip()
            if model:
                return f"{reaction} Du kannst auch sagen: „{model}“ {follow_up}".strip()
            return f"{reaction} {follow_up}".strip()

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


def _is_explicit_learner_question(text):
    """True for a clear learner-led question that must outrank stale context."""
    raw = str(text or "").strip()
    if "?" not in raw:
        return False
    low = _norm(raw).strip(" .?!")
    # Spoken German often hands the turn back with "Und ...?", "Aber ...?"
    # or "Also ...?". These particles do not change the question's intent.
    low = re.sub(r"^(?:(?:und|aber|also)\s+)+", "", low)
    starts = (
        "was ", "wie ", "wo ", "woher ", "wohin ", "wann ", "warum ", "wer ",
        "welcher ", "welche ", "welches ", "arbeitest ", "wohnst ", "isst ",
        "trinkst ", "magst ", "machst ", "hast ", "bist ", "kommst ",
    )
    return low.startswith(starts)


PERFECT_FORMS = {
    "lesen": ("habe", "gelesen"),
    "spielen": ("habe", "gespielt"),
    "arbeiten": ("habe", "gearbeitet"),
    "kochen": ("habe", "gekocht"),
    "gehen": ("bin", "gegangen"),
    "fahren": ("bin", "gefahren"),
}

def _perfect_sentence(verb):
    form = PERFECT_FORMS.get(_norm(verb))
    if not form:
        return None
    auxiliary, participle = form
    return f"Ich {auxiliary} gestern {participle}."

def _short_answer_followup(text, last_question, memory):
    """Interpret a short A1 answer through the question Nele asked before."""
    raw = str(text or "").strip()
    low = _norm(raw).strip(" .?!")
    question = _norm(last_question)

    if not low or len(_words(low)) > 5:
        return None

    # Yesterday context controls tense for short verb answers. Keep the thread
    # alive instead of converting "lesen" into the timeless "Ich lese gern".
    if "gestern" in question or "hast du" in question and "gemacht" in question:
        model = _perfect_sentence(low)
        if model:
            memory["yesterday_activity"] = low
            memory.setdefault("filled_slots", {})["yesterday_activity"] = low
            if low == "lesen":
                return f"Du kannst sagen: „{model}“ Was hast du gelesen?"
            return f"Du kannst sagen: „{model}“ Was hast du danach gemacht?"
        if re.match(r"^ich\s+(?:habe|bin)\b.+\b(?:gelesen|gespielt|gearbeitet|gekocht|gegangen|gefahren)\b", low):
            memory["yesterday_sentence"] = raw
            if "gelesen" in low:
                return "Was hast du gelesen?"
            return "Was hast du danach gemacht?"

    # Work start time: acknowledge the learner's short time answer and keep
    # the work thread. A bare number is meaningful because of the last question.
    if "wann fängst du an" in question or "wann faengst du an" in question:
        match = re.fullmatch(r"(?:um\s+)?(\d{1,2})(?::(\d{2}))?(?:\s+uhr)?", low)
        if match:
            hour = match.group(1)
            minute = match.group(2)
            time_value = f"{hour}:{minute}" if minute else hour
            memory["work_start"] = time_value
            memory.setdefault("filled_slots", {})["work_start"] = time_value
            return f"Du kannst sagen: „Ich fange um {time_value} Uhr an.“ Was machst du bei der Arbeit?"

    # A yes/no answer after the cooking follow-up belongs to the cooking
    # subthread; do not let the broad work router restart the work interview.
    if "kochst du jeden tag bei der arbeit" in question and low in {"ja", "ja genau", "ja natürlich", "ja natuerlich"}:
        memory["work_activity"] = "kochen"
        return "Ja, genau. Was kochst du gern bei der Arbeit?"
    if "kochst du jeden tag bei der arbeit" in question and low in {"nein", "nein nicht jeden tag"}:
        memory["work_activity"] = "kochen"
        return "Verstehe. Was kochst du gern bei der Arbeit?"

    # Arbeit: "Bis wann arbeitest du?" -> "Bis 2."
    if "bis wann arbeitest du" in question:
        match = re.fullmatch(r"(?:bis\s+)?(\d{1,2})(?::(\d{2}))?(?:\s+uhr)?", low)
        if match:
            hour = match.group(1)
            minute = match.group(2)
            time_value = f"{hour}:{minute}" if minute else hour
            memory["work_until"] = time_value
            return f"Du kannst sagen: „Ich arbeite bis {time_value} Uhr.“ Was machst du danach?"

    # Arbeit: "Was machst du bei der Arbeit?" -> one activity.
    if "was machst du" in question and "arbeit" in question:
        activities = {
            "kochen": ("Ich koche.", "Kochst du jeden Tag bei der Arbeit?"),
            "putzen": ("Ich putze.", "Was putzt du bei der Arbeit?"),
            "reinigen": ("Ich reinige.", "Was reinigst du bei der Arbeit?"),
            "zimmer reinigen": ("Ich reinige Zimmer.", "Wie viele Zimmer reinigst du normalerweise?"),
        }
        if low in activities:
            model, follow_up = activities[low]
            memory["work_activity"] = low
            memory.setdefault("filled_slots", {})["work_activity"] = low
            return f"Du kannst sagen: „{model}“ {follow_up}"

    # Cooking at work: short food nouns answer "Was kochst du gern ...?".
    # Keep the cooking branch alive instead of falling back to generic work.
    if "was kochst du gern" in question:
        foods = {"pizza", "brot", "salat", "nudeln", "reis", "suppe", "fleisch", "gemüse", "gemuese"}
        if low in foods:
            food = "Gemüse" if low == "gemuese" else raw.strip(" .?!").capitalize()
            memory["cooked_food"] = food
            memory.setdefault("filled_slots", {})["cooked_food"] = food
            return f"Du kannst sagen: „Ich koche gern {food}.“ Kochst du auch gern etwas anderes?"

    # Follow-up after a cooking preference stays with food.
    if "kochst du auch gern etwas anderes" in question:
        foods = {"pizza", "brot", "salat", "nudeln", "reis", "suppe", "fleisch", "gemüse", "gemuese"}
        if low in foods:
            food = "Gemüse" if low == "gemuese" else raw.strip(" .?!").capitalize()
            memory["other_cooked_food"] = food
            return f"Schön! Du kannst sagen: „Ich koche auch gern {food}.“ Was kochst du am liebsten?"

    # A food noun after "Was kochst du noch gern?" remains in the cooking thread.
    if "was kochst du noch gern" in question:
        foods = {"pizza", "brot", "salat", "nudeln", "reis", "suppe", "fleisch", "gemüse", "gemuese"}
        if low in foods:
            food = "Gemüse" if low == "gemuese" else raw.strip(" .?!").capitalize()
            memory["other_cooked_food"] = food
            return f"Du kannst sagen: „Ich koche auch gern {food}.“ Was kochst du am liebsten?"

    # Favourite cooked food: keep the same cooking thread for another food noun.
    if "was kochst du am liebsten" in question:
        foods = {"pizza", "brot", "salat", "nudeln", "reis", "suppe", "fleisch", "gemüse", "gemuese"}
        if low in foods:
            food = "Gemüse" if low == "gemuese" else raw.strip(" .?!").capitalize()
            memory["favorite_cooked_food"] = food
            return f"Du kannst sagen: „Am liebsten koche ich {food}.“ Wie kochst du {food} gern?"

    # Cooking context: once the learner says they cook, short food/detail
    # turns belong to that local thread even if the previous generic question
    # still mentions "today". This is stronger than broad topic routing.
    if memory.get("cooking_thread"):
        foods = {"pizza", "brot", "salat", "nudeln", "reis", "suppe", "fleisch", "gemüse", "gemuese"}
        if low in foods:
            food = "Gemüse" if low == "gemuese" else raw.strip(" .?!").capitalize()
            memory["cooked_food"] = food
            return f"{food}? Was kommt bei dir auf die {food}?"
        if low.startswith("mit ") and memory.get("cooked_food"):
            detail = raw.strip(" .?!")
            return f"{detail} klingt gut. Kochst du das oft?"

    # Essen: a food noun is a valid answer, not a new unrelated topic.
    if any(key in question for key in ("was isst du", "was hast du gegessen", "was möchtest du essen")):
        if low in {"pizza", "brot", "salat", "nudeln", "reis", "suppe", "fleisch", "gemüse", "gemuese"}:
            food = "Gemüse" if low == "gemuese" else raw.strip(" .?!").capitalize()
            memory["food"] = food
            return f"Du kannst sagen: „Ich esse gern {food}.“ Isst du das oft?"

    # Hobby activity: a one-word answer such as "spazieren" already answers
    # "Was machst du gern ...?". Move the thread forward instead of asking the
    # same semantic question again.
    if ("was machst du gern" in question or "freizeit" in question) and low in {"spazieren", "spazieren gehen"}:
        memory["hobby_activity"] = "spazieren"
        memory.setdefault("filled_slots", {})["hobby_activity"] = "spazieren"
        return "Gehst du lieber allein oder mit jemandem spazieren?"

    # Company: "Mit wem ...?" / "allein oder mit jemandem?"
    if "mit wem" in question or "allein oder mit jemandem" in question:
        if low in {"mit meinem mann", "mit meiner frau", "mit freunden", "mit meiner familie"}:
            memory["activity_company"] = raw.strip(" .?!")
            return f"Schön! {raw.strip(' .?!').capitalize()}. Macht ihr das oft zusammen?"

    return None


def _model_sentence_from_knowledge(user_message, topic, level="A1", free_state=None):
    """Use shared knowledge only when it is a close semantic match."""
    free_state = free_state if isinstance(free_state, dict) else {}
    recent = free_state.setdefault("recent_knowledge", [])
    items = retrieve(
        query=user_message,
        topic=topic,
        level=str(level or "A1").split(".")[0],
        intent="model_sentence",
        sources=("dialogue", "meine_saetze"),
        limit=5,
        recently_used=tuple(recent),
    )
    if not items:
        return None
    best = items[0]
    # Avoid inventing unrelated learner meaning. The retriever must have a
    # concrete lexical match in addition to topic/level ranking.
    query_words = {w for w in _words(_norm(user_message)) if len(w) >= 3}
    text_low = _norm(best.text)
    if not query_words or not any(word in text_low for word in query_words):
        return None
    # RETRIEVE only selects knowledge. LEARN records it later, after the
    # response pipeline has accepted the MODEL_SENTENCE action.
    free_state["_pending_knowledge_usage"] = {
        "item_id": best.item_id,
        "source": best.source,
        "text": best.text,
        "topic": best.topic,
        "level": best.level,
        "intent": "model_sentence",
    }
    return best.text


def _learn_pending_knowledge(free_state, learning_action):
    """Commit retrieved knowledge only after it reached the response action."""
    if not isinstance(free_state, dict):
        return None
    pending = free_state.pop("_pending_knowledge_usage", None)
    if not isinstance(pending, dict):
        return None
    if (learning_action or {}).get("action") != "MODEL_SENTENCE":
        return None
    knowledge_key = pending.get("item_id") or pending.get("text")
    if knowledge_key:
        recent = free_state.setdefault("recent_knowledge", [])
        recent.append(knowledge_key)
        del recent[:-8]
    usage = free_state.setdefault("knowledge_usage", [])
    usage.append(dict(pending))
    del usage[:-20]
    return dict(pending)


def _model_sentence_from_turn(user_message, topic, subtopic=None):
    """Build a simple A1 model from the learner's current meaning."""
    raw = str(user_message or "").strip(" .?!")
    low = _norm(raw)
    if not raw:
        return None
    if re.fullmatch(r"(?:pizza|brot|salat|nudeln|reis|suppe|fleisch|gemüse|gemuese)", low):
        food = "Gemüse" if low == "gemuese" else raw.capitalize()
        return f"Ich esse gern {food}."
    if low in {"lesen", "bücher lesen", "buch lesen"}:
        return "Ich lese gern."
    if low in {"musik", "musik hören", "musik hoeren"}:
        return "Ich höre gern Musik."
    if low in {"schwimmen", "sport", "radfahren", "rad fahren"}:
        forms = {
            "schwimmen": "Ich schwimme gern.",
            "sport": "Ich mache gern Sport.",
            "radfahren": "Ich fahre gern Rad.",
            "rad fahren": "Ich fahre gern Rad.",
        }
        return forms[low]
    if topic == "work" and low in {"kochen", "putzen", "reinigen"}:
        forms = {"kochen": "Ich koche.", "putzen": "Ich putze.", "reinigen": "Ich reinige."}
        return forms[low]
    # If the learner already supplied a usable first-person sentence, the
    # curriculum model can reinforce that meaning without inventing content.
    if re.match(r"^ich\s+[a-zäöüß]+(?:\s+.+)?$", low) and "?" not in raw:
        return raw[0].upper() + raw[1:] + "."
    return None


def _correction_followup(error_result, topic, memory):
    """Continue from the corrected meaning instead of abandoning the subtopic."""
    error = (error_result or {}).get("error") or {}
    correct = str(error.get("correct") or "").strip()
    if not correct or not (error_result or {}).get("recast"):
        return None
    low = _norm(correct)
    if topic == "work" or "koche " in low:
        match = re.match(r"ich koche\s+(.+?)[.!]?$", correct, re.I)
        if match:
            food = match.group(1).strip(" .")
            memory["cooked_food"] = food
            memory.setdefault("filled_slots", {})["cooked_food"] = food
            return f"Kochst du oft {food}?"
    if "ich höre " in low:
        return "Welche Musik hörst du am liebsten?"
    if "ich kaufe " in low:
        return "Wo kaufst du das gern?"
    if "ich fahre gern rad" in low:
        return "Wo fährst du gern Rad?"
    if "ich schwimme gern" in low:
        return "Wo schwimmst du gern?"
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
        return "Du schwimmst gern. Schwimmst du oft?"

    if re.search(r"\bich\s+arbeite\b", low):
        return "Wann fängst du an?"
    if re.search(r"\bich\s+(?:höre|mag)\b.*musik", low):
        return "Welche Musik hörst du gern?"
    if re.search(r"\bich\s+lese\b", low):
        if re.search(r"\bkrimis?\b", low):
            memory["reading_kind"] = "Krimis"
            return "Krimis? Welche Krimis liest du gern?"
        return "Was liest du gern?"
    last_reading_question = _norm(free.get("last_question", ""))
    if (
        memory.get("reading_kind") == "Krimis"
        and "welche krimis liest du gern" in last_reading_question
        and re.search(r"\bkommissar(?:e|en|in|innen)?\b", low)
    ):
        memory["reading_detail"] = "Kommissare"
        return "Liest du solche Krimis oft?"
    if re.search(r"\bkrimis?\b", low):
        memory["reading_kind"] = "Krimis"
        if "welche krimis liest du gern" in last_reading_question:
            return "Was gefällt dir an Krimis besonders?"
        return "Krimis? Welche Krimis liest du gern?"
    if memory.get("cooking_thread") and re.search(r"\b(?:ich meine\s+)?pizza\b", low):
        memory["cooked_food"] = "Pizza"
        return "Ja, Pizza. Kochst du sie oft?"

    return None

def _semantic_fallbacks(topic, state):
    """Remove fallback questions whose semantic answer is already known."""
    pool = list(FALLBACKS.get(topic, FALLBACKS["today"]))
    slots = ((state.get("conversation_state_v2") or {}).get("semantic_slots") or {})
    if topic == "food" and (slots.get("food") or slots.get("food_item")):
        pool = [q for q in pool if _question_key(q) != _question_key("Was isst du gern?")]
    return pool


def _generic_followup(topic, free, support, independent, level, state=None):
    allowed = _allowed_skills(level)
    if topic == "yesterday" and "yesterday" not in allowed:
        topic = "today"
    pool = _not_recent(free, _semantic_fallbacks(topic, state or {}))
    filled = free.get("conversation_facts", {}).get("filled_slots", {})
    if topic == "work":
        if filled.get("work_start"):
            pool = [q for q in pool if _question_key(q) != _question_key("Wann fängst du an?")]
        if filled.get("work_activity"):
            pool = [q for q in pool if _question_key(q) != _question_key("Was machst du bei der Arbeit?")]
    if not pool:
        topic_order = ["work", "hobby", "food", "today", "weather", "holiday", "place", "shopping", "yesterday"]
        for next_topic in topic_order:
            if next_topic == topic or next_topic not in allowed:
                continue
            pool = _not_recent(free, FALLBACKS.get(next_topic, []))
            if pool:
                break
    if not pool:
        return "Erzähl mir noch etwas darüber."
    # More independent learners get the more open end of the same A1 material.
    index = -1 if independent >= 3 and support == 0 else 0
    return pool[index]

def generate_free_welcome(state, session_id=None):
    free = state.setdefault("free_conversation", {})

    # Entering free mode is a hard boundary: a dialogue inherited from course
    # mode must never own the free-conversation welcome.
    if is_dialogue_active(state):
        clear_dialogue(state)
        state.pop("dialogue_origin", None)
    index = int(free.get("welcome_index", 0) or 0)
    free["welcome_index"] = (index + 1) % len(OPENERS)
    free["last_question"] = OPENERS[index]
    free["recent_questions"] = [OPENERS[index]]
    free["asked"] = [_question_key(OPENERS[index])]
    free["turn_count"] = 0
    free["support_level"] = 1
    free["independent_turns"] = 0
    free["struggle_turns"] = 0
    free["topic_turns"] = 0
    free["conversation_facts"] = {}
    free.setdefault("error_counts", {})
    level = state.setdefault("student_progress", {}).setdefault("current_level", "A1.1")
    reset_conversation_state(state, opener=OPENERS[index], level=level)
    return OPENERS[index]

def _should_activate_dialogue_in_free(dialogue):
    """Return True only when a dialogue represents a concrete role-play.

    Active dialogues contain both conversational knowledge (birthday, hobbies,
    music, sport, travel preferences) and transactional/situational practice
    (directions, invitations, station, post, bus, package).  A knowledge match
    must not by itself transfer ownership away from Conversation Engine.
    """
    if not isinstance(dialogue, dict):
        return False

    topic = _norm(dialogue.get("topic", ""))
    section = _norm(dialogue.get("section", ""))
    situation = _norm(dialogue.get("situation", ""))
    text = " ".join((topic, section, situation))

    # Concrete role-play families. Keep this semantic and data-driven from
    # dialogue metadata; do not key it to individual learner answers.
    roleplay_patterns = (
        r"\bweg(?:beschreibung)?\b",
        r"\bbahnhof\b",
        r"\bpost\b",
        r"\bbus\b",
        r"\bfahrkarte\b",
        r"\bzugverbindung\b",
        r"\beinladung\b",
        r"\beinladen\b",
        r"\babsagen\b",
        r"\bpaket\b",
    )
    return any(re.search(pattern, text) for pattern in roleplay_patterns)


def generate_free_conversation_reply(user_message, state, session_id=None):
    free = state.setdefault("free_conversation", {})

    # A dialogue may continue in free mode only when free mode started it.
    # This also protects reload/direct-entry paths that skip generate_free_welcome().
    if is_dialogue_active(state) and state.get("dialogue_origin") != "free":
        clear_dialogue(state)
        state.pop("dialogue_origin", None)

    # Priority -3: reusable Dialogue Knowledge router. A concrete dialogue may
    # start later in free conversation only when the learner asks an explicit
    # new-topic question that is not already handled by the active A1 context.
    dialogue_candidate = None
    if not is_dialogue_active(state):
        raw_dialogue_message = str(user_message or "").strip()
        current_context_reply = None
        if free.get("last_question"):
            current_context_reply = a1_everyday_reply(
                raw_dialogue_message,
                free.get("last_question", ""),
                state,
            )
        may_route_dialogue = (
            int(free.get("turn_count", 0) or 0) == 0
            or (
                "?" in raw_dialogue_message
                and _is_explicit_learner_question(raw_dialogue_message)
                and current_context_reply is None
            )
        )
        if may_route_dialogue:
            dialogue_candidate = find_dialogue_for_message(
                raw_dialogue_message,
                "A1-A2",
            )

    if dialogue_candidate is not None and _should_activate_dialogue_in_free(dialogue_candidate):
        dialogue_reply = auto_start_dialogue_from_message(
            user_message,
            state,
            level="A1-A2",
        )
        if dialogue_reply:
            state["dialogue_origin"] = "free"
            free["last_user_message"] = str(user_message or "").strip()
            free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
            _remember_question(free, dialogue_reply)
            return dialogue_reply, {
                "conversation_mode": "free",
                "dialogue_knowledge": True,
                "dialogue_id": state.get("dialogue_id"),
                "dialogue_topic": state.get("last_activity_detail"),
            }

    # Shared wellbeing corrections are semantic language corrections and must
    # run before personal/fuzzy routers. This prevents malformed but recognized
    # phrases such as "mir geht gut" from being swallowed on the first turn.
    early_wellbeing = analyze_wellbeing_response(user_message)
    early_norm = _norm(user_message).strip(" ?!.,")
    if (
        early_wellbeing.get("recognized")
        and early_wellbeing.get("corrected_message")
        and (
            early_norm.startswith("mir geht ")
            or early_norm.startswith("ich bin ")
            or early_norm.startswith("ich geht ")
            or early_norm.startswith("ich gehe ")
        )
    ):
        feedback = early_wellbeing.get("feedback") or early_wellbeing.get("corrected_message")
        reaction = early_wellbeing.get("reaction") or ""
        reply = " ".join(part for part in (feedback, reaction) if part).strip()
        _remember_question(free, reply)
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        free["last_topic"] = "today"
        return reply, {
            "conversation_mode": "free",
            "topic": "today",
            "shared_wellbeing": True,
            "wellbeing_type": early_wellbeing.get("type"),
            "wellbeing_correction": True,
        }

    # Personal real-life sentences remain available when no dialogue was selected.
    personal = handle_personal_sentence(user_message, state, mode="free")
    if personal:
        reply = personal["reply"]
        _remember_question(free, reply)
        return reply, {
            "conversation_mode": "free",
            **personal.get("meta", {}),
        }

    # Active Dialogue Engine state owns every following learner turn.
    if is_dialogue_active(state):
        dialogue_reply = handle_dialogue(user_message, state)
        if dialogue_reply is not None:
            _remember_question(free, dialogue_reply)
            free["last_user_message"] = str(user_message or "").strip()
            free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
            return dialogue_reply, {
                "conversation_mode": "free",
                "dialogue_knowledge": True,
                "dialogue_id": state.get("dialogue_id"),
                "dialogue_topic": state.get("last_activity_detail"),
                "dialogue_active": is_dialogue_active(state),
            }

    # Priority -2.5: shared social/wellbeing semantics must outrank generic
    # lesson/fallback routers. A wellbeing answer belongs to the last wellbeing
    # question; explicit states such as "mir geht ...", "müde", "schlecht" or
    # "gestresst" are also meaningful learner-led updates on their own.
    last_social_question = _norm(free.get("last_question", ""))
    wellbeing_context = any(x in last_social_question for x in (
        "wie geht's dir", "wie geht es dir", "wie geht es ihnen", "wie geht's ihnen"
    ))
    wellbeing_analysis = analyze_wellbeing_response(user_message)
    explicit_wellbeing = bool(
        wellbeing_analysis.get("recognized")
        and (
            wellbeing_context
            or wellbeing_analysis.get("type") in {"bad", "tired", "stressed", "sad", "sick"}
            or re.match(r"^(?:mir\s+geht|ich\s+bin)\b", _norm(user_message))
            or (
                wellbeing_context
                and _norm(user_message).strip(" ?!.,") in {"gut", "sehr gut", "ganz gut", "prima", "super", "so lala", "es geht", "geht so"}
            )
        )
    )
    if explicit_wellbeing:
        social_reply = _social_a1_reply(
            user_message,
            {**free, "last_question": free.get("last_question") if wellbeing_context else "Wie geht es dir?"},
            state,
        )
        if social_reply:
            _remember_question(free, social_reply)
            free["last_user_message"] = str(user_message or "").strip()
            free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
            free["last_topic"] = "today"
            # Early wellbeing routing still exposes the shared pipeline
            # diagnostics expected by every free-conversation turn.
            response_understanding = understand_response(
                user_message,
                conversation_state=state.get("conversation_state_v2") or {},
                vocabulary_context=free.get("vocabulary_context") or {},
            )
            error_result = process_error(
                user_message,
                state,
                support_level=free.get("support_level", "high"),
                expected_answer=(state.get("conversation_state_v2") or {}).get("expected_answer"),
                context={"mode": "free", "topic": "today", "last_question": last_social_question},
            )
            return social_reply, {
                "conversation_mode": "free",
                "topic": "today",
                "shared_wellbeing": True,
                "wellbeing_type": wellbeing_analysis.get("type"),
                "response_understanding": response_understanding,
                "error_engine": error_result,
            }

    # "Und du?" is a learner-led hand-back, not permission to rotate to an
    # unrelated fallback topic. Answer within the active topic and keep it.
    if _norm(user_message).strip(" ?!.,") in {"und du", "und sie"}:
        active_topic = free.get("last_topic") or "today"
        topic_answers = {
            "holiday": "Ich reise nicht wirklich, aber ich spreche gern mit dir über Reisen. Wie reist du am liebsten?",
            "weather": "Ich habe kein eigenes Wetter. Welches Wetter magst du am liebsten?",
            "hobby": "Ich spreche gern mit dir. Was machst du gern in deiner Freizeit?",
            "work": "Ich bin deine Deutschtrainerin. Was machst du bei der Arbeit?",
            "shopping": "Ich kaufe nicht wirklich ein. Was kaufst du gern?",
            "food": "Ich esse nicht wirklich, aber ich spreche gern mit dir über Essen. Was kochst du noch gern?",
        }
        reply = topic_answers.get(active_topic, "Ich bin gern hier und spreche mit dir. Und was machst du gern?")
        _remember_question(free, reply)
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        return reply, {
            "conversation_mode": "free",
            "topic": active_topic,
            "topic_handoff": True,
        }

    # Priority -2.4: a clear learner-led question may activate Dialogue
    # Knowledge at ANY point in free conversation, not only on the first turn.
    # This prevents stale generic chains from stealing questions such as
    # "Wie komme ich zum Bahnhof?" after a travel topic switch.
    if not is_dialogue_active(state) and _is_explicit_learner_question(user_message):
        late_dialogue_candidate = find_dialogue_for_message(
            user_message,
            "A1",
            min_score=0.92,
        )
        dialogue_reply = None
        if _should_activate_dialogue_in_free(late_dialogue_candidate):
            dialogue_reply = auto_start_dialogue_from_message(
                user_message,
                state,
                level="A1",
                min_score=0.92,
            )
        if dialogue_reply:
            state["dialogue_origin"] = "free"
            _remember_question(free, dialogue_reply)
            free["last_user_message"] = str(user_message or "").strip()
            free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
            return dialogue_reply, {
                "conversation_mode": "free",
                "dialogue_knowledge": True,
                "dialogue_id": state.get("dialogue_id"),
                "dialogue_topic": state.get("last_activity_detail"),
            }

    # Priority -2.3: a learner-led question outranks Nele's stale previous
    # question. Answer it first; only then hand the turn back to the learner.
    learner_turn = analyze_learner_turn(
        user_message,
        last_question=free.get("last_question", ""),
    )
    state["learner_turn_v1"] = learner_turn
    if learner_turn.get("intent") == "question_to_nele":
        direct_reply = direct_nele_answer(user_message)
        if direct_reply:
            previous_question = free.get("last_question", "")
            record_answer(state, user_message, previous_question)
            slot_topic = {
                "food": "food",
                "film_genre": "hobby",
                "reading": "hobby",
                "reading_genre": "hobby",
                "music_genre": "hobby",
                "sport_kind": "hobby",
                "activity": "hobby",
                "birthday": "personal",
                "work": "work",
            }.get(learner_turn.get("slot"))
            topic = slot_topic or ("today" if "heute" in _norm(user_message) else (free.get("last_topic") or "today"))
            free["last_topic"] = topic
            _remember_question(free, direct_reply)
            free["last_user_message"] = str(user_message or "").strip()
            free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
            level = str(state.setdefault("student_progress", {}).get("current_level", "A1.1") or "A1.1")
            conversation_state = sync_conversation_state(
                state, topic=topic, last_question=free.get("last_question", ""), level=level
            )
            topic_manager = update_topic_manager(
                state, topic=topic, source="learner_question", subtopic=conversation_state.get("subtopic")
            )
            response_understanding = understand_response(
                user_message,
                conversation_state={**conversation_state, "last_question": previous_question},
                vocabulary_context=free.get("vocabulary_context") or {},
            )
            return direct_reply, {
                "conversation_mode": "free",
                "course_level": level,
                "topic": topic,
                "learner_turn": learner_turn,
                "response_understanding": response_understanding,
                "conversation_state": conversation_state,
                "topic_manager": topic_manager,
                "answered_learner_question": True,
            }

    # A yes/no answer cannot satisfy an open content question. Repair the
    # answer shape and stay on the same topic instead of jumping elsewhere.
    active_semantic_slot = (state.get("conversation_state_v2") or {}).get("active_slot")
    answer_type_repair = None
    if not active_semantic_slot:
        answer_type_repair = _content_question_repair(user_message, free.get("last_question", ""))
    if answer_type_repair:
        _remember_question(free, answer_type_repair)
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        return answer_type_repair, {
            "conversation_mode": "free",
            "answer_type_repair": True,
        }

    # Priority -3: interpret short beginner answers through the exact
    # question Nele asked. This shared contextual layer must run before the
    # broad A1 content bank, otherwise nouns/times such as "Pizza", "8" or
    # "Kochen" lose their local meaning and the conversation jumps topics.
    # A new learner question is not an answer to Nele's previous question.
    # Do not reinterpret it through stale weather/work/home context.
    contextual_reply = None
    early_content = _norm(user_message)
    explicit_reading_content = bool(
        re.search(r"\b(?:ich\s+lese|lese\s+ich)\b", early_content)
        or re.search(r"\bkrimis?\b", early_content)
    )
    active_semantic_slot = (state.get("conversation_state_v2") or {}).get("active_slot")
    if not active_semantic_slot and not _is_explicit_learner_question(user_message) and not explicit_reading_content:
        contextual_reply = _short_answer_followup(
            user_message,
            free.get("last_question", ""),
            free.setdefault("conversation_facts", {}),
        )
    if contextual_reply:
        # A curriculum MODEL_SENTENCE is an explicit pedagogical action and must
        # reach the shared executor instead of being swallowed by this shortcut.
        # Only bypass this early return when the current turn can supply a
        # concrete model; all other contextual-short-answer behavior is unchanged.
        early_model = _model_sentence_from_turn(
            user_message,
            free.get("last_topic") or (state.get("topic_manager_v2") or {}).get("topic") or "today",
            (state.get("conversation_state_v2") or {}).get("subtopic"),
        )
        early_learner_model = build_learner_model(state) if early_model else {}
        early_next_skill = early_learner_model.get("next_curriculum_skill") or {}
        early_requires_model_sentence = (
            bool(early_model)
            and early_next_skill.get("skill") == "conversation:full_sentence"
            and early_next_skill.get("reason") in {"prerequisites_met", "curriculum_review", "dynamic_review"}
        )
        if early_requires_model_sentence:
            contextual_reply = None

    if contextual_reply:
        previous_question = free.get("last_question", "")
        # This shortcut used to return before Response Understanding, so the
        # learner received a contextual reply but canonical state forgot the
        # value (e.g. Pizza -> next turn lost Pizza). Commit the answer against
        # the question that actually produced it before storing Nele's next
        # question.
        early_understanding = understand_response(
            user_message,
            conversation_state={
                **(state.get("conversation_state_v2") or {}),
                "last_question": previous_question,
            },
            vocabulary_context=free.get("vocabulary_context") or {},
        )
        state["response_understanding_v1"] = early_understanding
        apply_response_to_conversation_state(state, early_understanding)
        record_answer(state, user_message, previous_question)
        _remember_question(free, contextual_reply)
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        level = str(state.setdefault("student_progress", {}).get("current_level", "A1.1") or "A1.1")
        previous_topic = free.get("last_topic") or (state.get("topic_manager_v2") or {}).get("topic") or "today"

        # A dependent short answer inherits the active semantic topic.
        # The wording of the previous question may describe an activity such as
        # cooking without meaning "work"; lexical guesses must not override
        # established conversation state.
        active_topic = previous_topic
        if active_topic in {None, "today", "everyday_a1"}:
            question_low = _norm(previous_question)
            if "arbeit" in question_low:
                active_topic = "work"
            elif any(x in question_low for x in ("isst du", "essen", "trinkst du", "frühstück", "fruehstueck")):
                active_topic = "food"
            else:
                active_topic = active_topic or "today"
        free["last_topic"] = active_topic
        vocabulary_context = build_personalized_conversation_vocabulary(
            user_message, state=state, topic=active_topic, limit=8,
        )
        free["vocabulary_context"] = vocabulary_context
        conversation_state = sync_conversation_state(
            state, topic=active_topic, last_question=free.get("last_question", ""), level=level
        )
        topic_manager = update_topic_manager(
            state, topic=active_topic, source="contextual_short_answer",
            subtopic=conversation_state.get("subtopic"),
        )
        turn_plan = build_turn_plan(
            teacher_policy={"action": "CONTINUE"},
            topic=active_topic,
            response_understanding={"confidence": "high"},
        )
        orchestration = record_orchestration(
            state,
            enforce_orchestration(build_orchestration_contract(
                teacher_policy={"action": "CONTINUE"},
                turn_plan=turn_plan,
            )),
        )
        return contextual_reply, {
            "conversation_mode": "free",
            "course_level": level,
            "topic": active_topic,
            "vocabulary": vocabulary_context,
            "conversation_state": conversation_state,
            "topic_manager": topic_manager,
            "conversation_orchestrator": orchestration,
            "turn_plan": turn_plan,
            "global_conversation_guard": {
                "version": (state.get("global_conversation_guard_v1") or {}).get("version", 2),
                "blocked": False,
                "reason": "contextual_short_answer",
            },
            "contextual_short_answer": True,
            "response_understanding": early_understanding,
        }

    # Priority -2: the reusable A1 lessons 1-10 router may enrich a neutral
    # conversation, but it must not take ownership away from an already active
    # semantic topic. This prevents broad legacy rules (e.g. any "Ich arbeite")
    # from restarting an established work thread.
    current_semantic_topic = free.get("last_topic") or (state.get("topic_manager_v2") or {}).get("topic")
    protected_semantic_topics = {"work", "holiday", "weather", "hobby", "shopping", "food"}
    # Explicit origin/residence language is a real topic switch. Let the A1
    # router handle it even when the previous topic was sticky (for example food).
    early_low = _norm(user_message)
    explicit_place_turn = bool(
        early_low.startswith(("ich komme aus ", "ich wohne in "))
        or (
            _is_explicit_learner_question(user_message)
            and early_low.startswith(("woher ", "wohnst ", "kommst ", "wo wohnst"))
        )
    )
    a1_reply = None
    if current_semantic_topic not in protected_semantic_topics or explicit_place_turn:
        a1_reply = a1_everyday_reply(user_message, free.get("last_question", ""), state)
    if a1_reply:
        previous_question = free.get("last_question", "")
        # Early A1 turns still have to commit the same global conversation
        # contracts as the full pipeline. Otherwise the next turn sees a
        # partially updated session and loses semantic/orchestrator context.
        record_answer(state, user_message, previous_question)
        _remember_question(free, a1_reply)
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        level = str(state.setdefault("student_progress", {}).get("current_level", "A1.1") or "A1.1")
        a1_topic = "place" if explicit_place_turn else "everyday_a1"
        free["last_topic"] = a1_topic
        conversation_state = sync_conversation_state(
            state, topic=a1_topic, last_question=free.get("last_question", ""), level=level
        )
        topic_manager = update_topic_manager(
            state, topic=a1_topic, source="a1_everyday_router",
            subtopic=conversation_state.get("subtopic"),
        )
        turn_plan = build_turn_plan(
            teacher_policy={"action": "CONTINUE"},
            topic=a1_topic,
            response_understanding={"confidence": "high"},
        )
        orchestration_contract = build_orchestration_contract(
            teacher_policy={"action": "CONTINUE"},
            turn_plan=turn_plan,
        )
        orchestration = record_orchestration(
            state,
            enforce_orchestration(orchestration_contract),
        )
        guard_store = state.get("global_conversation_guard_v1") or {}
        guard = {
            "version": guard_store.get("version", 2),
            "blocked": False,
            "reason": "a1_everyday_router",
        }
        return a1_reply, {
            "conversation_mode": "free",
            "course_level": level,
            "topic": a1_topic,
            "conversation_state": conversation_state,
            "topic_manager": topic_manager,
            "conversation_orchestrator": orchestration,
            "turn_plan": turn_plan,
            "global_conversation_guard": guard,
            "a1_everyday_router": True,
        }

    # First evaluate whether the previous pedagogical action worked. The
    # resulting signal is available to Learner Model before the next policy.
    learning_outcome = evaluate_learning_outcome(user_message, state)
    progress = state.setdefault("student_progress", {})
    level = str(progress.get("current_level", "A1.1") or "A1.1")

    # Understand the learner's response against the question they actually
    # received. Keep original text untouched for grammar/error detection.
    response_understanding = understand_response(
        user_message,
        conversation_state=state.get("conversation_state_v2") or {},
        vocabulary_context=(state.get("free_conversation") or {}).get("vocabulary_context") or {},
    )
    state["response_understanding_v1"] = response_understanding
    # CONTEXT stage: commit the understood answer into canonical working
    # memory before topic selection, pedagogy or fallback routing can act.
    apply_response_to_conversation_state(state, response_understanding)

    # Recovery must run before generic question selection. Otherwise an
    # obviously unclear learner turn can be converted into a perfectly valid
    # but unrelated fallback question before Conversation Recovery sees it.
    if not response_understanding.get("understood", True) and response_understanding.get("confidence") == "low":
        cooking_active = bool(free.setdefault("conversation_facts", {}).get("cooking_thread"))
        active_topic = "food" if cooking_active else (free.get("last_topic") or (state.get("conversation_state_v2") or {}).get("topic") or "today")
        recovery = recover_reply(
            free.get("last_question", ""),
            {},
            topic=active_topic,
            action="CONTINUE",
            response_understanding=response_understanding,
            user_message=user_message,
        )
        recovery_reply = recovery.get("reply")
        if recovery_reply:
            free["last_user_message"] = str(user_message or "").strip()
            free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
            state["conversation_recovery_v2"] = recovery
            state["conversation_recovery_v1"] = recovery
            return recovery_reply, {
                "conversation_mode": "free",
                "topic": active_topic,
                "response_understanding": response_understanding,
                "conversation_recovery": recovery,
                "recovery_before_routing": True,
            }

    # Vocabulary Engine is the single vocabulary source for free conversation.
    # Existing handcrafted rules below remain conversational fallbacks only.
    previous_topic = free.get("last_topic", "today")
    vocabulary_context = build_personalized_conversation_vocabulary(
        user_message,
        state=state,
        topic=previous_topic,
        limit=8,
    )
    free["vocabulary_context"] = vocabulary_context

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
    user_low = _norm(user_message)
    if re.search(r"\bich\s+koche\b", user_low):
        memory["cooking_thread"] = True
        # Cooking is a semantic food subtopic even when the sentence also
        # mentions "heute" or "Wochenende".
        free["last_topic"] = "food"
    memory.update({k: v for k, v in facts.items() if k not in {"topic", "day_statement"}})
    personalization_memory = remember_conversation_facts(
        state,
        {k: v for k, v in facts.items() if k not in {"topic", "day_statement"}},
        topic=facts.get("topic") or free.get("last_topic"),
    )

    # A clear new everyday topic closes the active shopping branch. Keep the
    # useful facts (place/color) in memory, but do not let them hijack replies.
    if facts.get("day_statement"):
        memory["shopping_complete"] = True

    vocabulary_topic_map = {
        "arbeit": "work",
        "freizeit": "hobby",
        "wetter": "weather",
        "essen": "food",
        "hotel": "work",
        "alltag": "today",
    }
    vocabulary_topic = vocabulary_topic_map.get(vocabulary_context.get("topic"))
    explicit_topic = facts.get("topic")
    # Explicit topic words in the learner message must outrank context. This is
    # deliberately checked again here because social/weather handlers may have
    # already enriched memory while the active state still says work/kochen.
    low_message = _norm(user_message)
    learner_question = _is_explicit_learner_question(user_message)
    # One topic classifier owns learner intent. Do not run a second classifier
    # afterwards that can silently overwrite a stronger semantic decision.
    detected_topic = explicit_topic
    if any(x in low_message for x in ("wetter", "sonne", "sonnig", "regen", "regnet", "windig", "schnee")):
        detected_topic = "weather"
    elif any(x in low_message for x in ("urlaub", "reise", "ferien", "meer", "berge")):
        detected_topic = "holiday"
    elif "gestern" in low_message:
        detected_topic = "yesterday"
    elif any(x in low_message for x in ("arbeit", "job", "hotel")):
        detected_topic = "work"
    elif re.search(r"\bich\s+koche\b", low_message):
        detected_topic = "food"
    elif learner_question and (
        re.search(r"\b(?:isst|esse|essen|frühstückst|fruehstueckst|frühstücke|fruehstuecke)\b", low_message)
        or any(x in low_message for x in ("speise", "gericht"))
    ):
        detected_topic = "food"
    elif learner_question and low_message.startswith(("woher ", "wohnst ", "kommst ", "wo wohnst")):
        detected_topic = "place"
    elif learner_question and any(x in low_message for x in ("wochenende", "freizeit", "hobby", "musik", "sport", "lesen", "buch")):
        detected_topic = "hobby"
    elif learner_question and any(x in low_message for x in ("heute abend", "heute noch", "machst du heute")):
        detected_topic = "today"
    elif any(x in low_message for x in ("hobby", "freizeit", "musik", "sport", "lesen", "buch")):
        detected_topic = "hobby"

    if facts.get("activity") == "shopping":
        detected_topic = "shopping"
    elif facts.get("place"):
        detected_topic = "place"
    explicit_topic = detected_topic

    # Neutral content must not silently abandon an explicit active topic.
    # Vocabulary may enrich a topic, but it may not demote holiday/weather/etc.
    # to generic "today" merely because the current sentence has no topic word.
    sticky_topics = {"holiday", "weather", "hobby", "work", "shopping", "food", "family", "friends", "housing", "weekend", "transport", "technology", "health"}
    topic_hint = vocabulary_topic or previous_topic
    if (
        not explicit_topic
        and previous_topic in sticky_topics
        and topic_hint in {None, "today", "alltag"}
    ):
        topic_hint = previous_topic

    topic, topic_source = choose_topic(
        state,
        explicit_topic=explicit_topic,
        vocabulary_topic=topic_hint,
    )

    last_question = free.get("last_question", "")
    # Global, topic-agnostic memory: the learner just answered the previous
    # question. Record that semantic slot before any handler chooses the next
    # question, so paraphrases cannot ask for the same information again.
    record_answer(state, user_message, last_question)
    # Central Error Engine handles clear A1 corrections and writes them to
    # Student Memory 2.0. Legacy social rules below remain compatible while
    # they are migrated incrementally.
    current_state = state.get("conversation_state_v2") or {}
    error_result = process_error(
        user_message,
        state,
        support_level=support,
        expected_answer=current_state.get("expected_answer"),
        context={
            "mode": "free",
            "topic": current_state.get("topic") or previous_topic,
            "last_question": last_question,
        },
    )
    recast = error_result.get("recast")
    learner_model = build_learner_model(state)
    teacher_action = choose_teacher_action(
        user_message,
        conversation_state=current_state,
        topic_manager=state.get("topic_manager_v2") or {},
        error_result=error_result,
        support_level=support,
        struggle=struggle,
        independent_turns=independent,
        vocabulary_context=vocabulary_context,
        learner_model=learner_model,
    )
    teacher_policy = choose_next_best_learning_action(
        teacher_action=teacher_action,
        learner_model=learner_model,
        conversation_state=current_state,
        topic_manager=state.get("topic_manager_v2") or {},
        error_result=error_result,
        vocabulary_context=vocabulary_context,
    )
    # Curriculum can request MODEL_SENTENCE even when Teacher Engine selected
    # ordinary continuation. Supply the concrete model here, where the current
    # learner utterance and active subtopic are available.
    if teacher_policy.get("action") == "MODEL_SENTENCE" and not teacher_policy.get("model"):
        active_model_topic = teacher_policy.get("topic") or topic
        turn_model = _model_sentence_from_knowledge(
            user_message,
            active_model_topic,
            state.setdefault("student_progress", {}).get("current_level", "A1.1"),
            free,
        )
        if not turn_model:
            turn_model = _model_sentence_from_turn(
                user_message,
                active_model_topic,
                teacher_policy.get("subtopic") or current_state.get("subtopic"),
            )
        if turn_model:
            teacher_policy = {**teacher_policy, "model": turn_model}
            teacher_action = {**teacher_action, "model": turn_model}

    teacher_action = policy_to_teacher_action(teacher_policy, teacher_action)
    state["teacher_policy_v2"] = teacher_policy
    executable_policy = resolve_learning_action(
        teacher_policy,
        teacher_action=teacher_action,
        error_result=error_result,
    )
    # Plan records the policy decision before execution/fallback resolution.
    # This keeps planned_action observable even when validation must fall back.
    turn_plan = build_turn_plan(
        teacher_policy=teacher_policy,
        topic=topic,
        struggle=struggle,
        explicit_topic=explicit_topic,
        error_result=error_result,
        response_understanding=response_understanding,
    )
    state["turn_plan_v1"] = turn_plan

    # Keep dependent answers inside an active reading subtopic. A learner
    # saying "oft am Abend" after a Krimi/reading question is still talking
    # about reading, not inviting a generic hobby rotation to music.
    reading_active = (
        memory.get("reading_kind") == "Krimis"
        or (state.get("conversation_state_v2") or {}).get("subtopic") == "reading"
    )
    reading_low = _norm(user_message).strip(" ?!.,")
    active_semantic_slot = (state.get("conversation_state_v2") or {}).get("active_slot")
    if reading_active and active_semantic_slot not in {"reading_genre", "reading_detail", "reading_frequency", "reading_place"} and (
        re.search(r"\b(?:oft|manchmal|selten)\b", reading_low)
        or re.search(r"\b(?:am abend|abends|am wochenende)\b", reading_low)
    ):
        reading_reply = "Liest du Krimis lieber am Abend oder am Wochenende?"
        _remember_question(free, reading_reply)
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        free["last_topic"] = "hobby"
        conversation_state = sync_conversation_state(
            state, topic="hobby", last_question=free.get("last_question", reading_reply), level=level
        )
        topic_manager = update_topic_manager(
            state, topic="hobby", source="active_reading_subtopic", subtopic="reading"
        )
        return reading_reply, {
            "conversation_mode": "free",
            "topic": "hobby",
            "conversation_facts": dict(memory),
            "conversation_state": conversation_state,
            "topic_manager": topic_manager,
            "response_understanding": response_understanding,
            "global_conversation_guard": {"version": 2, "blocked": False, "reason": "active_reading_subtopic"},
        }

    # Priority -1: preserve a specific active yes/no subthread before the
    # broad social/work router sees the same short answer. This prevents a
    # contextual "ja" in cooking from being reinterpreted as "ja, ich arbeite".
    contextual_yes_no = _yes_no_followup(user_message, last_question, memory)
    if contextual_yes_no and (
        "kochst du " in _norm(last_question)
        or "isst du " in _norm(last_question)
    ):
        _remember_question(free, contextual_yes_no)
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        free["last_topic"] = topic
        conversation_state = sync_conversation_state(
            state, topic=topic, last_question=free.get("last_question", contextual_yes_no), level=level
        )
        topic_manager = update_topic_manager(
            state, topic=topic, source=topic_source, subtopic=conversation_state.get("subtopic")
        )
        return contextual_yes_no, {
            "conversation_mode": "free",
            "support_level": support,
            "topic": topic,
            "independent_turns": independent,
            "course_level": level,
            "conversation_facts": dict(memory),
            "recurring_errors": list((state.get("learner_memory") or {}).get("recurring_errors", [])),
            "vocabulary": vocabulary_context,
            "conversation_state": conversation_state,
            "topic_manager": topic_manager,
            "error_engine": error_result,
            "teacher_engine": teacher_action,
            "teacher_policy": teacher_policy,
            "turn_plan": turn_plan,
            "learning_outcome": learning_outcome,
            "response_understanding": response_understanding,
            "learner_model": learner_model,
            "global_conversation_guard": {"version": 2, "blocked": False, "reason": "active_subthread"},
        }

    # Priority -0.5: explicit learner content should deepen its semantic
    # thread before the broad social A1 shortcut can turn it into a generic
    # "Machst du das oft?" response. Keep this narrow: only use content
    # followups that identify a concrete reading kind such as Krimis.
    previous_subtopic = (
        (state.get("topic_manager_v2") or {}).get("subtopic")
        or (state.get("conversation_state_v2") or {}).get("subtopic")
    )
    active_semantic_slot = (state.get("conversation_state_v2") or {}).get("active_slot")
    # Canonical semantic threads own their learner answers. Legacy content
    # followups are only discovery/fallback logic and must not manufacture a
    # parallel reading chain while a semantic reading slot is active.
    canonical_reading_active = active_semantic_slot in {
        "reading_genre", "reading_detail", "reading_frequency", "reading_place"
    }
    explicit_content_followup = None if canonical_reading_active else _content_followup(
        user_message, facts, memory, free, level
    )
    if (
        explicit_content_followup
        and memory.get("reading_kind") == "Krimis"
    ):
        memory.setdefault("activity", "reading")
        _remember_question(free, explicit_content_followup)
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        free["last_topic"] = topic
        conversation_state = sync_conversation_state(
            state, topic=topic, last_question=free.get("last_question", explicit_content_followup), level=level
        )
        topic_manager = update_topic_manager(
            state, topic=topic, source=topic_source, subtopic=conversation_state.get("subtopic")
        )
        return explicit_content_followup, {
            "conversation_mode": "free",
            "support_level": support,
            "topic": topic,
            "independent_turns": independent,
            "course_level": level,
            "conversation_facts": dict(memory),
            "conversation_state": conversation_state,
            "topic_manager": topic_manager,
            "error_engine": error_result,
            "teacher_engine": teacher_action,
            "teacher_policy": teacher_policy,
            "turn_plan": turn_plan,
            "response_understanding": response_understanding,
            "global_conversation_guard": {"version": 2, "blocked": False, "reason": "explicit_content_followup"},
        }

    # Generic subtopic safety net. Existing specific content routes above keep
    # priority; this only preserves an already established subtopic when the
    # current short/unexpected answer has no explicit new activity/topic.
    subtopic_followup = None
    if (
        not explicit_content_followup
        and previous_subtopic
        and topic_source != "explicit"
    ):
        subtopic_followup = _subtopic_followup(
            topic, previous_subtopic, free, memory, state=state
        )
    if subtopic_followup:
        _remember_question(free, subtopic_followup)
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        free["last_topic"] = topic
        conversation_state = sync_conversation_state(
            state, topic=topic,
            last_question=free.get("last_question", subtopic_followup),
            level=level,
        )
        topic_manager = update_topic_manager(
            state, topic=topic, source=topic_source, subtopic=previous_subtopic
        )
        return subtopic_followup, {
            "conversation_mode": "free",
            "support_level": support,
            "topic": topic,
            "independent_turns": independent,
            "course_level": level,
            "conversation_facts": dict(memory),
            "conversation_state": conversation_state,
            "topic_manager": topic_manager,
            "error_engine": error_result,
            "teacher_engine": teacher_action,
            "teacher_policy": teacher_policy,
            "turn_plan": turn_plan,
            "response_understanding": response_understanding,
            "global_conversation_guard": {
                "version": 2, "blocked": False, "reason": "active_subtopic"
            },
        }

    # Priority 0: core A1 social language (greetings, wellbeing, introductions).
    # A clear "Ich ... gern ..." statement normally belongs to the social A1
    # shortcut. One narrow exception exists: when curriculum explicitly targets
    # a full sentence and Teacher Policy resolved MODEL_SENTENCE, let the turn
    # continue through the shared learning-action executor.
    social_key = _norm(user_message).strip(" ?!.,")
    policy_next_skill = executable_policy.get("next_curriculum_skill") or {}
    curriculum_model_sentence = (
        executable_policy.get("action") == "MODEL_SENTENCE"
        and (
            executable_policy.get("curriculum_skill") == "conversation:full_sentence"
            or policy_next_skill.get("skill") == "conversation:full_sentence"
        )
        and bool(re.fullmatch(r"ich\s+.+?\s+gern(?:e)?(?:\s+.+)?", social_key))
    )
    social_reply = None if curriculum_model_sentence else _social_a1_reply(user_message, free, state)
    if social_reply:
        # Store its final question as conversational context for the next turn.
        parts = re.findall(r"[^.!?]*[?]", social_reply)
        next_question = parts[-1].strip() if parts else ""
        if next_question:
            # A1 may have resolved a short answer from the immediately previous
            # question (for example "Um acht Uhr." after "Wann fängst du morgen
            # an?"). That continuation is semantic context, not a generic
            # suggestion, so a later guard must not replace it with another
            # topic merely because the question history is similar.
            dependent_answer = bool(
                re.fullmatch(
                    r"(?:um\s+)?(?:[01]?\d|2[0-3])(?:(?::|\.)[0-5]\d)?(?:\s*uhr)?[.!]?",
                    str(user_message or "").strip().lower(),
                )
                or _norm(user_message).strip(" ?!.,") in YES
                or _norm(user_message).strip(" ?!.,") in NO
            )
            if dependent_answer:
                guard = {
                    "version": 2,
                    "blocked": False,
                    "reason": "contextual_a1_continuation",
                    "selected": next_question,
                }
                guarded_question = next_question
            else:
                # A learner-led question owns this turn. The semantic guard may
                # veto repeats, but it must never replace the new branch's
                # question with a fallback from the PREVIOUS topic.
                if _is_explicit_learner_question(user_message):
                    social_alternatives = []
                else:
                    social_alternatives = _not_recent(
                        free,
                        FALLBACKS.get(explicit_topic or previous_topic, FALLBACKS["today"]),
                    )
                guard = select_question(state, next_question, social_alternatives)
                guarded_question = guard.get("selected")
                if guarded_question is None:
                    guarded_question = "Erzähl mir noch etwas darüber."
            social_reply = replace_final_question(
                social_reply, next_question, guarded_question
            )
            _remember_question(free, guarded_question)
        else:
            guard = {"version": 1, "blocked": False, "reason": "no_question"}
        free["last_user_message"] = str(user_message or "").strip()
        free["turn_count"] = int(free.get("turn_count", 0) or 0) + 1
        # Reuse the topic already resolved for this turn. Re-running
        # choose_topic here with raw vocabulary used to undo sticky/explicit
        # topics (e.g. holiday -> today after "Ich fahre gern mit dem Zug.").
        social_topic, social_topic_source = topic, topic_source
        free["last_topic"] = social_topic
        conversation_state = sync_conversation_state(
            state,
            topic=social_topic,
            last_question=free.get("last_question", ""),
            level=level,
        )
        topic_manager = update_topic_manager(
            state,
            topic=social_topic,
            source=social_topic_source,
            subtopic=conversation_state.get("subtopic"),
        )
        return social_reply, {
            "conversation_mode": "free",
            "support_level": support,
            "topic": social_topic,
            "independent_turns": independent,
            "course_level": level,
            "conversation_facts": dict(free.get("conversation_facts", {})),
            "recurring_errors": list((state.get("learner_memory") or {}).get("recurring_errors", [])),
            "vocabulary": vocabulary_context,
            "conversation_state": conversation_state,
            "topic_manager": topic_manager,
            "error_engine": error_result,
            "teacher_engine": teacher_action,
            "teacher_policy": teacher_policy,
            "turn_plan": turn_plan,
            "learning_action": state.get("learning_action_executor_v1"),
            "learning_outcome": learning_outcome,
            "response_understanding": response_understanding,
            "learner_model": learner_model,
            "global_conversation_guard": guard,
        }

    topic_transition = decide_topic_transition(
        state,
        topic=topic,
        independent_turns=independent,
        struggle=struggle,
        error_result=error_result,
        teacher_policy=teacher_policy,
        explicit_topic=bool(explicit_topic),
    )
    orchestration_contract = build_orchestration_contract(
        teacher_policy=teacher_policy,
        struggle=struggle,
        explicit_topic=explicit_topic,
        topic_transition=topic_transition,
        turn_plan=turn_plan,
    )
    transition_guard = enforce_orchestration(
        orchestration_contract,
        topic_transition=topic_transition,
    )
    topic_transition = transition_guard["topic_transition"]
    if topic_transition.get("transition"):
        topic = topic_transition["next_topic"]
        topic_source = "goal_transition"

    # A correction must preserve the semantic thread. Build the next question
    # from the corrected meaning before generic/personalized routing can move on.
    correction_question = _correction_followup(error_result, topic, memory)

    # Priority: answer context -> learner content -> safe course-level fallback.
    # On a deliberate topic transition, start with the new topic's safe
    # fallback instead of letting the old answer context pull us backwards.
    if correction_question:
        topic_transition = {**topic_transition, "transition": False, "next_topic": topic, "reason": "correction_topic_continuity"}
    question = correction_question
    if not question:
        question = None if topic_transition.get("transition") or learner_question else _yes_no_followup(user_message, last_question, memory)
    if not question and not learner_question:
        question = _short_answer_followup(user_message, last_question, memory)
    if not question:
        question = _content_followup(user_message, facts, memory, free, level)
    if not question:
        # Personalization is an optional question source. Do not create it
        # when the Turn Plan forbids personalization, otherwise the
        # orchestrator has to block work that should never have been proposed.
        if turn_plan.get("allow_personalization", True):
            personalized = choose_personalized_followup(
                state,
                topic=topic,
                recent_questions=free.get("recent_questions", []),
                turn_count=free.get("turn_count", 0),
            )
        else:
            personalized = None
        question = (personalized or {}).get("question")
    else:
        personalized = None
    if not question:
        question = _generic_followup(topic, free, support, independent, level, state=state)

    if topic_transition.get("transition"):
        question = _smooth_topic_transition(question, topic)

    # Conversation Coherence Engine keeps the local thread and avoids loops.
    # Prefer alternatives from the active topic before falling back to today.
    topic_alternatives = _not_recent(free, _semantic_fallbacks(topic, state))
    coherence = choose_coherent_question(
        question,
        topic=topic,
        recent_questions=free.get("recent_questions", []),
        previous_question=last_question,
        alternatives=topic_alternatives,
    )
    question = coherence.get("selected") or question

    # Global semantic guard: use it as a veto, not as a topic selector.
    # If it blocks a question, prefer a coherent alternative from the ACTIVE
    # conversational branch. Do not let a generic fallback pull the learner
    # back to an older topic such as "Arbeitest du heute?".
    branch_alternatives = _not_recent(
        free, _semantic_fallbacks(topic, state)
    )
    guard = select_question(state, question, branch_alternatives)
    guarded_question = guard.get("selected")
    if guarded_question is None:
        # All candidates were semantically blocked. Do not resurrect the
        # blocked original; continue openly inside the current conversation.
        question = "Erzähl mir noch etwas darüber."
    else:
        question = guarded_question

    # Final safety fallback: never reopen a question merely because it fell
    # outside the short recent window. The session-wide normalized `asked`
    # history is authoritative; if every safe question is exhausted, use an
    # open continuation instead of repeating an old fallback.
    asked_keys = set(free.get("asked", []))
    if _question_key(question) in asked_keys:
        question = _generic_followup(topic, free, support, independent, level, state=state)
        if _question_key(question) in asked_keys:
            question = "Erzähl mir noch etwas darüber."

    question_support = None
    action_question = question
    if teacher_policy.get("action") == "SIMPLIFY" and struggle:
        question_support = simplify_question(
            question,
            topic=topic,
            subtopic=current_state.get("subtopic"),
            recent_questions=free.get("recent_questions", []),
        )
        action_question = question_support.get("question") or question

    learning_action = execute_learning_action(
        executable_policy,
        teacher_action=teacher_action,
        vocabulary_context=vocabulary_context,
        fallback_question=action_question,
    )
    reply = learning_action.get("reply") or question
    if correction_question and recast:
        reply = f"{recast} {correction_question}"
    quality = check_reply(
        reply,
        topic=topic,
        action=learning_action.get("action"),
        model=learning_action.get("model"),
        user_message=user_message,
        response_understanding=response_understanding,
        personalization_facts=personalization_memory.get("facts") or {},
    )
    reply = quality.get("reply") or reply
    recovery = recover_reply(
        reply,
        quality,
        topic=topic,
        action=learning_action.get("action"),
        response_understanding=response_understanding,
        safe_question=action_question,
        user_message=user_message,
        explicit_topic=explicit_topic,
    )
    final_orchestration = enforce_orchestration(
        orchestration_contract,
        topic_transition=topic_transition,
        personalized_followup=personalized,
        question_support=question_support,
        recovery=recovery,
    )
    topic_transition = final_orchestration["topic_transition"]
    personalized = final_orchestration["personalized_followup"]
    question_support = final_orchestration["question_support"]
    recovery = final_orchestration["recovery"]
    reply = recovery.get("reply") or reply
    orchestration = record_orchestration(state, final_orchestration)
    state["conversation_recovery_v2"] = recovery
    state["conversation_recovery_v1"] = recovery
    state["conversation_quality_controller_v2"] = quality
    state["conversation_quality_controller_v1"] = quality
    state["learning_action_executor_v1"] = learning_action
    _learn_pending_knowledge(free, learning_action)
    compliance = evaluate_turn_plan_compliance(
        turn_plan,
        learning_action=learning_action,
        topic_transition=topic_transition,
        personalized_followup=personalized,
        question_support=question_support,
        recovery=recovery,
        orchestration=orchestration,
    )
    record_turn_plan_compliance(state, compliance)

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
    # Persist the question the learner actually received. Recovery may
    # replace the planned action_question with a more contextual reply; keeping
    # the stale planned question here makes the next turn reason about text
    # Nele never said.
    final_questions = re.findall(r"[^.!?]*[?]", str(reply or ""))
    delivered_question = final_questions[-1].strip() if final_questions else action_question
    _remember_question(free, delivered_question)
    conversation_state = sync_conversation_state(
        state,
        topic=topic,
        last_question=free.get("last_question", delivered_question),
        level=level,
    )
    topic_manager = update_topic_manager(
        state,
        topic=topic,
        source=topic_source,
        subtopic=conversation_state.get("subtopic"),
    )
    coherence_state = update_coherence_state(
        state,
        user_message=user_message,
        topic=topic,
        question=action_question,
        facts=memory,
        decision=coherence,
    )

    return reply, {
        "conversation_mode": "free",
        "support_level": support,
        "topic": topic,
        "independent_turns": independent,
        "course_level": level,
        "conversation_facts": dict(memory),
        "recurring_errors": list((state.get("learner_memory") or {}).get("recurring_errors", [])),
        "vocabulary": vocabulary_context,
        "conversation_state": conversation_state,
        "topic_manager": topic_manager,
        "conversation_coherence": coherence_state,
        "conversation_personalization": personalization_memory,
        "personalized_followup": personalized,
        "topic_transition": topic_transition,
        "error_engine": error_result,
        "teacher_engine": teacher_action,
        "teacher_policy": teacher_policy,
        "turn_plan": turn_plan,
        "learning_action": learning_action,
        "conversation_quality": quality,
        "conversation_recovery": recovery,
        "conversation_orchestrator": orchestration,
        "turn_plan_compliance": compliance,
        "question_simplifier": question_support,
        "learning_outcome": learning_outcome,
        "response_understanding": response_understanding,
        "learner_model": learner_model,
        "global_conversation_guard": guard,
    }
