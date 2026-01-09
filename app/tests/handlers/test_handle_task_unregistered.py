import pytest

from app.bot.handlers import handle_task


@pytest.mark.asyncio
async def test_handle_task_unregistered(fake_message, session, monkeypatch):
    fake_message.text = "Исследуй что-нибудь"

    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    await handle_task(fake_message)

    fake_message.answer.assert_called_with("Сначала отправь /start, чтобы зарегистрироваться.")
