"""
Block-level tokenizer for mistletoe.
"""
from mistletoe.base_elements import SourceLines
from mistletoe.span_tokens import PendingReference, Image, Link, EscapeSequence, RawText
from mistletoe.parse_context import get_parse_context


def tokenize_main(
    iterable,
    token_types=None,
    start_line: int = 0,
    resolve_references: bool = True,
    skip_tokens: list = ("LinkDefinition", "Footnote"),
):
    """Searches for token_types in an iterable.

    :param iterable: list of strings (each line must end with a newline `\\n`!).
    :param token_types: override block-level tokens set in global context
    :param start_line: the source line number corresponding to `iterable[0]`
    :param resolve_references:

    After the initial parse the span text is not yet tokenized,
        but stored instead as raw text in `SpanContainer`, in order to ensure
        all link definitons are read first. Setting True, runs a second walk of the
        syntax tree to replace these `SpanContainer` with the final span tokens.
    :param skip_tokens: do not store these ``token.name`` in the syntax tree.
        These are usually tokens that store themselves in the global context

    :returns: list of block-level token instances.
    """
    if token_types is None:
        token_types = get_parse_context().block_tokens
    tokens = tokenize_block(
        iterable,
        token_types=token_types,
        start_line=start_line,
        skip_tokens=skip_tokens,
    )
    if resolve_references:
        for token in tokens:
            for result in list(token.walk()):
                if isinstance(result.node, PendingReference):
                    new_nodes = resolve_reference(result.node)
                    result.parent.children = (
                        result.parent.children[: result.index]
                        + new_nodes
                        + result.parent.children[result.index + 1 :]
                    )
                    print(result.parent.children)

    return tokens


def resolve_reference(token: PendingReference):
    link_definitions = get_parse_context().link_definitions
    if token.target in link_definitions:
        destination, title = link_definitions[token.target]
        if token.is_image:
            return [
                Image(
                    src=destination,
                    title=title,
                    position=token.position,
                    children=token.children,
                )
            ]
        return [
            Link(
                target=EscapeSequence.strip(destination.strip()),
                title=EscapeSequence.strip(title),
                position=token.position,
                children=token.children,
            )
        ]

    init_raw = RawText("![" if token.is_image else "[")
    print(token)
    if token.ref_type == "shortcut":
        return [init_raw] + token.children + [RawText("]")]
    if token.ref_type == "collapsed":
        return [init_raw] + token.children + [RawText("]")]
    if token.ref_type == "full":
        return [init_raw] + token.children + [RawText("]")]

    return [token]


def tokenize_block(
    iterable, token_types=None, start_line=0, skip_tokens=("LinkDefinition", "Footnote")
):
    """Returns a list of parsed tokens."""
    if token_types is None:
        token_types = get_parse_context().block_tokens
    lines = SourceLines(iterable, start_line)
    parsed_tokens = ParseBuffer()
    line = lines.peek()
    while line is not None:
        for token_type in token_types:
            if token_type.start(line):
                token = token_type.read(lines)
                if token is not None:
                    if token.name not in skip_tokens:
                        parsed_tokens.append(token)
                    break
        else:  # unmatched newlines
            next(lines)
            parsed_tokens.loose = True
        line = lines.peek()
    return parsed_tokens


class ParseBuffer(list):
    """
    A wrapper around builtin list,
    so that setattr(list, 'loose') is legal.
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.loose = False
