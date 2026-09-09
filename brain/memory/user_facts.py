# ==========================================
# NELE – INFORMACJE O UŻYTKOWNIKU
# ==========================================


# ==========================================
# POBRANIE MAGAZYNU FAKTÓW
# ==========================================

def get_user_facts(
    state
):

    if not isinstance(
        state,
        dict
    ):
        return {}

    user_facts = state.get(
        "user_facts"
    )

    if not isinstance(
        user_facts,
        dict
    ):

        user_facts = {}

        state[
            "user_facts"
        ] = user_facts

    return user_facts


# ==========================================
# ZAPISANIE FAKTU
# ==========================================

def remember_user_fact(
    state,
    key,
    value
):

    if not key:
        return False

    if value is None:
        return False

    user_facts = get_user_facts(
        state
    )

    user_facts[
        key
    ] = value

    return True


# ==========================================
# POBRANIE FAKTU
# ==========================================

def get_user_fact(
    state,
    key,
    default=None
):

    if not key:
        return default

    user_facts = get_user_facts(
        state
    )

    return user_facts.get(
        key,
        default
    )


# ==========================================
# SPRAWDZENIE, CZY FAKT ISTNIEJE
# ==========================================

def has_user_fact(
    state,
    key
):

    if not key:
        return False

    user_facts = get_user_facts(
        state
    )

    value = user_facts.get(
        key
    )

    return value is not None


# ==========================================
# USUNIĘCIE JEDNEGO FAKTU
# ==========================================

def forget_user_fact(
    state,
    key
):

    if not key:
        return False

    user_facts = get_user_facts(
        state
    )

    if key not in user_facts:
        return False

    del user_facts[
        key
    ]

    return True


# ==========================================
# POBRANIE WSZYSTKICH FAKTÓW
# ==========================================

def get_all_user_facts(
    state
):

    user_facts = get_user_facts(
        state
    )

    return dict(
        user_facts
    )
