"""
Built-in span-level token classes.
"""
import re

from mistletoe import nested_tokenizer
from mistletoe.base_elements import SpanToken

"""
Tokens to be included in the parsing process, in the order specified.
"""
__all__ = [
    "EscapeSequence",
    "Strikethrough",
    "AutoLink",
    "CoreTokens",
    "InlineCode",
    "LineBreak",
    "RawText",
]


class CoreTokens(SpanToken):
    precedence = 3

    def __new__(self, match):
        # TODO this needs to be made more general (so tokens can be in diffent modules)
        return globals()[match.type](match)

    @classmethod
    def find(cls, string):
        return nested_tokenizer.find_nested_tokenizer(string)


class Strong(SpanToken):
    """
    Strong tokens. ("**some text**")
    """


class Emphasis(SpanToken):
    """
    Emphasis tokens. ("*some text*")
    """


class InlineCode(SpanToken):
    """
    Inline code tokens. ("`some code`")
    """

    pattern = re.compile(r"(?<!\\|`)(?:\\\\)*(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
    parse_inner = False
    parse_group = 2

    def __init__(self, match):
        content = match.group(self.parse_group)
        self.children = (RawText(" ".join(re.split("[ \n]+", content.strip()))),)

    @classmethod
    def find(cls, string):
        matches = nested_tokenizer._code_matches.value
        nested_tokenizer._code_matches.value = []
        return matches


class Strikethrough(SpanToken):
    """
    Strikethrough tokens. ("~~some text~~")
    """

    pattern = re.compile(r"(?<!\\)(?:\\\\)*~~(.+)~~", re.DOTALL)


class Image(SpanToken):
    """
    Image tokens, with inline targets: "![alt](src "title")".

    Attributes:
        src (str): image source.
        title (str): image title (default to empty).
    """

    def __init__(self, match):
        self.src = match.group(2).strip()
        self.title = match.group(3)


class Link(SpanToken):
    """
    Link tokens, with inline targets: "[name](target)"

    Attributes:
        target (str): link target.
    """

    def __init__(self, match):
        self.target = EscapeSequence.strip(match.group(2).strip())
        self.title = EscapeSequence.strip(match.group(3))


class AutoLink(SpanToken):
    """
    Autolink tokens. ("<http://www.google.com>")

    Attributes:
        children (iterator): a single RawText node for alternative text.
        target (str): link target.
    """

    pattern = re.compile(
        r"(?<!\\)(?:\\\\)*<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^ <>]*?|[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*)>"  # noqa: E501
    )
    parse_inner = False

    def __init__(self, match):
        content = match.group(self.parse_group)
        self.children = (RawText(content),)
        self.target = content
        self.mailto = "@" in self.target and "mailto" not in self.target.casefold()


class EscapeSequence(SpanToken):
    """
    Escape sequences. ("\\*")

    Attributes:
        children (iterator): a single RawText node for alternative text.
    """

    pattern = re.compile(r"\\([!\"#$%&'()*+,-./:;<=>?@\[\\\]^_`{|}~])")
    parse_inner = False
    precedence = 2

    def __init__(self, match):
        self.children = (RawText(match.group(self.parse_group)),)

    @classmethod
    def strip(cls, string):
        return cls.pattern.sub(r"\1", string)


class LineBreak(SpanToken):
    """
    Hard or soft line breaks.
    """

    pattern = re.compile(r"( *|\\)\n")
    parse_inner = False
    parse_group = 0

    def __init__(self, match):
        content = match.group(1)
        self.soft = not content.startswith(("  ", "\\"))
        self.content = ""


class RawText(SpanToken):
    """
    Raw text. A leaf node.

    RawText is the only token that accepts a string for its constructor,
    instead of a match object. Also, all recursions should bottom out here.
    """

    def __init__(self, content):
        self.content = content


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

    Attributes:
        content (str): literal strings rendered as-is.
    """

    pattern = re.compile(
        "|".join(
            [_open_tag, _closing_tag, _comment, _instruction, _declaration, _cdata]
        ),
        re.DOTALL,
    )
    parse_inner = False
    parse_group = 0
