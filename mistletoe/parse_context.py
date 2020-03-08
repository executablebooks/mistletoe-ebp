"""This module provides a container for global variables of a single parse.

It uses the `threading.local` object to ensure that global variables
are not changed by different threads.
"""
from copy import deepcopy
from importlib import import_module
from threading import local

THREAD = local()


class ParseContext:
    def __init__(self, find_blocks=None, find_spans=None, link_definitions=None):
        """A class to contain context for a single parse.

        :param find_blocks: a list of block tokens to use during the parse.
            If None the standard blocks will be used from `block_tokens.__all__`
        :param find_spans: a list of span tokens to use during the parse.
            If None the standard blocks will be used from `span_tokens.__all__`
        :param link_definitions: a dict of link definitons, obtained from `[def]: link`
        :param nesting_matches: a dict of matches recorded from `find_nested_tokenizer`
        """
        if link_definitions is None:
            self.link_definitions = {}
        else:
            self.link_definitions = link_definitions
        if find_blocks is not None:
            self.block_tokens = tokens_from_classes(find_blocks)
        else:
            from mistletoe.renderers.base import BaseRenderer

            self.block_tokens = list(BaseRenderer.default_block_tokens)
        if find_spans is not None:
            self.span_tokens = tokens_from_classes(find_spans)
        else:
            from mistletoe.renderers.base import BaseRenderer

            self.span_tokens = list(BaseRenderer.default_span_tokens)

        self.nesting_matches = {}

    def copy(self):
        return deepcopy(self)


def get_parse_context(reset=False) -> ParseContext:
    """Return the current `ParseContext`."""
    global THREAD
    if reset:
        THREAD.context = ParseContext()
    else:
        try:
            THREAD.context
        except AttributeError:
            THREAD.context = ParseContext()
    return THREAD.context


def set_parse_context(parse_context):
    """Set an existing `ParseContext`."""
    global THREAD
    THREAD.context = parse_context


def tokens_from_module(module):
    """
    Helper method; takes a module and returns a list of all token classes
    specified in module.__all__.
    Useful when custom tokens are defined in single module.
    """
    return [getattr(module, name) for name in module.__all__]


def tokens_from_classes(classes):
    """
    Helper method; take a list of classes and/or class paths
    (e.g. `mistletoe.span_tokens.Math`) and return the loaded classes.
    """
    return [
        getattr(import_module(".".join(cls.split(".")[:-1])), cls.split(".")[-1])
        if isinstance(cls, str)
        else cls
        for cls in classes
    ]
