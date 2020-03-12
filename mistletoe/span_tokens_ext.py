"""Extended span tokens, that are not part of the CommonMark spec."""
import re
from typing import Pattern

import attr

from mistletoe.attr_doc import autodoc
from mistletoe.base_elements import Position, SpanToken
from mistletoe.parse_context import get_parse_context

__all__ = ("Math", "Strikethrough", "FootReference")


class Strikethrough(SpanToken):
    """Strikethrough tokens: `~~some text~~`.

    Must be ordered after `CoreTokens` in the parsing list.
    """

    pattern = re.compile(r"(?<!\\)(?:\\\\)*~~(.+?)~~", re.DOTALL)

    @classmethod
    def find(cls, string):
        matches = get_parse_context().nesting_matches.pop("Strikethrough", [])
        return matches


class Math(SpanToken):
    """Dollar Math tokens (single or double): `$a=1$`.

    Must be ordered after `CoreTokens` in the parsing list.
    """

    pattern = re.compile(r"(?<!\\)(?:\\\\)*(\${1,2})([^\$]+?)\1")
    parse_inner = False
    parse_group = 0

    @classmethod
    def find(cls, string):
        matches = get_parse_context().nesting_matches.pop("Math", [])
        return matches


@autodoc
@attr.s(kw_only=True, slots=True)
class FootReference(SpanToken):
    """Footnote reference tokens. ("[^a]")

    As outlined in
    `markdownguide <https://www.markdownguide.org/extended-syntax/#footnotes>`_
    and `php-markdown <https://michelf.ca/projects/php-markdown/extra/#footnotes>`_;
    When you create a footnote, a superscript number with a link appears where you
    added the footnote reference. Readers can click the link to jump to the content
    of the footnote at the bottom of the page.

    Unlike, the implementations above, it is allowed to have multiple
    footnote references per footnote definition.

    Must be ordered after `CoreTokens` in the token parsing list.
    """

    pattern = re.compile(r"^\[\^([a-zA-Z0-9#@]+)\]")
    parse_inner = False
    parse_group = 0

    target: str = attr.ib(metadata={"doc": "footnote reference target"})
    position: Position = attr.ib(
        default=None, repr=False, metadata={"doc": "Line position in source text"}
    )

    @classmethod
    def find(cls, string):
        matches = get_parse_context().nesting_matches.pop("FootReference", [])
        return matches

    @classmethod
    def read(cls, match: Pattern):
        target = match.group(1)
        # add the targets to an ordered set, so we record the order of reference
        get_parse_context().foot_references.add(target)
        return cls(target=target)
