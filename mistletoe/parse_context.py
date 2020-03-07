"""This module provides a container for global variables of a single parse.

It uses the `threading.local` object to ensure that global variables
are not changed by different threads.
"""
from copy import deepcopy
from threading import local

THREAD = local()


class ParseContext:
    def __init__(self, block_tokens=None, span_tokens=None, link_definitions=None):
        """A class to contain context for a single parse.

        :param block_tokens: a list of block tokens to use during the parse.
            If None the standard blocks will be used from `block_tokens.__all__`
        :param span_tokens: a list of span tokens to use during the parse.
            If None the standard blocks will be used from `span_tokens.__all__`
        :param span_tokens: [description], defaults to None
        :param link_definitions: a dict of link definitons, obtained from `[def]: link`
        """
        if link_definitions is None:
            self.link_definitions = {}
        else:
            self.link_definitions = link_definitions
        if block_tokens is not None:
            self.block_tokens = block_tokens
        else:
            from mistletoe import block_tokens

            self.block_tokens = tokens_from_module(block_tokens)
        if span_tokens is not None:
            self.span_tokens = span_tokens
        else:
            from mistletoe import span_tokens

            self.span_tokens = tokens_from_module(span_tokens)

    def copy(self):
        return deepcopy(self)


def get_parse_context(reset=False) -> ParseContext:
    """Return the current `ParseContext`."""
    global THREAD
    if not hasattr(THREAD, "context") or reset:
        THREAD.context = ParseContext()
    return THREAD.context


def set_parse_context(parse_context):
    """Set an existing `ParseContext`."""
    global THREAD
    THREAD.context = parse_context


def tokens_from_module(module):
    """
    Helper method; takes a module and returns a list of all token classes
    specified in module.__all__. Useful when custom tokens are defined in a
    separate module.
    """
    return [getattr(module, name) for name in module.__all__]
