"""
Base class for renderers.
"""

import re
import sys
from mistletoe import base_elements
from mistletoe.parse_context import get_parse_context, set_parse_context


class BaseRenderer:
    """
    Base class for renderers.

    All renderers should ...

    * define all render functions specified in `self.render_map`;
    * be a context manager (by inheriting `__enter__` and `__exit__`);

    Custom renderers could ...

    * add additional tokens into the parsing process by passing custom
      tokens to `super().__init__()`;
    * add additional render functions by appending to self.render_map;

    Usage:

    Suppose SomeRenderer inherits BaseRenderer, and fin is the input file.
    The syntax looks something like this::

        >>> from mistletoe import Document
        >>> from some_renderer import SomeRenderer
        >>> with SomeRenderer() as renderer:
        ...     rendered = renderer.render(Document.read(fin))

    See mistletoe.renderers.html for an implementation example.

    Naming conventions:

    * The keys of `self.render_map` should exactly match the class
      name of tokens;
    * Render function names should be of form: `render_` + the
      "snake-case" form of token's class name.

    :param render_map: maps tokens to their corresponding render functions.
    :type render_map: dict
    :param extras: a list of custom tokens to be added to the parsing process.
    :type extras: list
    """

    _parse_name = re.compile(r"([A-Z][a-z]+|[A-Z]+(?![a-z]))")

    def __init__(self, *extras):
        self.render_map = {
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
            "SetextHeading": self.render_heading,
            "Quote": self.render_quote,
            "Paragraph": self.render_paragraph,
            "CodeFence": self.render_block_code,
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
        }
        self._extras = extras
        parse_context = get_parse_context(reset=True)
        for token in extras:
            if issubclass(token, base_elements.SpanToken):
                # insert at position 1 (since backslash escape should also be 1st)
                parse_context.span_tokens.insert(1, token)
            else:
                parse_context.block_tokens.insert(0, token)
            render_func = getattr(self, self._cls_to_func(token.__name__))
            self.render_map[token.__name__] = render_func

        self.parse_context = parse_context.copy()
        self.link_definitions = {}

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
        Make renderer classes into context managers.
        """
        set_parse_context(self.parse_context)
        return self

    def __exit__(self, exception_type, exception_val, traceback):
        """
        Make renderer classes into context managers.
        """
        get_parse_context(reset=True)

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

    def __getattr__(self, name):
        """
        Provides a default render method for all tokens.

        Any token without a custom render method will simply be rendered by
        self.render_inner.

        If name does not start with 'render_', raise AttributeError as normal,
        for less magic during debugging.

        This method would only be called if the attribute requested has not
        been defined. Defined attributes will not be overridden.

        I still think this is heavy wizardry.
        Let me know if you would like this method removed.
        """
        if not name.startswith("render_"):
            msg = "{cls} object has no attribute {name}".format(
                cls=type(self).__name__, name=name
            )
            raise AttributeError(msg).with_traceback(sys.exc_info()[2])
        return self.render_inner
