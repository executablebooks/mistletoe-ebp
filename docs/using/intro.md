# Getting Started

(intro/install)=

## Installation

[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

mistletoe-ebp is tested for Python 3.5 and above. Install mistletoe within a
[Conda Environment][conda-env] (recommended):

```sh
conda install -c conda-forge mistletoe-ebp
```

or *via* pip:

```sh
pip install mistletoe-ebp
```

Alternatively, for code development, clone the repo:

```sh
git clone https://github.com/ExecutableBookProject/mistletoe-ebp.git
cd mistletoe-ebp
pip install -e .[testing,code_style]
```

```{seealso}
The {ref}`Contributing section <contribute>` to contribute to mistletoe's development!
```

(intro/usage)=

## Usage

### Basic usage

Here's how you can use mistletoe in a Python script:

```python
import mistletoe

with open('foo.md', 'r') as fin:
    rendered = mistletoe.markdown(fin)
```

{py:func}`mistletoe.markdown` defaults to
using the {py:class}`~mistletoe.renderers.html.HTMLRenderer`,
but other renderers can be chosen, such as the ones listed in {ref}`renderers/core`. To produce LaTeX output:

```python
import mistletoe
from mistletoe.renderers.latex import LaTeXRenderer

with open('foo.md', 'r') as fin:
    rendered = mistletoe.markdown(fin, LaTeXRenderer)
```

### From the command-line

pip installation enables mistletoe's command-line utility. Type the following
directly into your shell:

```sh
mistletoe foo.md
```

This will transpile `foo.md` into HTML, and dump the output to stdout. To save
the HTML, direct the output into a file:

```sh
mistletoe foo.md > out.html
```

You can pass in custom renderers by including the full path to your renderer
class after a `-r` or `--renderer` flag:

```sh
mistletoe foo.md --renderer custom_renderer.CustomRenderer
```

Running `mistletoe` without specifying a file will land you in interactive
mode.  Like Python's REPL, interactive mode allows you to test how your
Markdown will be interpreted by mistletoe:

```html
mistletoe [version 0.9.2] (interactive)
Type Ctrl-D to complete input, or Ctrl-C to exit.
>>> some **bold** text
... and some *italics*
...
<p>some <strong>bold</strong> text
and some <em>italics</em></p>
>>>
```

The interactive mode also accepts the `--renderer` flag:

```latex
mistletoe [version 0.9.2] (interactive)
Type Ctrl-D to complete input, or Ctrl-C to exit.
Using renderer: LaTeXRenderer
>>> some **bold** text
... and some *italics*
...
\documentclass{article}
\begin{document}

some \textbf{bold} text
and some \textit{italics}
\end{document}
>>>
```

### Customise the parse

To exert even greater control over the parsing process,
renderers can be initialised with an existing {py:class}`~mistletoe.parse_context.ParseContext` instance.
This class stores global variables that are utilised during the parsing process,
such as such as the block/span tokens to search for,
and link/footnote definitions that have been collected.
At any one time, one of these objects is set per thread;
which can be changed by {py:func}`~mistletoe.parse_context.set_parse_context` and
retrieved by {py:func}`~mistletoe.parse_context.get_parse_context`.

In the following example, we use the {py:class}`~mistletoe.renderers.html.HTMLRenderer` to parse a file:

- first parsing only tokens that are strictly CommonMark compliant
(see {ref}`block tokens <tokens/block>` and {ref}`span tokens <tokens/span>`), then
- including an extended token set (see {ref}`extended tokens <tokens/extension>`).

```python
from mistletoe import Document, HTMLRenderer, ParseContext, token_sets

commonmark_context = ParseContext(
    find_blocks=token_sets.get_commonmark_block_tokens(),
    find_spans=token_sets.get_commonmark_span_tokens(),
)
extended_context = ParseContext(
    find_blocks=token_sets.get_extended_block_tokens(),
    find_spans=token_sets.get_extended_span_tokens(),
)

with open('foo.md', 'r') as fin:
    rendered1 = mistletoe.markdown(
        fin, renderer=HTMLRenderer,
        parse_context=commonmark_context
    )

    rendered2 = mistletoe.markdown(
        fin, renderer=HTMLRenderer,
        parse_context=extended_context
    )

```

```{seealso}
{ref}`api/utils`
```

(intro/api_use)=

### Programmatic Use

To parse the text only to the mistletoe AST, the general entry point is the {py:meth}`mistletoe.block_tokens.Document.read` method
(athough actually all block tokens have a ``read`` method that can be used directly).

```python
>> from mistletoe import Document
>> text = """
.. Here's some *text*
..
.. 1. a list
..
.. > a *quote*"""
>> doc = Document.read(text)
>> doc
Document(children=3, link_definitions=0, footnotes=0, footref_order=0, front_matter=None)
```

All tokens have a `children` attribute:

```python
>> doc.children
[Paragraph(children=2, position=Position(lines=[2:2])),
 List(children=1, loose=False, start_at=1, position=Position(lines=[3:4])),
 Quote(children=1, position=Position(lines=[6:6]))]
```

or you can walk through the entire syntax tree, using the
{py:meth}`~mistletoe.base_elements.Token.walk` method:

```python
>> for item in doc.walk():
..     print(item)
WalkItem(node=Paragraph(children=2, position=Position(lines=[2:2])), parent=Document(children=3, link_definitions=0, footnotes=0, footref_order=0, front_matter=None), index=0, depth=1)
WalkItem(node=List(children=1, loose=False, start_at=1, position=Position(lines=[3:4])), parent=Document(children=3, link_definitions=0, footnotes=0, footref_order=0, front_matter=None), index=1, depth=1)
WalkItem(node=Quote(children=1, position=Position(lines=[6:6])), parent=Document(children=3, link_definitions=0, footnotes=0, footref_order=0, front_matter=None), index=2, depth=1)
WalkItem(node=RawText(), parent=Paragraph(children=2, position=Position(lines=[2:2])), index=0, depth=2)
WalkItem(node=Emphasis(children=1), parent=Paragraph(children=2, position=Position(lines=[2:2])), index=1, depth=2)
WalkItem(node=ListItem(children=1, loose=False, leader='1.', prepend=3, next_marker=None, position=Position(lines=[3:4])), parent=List(children=1, loose=False, start_at=1, position=Position(lines=[3:4])), index=0, depth=2)
WalkItem(node=Paragraph(children=2, position=Position(lines=[7:7])), parent=Quote(children=1, position=Position(lines=[6:6])), index=0, depth=2)
WalkItem(node=RawText(), parent=Emphasis(children=1), index=0, depth=3)
WalkItem(node=Paragraph(children=1, position=Position(lines=[4:4])), parent=ListItem(children=1, loose=False, leader='1.', prepend=3, next_marker=None, position=Position(lines=[3:4])), index=0, depth=3)
WalkItem(node=RawText(), parent=Paragraph(children=2, position=Position(lines=[7:7])), index=0, depth=3)
WalkItem(node=Emphasis(children=1), parent=Paragraph(children=2, position=Position(lines=[7:7])), index=1, depth=3)
WalkItem(node=RawText(), parent=Paragraph(children=1, position=Position(lines=[4:4])), index=0, depth=4)
WalkItem(node=RawText(), parent=Emphasis(children=1), index=0, depth=4)
```

You could even build your own AST programatically!

```python
>> from mistletoe import block_tokens, span_tokens, HTMLRenderer
>> doc = block_tokens.Document(children=[
..    block_tokens.Paragraph(
..        children=[
..            span_tokens.Emphasis(
..                children=[span_tokens.RawText("hallo")]
..            )
..    ])
.. ])
>> HTMLRenderer().render(doc)
"<p><em>hallo</em></p>"
```

### The Parse Process

At a lower level, the actual parsing process is split into two stages:

1. The full source text is read into an AST with all the span/inline level text stored
   as raw text in {py:class}`~mistletoe.base_elements.SpanContainer`.
   This allows all link definitions and (if included) footnote definitions to be read,
   before references are processed.
2. We walk through this intermediary AST and 'expand' the `SpanContainer`
   to produce all the span tokens; inspecting the global context for available definitions.

This process is illustrated in the following example, using the lower level parse method,
{py:func}`~mistletoe.block_tokenizer.tokenize_main`:

```python
>> from mistletoe.block_tokenizer import tokenize_main, SourceLines
>> lines = SourceLines('a [text][key]\n\n[key]: link "target"', standardize_ends=True)
>> paragraph = tokenize_main(lines, expand_spans=False)[0]
>> paragraph.children
SpanContainer('a [text][key]')
```

```python
>> from mistletoe.parse_context import get_parse_context
>> get_parse_context()
ParseContext(block_cls=11,span_cls=9,link_defs=1,footnotes=0)
>> get_parse_context().link_definitions
{'key': ('link', 'target')}
```

```python
>> paragraph.children.expand()
[RawText(), Link(target='link', title='target')]
```

````{important}
If directly using {py:func}`~mistletoe.block_tokenizer.tokenize_main`,
you should ensure that the global context is reset,
if you don't want to use previously read defintions:

```python
>> get_parse_context(reset=True)
```
````

(intro/performance)=

## Performance

mistletoe is the fastest CommonMark compliant implementation in Python.
Try the benchmarks yourself by installing
`pip install mistletoe-ebp[benchmark]` and running:

```sh
$ mistletoe-bench test/test_samples/syntax.md
Test document: syntax.md
Test iterations: 1000
Running 7 test(s) ...
=====================
markdown        (3.2.1): 31.13 s
markdown:extra  (3.2.1): 42.45 s
mistune         (0.8.4): 11.49 s
commonmark      (0.9.1): 47.94 s
mistletoe       (0.9.4): 35.58 s
mistletoe:extra (0.9.4): 40.37 s
panflute        (1.12.5): 168.06 s
```

notes:

- `markdown` without `extra` does not parse some CommonMark syntax,
  like fenced code blocks (see [Python-Markdown Extra](https://python-markdown.github.io/extensions/extra/))
- `mistletoe` uses only CommonMark compliant tokens, whereas `mistletoe:extra`
  includes {ref}`tokens/extension`.
- `panflute` calls [pandoc](https://pandoc.org/) *via* a subprocess

We notice that [Mistune][mistune] is the fastest Markdown parser,
and by a good margin, which demands some explanation.
mistletoe's biggest performance penalty
comes from stringently following the CommonMark spec,
which outlines a highly context-sensitive grammar for Markdown.
Mistune takes a simpler approach to the lexing and parsing process,
but this means that it cannot handle more complex cases,
e.g., precedence of different types of tokens, escaping rules, etc.

To see why this might be important to you,
consider the following Markdown input
([example 392][example-392] from the CommonMark spec):

```md
***foo** bar*
```

The natural interpretation is:

```html
<p><em><strong>foo</strong> bar</em></p>
```

... and it is indeed the output of [Python-Markdown], [Commonmark-py] and mistletoe.
Mistune (version 0.8.3) greedily parses the first two asterisks
in the first delimiter run as a strong-emphasis opener,
the second delimiter run as its closer,
but does not know what to do with the remaining asterisk in between:

```html
<p><strong>*foo</strong> bar*</p>
```

The implication of this runs deeper,
and it is not simply a matter of dogmatically following an external spec.
By adopting a more flexible parsing algorithm,
mistletoe allows us to specify a precedence level to each token class,
including custom ones that you might write in the future.
Code spans, for example, has a higher precedence level than emphasis,
so

```md
*foo `bar* baz`
```

... is parsed as:

```html
<p>*foo <code>bar* baz</code></p>
```

... whereas Mistune parses this as:

```html
<p><em>foo `bar</em> baz`</p>
```

Of course, it is not *impossible* for Mistune to modify its behavior,
and parse these two examples correctly,
through more sophisticated regexes or some other means.
It is nevertheless *highly likely* that,
when Mistune implements all the necessary context checks,
it will suffer from the same performance penalties.

Contextual analysis is why [Python-Markdown] is slow,
and why [CommonMark-py] is slower.
The lack thereof is the reason mistune enjoys stellar performance
among similar parser implementations,
as well as the limitations that come with these performance benefits.

If you want an implementation that focuses on raw speed,
mistune remains a solid choice.
If you need a spec-compliant and readily extensible implementation, however,
mistletoe is still marginally faster than [Python-Markdown],
while supporting more functionality (lists in block quotes, for example),
and significantly faster than [CommonMark-py].

One last note: another bottleneck of mistletoe compared to mistune
is the function overhead. Because, unlike mistune, mistletoe chooses to split
functionality into modules, function lookups can take significantly longer than
mistune. To boost the performance further, it is suggested to use PyPy with mistletoe.
Benchmark results show that on PyPy, mistletoe's performance is on par with mistune:

```sh
$ pypy3 test/benchmark.py mistune mistletoe
Test document: test/samples/syntax.md
Test iterations: 1000
Running tests with mistune, mistletoe...
========================================
mistune: 13.645681533998868
mistletoe: 15.088351159000013
```

[pypi-badge]: https://img.shields.io/pypi/v/mistletoe-ebp.svg
[pypi-link]: https://pypi.org/project/mistletoe-ebp
[conda-badge]: https://anaconda.org/conda-forge/mistletoe-ebp/badges/version.svg
[conda-link]: https://anaconda.org/conda-forge/mistletoe-ebp
[conda-env]: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands
[mistune]: https://mistune.readthedocs.io
[Python-Markdown]: https://Python-Markdown.github.io
[python-markdown2]: https://github.com/trentm/python-markdown2
[CommonMark-py]: https://commonmarkpy.readthedocs.io
[oilshell]: https://www.oilshell.org/blog/2018/02/14.html
[commonmark]: https://spec.commonmark.org/
[contrib]: https://github.com/ExecutableBookProject/mistletoe-ebp/tree/master/contrib
[scheme]: https://github.com/ExecutableBookProject/mistletoe-ebp/blob/dev/contrib/scheme.py
[example-392]: https://spec.commonmark.org/0.28/#example-392
