import inspect

from brain.logic.conversation_orchestrator import build_turn_plan
from brain.logic import free_conversation


def test_turn_plan_exposes_compact_learner_context():
    plan = build_turn_plan(
        teacher_policy={"action": "CONTINUE"},
        learner_model={
            "autonomy": "needs_support",
            "adaptive_support": 3,
            "weaknesses": ["conversation_support"],
            "vocabulary": {"review_due": ["der Bahnhof"]},
            "next_curriculum_skill": {"skill": "conversation:full_sentence", "reason": "prerequisites_met"},
            "learning_outcomes": {"last": {"status": "NOT_YET", "action": "MODEL_SENTENCE"}},
        },
    )
    assert plan["version"] == 3
    assert plan["learner_context"]["autonomy"] == "needs_support"
    assert plan["learner_context"]["adaptive_support"] == 3
    assert plan["learner_context"]["review_words"] == ["der Bahnhof"]
    assert plan["learner_context"]["next_curriculum_skill"] == "conversation:full_sentence"
    assert plan["learner_context"]["last_learning_outcome"]["status"] == "NOT_YET"


def test_free_conversation_passes_learner_model_to_turn_plan():
    assert "learner_model=learner_model" in inspect.getsource(free_conversation)
