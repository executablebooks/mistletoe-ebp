from textwrap import dedent

from mistletoe import Document
from mistletoe.renderers.json import ast_to_json, JsonRenderer
from mistletoe.latex_token import Math


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
        store_definitions=True,
        front_matter=True,
    )
    output = ast_to_json(doc)
    data_regression.check(output)


def test_link_references(data_regression):
    doc = Document.read(["[bar][baz]\n", "\n", "[baz]: spam\n"], store_definitions=True)
    output = ast_to_json(doc)
    data_regression.check(output)


def test_extra_tokens():
    """Extra tokens should persist between multiple calls of the same renderer,
    but be reset if initiating a new renderer.
    """
    output = {
        "type": "Document",
        "front_matter": None,
        "link_definitions": {},
        "children": [
            {
                "type": "Paragraph",
                "children": [{"type": "RawText", "content": "$b$"}],
                "position": [1, 1],
            }
        ],
    }
    output_math = {
        "type": "Document",
        "front_matter": None,
        "link_definitions": {},
        "children": [
            {
                "type": "Paragraph",
                "children": [{"type": "Math", "content": "$b$"}],
                "position": [1, 1],
            }
        ],
    }

    with JsonRenderer() as render:
        output = render.render(Document.read(["$b$"]), as_string=False)
    assert output == output
    renderer = JsonRenderer(Math)
    with renderer as render:
        output = render.render(Document.read(["$b$"]), as_string=False)
    assert output == output_math
    with renderer as render:
        output = render.render(Document.read(["$b$"]), as_string=False)
    assert output == output_math
    with JsonRenderer() as render:
        output = render.render(Document.read(["$b$"]), as_string=False)
    assert output == output
