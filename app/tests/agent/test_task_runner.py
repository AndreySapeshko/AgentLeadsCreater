from unittest.mock import AsyncMock

import pytest

from app.agent.task_runner import TaskRunner
from app.db.crud import add_task_steps, create_task, get_or_create_user
from app.db.models import TaskStepStatus


@pytest.mark.asyncio
async def test_task_runner_full_flow(session, mock_llm):
    # mock message
    message = AsyncMock()

    # LLM будет вызван:
    # 1. executor
    # 2. final_report
    mock_llm.side_effect = [
        # executor response
        type(
            "Resp",
            (),
            {
                "choices": [
                    type(
                        "Choice",
                        (),
                        {
                            "message": type(
                                "Msg",
                                (),
                                {"content": "TEXT:\nStep result\n\nSOURCES:\n- url"},
                            )
                        },
                    )
                ]
            },
        ),
        # final report response
        type(
            "Resp",
            (),
            {
                "choices": [
                    type(
                        "Choice",
                        (),
                        {
                            "message": type(
                                "Msg",
                                (),
                                {"content": "FINAL REPORT"},
                            )
                        },
                    )
                ]
            },
        ),
    ]

    # prepare DB
    user = await get_or_create_user(session, 123, "new")
    task = await create_task(session, user_id=user.id, title="Task")
    await add_task_steps(session, task.id, ["step 1"])

    runner = TaskRunner()
    result = await runner.run_task(session, task.id, message)

    assert result == "FINAL REPORT"

    # step updated
    await session.refresh(task, ["steps"])
    steps = task.steps
    assert steps[0].status == TaskStepStatus.DONE

    # telegram notified
    message.answer.assert_any_call("Шаг №1 изучен 🔍")
