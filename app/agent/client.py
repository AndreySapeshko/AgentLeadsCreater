import asyncio
import time

import openai
from openai import AsyncOpenAI

from app.config import OPEN_AI_KEY

client = AsyncOpenAI(api_key=OPEN_AI_KEY)


class LLMClient:
    def __init__(self, client, min_interval: float = 7.0):
        self.client = client
        self.min_interval = min_interval
        self._last_call = 0
        self._lock = asyncio.Lock()

    async def _throttled(self):
        async with self._lock:
            now = time.time()
            delta = now - self._last_call

            if delta < self.min_interval:
                await asyncio.sleep(self.min_interval - delta)

            self._last_call = time.time()

    async def chat(self, **kwargs):

        for attempt in range(7):
            await self._throttled()
            try:
                print("LLM CALL", time.time())
                return await self.client.chat.completions.create(**kwargs)

            except openai.RateLimitError:
                print("RateLimitError")
                await asyncio.sleep(31)

        raise RuntimeError("LLM rate limit retry failed")


llm_client = LLMClient(client, 31)
