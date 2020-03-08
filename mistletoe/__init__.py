"""
Make mistletoe easier to import.
"""

__version__ = "0.9.4"
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


def markdown(iterable, renderer=HTMLRenderer, init_token=Document, **kwargs):
    """
    Render text with a given renderer.

    :param iterable: string or list of strings
    :param init_token: The initial token to use for parsing the text `token.read`
    :param kwargs: key-word arguments to parse to the renderer initialisation
    """
    with renderer(**kwargs) as renderer:
        return renderer.render(init_token.read(iterable))
