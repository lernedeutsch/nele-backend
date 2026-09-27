"""Personal learner sentence layer for production Nele.

The catalogue defines reusable real-life German sentences. Recognition is global,
while exposure/mastery is stored per learner inside the existing persistent state,
so PostgreSQL keeps it across browser restarts.
"""
import re
from difflib import SequenceMatcher
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
        "reply": "Ich mag sonniges, mildes Wetter. Und du?",
        "practice_prompt": "Du möchtest jemanden nach seinem Lieblingswetter fragen. Was sagst du?",
    },
    {
        "id": "arbeitest_du_heute",
        "text": "Arbeitest du heute?",
        "category": "arbeit",
        "aliases": ["arbeitest du heute"],
        "reply": "Ja, heute habe ich einiges zu tun. Und du?",
        "practice_prompt": "Du möchtest jemanden fragen, ob er heute arbeitet. Was sagst du?",
    },
    {
        "id": "arbeitest_du_am_sonntag",
        "text": "Arbeitest du am Sonntag?",
        "category": "arbeit",
        "aliases": ["arbeitest du am sonntag"],
        "reply": "Nein, am Sonntag habe ich frei. Und du?",
        "practice_prompt": "Du möchtest jemanden fragen, ob er am Sonntag arbeitet. Was sagst du?",
    },
    {
        "id": "wann_hast_du_frei",
        "text": "Wann hast du frei?",
        "category": "arbeit",
        "aliases": ["wann hast du frei", "wann hast du einen freien tag"],
        "reply": "Am Sonntag habe ich meistens frei. Und du?",
        "practice_prompt": "Du möchtest jemanden fragen, wann er frei hat. Was sagst du?",
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

    # Exact forms stay authoritative.
    for item in PERSONAL_SENTENCES:
        candidates = [item["text"], *item.get("aliases", [])]
        if any(value == _norm(candidate) for candidate in candidates):
            return item

    # Learners often make one small article/ending/spelling error. Accept only
    # very close whole-sentence matches so Meine Sätze remains precise and does
    # not hijack unrelated conversation.
    value_words = value.split()
    if len(value_words) >= 3:
        best_item = None
        best_ratio = 0.0
        for item in PERSONAL_SENTENCES:
            for candidate in [item["text"], *item.get("aliases", [])]:
                candidate_norm = _norm(candidate)
                candidate_words = candidate_norm.split()
                if abs(len(candidate_words) - len(value_words)) > 1:
                    continue
                ratio = SequenceMatcher(None, value, candidate_norm).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_item = item
        if best_ratio >= 0.88:
            return best_item
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


def should_offer_personal_sentence_practice(
    state,
    *,
    normal_turns=0,
    learner_needs_support=False,
    has_active_error=False,
):
    """Return True only at calm course boundaries; never interrupt an active lesson."""
    if (
        not state
        or state.get("lesson_teaching_active")
        # A completed section can temporarily set lesson_teaching_active=False
        # while pending_new_learning already points at the next section. That is
        # still an active lesson handoff, not a safe boundary for Meine Sätze.
        or state.get("dialogue_active")
        or state.get("pending_new_learning")
        or state.get("last_question") == "continue_new_learning"
        or learner_needs_support
        or has_active_error
    ):
        return False

    if state.get("personal_sentence_practice"):
        return False

    memory = ensure_personal_sentence_memory(state)
    scheduler = memory.setdefault("scheduler", {"turns_since_practice": 0})
    scheduler["turns_since_practice"] = max(
        int(scheduler.get("turns_since_practice", 0) or 0),
        int(normal_turns or 0),
    )

    # Keep personal material occasional: at most one insertion after 5 normal turns.
    return scheduler["turns_since_practice"] >= 5


def note_personal_sentence_practice_started(state):
    memory = ensure_personal_sentence_memory(state)
    scheduler = memory.setdefault("scheduler", {})
    scheduler["turns_since_practice"] = 0
    scheduler["last_started_at"] = datetime.now(timezone.utc).isoformat()
