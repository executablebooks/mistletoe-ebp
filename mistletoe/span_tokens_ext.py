"""Extended span tokens, that are not part of the CommonMark spec."""
import re
from typing import Pattern, Tuple

import attr

from mistletoe.attr_doc import autodoc
from mistletoe.base_elements import SpanToken
from mistletoe.parse_context import get_parse_context

__all__ = ("Math", "Strikethrough", "FootReference")


class Strikethrough(SpanToken):
    """Strikethrough tokens: `~~some text~~`.

    Must be parsed after `CoreTokens`.
    """

    pattern = re.compile(r"(?<!\\)(?:\\\\)*~~(.+?)~~", re.DOTALL)

    @classmethod
    def find(cls, string):
        matches = get_parse_context().nesting_matches.pop("Strikethrough", [])
        return matches


class Math(SpanToken):
    """Dollar Math tokens (single or double): `$a=1$`.

    Must be parsed after `CoreTokens`.
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

    As outlined in <https://www.markdownguide.org/extended-syntax/#footnotes>
    and <https://michelf.ca/projects/php-markdown/extra/#footnotes>

    Must be parsed after `CoreTokens`.
    """

    pattern = re.compile(r"^\[\^([a-zA-Z0-9#]+)\]")
    parse_inner = False
    parse_group = 0

    target: str = attr.ib(metadata={"doc": "footnote reference target"})
    position: Tuple[int, int] = attr.ib(
        default=None,
        repr=False,
        metadata={"doc": "Line position in source text (start, end)"},
    )

    @classmethod
    def find(cls, string):
        matches = get_parse_context().nesting_matches.pop("FootReference", [])
        return matches

    @classmethod
    def read(cls, match: Pattern):
        return cls(target=match.group(1))
