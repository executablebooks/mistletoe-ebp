.. _tokens/extension:

Extension Tokens
----------------

These tokens do not form part of the core
`CommonMark specification <https://spec.commonmark.org/0.29/>`_,
but are commonly implemented
`extended syntax elements <https://www.markdownguide.org/extended-syntax/>`_.

.. list-table::
    :header-rows: 1
    :widths: 10 20 20

    * - Token
      - Description
      - Example
    * - Strikethrough
      - a line through the text
      - .. code-block:: md

           ~~some text~~

    * - Math
      - Dollar `$` enclosed math. Two ``$`` characters wrap multi-line math.
      - .. code-block:: latex

            $a=1$ $b=2$

            $$
            a=1
            $$

    * - FrontMatter
      - A YAML block at the start of the document enclosed by ``---``
      - .. code-block:: yaml

           ---
           key: value
           ---

    * - - Table
        - TableRow
        - TableCell
      - Markdown table style, with pipe delimitation.
      - .. code-block:: md

           | a    | b    |
           | :--- | ---: |
           | c    | d    |

    * - - Footnote
        - FootReference
      - A definition for a referencing footnote, that is placed at the bottom of the document.
      - .. code-block:: md

           Something that needs further explanation.[^ref]

           [^ref]: Some footnote text

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

Footnote
.........

.. autoclass:: mistletoe.block_tokens_ext.Footnote
    :members: label_pattern, start, read
    :undoc-members:
    :show-inheritance:
    :exclude-members: __init__

FootReference
.............

.. autoclass:: mistletoe.span_tokens_ext.FootReference
    :members: pattern, parse_inner, parse_group
    :undoc-members:
    :show-inheritance:
