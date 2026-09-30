"""Curriculum / Skill Graph v2 for Nele A1.

The fixed conversation graph remains available for shared speaking skills.
Course skills are derived from the real A1 lesson structure, so routing follows
pedagogical lesson/section order instead of alphabetical skill-key order.
"""

from brain.knowledge.A1.lessons import A1_LESSONS
from brain.logic.matcher import normalize

GRAPH_VERSION = 2

A1_SKILL_GRAPH = {
    "conversation:supported_answer": {
        "title": "Mit Unterstützung antworten",
        "level": "A1.1",
        "prerequisites": [],
    },
    "conversation:full_sentence": {
        "title": "Mit einem einfachen vollständigen Satz antworten",
        "level": "A1.1",
        "prerequisites": ["conversation:supported_answer"],
    },
    "conversation:continue_after_correction": {
        "title": "Nach einer Korrektur weiterreden",
        "level": "A1.1",
        "prerequisites": ["conversation:supported_answer"],
    },
    "conversation:continuation": {
        "title": "Ein kurzes Gespräch fortsetzen",
        "level": "A1.1",
        "prerequisites": ["conversation:full_sentence"],
    },
    "conversation:independent_answer": {
        "title": "Selbstständig mit einem vollständigen Satz antworten",
        "level": "A1.1",
        "prerequisites": ["conversation:full_sentence", "conversation:continuation"],
    },
}


def _course_slug(section):
    return normalize(str(section or "")).strip(" .?!„“\\\"'").replace(" ", "_")


def _build_a1_course_graph():
    graph = {}
    previous = None
    for lesson in sorted(A1_LESSONS):
        data = A1_LESSONS[lesson]
        for section in data.get("sections") or []:
            skill = f"course:a1:{lesson}:{_course_slug(section)}"
            graph[skill] = {
                "title": section,
                "level": "A1",
                "lesson": int(lesson),
                "section": section,
                "prerequisites": [previous] if previous else [],
            }
            previous = skill
    return graph


A1_COURSE_SKILL_GRAPH = _build_a1_course_graph()


def _progress_skills(state):
    return dict((((state or {}).get("learning_progress_v1") or {}).get("skills")) or {})


def _graph_item(skill):
    return A1_COURSE_SKILL_GRAPH.get(skill) or A1_SKILL_GRAPH.get(skill)


def get_skill(skill):
    item = _graph_item(skill)
    return dict(item) if item else None


def get_prerequisites(skill):
    return list((_graph_item(skill) or {}).get("prerequisites") or [])


def _mastered(skill, progress):
    return (progress.get(skill) or {}).get("status") == "mastered"


def prerequisites_met(skill, state):
    progress = _progress_skills(state)
    return all(_mastered(required, progress) for required in get_prerequisites(skill))


def _course_graph_active(state, progress):
    # Course prerequisites must never influence Frei sprechen, even when the
    # learner carries course mastery in persistent memory from an earlier
    # course session.
    if str((state or {}).get("conversation_mode") or "").strip().lower() != "course":
        return False
    if any(key.startswith("course:") for key in progress):
        return True
    student = (state or {}).get("student_progress") or {}
    return (
        str(student.get("current_level") or "").strip().upper() == "A1"
        and bool(student.get("current_lesson"))
    )


def _ordered_course_skills(skills):
    wanted = set(skills)
    ordered = [skill for skill in A1_COURSE_SKILL_GRAPH if skill in wanted]
    # Preserve unknown future/dynamic course skills after known curriculum
    # nodes rather than letting their spelling reorder the real A1 syllabus.
    ordered.extend(sorted(wanted - set(ordered)))
    return ordered


def get_curriculum_state(state):
    progress = _progress_skills(state)
    mastered = []
    ready = []
    blocked = []
    review = []

    for skill in A1_SKILL_GRAPH:
        status = (progress.get(skill) or {}).get("status")
        if status == "mastered":
            mastered.append(skill)
        elif status == "needs_review":
            review.append(skill)
        elif prerequisites_met(skill, state):
            ready.append(skill)
        else:
            blocked.append(skill)

    dynamic_review = sorted(
        key for key, item in progress.items()
        if key not in A1_SKILL_GRAPH
        and not key.startswith("course:")
        and item.get("status") == "needs_review"
    )

    course_mastered = _ordered_course_skills(
        key for key, item in progress.items()
        if key.startswith("course:") and item.get("status") == "mastered"
    )
    course_in_progress = _ordered_course_skills(
        key for key, item in progress.items()
        if key.startswith("course:") and item.get("status") in {"introduced", "practicing", "improving"}
    )
    course_review = _ordered_course_skills(
        key for key, item in progress.items()
        if key.startswith("course:") and item.get("status") == "needs_review"
    )

    course_ready = []
    course_blocked = []
    if _course_graph_active(state, progress):
        for skill in A1_COURSE_SKILL_GRAPH:
            status = (progress.get(skill) or {}).get("status")
            if status in {"mastered", "needs_review", "introduced", "practicing", "improving"}:
                continue
            if prerequisites_met(skill, state):
                course_ready.append(skill)
            else:
                course_blocked.append(skill)

    return {
        "version": GRAPH_VERSION,
        "level": "A1.1",
        "mastered": sorted(mastered),
        "ready": sorted(ready),
        "blocked": sorted(blocked),
        "needs_review": sorted(review),
        "dynamic_needs_review": dynamic_review,
        "course_mastered": course_mastered,
        "course_in_progress": course_in_progress,
        "course_needs_review": course_review,
        "course_ready": course_ready,
        "course_blocked": course_blocked,
    }


def _focused_course_choice(state, curriculum):
    """Keep explicit course lesson selection inside that lesson.

    Entering a lesson directly is a valid course action. Earlier lessons must
    not steal routing, while section order inside the selected lesson remains
    strict.
    """
    student = (state or {}).get("student_progress") or {}
    try:
        lesson = int(student.get("current_lesson"))
    except (TypeError, ValueError):
        return None
    prefix = f"course:a1:{lesson}:"
    ordered = [skill for skill in A1_COURSE_SKILL_GRAPH if skill.startswith(prefix)]
    if not ordered:
        return None
    progress = _progress_skills(state)
    for index, skill in enumerate(ordered):
        status = (progress.get(skill) or {}).get("status")
        if status == "needs_review":
            return {"skill": skill, "reason": "course_review"}
        if status in {"introduced", "practicing", "improving"}:
            return {"skill": skill, "reason": "course_mastery_in_progress"}
        if status == "mastered":
            continue
        earlier_in_lesson = ordered[:index]
        if all(_mastered(required, progress) for required in earlier_in_lesson):
            return {"skill": skill, "reason": "course_prerequisites_met"}
        return None
    return None


def choose_next_curriculum_skill(state):
    curriculum = get_curriculum_state(state)
    course_mode = str((state or {}).get("conversation_mode") or "").strip().lower() == "course"

    if course_mode:
        progress = _progress_skills(state)
        review = [
            skill for skill in A1_SKILL_GRAPH
            if (progress.get(skill) or {}).get("status") == "needs_review"
        ]
        ready = [
            skill for skill in A1_SKILL_GRAPH
            if (
                (progress.get(skill) or {}).get("status") not in {"mastered", "needs_review"}
                and prerequisites_met(skill, state)
            )
        ]
    else:
        review = curriculum["needs_review"]
        ready = curriculum["ready"]

    if course_mode:
        focused = _focused_course_choice(state, curriculum)
        if focused:
            return focused
    if curriculum["course_needs_review"]:
        return {"skill": curriculum["course_needs_review"][0], "reason": "course_review"}
    if course_mode and curriculum["course_in_progress"]:
        return {"skill": curriculum["course_in_progress"][0], "reason": "course_mastery_in_progress"}
    if course_mode and curriculum["course_ready"]:
        return {"skill": curriculum["course_ready"][0], "reason": "course_prerequisites_met"}
    if review:
        return {"skill": review[0], "reason": "curriculum_review"}
    if curriculum["dynamic_needs_review"]:
        return {"skill": curriculum["dynamic_needs_review"][0], "reason": "dynamic_review"}
    if ready:
        return {"skill": ready[0], "reason": "prerequisites_met"}
    return None
