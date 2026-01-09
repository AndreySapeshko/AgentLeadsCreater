from app.agent.client import llm_client
from app.agent.prompts import FINAL_REPORT_PROMPT


class FinalReportAgent:
    async def generate(
        self,
        steps_results: list[str],
        sources: list[str],
    ) -> str:
        content = (
            "Результаты шагов:\n\n"
            + "\n\n".join(f"Шаг {i + 1}:\n{result}" for i, result in enumerate(steps_results))
            + "\n\nИсточники:\n"
            + "\n".join(f"- {s}" for s in sources)
        )

        response = await llm_client.chat(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": FINAL_REPORT_PROMPT},
                {"role": "user", "content": content},
            ],
        )

        return response.choices[0].message.content
