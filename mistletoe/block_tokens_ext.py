"""
Extended block tokens, that are not part of the CommonMark spec.
"""
from itertools import zip_longest
import re
from typing import Optional, Tuple
from typing import List as ListType

import attr

from mistletoe.attr_doc import autodoc
from mistletoe.base_elements import Token, BlockToken, SpanContainer


__all__ = ["TableCell", "TableRow", "Table"]


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
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    @classmethod
    def read(cls, content, align=None, expand_spans=False, lineno=0):
        children = SpanContainer(content)
        if expand_spans:
            children = children.expand()
        return cls(children=children, align=align, position=(lineno, lineno))


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
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
    )

    @classmethod
    def read(cls, line, row_align=None, lineno=0):
        row_align = row_align or [None]
        cells = filter(None, line.strip().split("|"))
        children = [
            TableCell.read(cell.strip() if cell else "", align, lineno=lineno)
            for cell, align in zip_longest(cells, row_align)
        ]
        return cls(children=children, row_align=row_align, position=(lineno, lineno))


@autodoc
@attr.s(slots=True, kw_only=True)
class Table(BlockToken):
    """Table token."""

    children: ListType[TableRow] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )
    header: Optional[TableRow] = attr.ib(metadata={"doc": "The header row"})
    column_align: list = attr.ib(
        metadata={
            "doc": "align options for columns (left=None (default), center=0, right=1)"
        }
    )
    position: Tuple[int, int] = attr.ib(
        metadata={"doc": "Line position in source text (start, end)"}
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
    def read(cls, lines):
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
            header = TableRow.read(line_buffer[0], column_align, lineno=start_line)
            children = [
                TableRow.read(line, column_align, lineno=start_line + i)
                for i, line in enumerate(line_buffer[2:], 2)
            ]
        else:
            column_align = [None]
            header = None
            children = [
                TableRow.read(line, lineno=start_line + i)
                for i, line in enumerate(line_buffer)
            ]
        return cls(
            children=children,
            column_align=column_align,
            header=header,
            position=(start_line, lines.lineno),
        )
