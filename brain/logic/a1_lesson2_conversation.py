"""Generative tutor for A1 Lektion 2: Herkunft, Nationalitäten, kommen, Zahlen 1-20."""

import re
from brain.memory.error_memory import remember_error
from brain.logic.learning_progress_engine import update_learning_progress
from brain.logic.course_answer_evaluator import evaluate_course_answer
from brain.logic.course_teacher_engine import (
    choose_course_teacher_action,
    render_course_teacher_action,
)

from brain.logic.speaking_support import (
    consume_course_model_exhaustion,
    handle_pending_course_model,
    register_course_success,
)

COUNTRIES = {
    "polen": {"name":"Polen","aus":"aus Polen","m":"Pole","f":"Polin","aliases":["polen"],"typos":["polen"]},
    "deutschland": {"name":"Deutschland","aus":"aus Deutschland","m":"Deutscher","f":"Deutsche","aliases":["deutschland"],"typos":["deutchland","deutschlan"]},
    "österreich": {"name":"Österreich","aus":"aus Österreich","m":"Österreicher","f":"Österreicherin","aliases":["österreich","osterreich"],"typos":["osterreich"]},
    "schweiz": {"name":"die Schweiz","aus":"aus der Schweiz","m":"Schweizer","f":"Schweizerin","aliases":["schweiz"],"typos":["schweitz"]},
    "italien": {"name":"Italien","aus":"aus Italien","m":"Italiener","f":"Italienerin","aliases":["italien"],"typos":[]},
    "spanien": {"name":"Spanien","aus":"aus Spanien","m":"Spanier","f":"Spanierin","aliases":["spanien"],"typos":[]},
    "frankreich": {"name":"Frankreich","aus":"aus Frankreich","m":"Franzose","f":"Französin","aliases":["frankreich"],"typos":[]},
    "portugal": {"name":"Portugal","aus":"aus Portugal","m":"Portugiese","f":"Portugiesin","aliases":["portugal"],"typos":[]},
    "griechenland": {"name":"Griechenland","aus":"aus Griechenland","m":"Grieche","f":"Griechin","aliases":["griechenland"],"typos":[]},
    "türkei": {"name":"die Türkei","aus":"aus der Türkei","m":"Türke","f":"Türkin","aliases":["türkei","turkei"],"typos":["turkei"]},
    "ukraine": {"name":"die Ukraine","aus":"aus der Ukraine","m":"Ukrainer","f":"Ukrainerin","aliases":["ukraine"],"typos":[]},
    "rumänien": {"name":"Rumänien","aus":"aus Rumänien","m":"Rumäne","f":"Rumänin","aliases":["rumänien","rumanien"],"typos":[]},
    "bulgarien": {"name":"Bulgarien","aus":"aus Bulgarien","m":"Bulgare","f":"Bulgarin","aliases":["bulgarien"],"typos":[]},
    "tschechien": {"name":"Tschechien","aus":"aus Tschechien","m":"Tscheche","f":"Tschechin","aliases":["tschechien"],"typos":[]},
    "ungarn": {"name":"Ungarn","aus":"aus Ungarn","m":"Ungar","f":"Ungarin","aliases":["ungarn"],"typos":[]},
    "kroatien": {"name":"Kroatien","aus":"aus Kroatien","m":"Kroate","f":"Kroatin","aliases":["kroatien"],"typos":[]},
    "niederlande": {"name":"die Niederlande","aus":"aus den Niederlanden","m":"Niederländer","f":"Niederländerin","aliases":["niederlande","niederlanden"],"typos":[]},
    "großbritannien": {"name":"Großbritannien","aus":"aus Großbritannien","m":"Brite","f":"Britin","aliases":["großbritannien","grossbritannien"],"typos":[]},
    "usa": {"name":"die USA","aus":"aus den USA","m":"US-Amerikaner","f":"US-Amerikanerin","aliases":["usa"],"typos":[]},
}
NUMBERS = {1:"eins",2:"zwei",3:"drei",4:"vier",5:"fünf",6:"sechs",7:"sieben",8:"acht",9:"neun",10:"zehn",11:"elf",12:"zwölf",13:"dreizehn",14:"vierzehn",15:"fünfzehn",16:"sechzehn",17:"siebzehn",18:"achtzehn",19:"neunzehn",20:"zwanzig"}
NUMBER_ALIASES = {"zwolf":"zwölf","funf":"fünf","funfzehn":"fünfzehn","sechszehn":"sechzehn","siebenzehn":"siebzehn"}
KOMMEN = {"ich":"komme","du":"kommst","er":"kommt","sie":"kommt","es":"kommt","wir":"kommen","ihr":"kommt","sie_pl":"kommen","Sie":"kommen"}
PEOPLE = [("Anna","f"),("Paul","m"),("Maria","f"),("Thomas","m"),("Julia","f"),("Lukas","m"),("Emma","f"),("Max","m")]

def _norm(text):
    text=str(text or "").strip().lower()
    text=text.replace("„","").replace("“","").replace('"',"")
    return re.sub(r"[^a-zäöüß0-9 ]+"," ",text).strip()

def _mem(state):
    m=state.setdefault("a1_l2_tutor",{})
    m.setdefault("turn",0); m.setdefault("recent_intents",[]); m.setdefault("recent_questions",[])
    m.setdefault("errors",{}); m.setdefault("mastery",{}); m.setdefault("support_level",0)
    m.setdefault("pending_speaking_model",None)
    # A session should sample the country bank, not exhaust it. The bank stays
    # large so future sessions can vary naturally.
    m.setdefault("session_country_keys",[])
    m.setdefault("session_country_cursor",0)
    return m

SESSION_COUNTRY_LIMIT = 5

def _session_country(state):
    m=_mem(state)
    keys=m.get("session_country_keys") or []
    if not keys:
        all_keys=list(COUNTRIES.keys())
        # Deterministic rotation keeps tests stable while varying sessions via
        # the current tutor turn/state. Only a small sample is used per session.
        offset=(int(m.get("country_rotation_seed",0) or 0)) % len(all_keys)
        keys=(all_keys[offset:]+all_keys[:offset])[:SESSION_COUNTRY_LIMIT]
        m["session_country_keys"]=keys
    cursor=int(m.get("session_country_cursor",0) or 0)
    key=keys[cursor % len(keys)]
    m["session_country_cursor"]=cursor+1
    return key, COUNTRIES[key]

def _remember_error(state, kind, wrong, correct, context):
    m=_mem(state); item=m["errors"].setdefault(kind,{"attempts":0,"resolved":False,"review_due":None})
    item.update({"student_form":wrong,"expected_form":correct,"context":context,"resolved":False})
    item["attempts"]+=1; item["review_due"]=m["turn"]+3
    try: remember_error(state, kind, wrong, correct, context=context)
    except Exception: pass

def _country_from(text):
    n=_norm(text)
    for key,c in COUNTRIES.items():
        for form in [key]+c["aliases"]+c["typos"]:
            if _norm(form) in n.split() or _norm(form) in n:
                return key,c
    return None,None

def _number_from(text):
    n=_norm(text)
    if n.isdigit() and 1 <= int(n) <= 20: return int(n), False
    n2=NUMBER_ALIASES.get(n,n)
    for k,v in NUMBERS.items():
        if n2==v: return k, n!=v
    return None,False

def _course_answer_definition(task):
    """Translate a generated A1.2 task into the shared evaluator contract."""
    expected = str(task.get("expected", "") or "").strip()
    kind = task.get("kind")
    accepted = [expected] if expected else []

    if kind == "origin":
        expected_key, country = _country_from(expected)
        if country:
            accepted.extend([country["name"], country["aus"]])
            # A bare country is a natural short answer to an origin question.
            accepted.extend(country.get("aliases") or [])
        return {"accepted": list(dict.fromkeys(x for x in accepted if x))}

    if kind == "kommen":
        full = str(task.get("full_sentence_expected", "") or "").strip()
        if full:
            # Full-sentence tasks deliberately do not accept the isolated form.
            return {"accepted": [full]}
        return {"accepted": accepted}

    if kind == "number":
        number = task.get("number")
        if not task.get("require_word") and number is not None:
            accepted.append(str(number))
        return {"accepted": list(dict.fromkeys(x for x in accepted if x))}

    if kind == "nationality":
        # COUNTRY_TO_NATIONALITY is phrased as a real yes/no question
        # ("Ist Anna Polin?"). A natural affirmative answer must therefore be
        # accepted semantically, not forced into repeating the nationality.
        if task.get("intent") == "COUNTRY_TO_NATIONALITY":
            accepted.extend(["ja", "ja genau", "genau", "richtig"])
        return {"accepted": list(dict.fromkeys(x for x in accepted if x))}

    return {"accepted": accepted}


def evaluate_lesson2_answer(user_message, task):
    """Shared correctness first; A1.2 classify remains error diagnosis only."""
    shared = evaluate_course_answer(user_message, _course_answer_definition(task))
    if shared["correct"]:
        diagnostic = classify(user_message, task)
        status = diagnostic.get("status")
        if status == "CORRECT_WITH_TYPO":
            return dict(shared, status=status, correct=task.get("expected", ""))
        if status in {"CORRECT_SHORT", "CORRECT_FULL"}:
            return dict(shared, status=status, correct=task.get("expected", ""))
        return dict(shared, status="CORRECT_FULL", correct=task.get("expected", ""))

    diagnostic = classify(user_message, task)
    return dict(shared, status=diagnostic["status"], correct=diagnostic["correct"])


def classify(user_message, task):
    raw=str(user_message or "").strip(); n=_norm(raw)
    expected=task.get("expected",""); kind=task.get("kind")
    require_word = bool(task.get("require_word"))
    if not n: return {"status":"UNCLEAR","correct":expected}
    if kind=="origin":
        key,c=_country_from(n)
        if not c: return {"status":"UNCLEAR","correct":expected}
        expected_key, _expected_country = _country_from(expected)
        # A recognized country is only semantically correct when it matches
        # the country this task actually asks for. Previously any bare country
        # name (e.g. "Deutschland" for an expected "Polen") was accepted as
        # CORRECT_SHORT and could create false mastery evidence.
        if expected_key and key != expected_key:
            return {"status":"ORIGIN_MISMATCH","correct":expected}
        if n in c["aliases"] or n==key or n==_norm(c["aus"]): return {"status":"CORRECT_SHORT","correct":expected}
        if n in c["typos"]: return {"status":"CORRECT_WITH_TYPO","correct":expected}
        if re.match(r"^ich\s+(kommen|kommst|kommt)\b",n):
            return {"status":"CONJUGATION_ERROR","correct":expected}
        if re.match(r"^ich\s+komme\s+(?!aus\b)",n):
            return {"status":"PREPOSITION_ERROR","correct":expected}
        if c["aus"]=="aus Polen" and "aus der polen" in n:
            return {"status":"ARTICLE_ERROR","correct":expected}
        if c["aus"]=="aus der Schweiz" and "aus schweiz" in n:
            return {"status":"ARTICLE_ERROR","correct":expected}
        if c["aus"]=="aus der Türkei" and ("aus türkei" in n or "aus turkei" in n):
            return {"status":"ARTICLE_ERROR","correct":expected}
        if c["aus"]=="aus den USA" and "aus usa" in n:
            return {"status":"ARTICLE_ERROR","correct":expected}
        if c["aus"]=="aus den Niederlanden" and ("aus niederlanden" in n or "aus der niederlanden" in n):
            return {"status":"ARTICLE_ERROR","correct":expected}
        if _norm(expected)==n: return {"status":"CORRECT_FULL","correct":expected}
    if kind=="kommen":
        pron=task["pronoun"]; form=task["form"]
        if n==form or _norm(expected)==n: return {"status":"CORRECT_FULL","correct":expected}
        tokens=n.split()
        # A full-sentence gap task is correct only when the supplied form occurs
        # inside the complete sentence requested by the prompt. A fragment such
        # as "Thomas kommt aus" must not pass merely because it contains "kommt".
        if task.get("full_sentence_expected"):
            full_expected = _norm(task.get("full_sentence_expected"))
            if n == full_expected:
                return {"status":"CORRECT_FULL","correct":expected}
            if form in tokens:
                return {"status":"INCOMPLETE_ANSWER","correct":full_expected}
        elif form in tokens:
            return {"status":"CORRECT_FULL","correct":expected}
        if n in KOMMEN.values() or any(x in tokens for x in KOMMEN.values()):
            return {"status":"CONJUGATION_ERROR","correct":expected}
    if kind=="number":
        num,typo=_number_from(n)
        if num==task["number"]:
            if require_word and n.isdigit():
                return {"status":"NUMBER_WORD_REQUIRED","correct":expected}
            return {"status":"CORRECT_WITH_TYPO" if typo else ("CORRECT_SHORT" if n.isdigit() else "CORRECT_FULL"),"correct":expected}
        if num is not None: return {"status":"NUMBER_ERROR","correct":expected}
    if kind=="nationality":
        if task.get("intent")=="COUNTRY_TO_NATIONALITY" and n in {"ja","ja genau","genau","richtig"}:
            return {"status":"CORRECT_SHORT","correct":expected}
        if n==_norm(expected) or _norm(expected) in n: return {"status":"CORRECT_FULL","correct":expected}
        key,c=_country_from(n)
        if c: return {"status":"VOCABULARY_ERROR","correct":expected}
        all_nat=[_norm(c[x]) for c in COUNTRIES.values() for x in ("m","f")]
        if n in all_nat:
            exp=_norm(expected)
            same_country=task.get("country")
            if same_country and n in {_norm(COUNTRIES[same_country]["m"]),_norm(COUNTRIES[same_country]["f"])}:
                return {"status":"GENDER_FORM_ERROR","correct":expected}
            return {"status":"NATIONALITY_ERROR","correct":expected}
    return {"status":"UNCLEAR","correct":expected}

def _first_support_hint(task):
    kind = task.get("kind")
    if kind == "origin":
        return "Denk an: „aus …“ Versuch es noch einmal."
    if kind == "kommen":
        return "Welche Form von „kommen“ passt hier? Versuch es noch einmal."
    if kind == "number":
        return "Schreib die Zahl als deutsches Wort. Versuch es noch einmal."
    if kind == "nationality":
        country = task.get("country")
        if country and country in COUNTRIES:
            c = COUNTRIES[country]
            return f"„{c['name']}“ ist das Land. Gesucht ist die Nationalität. Versuch es noch einmal."
    return "Versuch es noch einmal."


def _correction(result, user_message, task, state):
    status = result["status"]
    correct = result["correct"]
    m = _mem(state)

    if status == "CORRECT_SHORT":
        register_course_success(state)
        if " " in str(correct).strip():
            state["course_pending_speaking_model"] = correct
            return "Genau. Du kannst auch sagen: „%s“ Sag es mal." % correct
        return "Genau."

    if status == "CORRECT_WITH_TYPO":
        register_course_success(state)
        state["course_pending_speaking_model"] = correct
        return "Fast. Sag: „%s“" % correct

    if status == "CORRECT_FULL":
        register_course_success(state)
        return None

    if status != "UNCLEAR":
        _remember_error(
            state,
            status,
            user_message,
            correct,
            task.get("prompt", ""),
        )

    hint = _first_support_hint(task)
    if status != "UNCLEAR":
        hint = "Fast. " + hint
    action = choose_course_teacher_action(
        state,
        answer_correct=False,
        partial=result.get("partial"),
        correct_answer=correct,
        retry=hint,
    )
    return render_course_teacher_action(action)

def _lesson2_skill_key(state):
    section = _norm(_mem(state).get("section", "lesson2")).replace(" ", "_")
    return f"course:a1:2:{section}"


def _record_lesson2_mastery(state, success, independent_confirmation=False):
    """Record Lektion 2 evidence under the shared course mastery contract.

    Generated tasks are useful practice evidence, but only a correct answer
    produced without scaffolding on that task may independently confirm
    mastery. This keeps the specialised Lektion 2 tutor aligned with the
    generic lesson/dialogue engines.
    """
    outcome = {
        "skill": _lesson2_skill_key(state),
        "expected_outcome": "course_step",
        "status": "SUCCESS" if success else "NOT_YET",
        "mastery_eligible": bool(success and independent_confirmation),
        "requires_independent_confirmation": True,
        "independent_confirmation": bool(success and independent_confirmation),
    }
    progress = update_learning_progress(state, outcome)
    state["last_course_learning_outcome"] = dict(outcome, progress=progress)
    return progress


def _set_task(state, task):
    m=_mem(state); m["task"]=task
    m["recent_intents"].append(task["intent"]); m["recent_intents"]=m["recent_intents"][-8:]
    m["recent_questions"].append(task["prompt"]); m["recent_questions"]=m["recent_questions"][-8:]
    state["last_question"]=task["intent"]
    return task["prompt"]

def _next_task(state, section):
    m=_mem(state); t=m["turn"]; review=None
    for k,item in m["errors"].items():
        if not item.get("resolved") and item.get("review_due") is not None and item["review_due"]<=t:
            review=k; break
    if review=="CONJUGATION_ERROR":
        return {"intent":"ERROR_REVIEW","kind":"kommen","pronoun":"ich","form":"komme","expected":"komme","prompt":"Noch einmal: „Ich ___ aus Deutschland.“"}
    s=_norm(section)
    if "zahl" in s:
        num=(t*3 % 20)+1
        modes=t%4
        if modes==0: p=f"Wie heißt {num} auf Deutsch?"
        elif modes==1: p=f"Sag {num} auf Deutsch."
        elif modes==2 and num<20: p=f"Was kommt nach {NUMBERS[num]}?"
        else: p=f"Wie heißt {num} auf Deutsch?"
        return {"intent":"NUMBER_PRODUCTION","kind":"number","number":num,"expected":NUMBERS[num],"prompt":p}
    if "verb kommen" in s or "kommen"==s:
        items=[("ich","komme"),("du","kommst"),("er","kommt"),("sie","kommt"),("wir","kommen"),("ihr","kommt"),("Sie","kommen")]
        pron,form=items[t%len(items)]
        country=list(COUNTRIES.values())[(t*2)%len(COUNTRIES)]["aus"]
        return {"intent":"PRACTICE_KOMMEN","kind":"kommen","pronoun":pron,"form":form,"expected":form,"prompt":f"Ergänze: „{pron} ___ {country}.“"}
    # Herkunft / Länder / Nationalitäten: rotate genuinely different acts.
    key,c=_session_country(state)
    person,gender=PEOPLE[t%len(PEOPLE)]
    mode=t%6
    if mode==0:
        return {"intent":"ASK_USER_ORIGIN","kind":"origin","expected":"Ich komme aus Polen.","prompt":"Woher kommst du?"}
    if mode==1:
        return {"intent":"ASK_PERSON_ORIGIN","kind":"origin","expected":f"{person} kommt {c['aus']}.","prompt":f"{person} kommt {c['aus']}. Woher kommt {person}?"}
    if mode==2:
        nat=c[gender]
        return {"intent":"COUNTRY_TO_NATIONALITY","kind":"nationality","country":key,"expected":nat,"prompt":f"{person} kommt {c['aus']}. Ist {person} {nat}?"}
    if mode==3:
        full = f"{person} kommt {c['aus']}."
        return {"intent":"COMPLETE_KOMMEN","kind":"kommen","pronoun":"sie" if gender=="f" else "er","form":"kommt","expected":"kommt","full_sentence_expected":full,"prompt":f"Ergänze: „{person} ___ {c['aus']}.“"}
    if mode==4:
        n=(t*2%20)+1
        return {"intent":"MIXED_REVIEW","kind":"number","number":n,"expected":NUMBERS[n],"require_word":True,"prompt":f"{person} ist {n} Jahre alt und kommt {c['aus']}. Wie alt ist {person}? Schreib die Zahl auf Deutsch."}
    return {"intent":"ROLEPLAY_FORMAL","kind":"origin","expected":f"Ich komme {c['aus']}.","prompt":f"Wir spielen ein formelles Gespräch. Ich frage: „Woher kommen Sie?“ Antworte mit {c['name']}."}

def start(section,state):
    m=_mem(state)
    previous_seed=int(m.get("country_rotation_seed",0) or 0)
    m["section"]=section; m["turn"]=0; m["task"]=None
    m["country_rotation_seed"]=previous_seed+SESSION_COUNTRY_LIMIT
    m["session_country_keys"]=[]
    m["session_country_cursor"]=0
    state["lesson_teaching_active"]=True; state["lesson_teaching_level"]="A1"; state["lesson_teaching_lesson"]=2
    state["lesson_teaching_section"]=section; state["lesson_teaching_step"]=1
    return _set_task(state,_next_task(state,section))

def current_prompt(state):
    task=_mem(state).get("task") or {}
    return task.get("prompt","Wir machen mit Lektion 2 weiter.")

def handle(user_message,state):
    m=_mem(state); task=m.get("task")
    if not task: return _set_task(state,_next_task(state,m.get("section","Woher kommen Sie?")))

    shared_pending = handle_pending_course_model(user_message, state)
    if shared_pending is not None:
        return shared_pending

    # The shared speaking-support layer reports when a learner has exhausted
    # the model/repetition ladder. Consume that signal here, while Lektion 2
    # still owns the active skill, so it cannot leak into another course engine
    # and be recorded against the wrong skill.
    exhausted = consume_course_model_exhaustion(state)
    if exhausted:
        state["course_mastery_assistance_used"] = True
        _record_lesson2_mastery(state, False)
        action = choose_course_teacher_action(
            state,
            answer_correct=True,
            mastery_status="needs_review",
        )
        return render_course_teacher_action(action, prompt=task.get("prompt", ""))

    result=evaluate_lesson2_answer(user_message,task)
    m["last_result"]=result
    if result["status"] in {"CORRECT_FULL","CORRECT_SHORT","CORRECT_WITH_TYPO"}:
        assisted = bool(state.get("course_mastery_assistance_used"))
        # Recognition-only answers (for example "ja" to "Ist Anna Polin?")
        # are valid task successes, but they do not demonstrate that the
        # learner can independently produce the target nationality.
        recognition_only = (
            task.get("intent") == "COUNTRY_TO_NATIONALITY"
            and _norm(user_message) in {"ja", "ja genau", "genau", "richtig"}
        )
        independent = (
            result["status"] in {"CORRECT_FULL", "CORRECT_SHORT"}
            and not assisted
            and not recognition_only
        )
        _record_lesson2_mastery(
            state,
            True,
            independent_confirmation=independent,
        )
        # mark matching pending error as resolved only after a later successful transfer
        if task.get("intent")=="ERROR_REVIEW":
            for item in m["errors"].values(): item["resolved"]=True
        correction=_correction(result,user_message,task,state)
        # A meaningful short answer is success, not an error. If we model
        # a fuller sentence, stop here and let the learner actually say it.
        if state.get("course_pending_speaking_model"):
            return correction
        # An assisted task is learned/practised, but cannot itself confirm
        # mastery. The next generated task starts clean and can do so.
        state["course_mastery_assistance_used"] = False
        m["turn"]+=1
        nxt=_set_task(state,_next_task(state,m.get("section","Woher kommen Sie?")))
        if correction: return correction+" "+nxt
        return "Genau! "+nxt
    state["course_mastery_assistance_used"] = True
    _record_lesson2_mastery(state, False)
    correction=_correction(result,user_message,task,state)
    # Keep the same target until the learner succeeds. The global speaking
    # engine now owns escalation and decides when to expose the full model.
    return correction
