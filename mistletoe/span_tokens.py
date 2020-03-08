"""
Built-in span-level token classes.
"""
import re
from typing import Pattern

import attr

from mistletoe import nested_tokenizer
from mistletoe.base_elements import SpanToken
from mistletoe.parse_context import get_parse_context
from mistletoe.attr_doc import autodoc

"""
Tokens to be included in the parsing process, in the order specified.
"""
__all__ = [
    "EscapeSequence",
    "AutoLink",
    "CoreTokens",
    "InlineCode",
    "LineBreak",
    "RawText",
]


class CoreTokens(SpanToken):
    precedence = 3

    @classmethod
    def read(cls, match: Pattern):
        # TODO this needs to be made more general (so tokens can be in diffent modules)
        return globals()[match.type].read(match)

    @classmethod
    def find(cls, string):
        return nested_tokenizer.find_nested_tokenizer(string)


class Strong(SpanToken):
    """
    Strong tokens. ("**some text**")

    :ivar content: raw string content of the token
    :ivar children: list of child tokens
    """


class Emphasis(SpanToken):
    """
    Emphasis tokens. ("*some text*")

    :ivar content: raw string content of the token
    :ivar children: list of child tokens
    """


@autodoc
@attr.s(kw_only=True, slots=True)
class InlineCode(SpanToken):
    """
    Inline code tokens. ("`some code`")
    """

    pattern = re.compile(r"(?<!\\|`)(?:\\\\)*(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
    parse_inner = False
    parse_group = 2

    children = attr.ib(metadata={"doc": "a single RawText node for alternative text."})

    @classmethod
    def read(cls, match: Pattern):
        content = match.group(cls.parse_group)
        return cls(children=(RawText(" ".join(re.split("[ \n]+", content.strip()))),))

    @classmethod
    def find(cls, string):
        matches = get_parse_context().nesting_matches.pop("InlineCode", [])
        return matches


@autodoc
@attr.s(kw_only=True, slots=True)
class Image(SpanToken):
    """
    Image tokens, with inline targets: "![alt](src "title")".
    """

    src: str = attr.ib(metadata={"doc": "image source"})
    title: str = attr.ib(default=None, metadata={"doc": "image title"})
    children = attr.ib(factory=list, metadata={"doc": "alternative text."})

    @classmethod
    def read(cls, match: Pattern):
        return cls(src=match.group(2).strip(), title=match.group(3))


@autodoc
@attr.s(kw_only=True, slots=True)
class Link(SpanToken):
    """
    Link tokens, with inline targets: "[name](target)"
    """

    target: str = attr.ib(metadata={"doc": "link target"})
    title: str = attr.ib(default=None, metadata={"doc": "link title"})
    children = attr.ib(factory=list, metadata={"doc": "link text."})

    @classmethod
    def read(cls, match: Pattern):
        return cls(
            target=EscapeSequence.strip(match.group(2).strip()),
            title=EscapeSequence.strip(match.group(3)),
        )


@autodoc
@attr.s(kw_only=True, slots=True)
class AutoLink(SpanToken):
    """
    Autolink tokens. ("<http://www.google.com>")
    """

    pattern = re.compile(
        r"(?<!\\)(?:\\\\)*<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^ <>]*?|[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*)>"  # noqa: E501
    )
    parse_inner = False

    target: str = attr.ib(metadata={"doc": "link target"})
    mailto: bool = attr.ib(metadata={"doc": "if the link is an email"})
    children = attr.ib(metadata={"doc": "a single RawText node for alternative text."})

    @classmethod
    def read(cls, match: Pattern):
        content = match.group(cls.parse_group)
        return cls(
            children=(RawText(content),),
            target=content,
            mailto="@" in content and "mailto" not in content.casefold(),
        )


@autodoc
@attr.s(kw_only=True, slots=True)
class EscapeSequence(SpanToken):
    """
    Escape sequences. ("\\*")

    Attributes:
        children (iterator): a single RawText node for alternative text.
    """

    pattern = re.compile(r"\\([!\"#$%&'()*+,-./:;<=>?@\[\\\]^_`{|}~])")
    parse_inner = False
    precedence = 2

    children = attr.ib(metadata={"doc": "a single RawText node for alternative text."})

    @classmethod
    def read(cls, match: Pattern):
        return cls(children=(RawText(match.group(cls.parse_group)),))

    @classmethod
    def strip(cls, string):
        return cls.pattern.sub(r"\1", string)


@autodoc
@attr.s(kw_only=True, slots=True)
class LineBreak(SpanToken):
    """
    Hard or soft line breaks.
    """

    pattern = re.compile(r"( *|\\)\n")
    parse_inner = False
    parse_group = 0

    content: bool = attr.ib(default="", metadata={"doc": "raw content."})
    soft: bool = attr.ib(metadata={"doc": "if the break is soft or hard."})

    @classmethod
    def read(cls, match: Pattern):
        content = match.group(1)
        return cls(soft=not content.startswith(("  ", "\\")))


@autodoc
@attr.s(slots=True)
class RawText(SpanToken):
    """
    Raw text. A leaf node.

    RawText is the only token that accepts a string for its `read` method,
    instead of a match object. Also, all recursions should bottom out here.
    """

    content: bool = attr.ib(metadata={"doc": "raw string content of the token"})

    @classmethod
    def read(cls, content: str):
        return cls(content=content)


_tags = {
    "address",
    "article",
    "aside",
    "base",
    "basefont",
    "blockquote",
    "body",
    "caption",
    "center",
    "col",
    "colgroup",
    "dd",
    "details",
    "dialog",
    "dir",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "frame",
    "frameset",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hr",
    "html",
    "iframe",
    "legend",
    "li",
    "link",
    "main",
    "menu",
    "menuitem",
    "meta",
    "nav",
    "noframes",
    "ol",
    "optgroup",
    "option",
    "p",
    "param",
    "section",
    "source",
    "summary",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "title",
    "tr",
    "track",
    "ul",
}

_tag = r"[A-Za-z][A-Za-z0-9-]*"
_attrs = r'(?:\s+[A-Za-z_:][A-Za-z0-9_.:-]*(?:\s*=\s*(?:[^ "\'=<>`]+|\'[^\']*?\'|"[^\"]*?"))?)*'  # noqa: E501

_open_tag = r"(?<!\\)<" + _tag + _attrs + r"\s*/?>"
_closing_tag = r"(?<!\\)</" + _tag + r"\s*>"
_comment = r"(?<!\\)<!--(?!>|->)(?:(?!--).)+?(?<!-)-->"
_instruction = r"(?<!\\)<\?.+?\?>"
_declaration = r"(?<!\\)<![A-Z].+?>"
_cdata = r"(?<!\\)<!\[CDATA.+?\]\]>"


class HTMLSpan(SpanToken):
    """
    Span-level HTML tokens.

    :ivar content: raw string content of the token
    :ivar children: list of child tokens
    """

    pattern = re.compile(
        "|".join(
            [_open_tag, _closing_tag, _comment, _instruction, _declaration, _cdata]
        ),
        re.DOTALL,
    )
    parse_inner = False
    parse_group = 0
