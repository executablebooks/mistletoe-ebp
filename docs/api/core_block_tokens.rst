.. _tokens/block:

Core Block Tokens
-----------------

These block tokens are defined in the
`CommonMark specification <https://spec.commonmark.org/0.29/>`_.

.. list-table::
    :header-rows: 1
    :widths: 10 20 20

    * - Token
      - Description
      - Example

    * - ATX Heading
      - Level 1-6 headings, denoted by number of ``#``
      - .. code-block:: md

           ### Heading level 3

    * - SetextHeading
      - Underlined header (using multiple ``=`` or ``-``)
      - .. code-block:: md

           Header
           ======

    * - Paragraph
      - General inline text
      - .. code-block:: md

           any *text*

    * - Quote
      - quoted text
      - .. code-block:: md

           > this is a quote

    * - BlockCode
      - indented text (4 spaces or a tab)
      - .. code-block:: md

           included as literal *text*

    * - CodeFence
      - enclosed in 3 or more backticks with an optional language name
      - .. code-block:: md

           .. code-block:: python

              print('this is python')

    * - ThematicBreak
      - Creates a horizontal line in the output
      - .. code-block:: md

           ---

    * - List
      - bullet points or enumerated.
      - .. code-block:: md

           - item
           - nested item
           1. numbered item

    * - LinkDefinition
      -  A substitution for an inline link, which can have a reference target (no spaces), and an optional title (in `"`)
      - .. code-block:: md

           [key]: https://www.google.com "a title"

    * - HTMLBlock
      - Any valid HTML (rendered in HTML output only)
      - .. code-block:: html

           <p>some text</p>


Document
........

.. autoclass:: mistletoe.block_tokens.Document
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


Atx Heading
...........

.. autoclass:: mistletoe.block_tokens.Heading
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


Setext Heading
..............

.. autoclass:: mistletoe.block_tokens.SetextHeading
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


Paragraph
.........

.. autoclass:: mistletoe.block_tokens.Paragraph
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


Quote
.....

.. autoclass:: mistletoe.block_tokens.Quote
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


BlockCode
.........

.. autoclass:: mistletoe.block_tokens.BlockCode
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


CodeFence
.........

.. autoclass:: mistletoe.block_tokens.CodeFence
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


List
....

.. autoclass:: mistletoe.block_tokens.List
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


ListItem
........

.. autoclass:: mistletoe.block_tokens.ListItem
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


LinkDefinition
..............

.. autoclass:: mistletoe.block_tokens.LinkDefinition
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__


ThematicBreak
.............

.. autoclass:: mistletoe.block_tokens.ThematicBreak
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__

HTMLBlock
.........

.. autoclass:: mistletoe.block_tokens.HTMLBlock
    :members:
    :no-undoc-members:
    :show-inheritance:
    :exclude-members: __init__
