(intro/top-level)=

# mistletoe-ebp

[![CI Status][travis-badge]][travis-link]
[![Coverage][coveralls-badge]][coveralls-link]
[![Code style: black][black-badge]][black-link]
[![PyPI][pypi-badge]][pypi-link]
[![Conda][conda-badge]][conda-link]

mistletoe is a Markdown parser in pure Python,
designed to be fast, spec-compliant and fully customizable.

This is a version of [mistletoe] maintained by the [Excutable Book Project (EBP)][ebp-link]. It tracks the `myst` branch of [ExecutableBookProject/mistletoe](https://github.com/ExecutableBookProject/mistletoe)
which eventually, it is hoped, will be merged into mistletoe itself.

Apart from being the fastest
CommonMark-compliant Markdown parser implementation in pure Python,
mistletoe also supports easy definitions of custom tokens.
Parsing Markdown into an abstract syntax tree
also allows us to swap out renderers for different output formats,
without touching any of the core components.

Remember to spell mistletoe in lowercase!

## Features

* **Fast**:
  mistletoe is the fastest implementation of CommonMark in Python,
  that is, 2 to 3 times as fast as [Commonmark-py][commonmark-py],
  and still roughly 30% faster than [Python-Markdown][python-markdown].
  Running with PyPy yields comparable performance with [mistune][mistune].

  See the [performance](#performance) section for details.

* **Spec-compliant**:
  CommonMark is [a useful, high-quality project][oilshell].
  mistletoe follows the [CommonMark specification][commonmark]
  to resolve ambiguities during parsing.
  Outputs are predictable and well-defined.

* **Extensible**:
  Strikethrough and tables are supported natively,
  and custom block-level and span-level tokens can easily be added.
  Writing a new renderer for mistletoe is a relatively
  trivial task.

  You can even write [a Lisp][scheme] in it.

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
using/contributing.md
api/index.rst
```

[ebp-link]: https://github.com/ExecutableBookProject
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
[mistletoe]: https://github.com/miyuchina/mistletoe
[mistune]: https://github.com/lepture/mistune
[python-markdown]: https://github.com/waylan/Python-Markdown
[python-markdown2]: https://github.com/trentm/python-markdown2
[commonmark-py]: https://github.com/rtfd/CommonMark-py
[oilshell]: https://www.oilshell.org/blog/2018/02/14.html
[commonmark]: https://spec.commonmark.org/
[contrib]: https://github.com/miyuchina/mistletoe/tree/master/contrib
[scheme]: https://github.com/miyuchina/mistletoe/blob/dev/contrib/scheme.py
[example-392]: https://spec.commonmark.org/0.28/#example-392
[icon]: https://www.freepik.com
[cc-by]: https://creativecommons.org/licenses/by/3.0/us/
