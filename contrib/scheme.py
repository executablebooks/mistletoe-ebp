from collections import ChainMap
from functools import reduce
import re
from typing import List as ListType

import attr

from mistletoe import BaseRenderer, base_elements
from mistletoe.span_tokenizer import tokenize_span
from mistletoe.nested_tokenizer import MatchObj


@attr.s(slots=True, kw_only=True)
class Program(base_elements.BlockToken):

    children: ListType[base_elements.Token] = attr.ib(
        repr=lambda c: str(len(c)), metadata={"doc": "Child tokens list"}
    )

    @classmethod
    def start(cls, line: str) -> bool:
        return True

    @classmethod
    def read(cls, lines):
        return cls(children=tokenize_span("".join([line.strip() for line in lines])))


class Expr(base_elements.SpanToken):
    @classmethod
    def find(cls, string):
        matches = []
        start = []
        for i, c in enumerate(string):
            if c == "(":
                start.append(i)
            elif c == ")":
                pos = start.pop()
                end_pos = i + 1
                content = string[pos + 1 : i]
                matches.append(MatchObj(pos, end_pos, (pos + 1, i, content)))
        return matches


class Number(base_elements.SpanToken):
    pattern = re.compile(r"(\d+)")
    parse_inner = False

    def __init__(self, *, number: int):
        self.number = number

    @classmethod
    def read(cls, match):
        return cls(number=eval(match.group(0)))


class String(base_elements.SpanToken):
    pattern = re.compile(r"\"([^\"]+)\"")
    parse_inner = False

    def __init__(self, *, string: int):
        self.string = string

    @classmethod
    def read(cls, match):
        return cls(string=match.group(0)[1:-1])


class Variable(base_elements.SpanToken):
    pattern = re.compile(r"([^\s()]+)")
    parse_inner = False

    def __init__(self, var_name: str):
        self.var_name = var_name

    @classmethod
    def read(cls, match):
        return cls(var_name=match.group(0))


class Whitespace(base_elements.SpanToken):
    parse_inner = False

    @classmethod
    def read(self, match):
        return None


class Procedure:
    def __init__(self, expr_token, body, env):
        self.params = [child.var_name for child in expr_token.children]
        self.body = body
        self.env = env


class Scheme(BaseRenderer):

    default_block_tokens = (Program,)
    default_span_tokens = (Expr, Number, String, Variable, Whitespace)

    def __init__(self):
        super().__init__()

        self.env = ChainMap(
            {
                "define": self.define,
                "lambda": lambda expr_token, *body: Procedure(
                    expr_token, body, self.env
                ),
                "+": lambda x, y: self.render(x) + self.render(y),
                "-": lambda x, y: self.render(x) - self.render(y),
                "*": lambda x, y: self.render(x) * self.render(y),
                "/": lambda x, y: self.render(x) / self.render(y),
                "<": lambda x, y: self.render(x) < self.render(y),
                ">": lambda x, y: self.render(x) > self.render(y),
                "<=": lambda x, y: self.render(x) <= self.render(y),
                ">=": lambda x, y: self.render(x) >= self.render(y),
                "=": lambda x, y: self.render(x) == self.render(y),
                "true": True,
                "false": False,
                "cons": lambda x, y: (self.render(x), self.render(y)),
                "car": lambda pair: self.render(pair)[0],
                "cdr": lambda pair: self.render(pair)[1],
                "and": lambda *args: all(map(self.render, args)),
                "or": lambda *args: any(map(self.render, args)),
                "not": lambda x: not self.render(x),
                "if": lambda cond, true, false: self.render(true)
                if self.render(cond)
                else self.render(false),
                "cond": self.cond,
                "null": None,
                "null?": lambda x: self.render(x) is None,
                "nil": (),
                "list": lambda *args: reduce(
                    lambda x, y: (y, x), map(self.render, reversed(args)), None
                ),
                "display": lambda *args: print(*map(self.render, args)),
            }
        )

    def render_inner(self, token):
        result = None
        for child in token.children:
            result = self.render(child)
        return result

    def render_expr(self, token):
        proc, *args = token.children
        proc = self.render(proc)
        return self.apply(proc, args) if isinstance(proc, Procedure) else proc(*args)

    def render_number(self, token):
        return token.number

    def render_string(self, token):
        return token.string

    def render_variable(self, token):
        return self.env[token.var_name]

    def define(self, *args):
        if len(args) == 2:
            name_token, val_token = args
            self.env[name_token.var_name] = self.render(val_token)
        else:
            name_token, expr_token, *body = args
            self.env[name_token.var_name] = Procedure(expr_token, body, self.env)

    def cond(self, *exprs):
        for expr in exprs:
            test, value = expr.children
            if test == "else" and "else" not in self.env:
                return self.render(value)
            if self.render(test):
                return self.render(value)

    def apply(self, proc, args):
        old_env = self.env
        self.env = proc.env.new_child()
        try:
            for param, arg in zip(proc.params, args):
                self.env[param] = self.render(arg)
            result = None
            for expr in proc.body:
                result = self.render(expr)
        finally:
            self.env = old_env
        return result
