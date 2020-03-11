from collections import namedtuple, OrderedDict
import json
import re
from typing import List, Optional, Pattern, Tuple, Union

import attr


WalkItem = namedtuple("WalkItem", ["node", "parent", "index", "depth"])


class Token:
    """Base class of all mistletoe tokens."""

    def __getattr__(self, name):
        # ensure certain attributes are always available
        if name == "children":
            return None
        if name == "content":
            return ""
        raise AttributeError(name)

    @property
    def name(self) -> str:
        """Return the name of the element."""
        return type(self).__name__

    def __contains__(self, text: str):
        """Return is text is contained in the element or its ancestors."""
        if self.children is None:
            return text in self.content
        return any(text in child for child in self.children)

    def __repr__(self):
        """A base represent method, that can be overriden for more complex elements."""
        info = []
        if self.children is not None:
            info.append("children={}".format(len(self.children)))
        return "{}({})".format(self.name, ",".join(info))

    def to_dict(self) -> dict:
        """Convert instatiated attributes to a dict"""
        try:
            return attr.asdict(self, recurse=False)
        except attr.exceptions.NotAnAttrsClassError:
            return self.__dict__

    def walk(
        self,
        tokens: Optional[List[str]] = None,
        depth: Optional[int] = None,
        include_self: bool = False,
    ) -> WalkItem:
        """Traverse the syntax tree, recursively yielding children.

        :param elements: filter children by certain token names.
        :param depth: The depth to recurse into the tree.
        :param include_self: whether to first yield this element.

        :yield: A container for an element, its parent and depth

        """

        def _get_children(_parent):
            _children = [(_parent, c, i) for i, c in enumerate(_parent.children or [])]
            if _parent.name == "Table" and getattr(_parent, "header", None) is not None:
                _children.append((_parent, _parent.header, 0))
            if (
                _parent.name == "Document"
                and getattr(_parent, "footnotes", None) is not None
            ):
                _children.extend(
                    [
                        (_parent.footnotes, c, i)
                        for i, c in enumerate(_parent.footnotes.values())
                    ]
                )
            return _children

        current_depth = 0
        if include_self:
            yield WalkItem(self, None, None, current_depth)
        next_children = _get_children(self)
        while next_children and (depth is None or current_depth > depth):
            current_depth += 1
            new_children = []
            for idx, (parent, child, index) in enumerate(next_children):
                if tokens is None or child.name in tokens:
                    yield WalkItem(child, parent, index, current_depth)
                new_children.extend(_get_children(child))

            next_children = new_children


class TokenEncoder(json.JSONEncoder):
    """A JSON encoder for mistletoe tokens."""

    def default(self, obj):
        """Convert tokens to `{token.name: token.to_dict()}`,
        and expand `SpanContainer`.
        """
        if isinstance(obj, OrderedDict):
            return dict(obj)
        if isinstance(obj, SpanContainer):
            return list(obj.expand())
        if isinstance(obj, Token):
            return {obj.name: obj.to_dict()}
        return super().default(obj)


def serialize_tokens(tokens, as_dict=False):
    """Serialize one or more tokens, to a JSON representation."""
    string = json.dumps(tokens, cls=TokenEncoder)
    if as_dict:
        return json.loads(string)
    return string


class SpanContainer:
    """This is a container for inline span text.

    We use it in order to delay the assessment of span text, when parsing a document,
    so that all link definitions can be gathered first.
    After the initial block parse, we walk through the document
    and replace these span containers with the actual span tokens
    (see `block_tokenizer.tokenize_main`).
    """

    def __init__(self, text):
        """Store text for later tokenisation."""
        self.text = text

    def expand(self):
        """Apply `tokenize_span` to text."""
        from mistletoe.span_tokenizer import tokenize_span

        return tokenize_span(self.text)

    def __iter__(self):
        for _ in []:
            yield

    def __len__(self):
        return 0

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, repr(self.text))


class SourceLines:
    """A class for storing source lines and tracking current line index.

    :param lines: the source lines
    :param start_line: the position of the initial line within the full source text.
    :param standardize_ends: standardize all lines to end with ``\\n``
    :param metadata: any metadata associated with the lines
    """

    line_end_pattern = re.compile(".*(\n|\r)$")

    def __init__(
        self,
        lines: Union[str, List[str]],
        start_line: int = 0,
        standardize_ends: bool = False,
        metadata: Optional[dict] = None,
    ):

        if isinstance(lines, str):
            lines = lines.splitlines(keepends=True)
        if standardize_ends:
            lines = [
                "{}\n".format(l[:-1] if self.line_end_pattern.match(l) else l)
                for l in lines
            ]

        self.lines = lines
        self._index = -1
        self._anchor = 0
        self.start_line = start_line
        self.metadata = metadata or {}

    @property
    def lineno(self):
        """Return the line number in the source text
        (taking into account the ``start_line``).
        """
        return self.start_line + self._index + 1

    def __next__(self):
        """Progress the line index and return the line.

        :raises: ``StopIteration`` if reached the end of the source lines.
        """
        if self._index + 1 < len(self.lines):
            self._index += 1
            return self.lines[self._index]
        raise StopIteration

    def __iter__(self):
        return self

    def __repr__(self):
        return repr(self.lines[self._index + 1 :])

    def anchor(self):
        """Set an anchor for resetting the line index."""
        self._anchor = self._index

    def reset(self):
        """Revert the line index to the set anchor (or 0)."""
        self._index = self._anchor

    def peek(self) -> Optional[str]:
        """Return the next line, if exists,
        without actually advancing the line index.
        """
        if self._index + 1 < len(self.lines):
            return self.lines[self._index + 1]
        return None

    def backstep(self):
        """Step back the line index by 1."""
        if self._index != -1:
            self._index -= 1


class BlockToken(Token):
    """Base class for block-level tokens. Recursively parse inner tokens.

    Naming conventions:

    * lines denotes a list of (possibly unparsed) input lines,
      and is commonly used as the argument name for constructors.

    * BlockToken.children is a list with all the inner tokens
      (thus if a token has children attribute, it is not a leaf node; if a token
      calls tokenize_span, it is the boundary between
      span-level tokens and block-level tokens);

    * BlockToken.start takes a line from the document as argument,
      and returns a boolean representing whether that line marks the start
      of the current token. Every subclass of BlockToken must define a
      start function (see block_tokenizer.tokenize).

    * BlockToken.read takes the rest of the lines in the document as an
      iterator (including the start line), and consumes all the lines
      that should be read into this token.

      Default to stop at an empty line.

      Note that `BlockToken.read` returns a token (or None).

      If BlockToken.read returns None, the read result is ignored,
      but the token class is responsible for resetting the iterator
      to a previous state. See `SourceLines.anchor`,
      `SourceLines.reset`.

    """

    @classmethod
    def start(cls, line: str) -> bool:
        """Takes a line from the document as argument, and
        returns a boolean representing whether that line marks the start
        of the current token. Every subclass of BlockToken must define a
        start function (see `block_tokenizer.tokenize_main`).
        """
        raise NotImplementedError

    @classmethod
    def read(cls, lines: SourceLines) -> Optional[Token]:
        """takes the rest of the lines in the document as an
        iterator (including the start line), and consumes all the lines
        that should be read into this token.

        The default is to stop at an empty line.
        """
        line_buffer = [next(lines)]
        for line in lines:
            if line == "\n":
                break
            line_buffer.append(line)
        return line_buffer


class SpanToken(Token):
    """Base class for span-level tokens.

    :arg pattern: regex pattern to search for.
    :arg parse_inner: whether to do a nested parse of the content
    :arg parse_group: the group within the pattern match corresponding to the content
    :arg precedence: Alter the relative order by which the span token is assessed.
    """

    pattern = None
    parse_inner = True
    parse_group = 1
    precedence = 5

    def __init__(
        self,
        *,
        content: Optional[str] = None,
        children: Optional[list] = None,
        position: Tuple[int, int] = None
    ):
        """Initialise basic span token.

        :param content: raw string content of the token
        :param children: list of child tokens
        :param position: span position within the source text
        """
        if content is not None:
            self.content = content
        if children is not None:
            self.children = children

    @classmethod
    def read(cls, match: Pattern):
        """Take a pattern match and return the instatiated token."""
        if not cls.parse_inner:
            return cls(content=match.group(cls.parse_group))
        return cls()

    @classmethod
    def find(cls, string: str):
        """Find all tokens, matching a pattern in the given string"""
        if cls.pattern is not None:
            return cls.pattern.finditer(string)
        return []
