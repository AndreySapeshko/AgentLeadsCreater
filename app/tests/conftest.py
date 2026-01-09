import asyncio
import os
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.agent.client import llm_client
from app.db.crud import get_or_create_user
from app.db.models import Base

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USER = os.getenv("POSTGRES_USER")
TEST_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/test_db"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        async with session.begin():
            yield session


@pytest.fixture
def mock_llm(monkeypatch):
    async_mock = AsyncMock()

    monkeypatch.setattr(llm_client, "chat", async_mock)
    return async_mock


@pytest.fixture
async def user(session):
    return await get_or_create_user(session=session, telegram_id=123, username="test")


class From_user:
    def __init__(self, telegram_id=123, username="test"):
        self.id = telegram_id
        self.username = username


class FakeUser:
    def __init__(self, user_id=1, telegram_id=123, username="test"):
        self.id = user_id
        self.telegram_id = telegram_id
        self.username = username


class FakeMessage:
    def __init__(self, user, text=""):
        self.text = text
        self.user_id = user.id
        self.from_user = From_user(telegram_id=user.telegram_id, username=user.username)
        self.answer = AsyncMock()


@pytest.fixture
def fake_user():
    return FakeUser()


@pytest.fixture
def fake_message(fake_user):
    return FakeMessage(fake_user)


@pytest.fixture
def fake_message_from_auth_user(user):
    message = FakeMessage(user)
    return message
