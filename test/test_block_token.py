import pytest

from mistletoe import block_tokens, block_tokens_ext
from mistletoe.base_elements import serialize_tokens
from mistletoe.parse_context import get_parse_context
from mistletoe.block_tokenizer import tokenize_main


@pytest.mark.parametrize(
    "name,source",
    [
        ("match", ["### heading 3\n"]),
        ("enclosing_hashes", ["# heading 3 #####  \n"]),
        ("too_many_hashes", ["####### paragraph\n"]),
        ("heading_in_paragraph", ["foo\n", "# heading\n", "bar\n"]),
    ],
)
def test_atx_heading(name, source, data_regression):
    data_regression.check(
        serialize_tokens(tokenize_main(source), as_dict=True),
        basename=f"test_atx_heading_{name}",
    )


@pytest.mark.parametrize(
    "name,source",
    [
        ("match", ["some heading\n", "---\n"]),
        ("multiline", ["some\n", "heading\n", "---\n", "\n", "foobar\n"]),
    ],
)
def test_setext_heading(name, source, data_regression):
    data_regression.check(
        serialize_tokens(tokenize_main(source), as_dict=True),
        basename=f"test_setext_heading_{name}",
    )


@pytest.mark.parametrize(
    "name,source",
    [
        ("match", ["> line 1\n", "> line 2\n"]),
        ("lazy_continuation", ["> line 1\n", "line 2\n"]),
    ],
)
def test_quote(name, source, data_regression):
    data_regression.check(
        serialize_tokens(tokenize_main(source), as_dict=True),
        basename=f"test_quote_{name}",
    )


@pytest.mark.parametrize(
    "name,source",
    [
        ("with_ticks", ["```sh\n", "rm dir\n", "mkdir test\n", "```\n"]),
        ("with_tildas", ["~~~sh\n", "rm dir\n", "mkdir test\n", "~~~\n"]),
        (
            "mixed_tick_tilda",
            ["~~~markdown\n", "```sh\n", "some code\n", "```\n", "~~~\n"],
        ),
        ("lazy_continuation", ["```sh\n", "rm dir\n", "\n", "mkdir test\n", "```\n"]),
        ("no_wrapping_newlines", ["```\n", "hey", "```\n", "paragraph\n"]),
        ("unclosed", ["```\n", "hey"]),
    ],
)
def test_fenced_code(name, source, data_regression):
    data_regression.check(
        serialize_tokens(tokenize_main(source), as_dict=True),
        basename=f"test_fenced_code_{name}",
    )


@pytest.mark.parametrize(
    "name,source", [("match", ["    rm dir\n", "    mkdir test\n"])]
)
def test_block_code(name, source, data_regression):
    data_regression.check(
        serialize_tokens(tokenize_main(source), as_dict=True),
        basename=f"test_block_code_{name}",
    )


@pytest.mark.parametrize(
    "name,source",
    [
        ("basic", ["some\n", "continuous\n", "lines\n"]),
        ("encapsulate_code_fence", ["this\n", "```\n", "is some\n", "```\n", "code\n"]),
    ],
)
def test_paragraph(name, source, data_regression):
    data_regression.check(
        serialize_tokens(tokenize_main(source), as_dict=True),
        basename=f"test_paragraph_{name}",
    )


@pytest.mark.parametrize(
    "name,source",
    [
        (
            "allowed_markers",
            [
                "- foo\n",
                "*    bar\n",
                " + baz\n",
                "1. item 1\n",
                "2) item 2\n",
                "123456789. item x\n",
            ],
        ),
        (
            "non_markers",
            ["> foo\n", "1item 1\n", "2| item 2\n", "1234567890. item x\n"],
        ),
        ("before_block_code", [" -    foo\n", "   bar\n", "\n", "          baz\n"]),
        ("sub_list", ["- foo\n", "  - bar\n"]),
        ("deep_list", ["- foo\n", "  - bar\n", "    - baz\n"]),
        ("loose_list", ["- foo\n", "  ~~~\n", "  bar\n", "  \n", "  baz\n" "  ~~~\n"]),
        ("tight_list", ["- foo\n", "\n", "# bar\n"]),
    ],
)
def test_list_item(name, source, data_regression):
    data_regression.check(
        serialize_tokens(tokenize_main(source), as_dict=True),
        basename=f"test_list_item_{name}",
    )


@pytest.mark.parametrize(
    "name,source",
    [
        ("markers", ["- foo\n", "* bar\n", "1. baz\n", "2) spam\n"]),
        ("sub_list", ["- foo\n", "  + bar\n"]),
    ],
)
def test_list(name, source, data_regression):
    data_regression.check(
        serialize_tokens(tokenize_main(source), as_dict=True),
        basename=f"test_list_{name}",
    )


@pytest.mark.parametrize(
    "name,source",
    [
        ("basic", ["[key 1]: value1\n", "[key 2]: value2\n"]),
        ("title", ['[key 1]: value1 "title"\n']),
    ],
)
def test_link_definitions(name, source, data_regression):
    tree = serialize_tokens(tokenize_main(source), as_dict=True)
    data_regression.check(
        {"tree": tree, "link_definitions": get_parse_context().link_definitions},
        basename=f"test_link_definitions_{name}",
    )


@pytest.mark.parametrize(
    "name,source",
    [("dash", ["---\n"]), ("star", ["* * *\n"]), ("underscore", ["_    _    _\n"])],
)
def test_thematic_break(name, source, data_regression):
    data_regression.check(
        serialize_tokens(tokenize_main(source), as_dict=True),
        basename=f"test_thematic_break_{name}",
    )


@pytest.mark.parametrize(
    "name,source",
    [
        ("basic", ["# heading\n", "\n", "paragraph\n", "with\n", "`code`\n"]),
        ("link_defs", ["[key 1]: value1\n", "[key 2]: value2\n"]),
        ("auto_splitlines", "some\ncontinual\nlines\n"),
        ("front_matter_ignore", ["---\n", "a: 1\n", "---\n"]),
    ],
)
def test_doc_read(name, source, data_regression):
    data_regression.check(
        serialize_tokens(block_tokens.Document.read(source), as_dict=True),
        basename=f"test_doc_read_{name}",
    )


@pytest.mark.parametrize("name,source", [("basic", ["---\n", "a: 1\n", "---\n"])])
def test_doc_read_with_front_matter(name, source, data_regression):
    data_regression.check(
        serialize_tokens(
            block_tokens.Document.read(source, front_matter=True), as_dict=True
        ),
        basename=f"test_doc_read_with_front_matter_{name}",
    )


@pytest.mark.parametrize(
    "name,source", [("basic", ["[key 1]: value1\n", "[key 2]: value2\n"])]
)
def test_doc_read_store_link_defs(name, source, data_regression):
    data_regression.check(
        serialize_tokens(
            block_tokens.Document.read(source, store_definitions=True), as_dict=True
        ),
        basename=f"test_doc_read_store_link_defs_{name}",
    )


def test_table_parse_align():
    assert block_tokens_ext.Table.parse_align(":------") is None
    assert block_tokens_ext.Table.parse_align(":-----:") == 0
    assert block_tokens_ext.Table.parse_align("------:") == 1


def test_table_parse_delimiter():
    delimiters = list(
        block_tokens_ext.Table.split_delimiter("| :--- | :---: | ---:|\n")
    )
    assert delimiters == [":---", ":---:", "---:"]


@pytest.mark.parametrize(
    "name,source",
    [
        (
            "basic",
            [
                "| header 1 | header 2 | header 3 |\n",
                "| --- | --- | --- |\n",
                "| cell 1 | cell 2 | cell 3 |\n",
                "| more 1 | more 2 | more 3 |\n",
            ],
        ),
        (
            "aligned",
            ["header 1 | header 2\n", "    ---: | :---\n", "  cell 1 | cell 2\n"],
        ),
        ("not_table", ["not header 1 | not header 2\n", "foo | bar\n"]),
    ],
)
def test_table(name, source, data_regression):
    data_regression.check(
        serialize_tokens(tokenize_main(source), as_dict=True),
        basename=f"test_table_{name}",
    )


@pytest.mark.parametrize(
    "name,source,row_align",
    [
        ("basic", "| cell 1 | cell 2 |\n", None),
        ("no_outside", "cell 1 | cell 2\n", None),
        ("short", "| cell 1 |\n", [None, None]),
    ],
)
def test_table_row(name, source, row_align, data_regression):
    row = block_tokens_ext.TableRow.read(source, row_align=row_align)
    data_regression.check(
        serialize_tokens(row, as_dict=True), basename=f"test_table_row_{name}"
    )


def test_table_cell(data_regression):
    token = block_tokens_ext.TableCell.read("cell 2")
    data_regression.check(serialize_tokens(token, as_dict=True))
