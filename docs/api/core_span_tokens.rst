.. _tokens/span:

Core Span Tokens
----------------

These span tokens are defined in the
`CommonMark specification <https://spec.commonmark.org/0.29/>`_.

Core
....

This is a special token that runs a nested parse of the inline string
and extracts nested tokens.

.. autoclass:: mistletoe.span_tokens.CoreTokens
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


Image
.....

.. autoclass:: mistletoe.span_tokens.Image
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

RawText
.......

.. autoclass:: mistletoe.span_tokens.RawText
    :show-inheritance:

HTMLSpan
.........

.. autoclass:: mistletoe.span_tokens.HTMLSpan
    :members: pattern, parse_inner, parse_group
    :undoc-members:
    :show-inheritance:
