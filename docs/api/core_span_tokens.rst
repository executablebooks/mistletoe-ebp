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
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

Strong
......

.. autoclass:: mistletoe.span_tokens.Strong
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

Emphasis
.........

.. autoclass:: mistletoe.span_tokens.Emphasis
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

InlineCode
..........

.. autoclass:: mistletoe.span_tokens.InlineCode
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


Image
.....

.. autoclass:: mistletoe.span_tokens.Image
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

Link
....

.. autoclass:: mistletoe.span_tokens.Link
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

AutoLink
.........

.. autoclass:: mistletoe.span_tokens.AutoLink
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

EscapeSequence
..............

.. autoclass:: mistletoe.span_tokens.EscapeSequence
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

LineBreak
.........

.. autoclass:: mistletoe.span_tokens.LineBreak
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

RawText
.......

.. autoclass:: mistletoe.span_tokens.RawText
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

HTMLSpan
.........

.. autoclass:: mistletoe.span_tokens.HTMLSpan
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__
