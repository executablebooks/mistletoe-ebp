"""
Abstract syntax tree renderer for mistletoe.
"""

import json
from mistletoe.renderers.base import BaseRenderer


class JsonRenderer(BaseRenderer):
    def render(self, token, as_string=True):
        """
        Returns the JSON string representation of the AST.

        Overrides super().render. Delegates the logic to ast_to_json.
        """
        dct = ast_to_json(token)
        if as_string:
            return json.dumps(dct, indent=2) + "\n"
        return dct

    def __getattr__(self, name):
        return lambda token: ""


def ast_to_json(token):
    """
    Recursively unrolls token attributes into dictionaries (token.children
    into lists).

    Returns:
        a dictionary of token's attributes.
    """
    node = {}
    # Python 3.6 uses [ordered dicts] [1].
    # Put in 'type' entry first to make the final tree format somewhat
    # similar to [MDAST] [2].
    #
    #   [1]: https://docs.python.org/3/whatsnew/3.6.html
    #   [2]: https://github.com/syntax-tree/mdast
    node["type"] = token.name
    node.update(token.to_dict())
    if "header" in node:
        node["header"] = ast_to_json(token.header)
    if node.get("front_matter", None) is not None:
        node["front_matter"] = ast_to_json(token.front_matter)
    if token.children is not None:
        node["children"] = [ast_to_json(child) for child in token.children]
    return node
