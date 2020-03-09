(develop/intro)=

## Developer's Guide

[![CI Status][travis-badge]][travis-link]
[![Coverage][coveralls-badge]][coveralls-link]
[![Code style: black][black-badge]][black-link]
[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

To understand the core tokens that mistletoe parses, take a look at:

- {ref}`tokens/base`
- {ref}`tokens/block`
- {ref}`tokens/span`
- {ref}`tokens/extension`

Then, for more information on how rendrers are implemented see: {ref}`renderers/core`.

### The mistletoe AST

Both `BlockToken` and `SpanToken` can be instatiated programatically,
to build up an AST tree from scratch:

```python
from mistletoe.block_tokens import Document, Paragraph
from mistletoe.span_tokens import Link, RawText

doc = Document(
    children=[
        Paragraph(
            children=[Link(target="target", children=[RawText(content="some text")])],
            position=(0, 2),
        )
    ],
    link_definitions={},
)
```

All `Token`s then have a `read()` `classmethod`, which is used by the parser,
to dictate how the source text is converted to a token (possibly with nested children).

Here's an example to add GitHub-style wiki links to the parsing process,
and provide a renderer for this new token.

### A new token

GitHub wiki links are span-level tokens, meaning that they reside inline,
and don't really look like chunky paragraphs. To write a new span-level
token, all we need to do is make a subclass of {py:class}`~mistletoe.base_elements.SpanToken`:

```python
from mistletoe.base_elements import SpanToken

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

The regex will be picked up by {py:func}`~mistletoe.base_elements.SpanToken.find`, which is used by the
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

Lastly, the `SpanToken.read` method takes a regex match object as its argument, which is used to instatiate the token.
We can simply extract the `target` attribute from `match_obj.group(2)`.

```python
from mistletoe.base_elements import SpanToken

class GithubWiki(SpanToken):
    pattern = re.compile(r"\[\[ *(.+?) *\| *(.+?) *\]\]")

    def __init__(self, target: str):
        self.target = target

    @classmethod
    def read(cls, match):
        return cls(target=match.group(2))
```

There you go: a new token in a few lines of code.

### Side note about precedence

Normally there is no need to override the `precedence` value of a custom token.
The default value is the same as {py:class}`~mistletoe.span_tokens.InlineCode`, {py:class}`~mistletoe.span_tokens.AutoLink` and {py:class}`~mistletoe.span_tokens.HTMLSpan`,
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


[travis-badge]: https://travis-ci.org/ExecutableBookProject/mistletoe-ebp.svg?branch=master
[travis-link]: https://travis-ci.org/ExecutableBookProject/mistletoe-ebp
[coveralls-badge]: https://coveralls.io/repos/github/ExecutableBookProject/mistletoe-ebp/badge.svg?branch=master
[coveralls-link]: https://coveralls.io/github/ExecutableBookProject/mistletoe-ebp?branch=master
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[pypi-badge]: https://img.shields.io/pypi/v/mistletoe-ebp.svg
[pypi-link]: https://pypi.org/project/mistletoe-ebp
[conda-badge]: https://anaconda.org/conda-forge/mistletoe-ebp/badges/version.svg
[conda-link]: https://anaconda.org/conda-forge/mistletoe-ebp
[black-link]: https://github.com/ambv/black
