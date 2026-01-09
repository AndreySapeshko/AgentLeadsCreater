import pytest

from app.db.crud import (
    clear_clarification_state,
    get_or_create_user,
    get_task_waiting_clarification,
    save_clarification_state,
)


@pytest.mark.asyncio
async def test_clarification_flow(session):
    user = await get_or_create_user(session, 123, "new")
    await save_clarification_state(session, user_id=user.id, original_input="Topic")

    task = await get_task_waiting_clarification(session, user.id)
    assert task is not None
    assert task.clarification_needed is True

    await clear_clarification_state(session, task)

    task2 = await get_task_waiting_clarification(session, user.id)
    assert task2 is None
