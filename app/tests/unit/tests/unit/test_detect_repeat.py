from unittest.mock import patch

import pytest

from app.agent.detect_repeat import detect_repeat
from app.db.models import Memory


@pytest.mark.asyncio
@patch("app.agent.detect_repeat.llm_client.chat")
async def test_detect_repeat_yes(mock_chat):
    mock_chat.return_value.choices = [type("Choice", (), {"message": type("Msg", (), {"content": "YES"})()})]

    memories = [Memory(title="Исследуй дроны", summary="...")]

    result = await detect_repeat("Исследуй дроны в геологии", memories)

    assert result is True


@pytest.mark.asyncio
@patch("app.agent.detect_repeat.llm_client.chat")
async def test_detect_repeat_no(mock_chat):
    mock_chat.return_value.choices = [type("Choice", (), {"message": type("Msg", (), {"content": "NO"})()})]

    memories = [Memory(title="Солнечная энергетика", summary="...")]

    result = await detect_repeat("Дроны в геологии", memories)

    assert result is False
