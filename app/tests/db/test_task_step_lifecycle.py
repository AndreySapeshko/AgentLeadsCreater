import pytest

from app.db.crud import (
    add_task_steps,
    create_task,
    get_or_create_user,
    mark_step_error,
    mark_step_in_progress,
    update_step_result,
)
from app.db.models import TaskStepStatus


@pytest.mark.asyncio
async def test_mark_step_in_progress(session):
    await get_or_create_user(session, 123, "new")
    task = await create_task(session, 1, "Task")
    steps = await add_task_steps(session, task.id, ["s1"])

    step = steps[0]
    updated = await mark_step_in_progress(session, step.id)

    assert updated.status == TaskStepStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_update_step_result(session):
    await get_or_create_user(session, 123, "new")
    task = await create_task(session, 1, "Task")
    steps = await add_task_steps(session, task.id, ["s1"])

    step = steps[0]
    result = {"text": "done", "sources": ["url"]}

    updated = await update_step_result(session, step.id, result)

    assert updated.status == TaskStepStatus.DONE
    assert updated.result == "done"
    assert updated.sources_json == ["url"]


@pytest.mark.asyncio
async def test_mark_step_error(session):
    await get_or_create_user(session, 123, "new")
    task = await create_task(session, 1, "Task")
    steps = await add_task_steps(session, task.id, ["s1"])

    step = steps[0]
    updated = await mark_step_error(session, step.id, "error")

    assert updated.status == TaskStepStatus.ERROR
    assert updated.result == "error"
