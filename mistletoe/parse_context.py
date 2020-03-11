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


class OrderedSet(MutableSet):
    """An ordered set, optimized for `a in set` tests"""

    def __init__(self, iterable=()):
        self._items = OrderedDict((t, None) for t in iterable)

    def __repr__(self):
        return list(self._items).__repr__()

    def __contains__(self, item):
        return item in self._items

    def __iter__(self):
        for item in self._items:
            yield item

    def __len__(self):
        return len(self._items)

    def add(self, item):
        if item not in self._items:
            self._items[item] = None

    def discard(self, item):
        self._items.pop(item, None)

    def insert(self, index, item):
        item_list = list(self._items.items())
        item_list.insert(index, (item, None))
        self._items = OrderedDict(item_list)

    def insert_after(self, item, after_item):
        assert after_item in self._items, after_item
        indx = list(self._items.keys()).index(after_item) + 1
        token_list = list(self._items.items())
        token_list.insert(indx, (item, None))
        self._items = OrderedDict(token_list)

    def insert_before(self, item, before_item):
        assert before_item in self._items
        indx = list(self._items.keys()).index(before_item)
        token_list = list(self._items.items())
        token_list.insert(indx, (item, None))
        self._items = OrderedDict(token_list)


class ParseContext:
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

    def __init__(
        self,
        find_blocks=None,
        find_spans=None,
        link_definitions=None,
        foot_definitions=None,
    ):
        # tokens used for matching
        if find_blocks is not None:
            self.block_tokens = OrderedSet(tokens_from_classes(find_blocks))
        else:
            from mistletoe.renderers.base import BaseRenderer

            self.block_tokens = OrderedSet(BaseRenderer.default_block_tokens)
        if find_spans is not None:
            self.span_tokens = OrderedSet(tokens_from_classes(find_spans))
        else:
            from mistletoe.renderers.base import BaseRenderer

            self.span_tokens = OrderedSet(BaseRenderer.default_span_tokens)

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
        self._foot_references = OrderedSet()

    def __repr__(self):
        return "{0}(block_cls={1},span_cls={2},link_defs={3},footnotes={4})".format(
            self.__class__.__name__,
            len(self.block_tokens),
            len(self.span_tokens),
            len(self.link_definitions),
            len(self.foot_definitions),
        )

    @property
    def link_definitions(self) -> dict:
        return self._link_definitions

    @property
    def foot_definitions(self) -> dict:
        return self._foot_definitions

    @property
    def foot_references(self) -> OrderedSet:
        return self._foot_references

    def reset_definitions(self):
        self._link_definitions = {}
        self._foot_definitions = {}
        self._foot_references = OrderedSet()

    def copy(self):
        return deepcopy(self)


def get_parse_context(reset=False) -> ParseContext:
    """Return the current ``ParseContext`` (one per thread)."""
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
    """Set an existing ``ParseContext`` (one per thread)."""
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
