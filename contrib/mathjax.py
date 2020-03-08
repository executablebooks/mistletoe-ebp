"""
Provides MathJax support for rendering Markdown with LaTeX to html.
"""
from mistletoe import span_tokens, span_tokens_ext
from mistletoe.renderers.html import HTMLRenderer
from mistletoe.renderers.latex import LaTeXRenderer


class MathJaxRenderer(HTMLRenderer, LaTeXRenderer):
    """
    MRO will first look for render functions under HTMLRenderer,
    then LaTeXRenderer.
    """

    default_span_tokens = (
        span_tokens.EscapeSequence,
        span_tokens.HTMLSpan,
        span_tokens.AutoLink,
        span_tokens.CoreTokens,
        span_tokens_ext.Math,
        span_tokens_ext.Strikethrough,
        span_tokens.InlineCode,
        span_tokens.LineBreak,
        span_tokens.RawText,
    )

    mathjax_src = (
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js'
        '?config=TeX-MML-AM_CHTML"></script>\n'
    )

    def render_math(self, token):
        """
        Ensure Math tokens are all enclosed in two dollar signs.
        """
        if token.content.startswith("$$"):
            return self.render_raw_text(token)
        return "${}$".format(self.render_raw_text(token))

    def render_document(self, token):
        """
        Append CDN link for MathJax to the end of <body>.
        """
        return super().render_document(token) + self.mathjax_src
