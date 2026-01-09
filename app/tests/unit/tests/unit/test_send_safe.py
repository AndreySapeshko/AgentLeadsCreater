import pytest

from app.agent.utils import MAX_TG_LEN, ask_clarification, send_safe


class FakeMessage:
    def __init__(self):
        self.sent = []

    async def answer(self, text):
        self.sent.append(text)


@pytest.mark.asyncio
async def test_send_safe_short_message():
    msg = FakeMessage()
    text = "Привет"

    await send_safe(msg, text)

    assert msg.sent == ["Привет"]


@pytest.mark.asyncio
async def test_send_safe_long_message():
    msg = FakeMessage()
    text = "A\n" * 5000  # длинный текст

    await send_safe(msg, text)

    assert len(msg.sent) > 1
    assert all(len(part) <= MAX_TG_LEN for part in msg.sent)


@pytest.mark.asyncio
async def test_ask_clarification():
    msg = FakeMessage()

    await ask_clarification(msg)

    assert len(msg.sent) == 1
    assert "Цель исследования" in msg.sent[0]
