import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.handlers import start_cmd
from app.db.crud import get_user_by_telegram_id


@pytest.mark.asyncio
async def test_start_creates_user(fake_message, engine, monkeypatch):
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    monkeypatch.setattr(
        "app.bot.handlers.AsyncSessionLocal",
        async_session,
    )

    await start_cmd(fake_message)

    fake_message.answer.assert_called_once()

    async with async_session() as session:
        user = await get_user_by_telegram_id(
            session,
            fake_message.from_user.id,
        )

        assert user is not None
