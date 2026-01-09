import pytest

from app.db.crud import get_or_create_user, get_user_by_telegram_id


@pytest.mark.asyncio
async def test_get_or_create_user_creates(session):
    user = await get_or_create_user(
        session,
        telegram_id=123,
        username="testuser",
    )

    assert user.id is not None
    assert user.telegram_id == 123
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_or_create_user_updates_username(session):
    user1 = await get_or_create_user(session, 123, "old")
    user2 = await get_or_create_user(session, 123, "new")

    assert user1.id == user2.id
    assert user2.username == "new"


@pytest.mark.asyncio
async def test_get_user_by_telegram_id(session):
    await get_or_create_user(session, 555, "user555")

    user = await get_user_by_telegram_id(session, 555)

    assert user is not None
    assert user.telegram_id == 555
