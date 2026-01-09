from unittest.mock import AsyncMock

import pytest

import app
from app.bot.handlers import handle_task


@pytest.mark.asyncio
async def test_handle_task_repeat_short(fake_message_from_auth_user, session, monkeypatch):
    fake_message_from_auth_user.text = "дроны"

    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    monkeypatch.setattr(
        "app.bot.handlers.detect_repeat",
        AsyncMock(return_value=True),
    )

    monkeypatch.setattr(
        "app.bot.handlers.ask_clarification",
        AsyncMock(),
    )

    monkeypatch.setattr(
        "app.bot.handlers.run_research",
        AsyncMock(),
    )

    await handle_task(fake_message_from_auth_user)

    app.bot.handlers.ask_clarification.assert_awaited()
    app.bot.handlers.run_research.assert_not_awaited()
