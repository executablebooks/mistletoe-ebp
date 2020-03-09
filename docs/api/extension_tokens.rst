.. _tokens/extension:

Extension Tokens
----------------

These tokens do not form part of the core
`CommonMark specification <https://spec.commonmark.org/0.29/>`_,
but are commonly implemented
`extended syntax elements <https://www.markdownguide.org/extended-syntax/>`_.

Strikethrough
.............

.. autoclass:: mistletoe.span_tokens_ext.Strikethrough
    :members: pattern, parse_inner, parse_group
    :undoc-members:
    :show-inheritance:

Math
....

.. autoclass:: mistletoe.span_tokens_ext.Math
    :members: pattern, parse_inner, parse_group
    :undoc-members:
    :show-inheritance:


FootReference
.............

.. autoclass:: mistletoe.span_tokens_ext.FootReference
    :members: pattern, parse_inner, parse_group
    :undoc-members:
    :show-inheritance:


FrontMatter
...........

.. autoclass:: mistletoe.block_tokens.FrontMatter
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

Table
.....

.. autoclass:: mistletoe.block_tokens_ext.Table
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


TableRow
........

.. autoclass:: mistletoe.block_tokens_ext.TableRow
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


TableCell
.........

.. autoclass:: mistletoe.block_tokens_ext.TableCell
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__
