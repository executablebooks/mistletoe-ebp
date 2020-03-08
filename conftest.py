import pytest


@pytest.fixture(scope="function", autouse=True)
def reset_parse_context():
    """Ensure the parse context is reset before each test."""
    from mistletoe.parse_context import get_parse_context

    get_parse_context(reset=True)
