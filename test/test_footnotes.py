import pytest

from mistletoe import block_tokens, block_tokens_ext
from mistletoe.base_elements import serialize_tokens
from mistletoe.block_tokenizer import tokenize_main
from mistletoe.parse_context import get_parse_context
from mistletoe.span_tokenizer import tokenize_span
from mistletoe.span_tokens import CoreTokens
from mistletoe.span_tokens_ext import FootReference


@pytest.mark.parametrize(
    "name,source",
    [
        ("basic", "[^a]"),
        ("no_match", "[^b]"),
        ("multiple", "[^a] [^a]"),
        ("after_text", "[a](b) abc [^a] xyz"),
        ("not_image", "![^a] ![b](c)"),
        ("in_emphasis", "*[^a]*"),
        ("in_link", "[[^a]](b)"),
        ("in_code", "`[^a]`"),
    ],
)
def test_foot_ref_span(name, source, data_regression):
    get_parse_context().foot_definitions["a"] = True
    _span_tokens = get_parse_context().span_tokens
    _span_tokens.insert_after(FootReference, CoreTokens)
    data_regression.check(
        serialize_tokens(tokenize_span(source), as_dict=True),
        basename=f"test_foot_ref_span_{name}",
    )


@pytest.mark.parametrize(
    "name,source",
    [
        ("basic", ["[^1]: value1\n", "[2]: value2\n"]),
        ("include_spans", ["[^abcd]: *a*\n"]),
    ],
)
def test_foot_definition(name, source, data_regression):
    get_parse_context().block_tokens.insert_before(
        block_tokens_ext.Footnote, block_tokens.LinkDefinition
    )
    tree = serialize_tokens(tokenize_main(source), as_dict=True)
    footnotes = serialize_tokens(get_parse_context().foot_definitions, as_dict=True)
    data_regression.check(
        {
            "tree": tree,
            "footnotes": footnotes,
            "link_definitions": get_parse_context().link_definitions,
        },
        basename=f"test_foot_definitions_{name}",
    )


def test_repeated_footnote(caplog):
    get_parse_context().block_tokens.insert_before(
        block_tokens_ext.Footnote, block_tokens.LinkDefinition
    )
    tokenize_main(["[^1]: value1\n", "[^1]: value2\n"])
    assert "ignoring duplicate footnote definition" in caplog.text
    assert len(get_parse_context().foot_definitions) == 1


@pytest.mark.parametrize(
    "name,source", [("basic", ["[^1]\n", "\n", "[^1]: a *footnote*\n", "\n", "[^1]\n"])]
)
def test_resolution(name, source, data_regression):
    get_parse_context().span_tokens.insert_after(FootReference, CoreTokens)
    get_parse_context().block_tokens.insert_before(
        block_tokens_ext.Footnote, block_tokens.LinkDefinition
    )
    data_regression.check(
        serialize_tokens(block_tokens.Document.read(source), as_dict=True),
        basename=f"test_resolution_{name}",
    )
