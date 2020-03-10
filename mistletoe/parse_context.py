"""This module provides a container for global variables of a single parse.

It uses the `threading.local` object to ensure that global variables
are not changed by different threads.
"""
from collections import OrderedDict
from collections.abc import MutableSet
from copy import deepcopy
from importlib import import_module
from threading import local

THREAD = local()


class TokenSet(MutableSet):
    """An ordered set of tokens."""

    def __init__(self, tokens):
        self._tokens = OrderedDict((t, t.__name__) for t in tokens)

    def __contains__(self, token):
        return token in self._tokens

    def __iter__(self):
        for token in self._tokens:
            yield token

    def __len__(self):
        return len(self._tokens)

    def add(self, token):
        self._tokens[token] = token.__name__

    def discard(self, token):
        self._tokens.pop(token, None)

    def insert(self, index, token):
        token_list = list(self._tokens.items())
        token_list.insert(index, (token, token.__name__))
        self._tokens = OrderedDict(token_list)

    def insert_after(self, token, after_token):
        assert after_token in self._tokens, after_token
        indx = list(self._tokens.keys()).index(after_token) + 1
        token_list = list(self._tokens.items())
        token_list.insert(indx, (token, token.__name__))
        self._tokens = OrderedDict(token_list)

    def insert_before(self, token, before_token):
        assert before_token in self._tokens
        indx = list(self._tokens.keys()).index(before_token)
        token_list = list(self._tokens.items())
        token_list.insert(indx, (token, token.__name__))
        self._tokens = OrderedDict(token_list)


class ParseContext:
    def __init__(
        self,
        find_blocks=None,
        find_spans=None,
        link_definitions=None,
        foot_definitions=None,
    ):
        """A class to contain context for a single parse.

        :param find_blocks: a list of block tokens to use during the parse. If None,
            the standard blocks will be used from `BaseRenderer.default_block_token`.
        :param find_spans: a list of span tokens to use during the parse. If None,
            the standard blocks will be used from `BaseRenderer.default_span_tokens`.
        :param link_definitions: a dict of link definitons, obtained from `[def]: link`
        :param foot_definitions: a dict of footnote definitons,
            obtained from `[^def]: link` (if Footnote token active)
        :param nesting_matches: a dict of matches recorded from `find_nested_tokenizer`
        """
        # tokens used for matching
        if find_blocks is not None:
            self.block_tokens = TokenSet(tokens_from_classes(find_blocks))
        else:
            from mistletoe.renderers.base import BaseRenderer

            self.block_tokens = TokenSet(BaseRenderer.default_block_tokens)
        if find_spans is not None:
            self.span_tokens = TokenSet(tokens_from_classes(find_spans))
        else:
            from mistletoe.renderers.base import BaseRenderer

            self.span_tokens = TokenSet(BaseRenderer.default_span_tokens)

        # definition references, collected during parsing
        if link_definitions is None:
            self._link_definitions = {}
        else:
            self._link_definitions = link_definitions
        if foot_definitions is None:
            self._foot_definitions = OrderedDict()
        else:
            self._foot_definitions = foot_definitions

        self.nesting_matches = {}

    @property
    def link_definitions(self) -> dict:
        return self._link_definitions

    @property
    def foot_definitions(self) -> dict:
        return self._foot_definitions

    def reset_definitions(self):
        self._link_definitions = {}
        self._foot_definitions = {}

    def copy(self):
        return deepcopy(self)


def get_parse_context(reset=False) -> ParseContext:
    """Return the current `ParseContext`."""
    global THREAD
    if reset:
        THREAD.context = ParseContext()
    else:
        try:
            return THREAD.context
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
