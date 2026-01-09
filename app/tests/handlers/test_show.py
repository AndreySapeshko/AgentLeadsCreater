import pytest
from aiogram.filters import CommandObject

from app.bot.handlers import show_handler
from app.db.crud import create_task, save_memory


@pytest.mark.asyncio
async def test_show_from_unauthorized_user(session, fake_message, monkeypatch):
    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    cmd = CommandObject(command="show", args="77")

    await show_handler(fake_message, cmd)

    fake_message.answer.assert_called_with("Сначала отправь /start, чтобы зарегистрироваться.")


@pytest.mark.asyncio
async def test_show_without_args(fake_message_from_auth_user):
    cmd = CommandObject(command="show", args=None)

    await show_handler(fake_message_from_auth_user, cmd)

    fake_message_from_auth_user.answer.assert_called_with("Укажи ID исследования: /show 3")


@pytest.mark.asyncio
async def test_show_not_found(fake_message_from_auth_user, session, monkeypatch):
    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    cmd = CommandObject(command="show", args="999")

    await show_handler(fake_message_from_auth_user, cmd)

    fake_message_from_auth_user.answer.assert_called_with("Исследование не найдено.")


@pytest.mark.asyncio
async def test_show_success(fake_message_from_auth_user, user, session, monkeypatch):
    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        lambda: session,
    )

    task = await create_task(session, user.id, "Task")
    memory = await save_memory(
        session,
        user_id=user.id,
        task_id=task.id,
        title="Title",
        summary="Summary",
    )

    cmd = CommandObject(command="show", args=str(memory.id))

    await show_handler(fake_message_from_auth_user, cmd)

    fake_message_from_auth_user.answer.assert_called_with(f"📌 {memory.title}\n\n{memory.summary}")
