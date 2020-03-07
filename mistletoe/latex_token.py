import re
from mistletoe.base_elements import SpanToken


__all__ = ["Math"]


class Math(SpanToken):
    pattern = re.compile(r"(\${1,2})([^$]+?)\1")
    parse_inner = False
    parse_group = 0
