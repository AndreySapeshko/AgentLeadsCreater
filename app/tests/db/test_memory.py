import pytest

from app.db.crud import (
    create_task,
    get_last_memories,
    get_memory_by_id,
    get_or_create_user,
    save_memory,
)


@pytest.mark.asyncio
async def test_save_memory(session):
    user = await get_or_create_user(session, 123, "new")
    task = await create_task(session, 1, "Task")
    memory = await save_memory(
        session,
        user_id=user.id,
        task_id=task.id,
        title="Topic",
        summary="Summary",
        sources_json=["url"],
    )

    assert memory.id is not None
    assert memory.title == "Topic"


@pytest.mark.asyncio
async def test_get_last_memories(session):
    user = await get_or_create_user(session, 123, "new")
    task1 = await create_task(session, 1, "Task")
    task2 = await create_task(session, 1, "Task")
    await save_memory(session, user.id, task1.id, "T1", "S1")
    await save_memory(session, user.id, task2.id, "T2", "S2")

    memories = await get_last_memories(session, user.id)

    assert len(memories) == 2
    assert memories[0].title in ["T2", "T1"]


@pytest.mark.asyncio
async def test_get_memory_by_id(session):
    user = await get_or_create_user(session, 123, "new")
    task = await create_task(session, 1, "Task")
    memory = await save_memory(session, user.id, task.id, "T", "S")

    found = await get_memory_by_id(session, memory.id, user.id)

    assert found is not None
    assert found.id == memory.id
