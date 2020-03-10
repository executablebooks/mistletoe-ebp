from textwrap import dedent
import pytest

from mistletoe import block_tokens, block_tokens_ext, span_tokens, span_tokens_ext
from mistletoe.renderers.html import HTMLRenderer
from mistletoe import Document


@pytest.fixture()
def html_renderer():
    with HTMLRenderer() as renderer:
        yield renderer


@pytest.fixture()
def html_renderer_standalone():
    with HTMLRenderer(as_standalone=True) as renderer:
        yield renderer


def test_render_funcs_document(html_renderer):
    token = block_tokens.Document(children=[])
    render_func = html_renderer.render_map[token.name]
    assert render_func(token) == ""


@pytest.mark.parametrize(
    "token_cls,kwargs,expected",
    (
        [span_tokens.RawText, {"content": "inner"}, "inner"],
        [span_tokens.HTMLSpan, {"content": "<p>"}, "<p>"],
        [span_tokens.LineBreak, {"soft": True}, "\n"],
        [span_tokens.LineBreak, {"soft": False}, "<br />\n"],
        [block_tokens.ThematicBreak, {"position": (0, 0)}, "<hr />"],
        [block_tokens.HTMLBlock, {"content": "<p>"}, "<p>"],
        [
            block_tokens_ext.TableRow,
            {"children": [], "row_align": [None]},
            "<tr>\n</tr>\n",
        ],
    ),
)
def test_render_funcs_no_children(html_renderer, token_cls, expected, kwargs):
    kwargs["position"] = (0, 0)
    token = token_cls(**kwargs)
    render_func = html_renderer.render_map[token.name]
    assert render_func(token) == expected


@pytest.mark.parametrize(
    "token_cls,kwargs,expected",
    (
        [span_tokens.Strong, {}, "<strong>inner</strong>"],
        [span_tokens.Emphasis, {}, "<em>inner</em>"],
        [span_tokens_ext.Strikethrough, {}, "<del>inner</del>"],
        [span_tokens.InlineCode, {}, "<code>inner</code>"],
        [span_tokens.EscapeSequence, {}, "inner"],
        [span_tokens.Link, {"target": "a"}, '<a href="a">inner</a>'],
        [
            span_tokens.AutoLink,
            {"target": "b", "mailto": False},
            '<a href="b">inner</a>',
        ],
        [span_tokens.Image, {"src": "a"}, '<img src="a" alt="inner" />'],
        [
            span_tokens.Image,
            {"src": "a", "title": "title"},
            '<img src="a" alt="inner" title="title" />',
        ],
        [block_tokens.Paragraph, {}, "<p>inner</p>"],
        [block_tokens.Heading, {"level": 1}, "<h1>inner</h1>"],
        [block_tokens.SetextHeading, {"level": 1}, "<h1>inner</h1>"],
        [block_tokens.Quote, {}, "<blockquote>\ninner\n</blockquote>"],
        [block_tokens.BlockCode, {}, "<pre><code>inner</code></pre>"],
        [
            block_tokens.BlockCode,
            {"language": "python"},
            '<pre><code class="language-python">inner</code></pre>',
        ],
        [block_tokens_ext.TableCell, {"align": None}, '<td align="left">inner</td>\n'],
        [block_tokens_ext.TableCell, {"align": 0}, '<td align="center">inner</td>\n'],
        [block_tokens_ext.TableCell, {"align": 1}, '<td align="right">inner</td>\n'],
    ),
)
def test_render_funcs_with_inner(html_renderer, token_cls, expected, kwargs):
    kwargs["position"] = (0, 0)
    token = token_cls(children=[span_tokens.RawText(content="inner")], **kwargs)
    render_func = html_renderer.render_map[token.name]
    assert render_func(token) == expected


def test_render_funcs_list_ordered(html_renderer):
    list_item = block_tokens.ListItem(
        children=[], loose=True, leader="1.", prepend=1, position=(0, 0)
    )
    token = block_tokens.List(
        children=[list_item], loose=True, start_at=1, position=(0, 0)
    )
    render_func = html_renderer.render_map[token.name]
    assert render_func(token) == "<ol>\n<li></li>\n</ol>"


def test_render_funcs_list_unordered(html_renderer):
    list_item = block_tokens.ListItem(
        children=[], loose=True, leader="-", prepend=1, position=(0, 0)
    )
    token = block_tokens.List(
        children=[list_item], loose=False, start_at=None, position=(0, 0)
    )
    render_func = html_renderer.render_map[token.name]
    assert render_func(token) == "<ul>\n<li></li>\n</ul>"


def test_render_funcs_table_no_header(html_renderer):
    token = block_tokens_ext.Table(
        children=[], header=None, column_align=[], position=(0, 0)
    )
    render_func = html_renderer.render_map[token.name]
    assert render_func(token) == "<table>\n<tbody>\n</tbody>\n</table>"


def test_render_funcs_table_with_header(html_renderer):
    header = block_tokens_ext.TableRow(children=[], row_align=[], position=(0, 0))
    token = block_tokens_ext.Table(
        children=[], header=header, column_align=[], position=(0, 0)
    )
    render_func = html_renderer.render_map[token.name]
    assert (
        render_func(token)
        == "<table>\n<thead>\n<tr>\n</tr>\n</thead>\n<tbody>\n</tbody>\n</table>"
    )


def test_link_definition_image(html_renderer):
    token = Document.read(["![alt][foo]\n", "\n", '[foo]: bar "title"\n'])
    output = '<p><img src="bar" alt="alt" title="title" /></p>\n'
    assert html_renderer.render(token) == output


def test_link_definition(html_renderer):
    token = Document.read(["[name][foo]\n", "\n", "[foo]: target\n"])
    output = '<p><a href="target">name</a></p>\n'
    assert html_renderer.render(token) == output


def test_link_definition_1st(html_renderer):
    token = Document.read(["[foo]: target\n", "\n", "[name][foo]\n"])
    output = '<p><a href="target">name</a></p>\n'
    assert html_renderer.render(token) == output


def test_link_definition_2reads(html_renderer):
    """The link definitions should not persist between parses."""
    token = Document.read(["[name][foo]\n", "\n", "[foo]: target\n"])
    token = Document.read(["[name][foo]\n", "\n"])
    output = "<p>[name][foo]</p>\n"
    assert html_renderer.render(token) == output


def test_footer_definitions(html_renderer_standalone, file_regression):
    """The link definitions should not persist between parses."""
    token = Document.read(
        [
            "[^name] a [^name] b [^1]\n",
            "\n",
            "[^name]: the footnote*text*\n",
            "[^1]: another footnote\n",
            "[^2]: unreferenced footnote\n",
        ]
    )
    file_regression.check(html_renderer_standalone.render(token), extension=".html")


def test_footer_ref_in_definition(html_renderer):
    """The link definitions should not persist between parses."""
    token = Document.read(["[^name]: [^name]\n"])
    assert html_renderer.render(token) == dedent(
        """\
        <hr class="footnotes-sep">
        <section class="footnotes">
        <ol class="footnotes-list">
        <li id="fn1" class="footnote-item">
        <sup class="footnote-ref"><a href="#fn1">[1]</a></sup>
        </li>
        </ol>
        </section>
        """
    )
