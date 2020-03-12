"""
Make mistletoe easier to import.
"""

__version__ = "0.10.0"
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
from mistletoe.parse_context import ParseContext  # noqa: F401


def markdown(
    iterable,
    renderer: BaseRenderer = HTMLRenderer,
    parse_context=None,
    init_token=Document,
    read_kwargs=None,
    **kwargs
):
    """
    Render text with a given renderer.

    :param iterable: string or list of strings
    :param renderer: the renderer to use
    :param parse_context: the parse context stores global parsing variables,
        such as the block/span tokens to search for,
        and link/footnote definitions that have been collected.
        If None, a new context will be instatiated, with the default
        block/span tokens for this renderer.
    :type parse_context: mistletoe.parse_context.ParseContext
    :param init_token: The initial token to use for parsing the text `init_token.read`
    :param read_kwargs: key-word arguments to parse to the ``init_token.read`` method
    :param kwargs: key-word arguments to parse to the renderer initialisation
    """
    with renderer(parse_context=parse_context, **kwargs) as renderer:
        return renderer.render(init_token.read(iterable, **(read_kwargs or {})))
