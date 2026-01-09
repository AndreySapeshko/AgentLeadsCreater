from app.agent.client import llm_client
from app.agent.prompts import STEP_EXECUTOR_PROMPT
from app.agent.tools import fetch_url_sync, search_web_sync

TOOLS_MAP = {
    "search_web_sync": search_web_sync,
    "fetch_url_sync": fetch_url_sync,
}


class StepExecutor:
    async def execute(self, step_text: str) -> dict:
        messages = [
            {"role": "system", "content": STEP_EXECUTOR_PROMPT},
            {"role": "user", "content": step_text},
        ]

        response = await llm_client.chat(
            model="gpt-4.1-mini",
            messages=messages,
        )

        content = response.choices[0].message.content

        from app.agent.utils import parse_executor_output

        text, sources = parse_executor_output(content)

        return {
            "text": text,
            "sources": sources,
        }
