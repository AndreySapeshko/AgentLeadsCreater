import pytest

from app.agent.step_executor import StepExecutor


@pytest.mark.asyncio
async def test_executor_parses_text_and_sources(mock_llm):
    mock_llm.return_value.choices = [
        type(
            "Choice",
            (),
            {
                "message": type(
                    "Msg",
                    (),
                    {"content": ("TEXT:\nResult text\n\n" "SOURCES:\n" "- https://example.com\n")},
                )
            },
        )
    ]

    executor = StepExecutor()
    result = await executor.execute("step description")

    assert result["text"] == "Result text"
    assert result["sources"] == ["https://example.com"]
