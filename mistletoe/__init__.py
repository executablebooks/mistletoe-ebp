"""
Make mistletoe easier to import.
"""

__version__ = "0.9.4a1"
__all__ = [
    "renderers",
    "base_elements",
    "block_tokens",
    "block_tokenizer",
    "span_tokens",
    "span_tokenizer",
]

from mistletoe.block_tokens import Document
from mistletoe.renderers.base import BaseRenderer  # noqa: F401
from mistletoe.renderers.html import HTMLRenderer


def markdown(iterable, renderer=HTMLRenderer):
    """
    Output HTML with default settings.
    Enables inline and block-level HTML tags.
    """
    with renderer() as renderer:
        return renderer.render(Document.read(iterable))
