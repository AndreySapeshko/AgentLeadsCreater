from app.agent.utils import is_short


def test_is_short_true():
    assert is_short("короткий текст") is True


def test_is_short_false():
    long_text = "a" * 150
    assert is_short(long_text) is False
