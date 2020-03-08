"""Extended span tokens, that are not part of the CommonMark spec."""
import re
from mistletoe.base_elements import SpanToken
from mistletoe.parse_context import get_parse_context


__all__ = ["Math", "Strikethrough"]


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
