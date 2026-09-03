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
