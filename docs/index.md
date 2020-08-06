(intro/top-level)=

# mistletoe-ebp

```{important}
This package is now archived in favour of [markdown-it-py](https://github.com/executablebooks/markdown-it-py).
```

mistletoe is a Markdown parser in pure Python,
designed to be fast, spec-compliant and fully customizable.

Apart from being the fastest
CommonMark-compliant Markdown parser implementation in pure Python,
mistletoe also supports easy definitions of custom tokens.
Parsing Markdown into an abstract syntax tree
also allows us to swap out renderers for different output formats,
without touching any of the core components.

```{note}
This is a version of [mistletoe] maintained by the [Excutable Book Project (EBP)][ebp-link].
It contains many improvements (see the `myst` branch of [ExecutableBookProject/mistletoe](https://github.com/ExecutableBookProject/mistletoe) for details)
which eventually, it is hoped, will be merged into mistletoe itself.

[ebp-link]: https://github.com/ExecutableBookProject
[mistletoe]: https://github.com/miyuchina/mistletoe
```

## Features

* **Fast**:
  mistletoe is the fastest implementation of CommonMark in Python,
  that is, 2 to 3 times as fast as [Commonmark-py][commonmark-py],
  and still roughly 30% faster than [Python-Markdown][python-markdown].
  Running with PyPy yields comparable performance with [mistune][mistune].
  See the {ref}`Performance section<intro/performance>` for details.

* **Spec-compliant**:
  CommonMark is [a useful, high-quality project][oilshell].
  mistletoe follows the [CommonMark specification][commonmark]
  to resolve ambiguities during parsing.
  Outputs are predictable and well-defined.

* **Clear API**:
  Documents can be built and assessed programatically,
  in an object-orientated manner.
  See {ref}`intro/api_use` and {ref}`api/main` for details.

* **Extensible**:
  Strikethrough and tables are supported natively,
  and custom block-level and span-level tokens can easily be added.
  Writing a new renderer for mistletoe is a relatively
  trivial task. See the {ref}`Developer section <develop/intro>` for details.

* **LSP compliant**:
  `mistletoe-ebp` aims to make it easy to use in implementations of the
  [Language Server Protocol][lsp], the requirements being that;
  (a) it is thread-safe for asynchronous parsing, and
  (b) the line and character ranges of the source text are recorded
  for each element in the syntax tree.

Some alternative output formats:

* HTML
* LaTeX
* Jira Markdown ([contrib][contrib])
* Mathjax ([contrib][contrib])
* Scheme ([contrib][contrib])
* HTML + code highlighting ([contrib][contrib])

## Why mistletoe?

"For fun," says David Beazley.

## Copyright & License

* mistletoe's logo uses artwork by [Freepik][icon], under
  [CC BY 3.0][cc-by].
* mistletoe is released under MIT license.

Here are the site contents:

```{toctree}
---
maxdepth: 2
caption: Contents
---
using/intro.md
using/develop.md
api/index.rst
using/contributing.md
```

[mistune]: https://github.com/lepture/mistune
[python-markdown]: https://github.com/waylan/Python-Markdown
[python-markdown2]: https://github.com/trentm/python-markdown2
[commonmark-py]: https://github.com/rtfd/CommonMark-py
[oilshell]: https://www.oilshell.org/blog/2018/02/14.html
[commonmark]: https://spec.commonmark.org/
[contrib]: https://github.com/ExecutableBookProject/mistletoe-ebp/tree/master/contrib
[scheme]: https://github.com/ExecutableBookProject/mistletoe-ebp/blob/dev/contrib/scheme.py
[example-392]: https://spec.commonmark.org/0.28/#example-392
[icon]: https://www.freepik.com
[cc-by]: https://creativecommons.org/licenses/by/3.0/us/
[lsp]: https://microsoft.github.io/language-server-protocol/
