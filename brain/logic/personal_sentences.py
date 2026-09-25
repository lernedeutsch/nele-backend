"""Personal learner sentence layer for production Nele.

The catalogue defines reusable real-life German sentences. Recognition is global,
while exposure/mastery is stored per learner inside the existing persistent state,
so PostgreSQL keeps it across browser restarts.
"""
import re
from datetime import datetime, timezone

# To add another sentence, append one small dictionary here. No router,
# lesson or frontend change is required.
PERSONAL_SENTENCES = [
    {
        "id": "welches_wetter_magst_du_am_liebsten",
        "text": "Welches Wetter magst du am liebsten?",
        "category": "wetter",
        "aliases": [
            "welches wetter magst du am liebsten",
            "was für wetter magst du am liebsten",
            "was fuer wetter magst du am liebsten",
        ],
        "reply": "Ich mag sonniges, mildes Wetter. Und du? Welches Wetter magst du am liebsten?",
        "practice_prompt": "Du möchtest jemanden nach seinem Lieblingswetter fragen. Was sagst du?",
    },
    {
        "id": "einen_moment_bitte",
        "text": "Einen Moment bitte.",
        "category": "hotel",
        "aliases": ["einen moment bitte", "einen moment"],
        "reply": "Natürlich. Ich warte einen Moment.",
        "practice_prompt": "Ein Gast bittet dich um etwas, aber du brauchst kurz Zeit. Was sagst du?",
    },
    {
        "id": "ich_kuemmere_mich_darum",
        "text": "Ich kümmere mich darum.",
        "category": "hotel",
        "aliases": ["ich kümmere mich darum", "ich kuemmere mich darum"],
        "reply": "Danke! Das ist sehr freundlich.",
        "practice_prompt": "Ein Gast sagt: Im Badezimmer fehlen Handtücher. Was sagst du?",
    },
    {
        "id": "ich_bringe_ihnen_sofort_frische_handtuecher",
        "text": "Ich bringe Ihnen sofort frische Handtücher.",
        "category": "hotel",
        "aliases": [
            "ich bringe ihnen sofort frische handtücher",
            "ich bringe ihnen sofort frische handtuecher",
            "ich bringe ihnen sofort handtücher",
            "ich bringe ihnen sofort handtuecher",
        ],
        "reply": "Vielen Dank. Könnten Sie mir bitte auch Duschgel bringen?",
        "practice_prompt": "Ein Gast braucht frische Handtücher. Was sagst du?",
    },
    {
        "id": "ich_frage_kurz_nach",
        "text": "Ich frage kurz nach.",
        "category": "hotel",
        "aliases": ["ich frage kurz nach"],
        "reply": "Danke. Sagen Sie mir bitte gleich Bescheid.",
        "practice_prompt": "Du kennst die Antwort auf die Frage eines Gastes nicht. Was sagst du?",
    },
    {
        "id": "ich_bin_gleich_fertig",
        "text": "Ich bin gleich fertig.",
        "category": "alltag",
        "aliases": ["ich bin gleich fertig"],
        "reply": "Okay, dann warte ich noch einen Moment. Was machst du danach?",
        "practice_prompt": "Jemand wartet auf dich und du brauchst nur noch kurz. Was sagst du?",
    },
    {
        "id": "ich_habe_heute_viel_zu_tun",
        "text": "Ich habe heute viel zu tun.",
        "category": "alltag",
        "aliases": ["ich habe heute viel zu tun"],
        "reply": "Oh, dann hast du einen vollen Tag. Was musst du heute noch machen?",
        "practice_prompt": "Du bist heute sehr beschäftigt. Wie sagst du das auf Deutsch?",
    },
]

def get_personal_sentence_catalog():
    """Return a safe copy for tests, dashboards and future UI."""
    return [dict(item) for item in PERSONAL_SENTENCES]


def validate_personal_sentence_catalog():
    """Fail fast on duplicate IDs/texts or incomplete catalogue entries."""
    ids = set()
    texts = set()
    for item in PERSONAL_SENTENCES:
        sentence_id = str(item.get("id") or "").strip()
        text = str(item.get("text") or "").strip()
        reply = str(item.get("reply") or "").strip()
        if not sentence_id or not text or not reply:
            raise ValueError("Each Meine Sätze item needs id, text and reply.")
        norm_text = _norm(text)
        if sentence_id in ids:
            raise ValueError(f"Duplicate Meine Sätze id: {sentence_id}")
        if norm_text in texts:
            raise ValueError(f"Duplicate Meine Sätze text: {text}")
        ids.add(sentence_id)
        texts.add(norm_text)
    return True


def _norm(value):
    value = str(value or "").strip().lower()
    value = value.replace("„", "").replace("“", "").replace('"', "")
    value = re.sub(r"[.!?,;:]+$", "", value)
    return re.sub(r"\s+", " ", value).strip()

def ensure_personal_sentence_memory(state):
    memory = state.setdefault("personal_sentences", {})
    memory.setdefault("items", {})
    memory.setdefault("recent_ids", [])
    return memory

def find_personal_sentence(user_message):
    value = _norm(user_message)
    if not value:
        return None
    for item in PERSONAL_SENTENCES:
        candidates = [item["text"], *item.get("aliases", [])]
        if any(value == _norm(candidate) for candidate in candidates):
            return item
    return None

def record_personal_sentence_use(state, item, mode="free"):
    memory = ensure_personal_sentence_memory(state)
    items = memory["items"]
    progress = items.setdefault(item["id"], {
        "text": item["text"],
        "category": item.get("category", "alltag"),
        "seen": 0,
        "successful_uses": 0,
        "mastery": 0,
    })
    progress["seen"] = int(progress.get("seen", 0) or 0) + 1
    progress["successful_uses"] = int(progress.get("successful_uses", 0) or 0) + 1
    progress["mastery"] = min(5, int(progress.get("mastery", 0) or 0) + 1)
    progress["last_mode"] = mode
    progress["last_used_at"] = datetime.now(timezone.utc).isoformat()
    recent = memory["recent_ids"]
    if item["id"] in recent:
        recent.remove(item["id"])
    recent.append(item["id"])
    del recent[:-12]
    return progress

def handle_personal_sentence(user_message, state, mode="free"):
    item = find_personal_sentence(user_message)
    if not item:
        return None
    progress = record_personal_sentence_use(state, item, mode=mode)
    return {
        "reply": item["reply"],
        "item": item,
        "progress": progress,
        "meta": {
            "personal_sentence": {
                "matched": True,
                "id": item["id"],
                "text": item["text"],
                "category": item.get("category", "alltag"),
                "mastery": progress["mastery"],
            }
        },
    }


def choose_personal_sentence_for_practice(state, category=None):
    """Choose a due learner sentence, prioritising low mastery and avoiding loops."""
    memory = ensure_personal_sentence_memory(state)
    progress_items = memory.get("items", {})
    recent = set(memory.get("recent_ids", [])[-3:])
    candidates = [
        item for item in PERSONAL_SENTENCES
        if (not category or item.get("category") == category)
    ]
    if not candidates:
        return None

    def score(item):
        progress = progress_items.get(item["id"], {})
        mastery = int(progress.get("mastery", 0) or 0)
        seen = int(progress.get("seen", 0) or 0)
        recent_penalty = 10 if item["id"] in recent else 0
        return (mastery + recent_penalty, seen, item["id"])

    return min(candidates, key=score)


def start_personal_sentence_practice(state, category=None):
    """Start one short contextual practice turn for a learner sentence."""
    item = choose_personal_sentence_for_practice(state, category=category)
    if not item:
        return None
    state["personal_sentence_practice"] = {"id": item["id"], "attempts": 0}
    return item.get("practice_prompt") or f'Sag bitte: „{item["text"]}“'


def handle_personal_sentence_practice(user_message, state):
    """Evaluate an active practice turn and update mastery without endless repetition."""
    active = state.get("personal_sentence_practice") or {}
    sentence_id = active.get("id")
    if not sentence_id:
        return None
    item = next((x for x in PERSONAL_SENTENCES if x["id"] == sentence_id), None)
    if not item:
        state.pop("personal_sentence_practice", None)
        return None

    if find_personal_sentence(user_message) == item:
        progress = record_personal_sentence_use(state, item, mode="course")
        state.pop("personal_sentence_practice", None)
        return {
            "reply": f'Sehr gut! „{item["text"]}“',
            "correct": True,
            "item": item,
            "progress": progress,
        }

    attempts = int(active.get("attempts", 0) or 0) + 1
    active["attempts"] = attempts
    if attempts >= 2:
        state.pop("personal_sentence_practice", None)
        return {
            "reply": f'Du kannst sagen: „{item["text"]}“ Wir üben den Satz später noch einmal.',
            "correct": False,
            "item": item,
        }
    return {
        "reply": f'Fast. Du kannst sagen: „{item["text"]}“ Sag den Satz bitte einmal.',
        "correct": False,
        "item": item,
    }
