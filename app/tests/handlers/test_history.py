import pytest

from app.bot.handlers import history_handler
from app.db.crud import create_task, save_memory


@pytest.mark.asyncio
async def test_history_from_unauthorized_user(fake_message, session, monkeypatch):
    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    await history_handler(fake_message)

    fake_message.answer.assert_called_with("Сначала отправь /start, чтобы зарегистрироваться.")


@pytest.mark.asyncio
async def test_history_no_memories(fake_message_from_auth_user, session, monkeypatch):
    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    await history_handler(fake_message_from_auth_user)

    fake_message_from_auth_user.answer.assert_called_with("История пока пуста.")


@pytest.mark.asyncio
async def test_history_with_memory(session, fake_message_from_auth_user, user, monkeypatch):
    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    # user = await get_or_create_user(session=session, telegram_id=123, username="test")
    # message = FakeMessage(user)
    task = await create_task(session, user.id, "Task")
    await save_memory(
        session,
        user_id=user.id,
        task_id=task.id,
        title="Test",
        summary="Summary text",
    )

    await history_handler(fake_message_from_auth_user)

    called_text = fake_message_from_auth_user.answer.call_args.args[0]
    assert "Последние исследования:" in called_text
