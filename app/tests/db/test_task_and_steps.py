import pytest

from app.db.crud import (
    add_task_steps,
    create_task,
    get_next_pending_step,
    get_or_create_user,
)
from app.db.models import TaskStepStatus


@pytest.mark.asyncio
async def test_create_task(session):
    await get_or_create_user(session, 123, "new")
    task = await create_task(session, user_id=1, title="Test Task")

    assert task.id is not None
    assert task.title == "Test Task"


@pytest.mark.asyncio
async def test_add_task_steps(session):
    await get_or_create_user(session, 123, "new")
    task = await create_task(session, user_id=1, title="Task")

    steps = await add_task_steps(session, task.id, ["step 1", "step 2"])

    assert len(steps) == 2
    assert steps[0].step_order == 1
    assert steps[1].step_order == 2


@pytest.mark.asyncio
async def test_get_next_pending_step(session):
    await get_or_create_user(session, 123, "new")
    task = await create_task(session, 1, "Task")
    await add_task_steps(session, task.id, ["s1", "s2"])

    step = await get_next_pending_step(session, task.id)

    assert step is not None
    assert step.step_order == 1
    assert step.status == TaskStepStatus.PENDING
