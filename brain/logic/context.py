# ==========================================
# NELE – ODPOWIEDZI KONTEKSTOWE
# ==========================================

from brain.logic.memory import (
    get_conversation_state
)

from brain.logic.matcher import (
    normalize,
    clean_short_answer,
    capitalize_value
)

from brain.memory.user_facts import (
    remember_user_fact
)


# ==========================================
# CZY UŻYTKOWNIK ZADAJE PYTANIE
# ==========================================

def is_user_question(
    normalized_answer
):

    question_starts = (
        "wie ",
        "was ",
        "wo ",
        "woher ",
        "wohin ",
        "wer ",
        "wann ",
        "warum ",
        "welche ",
        "welcher ",
        "welches ",
        "kann ",
        "kannst ",
        "ist ",
        "sind "
    )

    return normalized_answer.startswith(
        question_starts
    )


# ==========================================
# USUNIĘCIE POCZĄTKU ZDANIA
# ==========================================

def remove_prefix(
    text,
    normalized_text,
    prefixes
):

    for prefix in prefixes:

        if normalized_text.startswith(
            prefix
        ):

            return text[
                len(prefix):
            ].strip()

    return text


# ==========================================
# ZAPISANIE FAKTU
# ==========================================

def remember_context_fact(
    state,
    key,
    value
):

    if not value:
        return

    remember_user_fact(
        state,
        key,
        value
    )

    if key in {
        "name",
        "origin",
        "residence"
    }:

        state[
            key
        ] = value


# ==========================================
# POLECENIA ROZPOCZYNAJĄCE MINI-ROZMOWĘ
# ==========================================

def handle_context_prompt(
    user_message,
    state
):

    message = normalize(
        user_message
    )


    # ======================================
    # POCHODZENIE
    # ======================================

    origin_prompts = {
        "frag mich woher ich komme",
        "frag mich woher ich komme.",
        "frag mich nach meiner herkunft",
        "frag mich nach meiner herkunft."
    }

    if message in origin_prompts:

        state[
            "last_question"
        ] = "origin"

        return (
            "Gerne! "
            "Woher kommst du?"
        )


    # ======================================
    # MIEJSCE ZAMIESZKANIA
    # ======================================

    residence_prompts = {
        "frag mich wo ich wohne",
        "frag mich wo ich wohne.",
        "frag mich wo ich jetzt wohne",
        "frag mich wo ich jetzt wohne."
    }

    if message in residence_prompts:

        state[
            "last_question"
        ] = "residence"

        return (
            "Gerne! "
            "Wo wohnst du?"
        )


    # ======================================
    # HOBBY / CZAS WOLNY
    # ======================================

    hobby_prompts = {
        "frag mich nach meinem hobby",
        "frag mich nach meinem hobby.",
        "frag mich was ich gern in meiner freizeit mache",
        "frag mich was ich gern in meiner freizeit mache.",
        "frag mich was ich gerne in meiner freizeit mache",
        "frag mich was ich gerne in meiner freizeit mache."
    }

    if message in hobby_prompts:

        state[
            "last_question"
        ] = "hobby"

        return (
            "Gerne! "
            "Was machst du gern "
            "in deiner Freizeit?"
        )


    # ======================================
    # CZAS AKTYWNOŚCI
    # ======================================

    activity_time_prompts = {
        "frag mich wann ich rad fahre",
        "frag mich wann ich rad fahre.",
        "frag mich wann ich das mache",
        "frag mich wann ich das mache."
    }

    if message in activity_time_prompts:

        state[
            "last_question"
        ] = "activity_time"

        return (
            "Gerne! "
            "Wann machst du das normalerweise?"
        )


    # ======================================
    # SAMOPOCZUCIE
    # ======================================

    wellbeing_prompts = {
        "frag mich wie es mir geht",
        "frag mich wie es mir geht."
    }

    if message in wellbeing_prompts:

        state[
            "last_question"
        ] = "wellbeing"

        return (
            "Gerne! "
            "Wie geht es dir?"
        )


    return None


# ==========================================
# GŁÓWNA OBSŁUGA KONTEKSTU
# ==========================================

def handle_context_answer(
    user_message,
    session_id="default"
):

    state = get_conversation_state(
        session_id
    )


    # ======================================
    # NAJPIERW SPRAWDZAMY,
    # CZY UŻYTKOWNIK CHCE,
    # ŻEBY NELE ZADAŁA PYTANIE
    # ======================================

    prompt_answer = handle_context_prompt(
        user_message,
        state
    )

    if prompt_answer:

        return prompt_answer


    # ======================================
    # OSTATNIE PYTANIE NELE
    # ======================================

    last_question = state.get(
        "last_question"
    )

    if not last_question:
        return None


    answer = clean_short_answer(
        user_message
    )

    if not answer:
        return None


    normalized_answer = normalize(
        answer
    )


    # ======================================
    # PYTANIE UŻYTKOWNIKA
    # NIE JEST ODPOWIEDZIĄ
    # ======================================

    if is_user_question(
        normalized_answer
    ):

        return None


    # ======================================
    # IMIĘ
    # ======================================

    if last_question == "name":

        name = remove_prefix(
            answer,
            normalized_answer,
            (
                "ich heiße ",
                "ich heisse ",
                "ich bin ",
                "mein name ist "
            )
        )

        if not name:
            return None

        if len(
            name.split()
        ) > 4:
            return None


        name = capitalize_value(
            name
        )


        remember_context_fact(
            state,
            "name",
            name
        )


        state[
            "last_question"
        ] = "origin"


        return (
            f"Freut mich, {name}! "
            "Woher kommst du?"
        )


    # ======================================
    # POCHODZENIE
    # ======================================

    if last_question == "origin":

        origin = remove_prefix(
            answer,
            normalized_answer,
            (
                "ich komme aus ",
                "ich bin aus ",
                "aus "
            )
        )


        if not origin:
            return None


        origin = capitalize_value(
            origin
        )


        remember_context_fact(
            state,
            "origin",
            origin
        )


        state[
            "last_question"
        ] = "residence"


        return (
            f"Ah, aus {origin}. "
            "Und wo wohnst du jetzt?"
        )


    # ======================================
    # MIEJSCE ZAMIESZKANIA
    # ======================================

    if last_question == "residence":

        residence = remove_prefix(
            answer,
            normalized_answer,
            (
                "ich wohne in ",
                "ich lebe in ",
                "in "
            )
        )


        if not residence:
            return None


        residence = capitalize_value(
            residence
        )


        remember_context_fact(
            state,
            "residence",
            residence
        )


        state[
            "last_question"
        ] = None


        name = state.get(
            "name"
        )


        if name:

            return (
                f"Ah, {name}, "
                f"du wohnst in {residence}. "
                "Schön!"
            )


        return (
            f"Ah, du wohnst in "
            f"{residence}. Schön!"
        )


    # ======================================
    # HOBBY / CZAS WOLNY
    # ZWYKŁA ROZMOWA
    # ======================================

    if last_question in {
        "hobby",
        "free_time"
    }:

        hobby = answer


        if normalized_answer in {
            "radfahren",
            "fahrradfahren",
            "rad fahren",
            "fahrrad fahren"
        }:

            hobby = "Radfahren"


        elif (
            "fahre gern rad"
            in normalized_answer
            or
            "fahre gerne rad"
            in normalized_answer
        ):

            hobby = "Radfahren"


        elif normalized_answer in {
            "lesen",
            "kochen",
            "schwimmen",
            "wandern",
            "reisen",
            "tanzen",
            "joggen",
            "fotografieren"
        }:

            hobby = capitalize_value(
                answer
            )


        remember_context_fact(
            state,
            "hobby",
            hobby
        )


        state[
            "last_question"
        ] = "activity_time"


        if hobby == "Radfahren":

            return (
                "Schön! "
                "Wann fährst du normalerweise Rad?"
            )


        return (
            "Schön! "
            "Wann machst du das normalerweise?"
        )


    # ======================================
    # KIEDY UŻYTKOWNIK COŚ ROBI
    # ZWYKŁA ROZMOWA
    # ======================================

    if last_question == "activity_time":

        state[
            "last_question"
        ] = None


        if normalized_answer.startswith(
            "am wochenende"
        ):

            return (
                "Ah, am Wochenende. "
                "Das passt gut!"
            )


        if normalized_answer in {
            "morgens",
            "vormittags",
            "mittags",
            "nachmittags",
            "abends",
            "nachts"
        }:

            return (
                f"Ah, {answer.lower()}. "
                "Schön!"
            )


        if normalized_answer.startswith(
            (
                "am ",
                "um ",
                "nach ",
                "vor "
            )
        ):

            return (
                f"Ah, {answer}. "
                "Schön!"
            )


        return (
            f"Ah, {answer}. "
            "Danke!"
        )


    # ======================================
    # SAMOPOCZUCIE
    # ======================================

    if last_question == "wellbeing":

        state[
            "last_question"
        ] = None


        if normalized_answer in {
            "gut",
            "sehr gut",
            "ganz gut",
            "super",
            "prima",
            "mir geht es gut",
            "mir gehts gut",
            "mir geht es sehr gut",
            "mir gehts sehr gut"
        }:

            return (
                "Schön zu hören! "
                "Was möchtest du heute machen?"
            )


        if normalized_answer in {
            "geht so",
            "so lala",
            "naja",
            "na ja"
        }:

            return (
                "Verstehe. "
                "Möchtest du ein bisschen "
                "Deutsch üben?"
            )


        if normalized_answer in {
            "nicht gut",
            "schlecht",
            "mir geht es nicht gut",
            "mir gehts nicht gut"
        }:

            return (
                "Das tut mir leid. "
                "Möchtest du trotzdem "
                "ein bisschen Deutsch üben?"
            )


        if normalized_answer in {
            "müde",
            "ich bin müde"
        }:

            return (
                "Oh, du bist müde. "
                "Dann können wir heute "
                "etwas Leichtes machen."
            )


        return (
            "Danke, dass du mir das sagst."
        )


    return None
