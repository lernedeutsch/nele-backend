"""Curriculum / Skill Graph v1 for Nele A1.

Defines prerequisite relationships between skills Nele already measures.
It does not invent lesson completion and does not replace A1_LESSONS.
"""

GRAPH_VERSION = 1

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


def _progress_skills(state):
    return dict((((state or {}).get("learning_progress_v1") or {}).get("skills")) or {})


def get_skill(skill):
    item = A1_SKILL_GRAPH.get(skill)
    return dict(item) if item else None


def get_prerequisites(skill):
    return list((A1_SKILL_GRAPH.get(skill) or {}).get("prerequisites") or [])


def _mastered(skill, progress):
    return (progress.get(skill) or {}).get("status") == "mastered"


def prerequisites_met(skill, state):
    progress = _progress_skills(state)
    return all(_mastered(required, progress) for required in get_prerequisites(skill))


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

    # Dynamic vocabulary and correct-form skills are valid learning-progress
    # skills, but they are practice targets rather than fixed curriculum nodes.
    dynamic_review = sorted(
        key for key, item in progress.items()
        if key not in A1_SKILL_GRAPH and item.get("status") == "needs_review"
    )

    return {
        "version": GRAPH_VERSION,
        "level": "A1.1",
        "mastered": sorted(mastered),
        "ready": sorted(ready),
        "blocked": sorted(blocked),
        "needs_review": sorted(review),
        "dynamic_needs_review": dynamic_review,
    }


def choose_next_curriculum_skill(state):
    curriculum = get_curriculum_state(state)
    course_mode = str((state or {}).get("conversation_mode") or "").strip().lower() == "course"

    # Course routing must follow the pedagogical order encoded by the graph,
    # not the alphabetical presentation order used by the shared model.
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

    if review:
        return {"skill": review[0], "reason": "curriculum_review"}
    if curriculum["dynamic_needs_review"]:
        return {"skill": curriculum["dynamic_needs_review"][0], "reason": "dynamic_review"}
    if ready:
        return {"skill": ready[0], "reason": "prerequisites_met"}
    return None
