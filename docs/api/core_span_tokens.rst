.. _tokens/span:

Core Span Tokens
----------------

These span tokens are defined in the
`CommonMark specification <https://spec.commonmark.org/0.29/>`_.

.. list-table::
    :header-rows: 1
    :widths: 10 20 20

    * - Token
      - Description
      - Example
    * - RawText
      - any inline text
      - .. code-block:: md

           any text

    * - EscapeSequence
      - escaped symbols (to avoid them being interpreted as other syntax elements)
      - .. code-block:: md

           \*

    * - LineBreak
      - Soft or hard (ends with spaces or backslash)
      - .. code-block:: md

           A hard break\

    * - Strong
      - bold text
      - .. code-block:: md

           **strong**

    * - Emphasis
      - italic text
      - .. code-block:: md

           *emphasis*

    * - InlineCode
      - literal text
      - .. code-block:: md

           `a=1`

    * - AutoLink
      - link that is shown in final output
      - .. code-block:: md

           <https://www.google.com>

    * - Link
      - Reference a target or :py:class:`~mistletoe.block_tokens.LinkDefinition`
      - .. code-block:: md

           [text](target "title") or
           [text][key] or
           [key]

    * - Image
      - link to an image
      - .. code-block:: md

           ![alt](src "title")

    * - HTMLSpan
      - any valid HTML (rendered in HTML output only)
      - .. code-block:: html

           <p>some text</p>

Core
....

This is a special token that runs a nested parse of the inline string
and extracts nested tokens.

.. autoclass:: mistletoe.span_tokens.CoreTokens
    :show-inheritance:

RawText
.......

.. autoclass:: mistletoe.span_tokens.RawText
    :show-inheritance:

EscapeSequence
..............

.. autoclass:: mistletoe.span_tokens.EscapeSequence
    :members: pattern, parse_inner, parse_group
    :undoc-members:
    :show-inheritance:

LineBreak
.........

.. autoclass:: mistletoe.span_tokens.LineBreak
    :members: pattern, parse_inner, parse_group
    :undoc-members:
    :show-inheritance:

Strong
......

.. autoclass:: mistletoe.span_tokens.Strong
    :show-inheritance:

Emphasis
.........

.. autoclass:: mistletoe.span_tokens.Emphasis
    :show-inheritance:

InlineCode
..........

.. autoclass:: mistletoe.span_tokens.InlineCode
    :members: pattern, parse_inner, parse_group
    :undoc-members:
    :show-inheritance:


Link
....

.. autoclass:: mistletoe.span_tokens.Link
    :show-inheritance:

AutoLink
.........

.. autoclass:: mistletoe.span_tokens.AutoLink
    :members: pattern, parse_inner, parse_group
    :undoc-members:
    :show-inheritance:

Image
.....

.. autoclass:: mistletoe.span_tokens.Image
    :show-inheritance:

HTMLSpan
.........

.. autoclass:: mistletoe.span_tokens.HTMLSpan
    :members: pattern, parse_inner, parse_group
    :undoc-members:
    :show-inheritance:
