"""
Built-in block-level token classes.
"""
import re
from typing import Optional, Tuple
from typing import List as ListType

import attr

import mistletoe.block_tokenizer as tokenizer
from mistletoe import span_tokens
from mistletoe.nested_tokenizer import (
    follows,
    shift_whitespace,
    whitespace,
    is_control_char,
    normalize_label,
)
from mistletoe.parse_context import get_parse_context
from mistletoe.base_elements import Token, BlockToken, SpanContainer
from mistletoe.attr_doc import autodoc


"""
Tokens to be included in the parsing process, in the order specified.
"""
__all__ = [
    "BlockCode",
    "Heading",
    "Quote",
    "CodeFence",
    "ThematicBreak",
    "List",
    "LinkDefinition",
    "Paragraph",
]


@autodoc
@attr.s(slots=True, kw_only=True)
class FrontMatter(BlockToken):
    """Front matter YAML block.

    ::

        ---
        a: b
        c: d
        ---

    NOTE: The content of the block should be valid YAML,
    but its parsing (and hence syntax testing) is deferred to the renderers.
    This is so that, given 'bad' YAML,
    the rest of the of document will still be parsed,
    and then the renderers can apply there own error reporting.

    Not included in the parsing process, but called by `Document.read`.
    """

    content: str = attr.ib(
        repr=False, metadata={"doc": "Source text (should be valid YAML)"}
    )
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    @classmethod
    def start(cls, line: str) -> bool:
        return False

    @classmethod
    def read(cls, lines):
        assert lines and lines[0].startswith("---")
        end_line = None
        for i, line in enumerate(lines[1:]):
            if line.startswith("---"):
                end_line = i + 2
                break
        # TODO raise/report error if closing block not found
        if end_line is None:
            end_line = len(lines)

        return cls(content="".join(lines[1 : end_line - 1]), position=(0, end_line))


@autodoc
@attr.s(slots=True, kw_only=True)
class Document(BlockToken):
    """Document container."""

    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    link_definitions: dict = attr.ib(
        repr=lambda d: str(len(d)), metadata={"doc": "Mapping of keys to (url, title)"}
    )
    front_matter: Optional[FrontMatter] = attr.ib(
        default=None, metadata={"doc": "Front matter YAML block"}
    )

    @classmethod
    def read(
        cls,
        lines,
        start_line: int = 0,
        reset_definitions=True,
        store_definitions=False,
        front_matter=False,
    ):
        """Read a document

        :param lines:  Lines or string to parse
        :param start_line: The initial line (used for nested parsing)
        :param reset_definitions: remove any previously stored link_definitions
        :param store_definitions: store LinkDefinitions or ignore them
        :param front_matter: search for an initial YAML block front matter block
            (note this is not strictly CommonMark compliant)
        """
        if isinstance(lines, str):
            lines = lines.splitlines(keepends=True)
        lines = [line if line.endswith("\n") else "{}\n".format(line) for line in lines]
        # reset link definitions
        if reset_definitions:
            get_parse_context().link_definitions = {}

        front_matter_token = None
        if front_matter and lines and lines[0].startswith("---"):
            front_matter_token = FrontMatter.read(lines)
            start_line += front_matter_token.position[1]
            lines = lines[front_matter_token.position[1] :]

        children = tokenizer.tokenize_main(
            lines, start_line=start_line, store_definitions=store_definitions
        )
        return cls(
            children=children,
            front_matter=front_matter_token,
            link_definitions=get_parse_context().link_definitions,
        )


@autodoc
@attr.s(slots=True, kw_only=True)
class Heading(BlockToken):
    """Heading token. (["### some heading ###\\n"])

    Boundary between span-level and block-level tokens.
    """

    level: int = attr.ib(metadata={"doc": "Heading level"})
    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    pattern = re.compile(r" {0,3}(#{1,6})(?:\n|\s+?(.*?)(?:\n|\s+?#+\s*?$))")

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if match_obj is None:
            return False
        cls.level = len(match_obj.group(1))
        cls.content = (match_obj.group(2) or "").strip()
        if set(cls.content) == {"#"}:
            cls.content = ""
        return True

    @classmethod
    def read(cls, lines, expand_spans=False):
        next(lines)
        children = SpanContainer(cls.content)
        if expand_spans:
            children = children.expand()
        return cls(
            level=cls.level, children=children, position=(lines.lineno, lines.lineno)
        )


@autodoc
@attr.s(slots=True, kw_only=True)
class SetextHeading(BlockToken):
    """Setext headings.

    Not included in the parsing process, but returned by `Paragraph.read`.
    """

    level: int = attr.ib(metadata={"doc": "Heading level"})
    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    @classmethod
    def start(cls, line):
        raise NotImplementedError()

    @classmethod
    def read(cls, lines):
        raise NotImplementedError()


@autodoc
@attr.s(slots=True, kw_only=True)
class Quote(BlockToken):
    """Quote token. (`["> # heading\\n", "> paragraph\\n"]`)."""

    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    @staticmethod
    def start(line):
        stripped = line.lstrip(" ")
        if len(line) - len(stripped) > 3:
            return False
        return stripped.startswith(">")

    @classmethod
    def transition(cls, next_line):
        return (
            next_line is None
            or next_line.strip() == ""
            or Heading.start(next_line)
            or CodeFence.start(next_line)
            or ThematicBreak.start(next_line)
            or List.start(next_line)
        )

    @classmethod
    def read(cls, lines):
        # first line
        start_line = lines.lineno + 1
        line = cls.convert_leading_tabs(next(lines).lstrip()).split(">", 1)[1]
        if len(line) > 0 and line[0] == " ":
            line = line[1:]
        line_buffer = [line]

        # set booleans
        in_code_fence = CodeFence.start(line)
        in_block_code = BlockCode.start(line)
        blank_line = line.strip() == ""

        # loop
        next_line = lines.peek()
        while not cls.transition(next_line):
            stripped = cls.convert_leading_tabs(next_line.lstrip())
            prepend = 0
            if stripped[0] == ">":
                # has leader, not lazy continuation
                prepend += 1
                if stripped[1] == " ":
                    prepend += 1
                stripped = stripped[prepend:]
                in_code_fence = CodeFence.start(stripped)
                in_block_code = BlockCode.start(stripped)
                blank_line = stripped.strip() == ""
                line_buffer.append(stripped)
            elif in_code_fence or in_block_code or blank_line:
                # not paragraph continuation text
                break
            else:
                # lazy continuation, preserve whitespace
                line_buffer.append(next_line)
            next(lines)
            next_line = lines.peek()

        # block level tokens are parsed here, so that link_definitions
        # in quotes can be recognized before span-level tokenizing.
        Paragraph.parse_setext = False
        try:
            child_tokens = tokenizer.tokenize_block(line_buffer, start_line=start_line)
        finally:
            Paragraph.parse_setext = True
        return cls(children=child_tokens, position=(start_line, lines.lineno))

    @staticmethod
    def convert_leading_tabs(string):
        string = string.replace(">\t", "   ", 1)
        count = 0
        for i, c in enumerate(string):
            if c == "\t":
                count += 4
            elif c == " ":
                count += 1
            else:
                break
        if i == 0:
            return string
        return ">" + " " * count + string[i:]


@autodoc
@attr.s(slots=True, kw_only=True)
class Paragraph(BlockToken):
    """Paragraph token. (`["some\\n", "continuous\\n", "lines\\n"]`)

    Boundary between span-level and block-level tokens.
    """

    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    _setext_pattern = re.compile(r" {0,3}(=|-)+ *$")
    parse_setext = True  # can be disabled by Quote

    @staticmethod
    def start(line):
        return line.strip() != ""

    @classmethod
    def is_setext_heading(cls, line):
        return cls._setext_pattern.match(line)

    @classmethod
    def transition(cls, next_line):
        return (
            next_line is None
            or next_line.strip() == ""
            or Heading.start(next_line)
            or CodeFence.start(next_line)
            or Quote.start(next_line)
        )

    @classmethod
    def read(cls, lines, expand_spans=False):
        line_buffer = [next(lines)]
        start_line = lines.lineno
        next_line = lines.peek()
        while not cls.transition(next_line):
            # check if next_line starts List
            list_pair = ListItem.parse_marker(next_line)
            if len(next_line) - len(next_line.lstrip()) < 4 and list_pair is not None:
                prepend, leader = list_pair
                # non-empty list item
                if next_line[:prepend].endswith(" "):
                    # unordered list, or ordered list starting from 1
                    if not leader[:-1].isdigit() or leader[:-1] == "1":
                        break

            # check if next_line starts HTMLBlock other than type 7
            html_block = HTMLBlock.start(next_line)
            if html_block and html_block != 7:
                break

            # check if we see a setext underline
            if cls.parse_setext and cls.is_setext_heading(next_line):
                line_buffer.append(next(lines))
                level = 1 if line_buffer.pop().lstrip().startswith("=") else 2
                children = SpanContainer(
                    "\n".join([line.strip() for line in line_buffer])
                )
                if expand_spans:
                    children = children.expand()
                return SetextHeading(
                    children=children, level=level, position=(start_line, lines.lineno)
                )

            # check if we have a ThematicBreak (has to be after setext)
            if ThematicBreak.start(next_line):
                break

            # no other tokens, we're good
            line_buffer.append(next(lines))
            next_line = lines.peek()

        content = "".join([line.lstrip() for line in line_buffer]).strip()
        children = SpanContainer(content)
        if expand_spans:
            children = children.expand()
        return cls(children=children, position=(start_line, lines.lineno))


@autodoc
@attr.s(slots=True, kw_only=True)
class BlockCode(BlockToken):
    """Indented code."""

    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    language: str = attr.ib(
        default="", metadata={"doc": "The code language (for sytax highlighting)"}
    )
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    @staticmethod
    def start(line):
        return line.replace("\t", "    ", 1).startswith("    ")

    @classmethod
    def read(cls, lines):
        start_line = lines.lineno
        line_buffer = []
        for line in lines:
            if line.strip() == "":
                line_buffer.append(line.lstrip(" ") if len(line) < 5 else line[4:])
                continue
            if not line.replace("\t", "    ", 1).startswith("    "):
                lines.backstep()
                break
            line_buffer.append(cls.strip(line))

        children = (span_tokens.RawText("".join(line_buffer).strip("\n") + "\n"),)

        return cls(children=children, language="", position=(start_line, lines.lineno))

    @staticmethod
    def strip(string):
        count = 0
        for i, c in enumerate(string):
            if c == "\t":
                return string[i + 1 :]
            elif c == " ":
                count += 1
            else:
                break
            if count == 4:
                return string[i + 1 :]
        return string


@autodoc
@attr.s(slots=True, kw_only=True)
class CodeFence(BlockToken):
    """Code fence. (["```sh\\n", "rm -rf /", ..., "```"])

    Boundary between span-level and block-level tokens.
    """

    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    language: str = attr.ib(
        default="", metadata={"doc": "The code language (for sytax highlighting)"}
    )
    arguments: str = attr.ib(
        default="", metadata={"doc": "Any string occuring after the language"}
    )
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    pattern = re.compile(r"^( {0,3})((?:`|~){3,}) *([^`~\s]*) *([^`~]*)$")
    _open_info = None

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if not match_obj:
            return False
        prepend, leader, lang, arguments = match_obj.groups()
        if leader[0] in lang or leader[0] in line[match_obj.end() :]:
            return False
        cls._open_info = len(prepend), leader, lang, arguments
        return True

    @classmethod
    def read(cls, lines):
        start_line = lines.lineno + 1
        next(lines)
        line_buffer = []
        for line in lines:
            stripped_line = line.lstrip(" ")
            diff = len(line) - len(stripped_line)
            if (
                stripped_line.startswith(cls._open_info[1])
                and len(stripped_line.split(maxsplit=1)) == 1
                and diff < 4
            ):
                break
            if diff > cls._open_info[0]:
                stripped_line = " " * (diff - cls._open_info[0]) + stripped_line
            line_buffer.append(stripped_line)

        language = span_tokens.EscapeSequence.strip(cls._open_info[2])
        arg_lines = cls._open_info[3].splitlines() or [""]
        arguments = span_tokens.EscapeSequence.strip(arg_lines[0])
        children = (span_tokens.RawText("".join(line_buffer)),)

        return cls(
            children=children,
            language=language,
            arguments=arguments,
            position=(start_line, lines.lineno),
        )


@autodoc
@attr.s(slots=True, kw_only=True)
class List(BlockToken):
    """List token (unordered or ordered)"""

    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    loose: bool = attr.ib(
        metadata={"doc": "Whether list items are separated by blank lines"}
    )
    start_at: Optional[int] = attr.ib(
        metadata={"doc": "None if unordered, starting number if ordered."}
    )
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    _pattern = re.compile(r" {0,3}(?:\d{0,9}[.)]|[+\-*])(?:[ \t]*$|[ \t]+)")

    @classmethod
    def start(cls, line):
        return cls._pattern.match(line)

    @classmethod
    def read(cls, lines):
        start_line = lines.lineno
        leader = None
        next_marker = None
        children = []
        while True:
            item = ListItem.read(lines, next_marker)
            next_marker = item.next_marker
            item_leader = item.leader
            if leader is None:
                leader = item_leader
            elif not cls.same_marker_type(leader, item_leader):
                lines.reset()
                break
            children.append(item)
            if next_marker is None:
                break

        if children:
            # Only consider the last list item loose if there's more than one element
            last_parse_buffer = children[-1]
            last_parse_buffer.loose = (
                len(last_parse_buffer.children) > 1 and last_parse_buffer.loose
            )

        loose = any(item.loose for item in children)
        leader = children[0].leader
        start = None
        if len(leader) != 1:
            start = int(leader[:-1])
        return cls(
            children=children,
            loose=loose,
            start_at=start,
            position=(start_line, lines.lineno),
        )

    @staticmethod
    def same_marker_type(leader, other):
        if len(leader) == 1:
            return leader == other
        return (
            leader[:-1].isdigit() and other[:-1].isdigit() and leader[-1] == other[-1]
        )


@autodoc
@attr.s(slots=True, kw_only=True)
class ListItem(BlockToken):
    """List items.

    Not included in the parsing process, but called by List.
    """

    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    loose: bool = attr.ib(
        metadata={"doc": "Whether list items are separated by blank lines"}
    )
    leader: str = attr.ib(metadata={"doc": "The prefix number or bullet point."})
    prepend = attr.ib(metadata={"doc": ""})
    next_marker = attr.ib(metadata={"doc": ""})
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    _pattern = re.compile(r"\s*(\d{0,9}[.)]|[+\-*])(\s*$|\s+)")

    @staticmethod
    def in_continuation(line, prepend):
        return line.strip() == "" or len(line) - len(line.lstrip()) >= prepend

    @staticmethod
    def transition(next_line):
        return (
            Heading.start(next_line)
            or Quote.start(next_line)
            or CodeFence.start(next_line)
            or ThematicBreak.start(next_line)
        )

    @classmethod
    def parse_marker(cls, line):
        """
        Returns a pair (prepend, leader) if the line has a valid leader.
        """
        match_obj = cls._pattern.match(line)
        if match_obj is None:
            return None  # no valid leader
        leader = match_obj.group(1)
        content = match_obj.group(0).replace(leader + "\t", leader + "   ", 1)
        # reassign prepend and leader
        prepend = len(content)
        if prepend == len(line.rstrip("\n")):
            prepend = match_obj.end(1) + 1
        else:
            spaces = match_obj.group(2)
            if spaces.startswith("\t"):
                spaces = spaces.replace("\t", "   ", 1)
            spaces = spaces.replace("\t", "    ")
            n_spaces = len(spaces)
            if n_spaces > 4:
                prepend = match_obj.end(1) + 1
        return prepend, leader

    @classmethod
    def read(cls, lines, prev_marker=None):
        next_marker = None
        lines.anchor()
        prepend = -1
        leader = None
        start_line = lines.lineno
        line_buffer = []

        # first line
        line = next(lines)
        prepend, leader = prev_marker if prev_marker else cls.parse_marker(line)
        line = line.replace(leader + "\t", leader + "   ", 1).replace("\t", "    ")
        empty_first_line = line[prepend:].strip() == ""
        if not empty_first_line:
            line_buffer.append(line[prepend:])
        next_line = lines.peek()
        if empty_first_line and next_line is not None and next_line.strip() == "":
            child_tokens = tokenizer.tokenize_block(
                [next(lines)], start_line=lines.lineno
            )
            next_line = lines.peek()
            if next_line is not None:
                marker_info = cls.parse_marker(next_line)
                if marker_info is not None:
                    next_marker = marker_info
            return cls(
                children=child_tokens,
                loose=child_tokens.loose,
                prepend=prepend,
                leader=leader,
                next_marker=next_marker,
                position=(start_line, lines.lineno),
            )

        # loop
        newline = 0
        while True:
            # no more lines
            if next_line is None:
                # strip off newlines
                if newline:
                    lines.backstep()
                    del line_buffer[-newline:]
                break
            next_line = next_line.replace("\t", "    ")
            # not in continuation
            if not cls.in_continuation(next_line, prepend):
                # directly followed by another token
                if cls.transition(next_line):
                    if newline:
                        lines.backstep()
                        del line_buffer[-newline:]
                    break
                # next_line is a new list item
                marker_info = cls.parse_marker(next_line)
                if marker_info is not None:
                    next_marker = marker_info
                    break
                # not another item, has newlines -> not continuation
                if newline:
                    lines.backstep()
                    del line_buffer[-newline:]
                    break
            next(lines)
            line = next_line
            stripped = line.lstrip(" ")
            diff = len(line) - len(stripped)
            if diff > prepend:
                stripped = " " * (diff - prepend) + stripped
            line_buffer.append(stripped)
            newline = newline + 1 if next_line.strip() == "" else 0
            next_line = lines.peek()

        child_tokens = tokenizer.tokenize_block(line_buffer, start_line=start_line)

        return cls(
            children=child_tokens,
            loose=child_tokens.loose,
            prepend=prepend,
            leader=leader,
            next_marker=next_marker,
            position=(start_line, lines.lineno),
        )


@autodoc
@attr.s(slots=True, kw_only=True)
class LinkDefinition(BlockToken):
    """LinkDefinition token: `[ref]: url "title"`"""

    definitions: list = attr.ib(metadata={"doc": "list of (label, dest, title)"})
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    label_pattern = re.compile(r"[ \n]{0,3}\[(.+?)\]", re.DOTALL)

    @classmethod
    def start(cls, line):
        return line.lstrip().startswith("[")

    @classmethod
    def read(cls, lines):
        line_buffer = []
        start_line = lines.lineno + 1
        next_line = lines.peek()
        while next_line is not None and next_line.strip() != "":
            line_buffer.append(next(lines))
            next_line = lines.peek()
        string = "".join(line_buffer)
        offset = 0
        matches = []
        while offset < len(string) - 1:
            match_info = cls.match_reference(lines, string, offset)
            if match_info is None:
                break
            offset, match = match_info
            matches.append(match)
        cls.append_link_definitions(matches)
        return (
            cls(position=(start_line, lines.lineno), definitions=matches)
            if matches
            else None
        )

    @classmethod
    def match_reference(cls, lines, string, offset):
        match_info = cls.match_link_label(string, offset)
        if not match_info:
            cls.backtrack(lines, string, offset)
            return None
        _, label_end, label = match_info

        if not follows(string, label_end - 1, ":"):
            cls.backtrack(lines, string, offset)
            return None

        match_info = cls.match_link_dest(string, label_end)
        if not match_info:
            cls.backtrack(lines, string, offset)
            return None
        _, dest_end, dest = match_info

        match_info = cls.match_link_title(string, dest_end)
        if not match_info:
            cls.backtrack(lines, string, dest_end)
            return None
        _, title_end, title = match_info

        return title_end, (label, dest, title)

    @classmethod
    def match_link_label(cls, string, offset):
        start = -1
        end = -1
        escaped = False
        for i, c in enumerate(string[offset:], start=offset):
            if c == "\\" and not escaped:
                escaped = True
            elif c == "[" and not escaped:
                if start == -1:
                    start = i
                else:
                    return None
            elif c == "]" and not escaped:
                end = i
                label = string[start + 1 : end]
                if label.strip() != "":
                    return start, end + 1, label
                return None
            elif escaped:
                escaped = False
        return None

    @classmethod
    def match_link_dest(cls, string, offset):
        offset = shift_whitespace(string, offset + 1)
        if offset == len(string):
            return None
        if string[offset] == "<":
            escaped = False
            for i, c in enumerate(string[offset + 1 :], start=offset + 1):
                if c == "\\" and not escaped:
                    escaped = True
                elif c == " " or c == "\n" or (c == "<" and not escaped):
                    return None
                elif c == ">" and not escaped:
                    return offset, i + 1, string[offset + 1 : i]
                elif escaped:
                    escaped = False
            return None
        else:
            escaped = False
            count = 0
            for i, c in enumerate(string[offset:], start=offset):
                if c == "\\" and not escaped:
                    escaped = True
                elif c in whitespace:
                    break
                elif not escaped:
                    if c == "(":
                        count += 1
                    elif c == ")":
                        count -= 1
                elif is_control_char(c):
                    return None
                elif escaped:
                    escaped = False
            if count != 0:
                return None
            return offset, i, string[offset:i]

    @classmethod
    def match_link_title(cls, string, offset):
        new_offset = shift_whitespace(string, offset)
        if (
            new_offset == len(string)
            or "\n" in string[offset:new_offset]
            and string[new_offset] == "["
        ):
            return offset, new_offset, ""
        if string[new_offset] == '"':
            closing = '"'
        elif string[new_offset] == "'":
            closing = "'"
        elif string[new_offset] == "(":
            closing = ")"
        elif "\n" in string[offset:new_offset]:
            return offset, offset, ""
        else:
            return None
        offset = new_offset
        escaped = False
        for i, c in enumerate(string[offset + 1 :], start=offset + 1):
            if c == "\\" and not escaped:
                escaped = True
            elif c == closing and not escaped:
                new_offset = shift_whitespace(string, i + 1)
                if "\n" not in string[i + 1 : new_offset]:
                    return None
                return offset, new_offset, string[offset + 1 : i]
            elif escaped:
                escaped = False
        return None

    @staticmethod
    def append_link_definitions(matches):
        for key, dest, title in matches:
            key = normalize_label(key)
            dest = span_tokens.EscapeSequence.strip(dest.strip())
            title = span_tokens.EscapeSequence.strip(title)
            link_definitions = get_parse_context().link_definitions
            if key not in link_definitions:
                link_definitions[key] = dest, title

    @staticmethod
    def backtrack(lines, string, offset):
        lines._index -= string[offset + 1 :].count("\n")


@autodoc
@attr.s(slots=True, kw_only=True)
class ThematicBreak(BlockToken):
    """Thematic break token (a.k.a. horizontal rule.)"""

    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    _pattern = re.compile(r" {0,3}(?:([-_*])\s*?)(?:\1\s*?){2,}$")

    @classmethod
    def start(cls, line):
        return cls._pattern.match(line)

    @classmethod
    def read(cls, lines):
        next(lines)
        return cls(position=(lines.lineno, lines.lineno))


@autodoc
@attr.s(slots=True, kw_only=True)
class HTMLBlock(BlockToken):
    """Block-level HTML token."""

    content: str = attr.ib(
        repr=False, metadata={"doc": "literal strings rendered as-is"}
    )
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    _end_cond = None
    multiblock = re.compile(r"<(script|pre|style)[ >\n]")
    predefined = re.compile(r"<\/?(.+?)(?:\/?>|[ \n])")
    custom_tag = re.compile(
        r"(?:" + "|".join((span_tokens._open_tag, span_tokens._closing_tag)) + r")\s*$"
    )

    @classmethod
    def start(cls, line):
        stripped = line.lstrip()
        if len(line) - len(stripped) >= 4:
            return False
        # rule 1: <pre>, <script> or <style> tags, allow newlines in block
        match_obj = cls.multiblock.match(stripped)
        if match_obj is not None:
            cls._end_cond = "</{}>".format(match_obj.group(1).casefold())
            return 1
        # rule 2: html comment tags, allow newlines in block
        if stripped.startswith("<!--"):
            cls._end_cond = "-->"
            return 2
        # rule 3: tags that starts with <?, allow newlines in block
        if stripped.startswith("<?"):
            cls._end_cond = "?>"
            return 3
        # rule 4: tags that starts with <!, allow newlines in block
        if stripped.startswith("<!") and stripped[2].isupper():
            cls._end_cond = ">"
            return 4
        # rule 5: CDATA declaration, allow newlines in block
        if stripped.startswith("<![CDATA["):
            cls._end_cond = "]]>"
            return 5
        # rule 6: predefined tags (see html_token._tags), read until newline
        match_obj = cls.predefined.match(stripped)
        if match_obj is not None and match_obj.group(1).casefold() in span_tokens._tags:
            cls._end_cond = None
            return 6
        # rule 7: custom tags, read until newline
        match_obj = cls.custom_tag.match(stripped)
        if match_obj is not None:
            cls._end_cond = None
            return 7
        return False

    @classmethod
    def read(cls, lines):
        # note: stop condition can trigger on the starting line
        start_line = lines.lineno
        line_buffer = []
        for line in lines:
            line_buffer.append(line)
            if cls._end_cond is not None:
                if cls._end_cond in line.casefold():
                    break
            elif line.strip() == "":
                line_buffer.pop()
                break
        return cls(
            content="".join(line_buffer).rstrip("\n"),
            position=(start_line, lines.lineno),
        )
