from textwrap import dedent

from mistletoe import Document
from mistletoe import ParseContext
from mistletoe.renderers.json import ast_to_json, JsonRenderer
from mistletoe.renderers.latex import LaTeXRenderer


def test_basic(data_regression):
    doc = Document.read(
        dedent(
            """\
    ---
    a: 1
    ---

    Setext Header
    ==============

    # Atx Header

    __*nested strong emphasis*__
    <www.google.com>

    - unordered list

    1. ordered list

    > quote *emphasis*

    [link][ref]

    [ref]: abc "xyz"

    ```python
    code = 1
    ```

        block
        quote

    ---

    a   | b
    --- | ---:
    1   | 2

    """
        ),
        skip_tokens=(),
        front_matter=True,
    )
    output = ast_to_json(doc)
    data_regression.check(output)


def test_link_references(data_regression):
    doc = Document.read(["[bar][baz]\n", "\n", "[baz]: spam\n"], skip_tokens=())
    output = ast_to_json(doc)
    data_regression.check(output)


def test_extra_tokens():
    """Extra tokens should persist between multiple calls of the same renderer,
    but be reset if initiating a new renderer.
    """
    output_nomath = {
        "type": "Document",
        "front_matter": None,
        "link_definitions": {},
        "footnotes": {},
        "footref_order": [],
        "children": [
            {
                "type": "Paragraph",
                "children": [{"type": "RawText", "content": "$b$", "position": None}],
                "position": {"line_start": 1, "line_end": 1, "uri": None, "data": {}},
            }
        ],
    }
    output_math = {
        "type": "Document",
        "front_matter": None,
        "link_definitions": {},
        "footnotes": {},
        "footref_order": [],
        "children": [
            {
                "type": "Paragraph",
                "children": [{"type": "Math", "content": "$b$"}],
                "position": {"line_start": 1, "line_end": 1, "uri": None, "data": {}},
            }
        ],
    }

    with JsonRenderer() as render:
        output = render.render(Document.read(["$b$"]), as_string=False)
    print(output)
    assert output == output_nomath
    renderer = JsonRenderer(
        parse_context=ParseContext(find_spans=LaTeXRenderer.default_span_tokens)
    )
    with renderer as render:
        output = render.render(Document.read(["$b$"]), as_string=False)
    assert output == output_math
    with renderer as render:
        output = render.render(Document.read(["$b$"]), as_string=False)
    assert output == output_math
    with JsonRenderer() as render:
        output = render.render(Document.read(["$b$"]), as_string=False)
    assert output == output_nomath
