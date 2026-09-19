# ==========================================
# NELE – ŁADOWANIE LEKCJI
# ==========================================

import importlib.util
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_lesson_module(
    level="A1",
    lesson=1
):

    lesson_path = (
        BASE_DIR
        / "responses"
        / level
        / f"{lesson}.py"
    )

    if not lesson_path.exists():
        return None

    module_name = (
        f"nele_{level}_{lesson}"
    )

    spec = importlib.util.spec_from_file_location(
        module_name,
        lesson_path
    )

    if spec is None:
        return None

    if spec.loader is None:
        return None

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    return module


def load_lesson(
    level="A1",
    lesson=1
):

    module = load_lesson_module(
        level,
        lesson
    )

    if module is None:
        return []

    return getattr(
        module,
        "LESSON_RESPONSES",
        []
    )


# ==========================================
# METADATEN / FLOW EINER LEKTION
# ==========================================

def load_lesson_metadata(
    level="A1",
    lesson=1
):

    module = load_lesson_module(
        level,
        lesson
    )

    if module is None:
        return None


    data = getattr(
        module,
        "LESSON",
        None
    )


    if isinstance(
        data,
        dict
    ):

        return dict(
            data
        )


    return None


def load_lesson_flow(
    level="A1",
    lesson=1
):

    module = load_lesson_module(
        level,
        lesson
    )

    if module is None:
        return None


    flow = getattr(
        module,
        "LESSON_FLOW",
        None
    )


    if isinstance(
        flow,
        dict
    ):

        return flow


    return None


def get_lesson_sections_from_module(
    level="A1",
    lesson=1
):

    flow = load_lesson_flow(
        level,
        lesson
    )


    if not isinstance(
        flow,
        dict
    ):

        return []


    sections = flow.get(
        "sections",
        {}
    )


    if isinstance(
        sections,
        dict
    ):

        return [
            str(
                name
            ).strip()
            for name in sections.keys()
            if str(
                name
            ).strip()
        ]


    if isinstance(
        sections,
        list
    ):

        result = []


        for item in sections:

            if isinstance(
                item,
                str
            ):

                name = item.strip()

            elif isinstance(
                item,
                dict
            ):

                name = str(
                    item.get(
                        "name"
                    )
                    or
                    ""
                ).strip()

            else:

                name = ""


            if (
                name
                and
                name not in result
            ):

                result.append(
                    name
                )


        return result


    return []


def lesson_module_exists(
    level="A1",
    lesson=1
):

    return (
        load_lesson_module(
            level,
            lesson
        )
        is not None
    )


def get_available_lesson_numbers(
    level="A1"
):

    level = str(
        level or "A1"
    ).strip().upper()


    directory = (
        BASE_DIR
        / "responses"
        / level
    )


    if not directory.exists():
        return []


    result = []


    for path in directory.glob(
        "*.py"
    ):

        try:

            number = int(
                path.stem
            )

        except (
            TypeError,
            ValueError
        ):

            continue


        if number > 0:
            result.append(
                number
            )


    return sorted(
        set(
            result
        )
    )


def get_next_lesson_number_from_modules(
    level,
    lesson
):

    try:

        lesson = int(
            lesson
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    for number in get_available_lesson_numbers(
        level
    ):

        if number > lesson:
            return number


    return None
