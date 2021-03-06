"""
Base class for renderers.
"""

from itertools import chain
import re
import sys
from typing import Optional

from mistletoe import block_tokens, block_tokens_ext, span_tokens, span_tokens_ext
from mistletoe.parse_context import ParseContext, set_parse_context


class BaseRenderer:
    """
    Base class for renderers.

    All renderers should ...

    * define all render functions specified in `self.render_map`;
    * be a context manager (by inheriting `__enter__` and `__exit__`);

    Custom renderers could ...

    * set the default tokens searched for during parsing, by overriding
      ``default_block_tokens`` and/or ``default_span_tokens``
    * add additional render functions by appending to self.render_map;

    :Usage:

    Suppose SomeRenderer inherits BaseRenderer, and ``fin`` is the input file.
    The syntax looks something like this::

        >>> from mistletoe import Document
        >>> from some_renderer import SomeRenderer
        >>> with SomeRenderer() as renderer:
        ...     rendered = renderer.render(Document.read(fin))

    See mistletoe.renderers.html for an implementation example.

    :Naming conventions:

    * The keys of `self.render_map` should exactly match the class
      name of tokens;
    * Render function names should be of form: `render_` + the
      "snake-case" form of token's class name.

    :param render_map: maps tokens to their corresponding render functions.
    :type render_map: dict

    """

    default_block_tokens = (
        block_tokens.HTMLBlock,
        block_tokens.BlockCode,
        block_tokens.Heading,
        block_tokens.Quote,
        block_tokens.CodeFence,
        block_tokens.ThematicBreak,
        block_tokens.List,
        block_tokens_ext.Table,
        block_tokens_ext.Footnote,
        block_tokens.LinkDefinition,
        block_tokens.Paragraph,
    )

    default_span_tokens = (
        span_tokens.EscapeSequence,
        span_tokens.HTMLSpan,
        span_tokens.AutoLink,
        span_tokens.CoreTokens,
        span_tokens_ext.FootReference,
        span_tokens_ext.Strikethrough,
        span_tokens.InlineCode,
        span_tokens.LineBreak,
        span_tokens.RawText,
    )

    _parse_name = re.compile(r"([A-Z][a-z]+|[A-Z]+(?![a-z]))")

    def __init__(self, *, parse_context: Optional[ParseContext] = None):
        """Initialise the renderer.

        :param parse_context: the parse context stores global parsing variables,
            such as the block/span tokens to search for,
            and link/footnote definitions that have been collected.
            If None, a new context will be instatiated, with the default
            block/span tokens for this renderer.
            These will be re-instatiated on ``__enter__``.
        :type parse_context: mistletoe.parse_context.ParseContext
        """
        if parse_context is None:
            parse_context = ParseContext(
                self.default_block_tokens, self.default_span_tokens
            )

        self.parse_context = parse_context
        set_parse_context(self.parse_context)

        self.render_map = self.get_default_render_map()
        for token in chain(
            self.parse_context.block_tokens, self.parse_context.span_tokens
        ):
            if token.__name__ not in self.render_map:
                render_func = getattr(self, self._cls_to_func(token.__name__))
                self.render_map[token.__name__] = render_func

    def get_default_render_map(self):
        """Return the default map of token names to methods."""
        return {
            "Strong": self.render_strong,
            "Emphasis": self.render_emphasis,
            "InlineCode": self.render_inline_code,
            "RawText": self.render_raw_text,
            "Strikethrough": self.render_strikethrough,
            "Image": self.render_image,
            "Link": self.render_link,
            "AutoLink": self.render_auto_link,
            "EscapeSequence": self.render_escape_sequence,
            "Heading": self.render_heading,
            "SetextHeading": self.render_setext_heading,
            "Quote": self.render_quote,
            "Paragraph": self.render_paragraph,
            "CodeFence": self.render_code_fence,
            "BlockCode": self.render_block_code,
            "List": self.render_list,
            "ListItem": self.render_list_item,
            "Table": self.render_table,
            "TableRow": self.render_table_row,
            "TableCell": self.render_table_cell,
            "ThematicBreak": self.render_thematic_break,
            "LineBreak": self.render_line_break,
            "Document": self.render_document,
            "LinkDefinition": self.render_link_definition,
            "Footnote": self.render_footnote,
        }

    def render(self, token):
        """
        Grabs the class name from input token and finds its corresponding
        render function.

        Basically a janky way to do polymorphism.

        Arguments:
            token: whose __class__.__name__ is in self.render_map.
        """
        return self.render_map[token.__class__.__name__](token)

    def render_inner(self, token):
        """
        Recursively renders child tokens. Joins the rendered
        strings with no space in between.

        If newlines / spaces are needed between tokens, add them
        in their respective templates, or override this function
        in the renderer subclass, so that whitespace won't seem to
        appear magically for anyone reading your program.

        :param token: a branch node who has children attribute.
        """
        return "".join(map(self.render, token.children or []))

    def __enter__(self):
        """
        Make renderer classes into context managers, reinstatiated the
        originally instatiated ``parse_context``.
        """
        set_parse_context(self.parse_context)
        return self

    def __exit__(self, exception_type, exception_val, traceback):
        """
        Make renderer classes into context managers.
        """
        pass

    @classmethod
    def _cls_to_func(cls, cls_name):
        snake = "_".join(map(str.lower, cls._parse_name.findall(cls_name)))
        return "render_{}".format(snake)

    @staticmethod
    def _tokens_from_module(module):
        """
        Helper method; takes a module and returns a list of all token classes
        specified in `module.__all__`. Useful when custom tokens are defined in a
        separate module.
        """
        return [getattr(module, name) for name in module.__all__]

    def render_raw_text(self, token):
        """
        Default render method for RawText. Simply return token.content.
        """
        return token.content

    def render_setext_heading(self, token):
        """
        Default render method for SetextHeader. Simply parse to render_header.
        """
        return self.render_heading(token)

    def render_code_fence(self, token):
        """
        Default render method for CodeFence. Simply parse to render_block_code.
        """
        return self.render_block_code(token)

    def render_core_tokens(self, token):
        raise TypeError(
            "CoreTokens span tokens should not be present in the final syntax tree"
        )

    def unimplemented_renderer(self, token):
        raise NotImplementedError("no render method set for {}".format(token))

    def __getattr__(self, name):
        """"""
        if name.startswith("render_"):
            return self.unimplemented_renderer
        raise AttributeError(name).with_traceback(sys.exc_info()[2])
