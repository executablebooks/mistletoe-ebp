"""
Block-level tokenizer for mistletoe.
"""
from mistletoe.base_elements import SpanContainer
from mistletoe.parse_context import get_parse_context


def tokenize_main(
    iterable, token_types=None, start_line=0, expand_spans=True, store_definitions=False
):
    """Searches for token_types in an iterable.

    :param iterable: list of strings (each line must end with a newline `\\n`!).
    :param token_types: override block-level tokens set in global context
    :param start_line: the source line number corresponding to `iterable[0]`
    :param expand_spans: After the initial parse the span text is not yet tokenized,
        but stored instead as raw text in `SpanContainer`, in order to ensure
        all link definitons are read first. Setting True, runs a second walk of the
        syntax tree to replace these `SpanContainer` with the final span tokens.
    :param store_definitions: store `LinkDefinitions` specifically in the syntax tree
        (or just record their target mappings globally and discard.)

    :returns: list of block-level token instances.
    """
    if token_types is None:
        token_types = get_parse_context().block_tokens
    tokens = tokenize_block(
        iterable,
        token_types=token_types,
        start_line=start_line,
        store_definitions=store_definitions,
    )
    if expand_spans:
        for token in tokens:
            for result in list(token.walk(include_self=True)):
                if isinstance(result.node.children, SpanContainer):
                    result.node.children = result.node.children.expand()
    return tokens


def tokenize_block(iterable, token_types=None, start_line=0, store_definitions=False):
    """Returns a list of parsed tokens."""
    if token_types is None:
        token_types = get_parse_context().block_tokens
    lines = FileWrapper(iterable, start_line)
    parsed_tokens = ParseBuffer()
    line = lines.peek()
    while line is not None:
        for token_type in token_types:
            if token_type.start(line):
                token = token_type.read(lines)
                if token is not None:
                    if store_definitions or token.name != "LinkDefinition":
                        parsed_tokens.append(token)
                    break
        else:  # unmatched newlines
            next(lines)
            parsed_tokens.loose = True
        line = lines.peek()
    return parsed_tokens


class FileWrapper:
    """A class for storing source lines and tracking current line number."""

    def __init__(self, lines, start_line=0):
        self.lines = lines if isinstance(lines, list) else list(lines)
        self._index = -1
        self._anchor = 0
        self.start_line = start_line

    @property
    def lineno(self):
        return self.start_line + self._index + 1

    def __next__(self):
        if self._index + 1 < len(self.lines):
            self._index += 1
            return self.lines[self._index]
        raise StopIteration

    def __iter__(self):
        return self

    def __repr__(self):
        return repr(self.lines[self._index + 1 :])

    def anchor(self):
        self._anchor = self._index

    def reset(self):
        self._index = self._anchor

    def peek(self):
        if self._index + 1 < len(self.lines):
            return self.lines[self._index + 1]
        return None

    def backstep(self):
        if self._index != -1:
            self._index -= 1


class ParseBuffer(list):
    """
    A wrapper around builtin list,
    so that setattr(list, 'loose') is legal.
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.loose = False
