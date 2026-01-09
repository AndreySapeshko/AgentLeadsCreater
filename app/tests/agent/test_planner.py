import json

import pytest

from app.agent.agent import ResearchPlanner


@pytest.mark.asyncio
async def test_planner_returns_valid_plan(mock_llm):
    mock_llm.return_value.choices = [
        type(
            "Choice",
            (),
            {
                "message": type(
                    "Msg",
                    (),
                    {
                        "content": json.dumps(
                            {
                                "title": "Test research",
                                "steps": ["step 1", "step 2"],
                            }
                        )
                    },
                )
            },
        )
    ]

    planner = ResearchPlanner()
    plan = await planner.plan("test input")

    assert plan["title"] == "Test research"
    assert len(plan["steps"]) == 2
