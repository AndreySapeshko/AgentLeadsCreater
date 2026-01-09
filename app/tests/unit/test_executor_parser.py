from app.agent.utils import parse_executor_output


def test_parse_with_sources():
    content = """
TEXT:
Это результат шага.

SOURCES:
- https://example.com
- wikipedia.org
"""

    text, sources = parse_executor_output(content)

    assert text == "Это результат шага."
    assert sources == [
        "https://example.com",
        "wikipedia.org",
    ]


def test_parse_without_sources():
    content = "Просто текст без источников."

    text, sources = parse_executor_output(content)

    assert text == "Просто текст без источников."
    assert sources == []
