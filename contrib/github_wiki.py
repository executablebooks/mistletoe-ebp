"""
GitHub Wiki support for mistletoe.
"""

import re

from mistletoe import span_tokens, span_tokens_ext
from mistletoe.base_elements import SpanToken
from mistletoe.renderers.html import HTMLRenderer


__all__ = ["GithubWiki", "GithubWikiRenderer"]


class GithubWiki(SpanToken):
    pattern = re.compile(r"\[\[ *(.+?) *\| *(.+?) *\]\]")

    def __init__(self, *, target: str):
        """:param target: link target"""
        self.target = target

    @classmethod
    def read(cls, match):
        return cls(target=match.group(2))


class GithubWikiRenderer(HTMLRenderer):
    default_span_tokens = (
        span_tokens.EscapeSequence,
        GithubWiki,
        span_tokens.HTMLSpan,
        span_tokens.AutoLink,
        span_tokens.CoreTokens,
        span_tokens_ext.Strikethrough,
        span_tokens.InlineCode,
        span_tokens.LineBreak,
        span_tokens.RawText,
    )

    def render_github_wiki(self, token):
        template = '<a href="{target}">{inner}</a>'
        target = self.escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)
