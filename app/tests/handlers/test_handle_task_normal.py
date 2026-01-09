from unittest.mock import AsyncMock

import pytest

from app.bot.handlers import handle_task


@pytest.mark.asyncio
async def test_handle_task_run_research(fake_message_from_auth_user, session, monkeypatch):
    fake_message_from_auth_user.text = "Исследуй дроны в геологии"

    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    monkeypatch.setattr(
        "app.bot.handlers.detect_repeat",
        AsyncMock(return_value=False),
    )

    run_mock = AsyncMock()
    monkeypatch.setattr(
        "app.bot.handlers.run_research",
        run_mock,
    )

    await handle_task(fake_message_from_auth_user)

    run_mock.assert_awaited_once()
