"""
Extended block tokens, that are not part of the CommonMark spec.
"""
from itertools import zip_longest
import re
from typing import Optional
from typing import List as ListType

import attr

from mistletoe.attr_doc import autodoc
from mistletoe.base_elements import (
    Token,
    BlockToken,
    Position,
    SourceLines,
    SpanContainer,
)
from mistletoe.parse_context import get_parse_context


__all__ = ["TableCell", "TableRow", "Table", "Footnote"]


@autodoc
@attr.s(slots=True, kw_only=True)
class Footnote(BlockToken):
    """Footnote token. ("[^a]: the footnote body")

    As outlined in
    `markdownguide <https://www.markdownguide.org/extended-syntax/#footnotes>`_
    and `php-markdown <https://michelf.ca/projects/php-markdown/extra/#footnotes>`_;
    Footnote definitions can be found anywhere in the document,
    but footnotes will always be listed in the order they are referenced to in the text
    (and will not be shown if they are not referenced).

    **NOTE**: currently this only supports single line footnotes,
    but it is intended that this will eventually support multi-line.

    Footnotes are stored in the `Document.footnotes` in the final syntax tree.

    This should be ordered for parsing, before the `LinkDefinition` token
    """

    target: str = attr.ib(metadata={"doc": "footnote reference target"})
    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    position: Position = attr.ib(
        default=None, metadata={"doc": "Line position in source text"}
    )

    label_pattern = re.compile(r"^[ \n]{0,3}\[\^([a-zA-Z0-9#@]+)\]\:\s*(.*)$")

    @classmethod
    def start(cls, line):
        return line.lstrip().startswith("[^")

    @classmethod
    def read(cls, lines: SourceLines):
        start_line = lines.lineno + 1
        next_line = lines.peek()
        first_line_match = cls.label_pattern.match(next_line)
        if not first_line_match:
            return None
        target = first_line_match.group(1)
        first_line = first_line_match.group(2)
        # line_buffer = []
        next(lines)
        position = Position.from_source_lines(lines, start_line=start_line)
        token = cls(
            target=target, children=SpanContainer(first_line), position=position
        )
        if target not in get_parse_context().foot_definitions:
            get_parse_context().foot_definitions[target] = token
        else:
            get_parse_context().logger.warning(
                "ignoring duplicate footnote definition '{}' at: {}".format(
                    target, position
                )
            )
        return token


@autodoc
@attr.s(slots=True, kw_only=True)
class TableCell(BlockToken):
    """Table cell token.

    Boundary between span-level and block-level tokens.
    """

    children: ListType[Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    align: Optional[int] = attr.ib(
        metadata={
            "doc": "align options for the cell (left=None (default), center=0, right=1)"
        }
    )
    position: Position = attr.ib(
        default=None, metadata={"doc": "Line position in source text"}
    )

    @classmethod
    def read(
        cls,
        content,
        align=None,
        expand_spans=False,
        lineno=0,
        lines: SourceLines = None,
    ):
        children = SpanContainer(content)
        if expand_spans:
            children = children.expand()
        if lines is not None:
            position = Position(line_start=lineno, uri=lines.uri, data=lines.metadata)
        else:
            position = Position(line_start=lineno)
        return cls(children=children, align=align, position=position)


@autodoc
@attr.s(slots=True, kw_only=True)
class TableRow(BlockToken):
    """Table row token."""

    children: ListType[TableCell] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    row_align: list = attr.ib(
        metadata={
            "doc": "align options for columns (left=None (default), center=0, right=1)"
        }
    )
    position: Position = attr.ib(
        default=None, metadata={"doc": "Line position in source text"}
    )

    @classmethod
    def read(cls, line, row_align=None, lineno=0, lines: SourceLines = None):
        row_align = row_align or [None]
        cells = filter(None, line.strip().split("|"))
        children = [
            TableCell.read(
                cell.strip() if cell else "", align, lineno=lineno, lines=lines
            )
            for cell, align in zip_longest(cells, row_align)
        ]
        if lines is not None:
            position = Position(line_start=lineno, uri=lines.uri, data=lines.metadata)
        else:
            position = Position(line_start=lineno)
        return cls(children=children, row_align=row_align, position=position)


@autodoc
@attr.s(slots=True, kw_only=True)
class Table(BlockToken):
    """Table token.

    **Note**: header delimiters must be of at least length 3 (`---`)

    Example::

        | Left Align  |   Centered  | Right Align   |
        | :---        |    :----:   |          ---: |
        | Header      | Title       | Here's this   |
        | Paragraph   | Text        | And more      |
    """

    children: ListType[TableRow] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    header: Optional[TableRow] = attr.ib(
        default=None, metadata={"doc": "The header row"}
    )
    column_align: list = attr.ib(
        metadata={
            "doc": "align options for columns (left=None (default), center=0, right=1)"
        }
    )
    position: Position = attr.ib(
        default=None, metadata={"doc": "Line position in source text"}
    )

    @staticmethod
    def split_delimiter(delimiter: str):
        """Helper function; returns a list of align options.

        :param delimiter: e.g.: `| :--- | :---: | ---: |`
        :return: a list of align options (None, 0 or 1).
        """
        return re.findall(r":?---+:?", delimiter)

    @staticmethod
    def parse_align(column):
        """Helper function; returns align option from cell content.

        :return:
            None if align = left;
            0    if align = center;
            1    if align = right.
        """
        return (0 if column[0] == ":" else 1) if column[-1] == ":" else None

    @staticmethod
    def start(line):
        return "|" in line

    @classmethod
    def read(cls, lines: SourceLines):
        start_line = lines.lineno + 1
        lines.anchor()
        line_buffer = [next(lines)]
        while lines.peek() is not None and "|" in lines.peek():
            line_buffer.append(next(lines))
        if len(line_buffer) < 2 or "---" not in line_buffer[1]:
            lines.reset()
            return None

        if "---" in line_buffer[1]:
            column_align = [
                cls.parse_align(column)
                for column in cls.split_delimiter(line_buffer[1])
            ]
            header = TableRow.read(
                line_buffer[0], column_align, lineno=start_line, lines=lines
            )
            children = [
                TableRow.read(line, column_align, lineno=start_line + i)
                for i, line in enumerate(line_buffer[2:], 2)
            ]
        else:
            column_align = [None]
            header = None
            children = [
                TableRow.read(line, lineno=start_line + i, lines=lines)
                for i, line in enumerate(line_buffer)
            ]
        return cls(
            children=children,
            column_align=column_align,
            header=header,
            position=Position.from_source_lines(lines, start_line=start_line),
        )
