.. _api/utils:

Parsing Functions
-----------------

Functions useful for simple parses:

.. autofunction:: mistletoe.markdown

.. autofunction:: mistletoe.block_tokenizer.tokenize_main

.. autofunction:: mistletoe.span_tokenizer.tokenize_span

.. autoclass:: mistletoe.base_elements.TokenEncoder
    :members:
    :undoc-members:
    :show-inheritance:


.. autofunction:: mistletoe.base_elements.serialize_tokens

Global Context
--------------

During a single parse, the require token sets and link definitions are stored
as a (thread-safe) global instance.
You can set this directly before using the functions above.


.. autoclass:: mistletoe.parse_context.ParseContext
    :members:
    :undoc-members:
    :show-inheritance:


.. autofunction:: mistletoe.parse_context.get_parse_context

.. autofunction:: mistletoe.parse_context.set_parse_context

.. autofunction:: mistletoe.parse_context.tokens_from_classes

.. autofunction:: mistletoe.parse_context.tokens_from_module
