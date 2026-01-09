import pytest

from app.bot.handlers import last_handler
from app.db.crud import create_task, get_or_create_user, save_memory
from app.tests.conftest import FakeMessage


@pytest.mark.asyncio
async def test_last_from_unauthorized_user(fake_message, session, monkeypatch):
    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    await last_handler(fake_message)

    fake_message.answer.assert_called_with("Сначала отправь /start, чтобы зарегистрироваться.")


@pytest.mark.asyncio
async def test_last_no_memories(fake_message_from_auth_user, session, monkeypatch):
    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    await last_handler(fake_message_from_auth_user)

    fake_message_from_auth_user.answer.assert_called_with("Нет сохранённых исследований.")


@pytest.mark.asyncio
async def test_last_with_memory(session, monkeypatch):
    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    user = await get_or_create_user(session=session, telegram_id=123, username="test")
    message = FakeMessage(user)
    task = await create_task(session, user.id, "Task")
    await save_memory(
        session,
        user_id=user.id,
        task_id=task.id,
        title="Test",
        summary="Summary text",
    )

    await last_handler(message)

    message.answer.assert_called_with("Summary text")
