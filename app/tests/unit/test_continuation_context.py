from app.agent.utils import build_continuation_context
from app.db.models import Memory


def test_build_context_without_memories():
    ctx = build_continuation_context(clarification_context="User уточнил цель", memories=[])

    assert "CURRENT CONTINUATION CONTEXT" in ctx
    assert "User уточнил цель" in ctx
    assert "BACKGROUND KNOWLEDGE" not in ctx


def test_build_context_with_memories():
    memories = [
        Memory(title="Тема 1", summary="Краткое описание 1"),
        Memory(title="Тема 2", summary="Краткое описание 2"),
    ]

    ctx = build_continuation_context(clarification_context="Уточнение пользователя", memories=memories)

    assert "BACKGROUND KNOWLEDGE" in ctx
    assert "Тема 1" in ctx
    assert "Тема 2" in ctx
