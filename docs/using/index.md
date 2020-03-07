# Using mistletoe

## Installation

mistletoe-ebp is tested for Python 3.5 and above. Install mistletoe within a
[Conda Environment][conda-env] (recommended):

```sh
conda install -c conda-forge mistletoe-ebp
```

or *via* pip:

```sh
pip install mistletoe-ebp
```

Alternatively, clone the repo:

```sh
git clone https://github.com/ExecutableBookProject/mistletoe-ebp.git
cd mistletoe-ebp
pip install -e .[testing,code_style]
```

<!-- See the [contributing][contributing] doc for how to contribute to mistletoe. -->

## Usage

### Basic usage

Here's how you can use mistletoe in a Python script:

```python
import mistletoe

with open('foo.md', 'r') as fin:
    rendered = mistletoe.markdown(fin)
```

`mistletoe.markdown()` uses mistletoe's default settings: allowing HTML mixins
and rendering to HTML. The function also accepts an additional argument
`renderer`. To produce LaTeX output:

```python
import mistletoe
from mistletoe.renderers.latex import LaTeXRenderer

with open('foo.md', 'r') as fin:
    rendered = mistletoe.markdown(fin, LaTeXRenderer)
```

Finally, here's how you would manually specify extra tokens and a renderer
for mistletoe. In the following example, we use `HTMLRenderer` to render
the AST, which adds `HTMLBlock` and `HTMLSpan` to the normal parsing
process.

```python
from mistletoe import Document, HTMLRenderer

with open('foo.md', 'r') as fin:
    with HTMLRenderer() as renderer:
        rendered = renderer.render(Document.read(fin))
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
mistletoe [version 0.7.2] (interactive)
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
mistletoe [version 0.7.2] (interactive)
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

## Performance

mistletoe is the fastest CommonMark compliant implementation in Python.
Try the benchmarks yourself by running:

```sh
$ python3 test/test_samples/benchmark.py  # all results in seconds
Test document: syntax.md
Test iterations: 1000
Running tests with markdown, mistune, commonmark, mistletoe...
==============================================================
markdown: 40.270715949
mistune: 11.054077996000004
commonmark: 44.426582849
mistletoe: 34.47910147500001
```

We notice that Mistune is the fastest Markdown parser,
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

... and it is indeed the output of Python-Markdown, Commonmark-py and mistletoe.
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

Contextual analysis is why Python-Markdown is slow, and why CommonMark-py is slower.
The lack thereof is the reason mistune enjoys stellar performance
among similar parser implementations,
as well as the limitations that come with these performance benefits.

If you want an implementation that focuses on raw speed,
mistune remains a solid choice.
If you need a spec-compliant and readily extensible implementation, however,
mistletoe is still marginally faster than Python-Markdown,
while supporting more functionality (lists in block quotes, for example),
and significantly faster than CommonMark-py.


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

## Developer's Guide

Here's an example to add GitHub-style wiki links to the parsing process,
and provide a renderer for this new token.

### A new token

GitHub wiki links are span-level tokens, meaning that they reside inline,
and don't really look like chunky paragraphs. To write a new span-level
token, all we need to do is make a subclass of `SpanToken`:

```python
from mistletoe.span_token import SpanToken

class GithubWiki(SpanToken):
    pass
```

mistletoe uses regular expressions to search for span-level tokens in the
parsing process. As a refresher, GitHub wiki looks something like this:
`[[alternative text | target]]`. We define a class variable, `pattern`,
that stores the compiled regex:

```python
class GithubWiki(SpanToken):
    pattern = re.compile(r"\[\[ *(.+?) *\| *(.+?) *\]\]")
    def __init__(self, match):
        pass
```

The regex will be picked up by `SpanToken.find`, which is used by the
tokenizer to find all tokens of its kind in the document.
If regexes are too limited for your use case, consider overriding
the `find` method; it should return a list of all token occurrences.

Three other class variables are available for our custom token class,
and their default values are shown below:

```python
class SpanToken:
    parse_group = 1
    parse_inner = True
    precedence = 5
```

Note that alternative text can also contain other span-level tokens. For
example, `[[*alt*|link]]` is a GitHub link with an `Emphasis` token as its
child. To parse child tokens, `parse_inner` should be set to `True`
(the default value in this case), and `parse_group` should correspond
to the match group in which child tokens might occur
(also the default value, 1, in this case).

Once these two class variables are set correctly,
`GitHubWiki.children` attribute will automatically be set to
the list of child tokens.
Note that there is no need to manually set this attribute,
unlike previous versions of mistletoe.

Lastly, the `SpanToken` constructors take a regex match object as its argument.
We can simply store off the `target` attribute from `match_obj.group(2)`.

```python
from mistletoe.span_token import SpanToken

class GithubWiki(SpanToken):
    pattern = re.compile(r"\[\[ *(.+?) *\| *(.+?) *\]\]")
    def __init__(self, match_obj):
        self.target = match_obj.group(2)
```

There you go: a new token in 5 lines of code.

### Side note about precedence

Normally there is no need to override the `precedence` value of a custom token.
The default value is the same as `InlineCode`, `AutoLink` and `HTMLSpan`,
which means that whichever token comes first will be parsed. In our case:

```md
`code with [[ text` | link ]]
```

... will be parsed as:

```html
<code>code with [[ text</code> | link ]]
```

If we set `GitHubWiki.precedence = 6`, we have:

```html
`code with <a href="link">text`</a>
```

### A new renderer

Adding a custom token to the parsing process usually involves a lot
of nasty implementation details. Fortunately, mistletoe takes care
of most of them for you. Simply pass your custom token class to
`super().__init__()` does the trick:

```python
from mistletoe.renderers.html import HTMLRenderer

class GithubWikiRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__(GithubWiki)
```

We then only need to tell mistletoe how to render our new token:

```python
def render_github_wiki(self, token):
    template = '<a href="{target}">{inner}</a>'
    target = token.target
    inner = self.render_inner(token)
    return template.format(target=target, inner=inner)
```
Cleaning up, we have our new renderer class:

```python
from mistletoe.renderers.html import HTMLRenderer, escape_url

class GithubWikiRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__(GithubWiki)

    def render_github_wiki(self, token):
        template = '<a href="{target}">{inner}</a>'
        target = escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)
```

### Take it for a spin?

It is preferred that all mistletoe's renderers be used as context managers.
This is to ensure that your custom tokens are cleaned up properly, so that
you can parse other Markdown documents with different token types in the
same program.

```python
from mistletoe import Document
from contrib.github_wiki import GithubWikiRenderer

with open('foo.md', 'r') as fin:
    with GithubWikiRenderer() as renderer:
        rendered = renderer.render(Document.read(fin))
```

For more info, take a look at the `base_renderer` module in mistletoe.
The docstrings might give you a more granular idea of customizing mistletoe
to your needs.

[conda-env]: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands
[mistune]: https://github.com/lepture/mistune
[python-markdown]: https://github.com/waylan/Python-Markdown
[python-markdown2]: https://github.com/trentm/python-markdown2
[commonmark-py]: https://github.com/rtfd/CommonMark-py
[oilshell]: https://www.oilshell.org/blog/2018/02/14.html
[commonmark]: https://spec.commonmark.org/
[contrib]: https://github.com/miyuchina/mistletoe/tree/master/contrib
[scheme]: https://github.com/miyuchina/mistletoe/blob/dev/contrib/scheme.py
[example-392]: https://spec.commonmark.org/0.28/#example-392
