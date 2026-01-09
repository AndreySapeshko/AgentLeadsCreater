import pytest

from app.agent.final_report import FinalReportAgent


@pytest.mark.asyncio
async def test_final_report_generate(mock_llm):
    mock_llm.return_value.choices = [
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

    agent = FinalReportAgent()

    report = await agent.generate(
        steps_results=["step 1 result", "step 2 result"],
        sources=["url1", "url2"],
    )

    assert report == "FINAL REPORT"
