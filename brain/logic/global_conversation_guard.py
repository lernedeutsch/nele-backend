"""Global conversation guard for Nele free conversation.

Tracks answered question meanings, known session facts and recent question
signatures.  It is deliberately topic-agnostic: examples such as weather,
work or food are inputs to the same semantic guard, not separate dialogue
scripts.
"""
import re

ENGINE_VERSION = 2

STOP = {
    "der","die","das","den","dem","ein","eine","einen","einem","einer",
    "du","dir","dich","dein","deine","ich","mir","mein","meine","es","ist",
    "sind","war","heute","gern","gerne","auch","noch","bei","im","in","am",
    "an","auf","zu","mit","von","für","fuer","und","oder","denn","mal",
}

def _norm(text):
    value = str(text or "").lower().replace("ß", "ss")
    value = value.replace("ä","ae").replace("ö","oe").replace("ü","ue")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", value)).strip()

def _tokens(text):
    return {x for x in _norm(text).split() if len(x) > 2 and x not in STOP}

def question_intent(question):
    q = _norm(question)
    if not q:
        return "none"
    if q.startswith(("wo ","wohin ","woher ")): return "place"
    if q.startswith(("wann ","bis wann ","um wie viel")): return "time"
    if q.startswith(("wer ","mit wem ")): return "person"
    if q.startswith(("warum ","wieso ")): return "reason"
    if q.startswith(("wie oft ","wie lange ")): return "frequency"
    if q.startswith(("wie heisst ","wie heißt ")): return "name"
    if q.startswith(("welche ","welcher ","welches ","was ")): return "content"
    if q.startswith(("wie ist ","wie war ")): return "description"
    return "yes_no" if q.split(" ",1)[0] in {
        "bist","hast","arbeitest","machst","gehst","faehrst","schwimmst",
        "kochst","magst","hoerst","spielst","kaufst","wohnst","kommst",
        "kannst","willst","moechtest","ist","sind"
    } else "open"

def signature(question):
    intent = question_intent(question)
    words = sorted(_tokens(question))
    return {"intent": intent, "tokens": words, "text": _norm(question)}

def _similar(a, b):
    if not a or not b:
        return False
    if a.get("text") == b.get("text"):
        return True
    ta, tb = set(a.get("tokens") or []), set(b.get("tokens") or [])
    if not ta or not tb:
        return False
    overlap = len(ta & tb) / max(1, min(len(ta), len(tb)))
    # Be conservative. The guard must stop a repeated information request,
    # never a legitimate next detail in the same topic. A strong lexical
    # subject match plus the same requested slot is required.
    if a.get("intent") != b.get("intent"):
        return False
    if overlap >= 0.75:
        return True
    # For slot-like questions (name/place/time/person) one stable subject token
    # is enough: "Wie heißt dein Hund?" and "Wie heißt dein Hund denn?".
    return a.get("intent") in {"name","place","time","person","frequency"} and overlap >= 0.5

def record_answer(state, user_message, previous_question):
    store = state.setdefault("global_conversation_guard_v1", {
        "version": ENGINE_VERSION, "answered": [], "recent": [], "facts": []
    })
    if previous_question and str(user_message or "").strip():
        sig = signature(previous_question)
        sig["answer"] = str(user_message).strip()
        answered = store.setdefault("answered", [])
        answered.append(sig)
        del answered[:-30]
        facts = store.setdefault("facts", [])
        facts.append({"question": previous_question, "answer": str(user_message).strip()})
        del facts[:-30]
    return store

def assess_question(state, question):
    store = state.setdefault("global_conversation_guard_v1", {
        "version": ENGINE_VERSION, "answered": [], "recent": [], "facts": []
    })
    candidate = signature(question)
    recent = store.get("recent") or []
    answered = store.get("answered") or []
    repeated = any(_similar(candidate, old) for old in recent[-8:])
    already_answered = any(_similar(candidate, old) for old in answered[-20:])
    return {
        "version": ENGINE_VERSION,
        "question": question,
        "signature": candidate,
        "repeated": repeated,
        "already_answered": already_answered,
        "blocked": repeated or already_answered,
        "reason": "already_answered" if already_answered else "semantic_repeat" if repeated else "ok",
    }

def select_question(state, candidate, alternatives=None):
    first = assess_question(state, candidate)
    selected = candidate if not first["blocked"] else None
    decision = first
    if first["blocked"]:
        for alt in alternatives or []:
            checked = assess_question(state, alt)
            if not checked["blocked"]:
                selected, decision = alt, checked
                break
    store = state["global_conversation_guard_v1"]
    if selected is not None:
        sig = signature(selected)
        recent = store.setdefault("recent", [])
        recent.append(sig)
        del recent[:-12]
    return {
        **decision,
        "selected": selected,
        "changed": selected != candidate,
        "original": candidate if selected != candidate else None,
        "need_new_candidate": selected is None,
    }

def replace_final_question(reply, old_question, new_question):
    if not old_question or not new_question or old_question == new_question:
        return reply
    text = str(reply or "")
    pos = text.rfind(old_question)
    if pos < 0:
        return text
    return text[:pos] + new_question + text[pos + len(old_question):]
