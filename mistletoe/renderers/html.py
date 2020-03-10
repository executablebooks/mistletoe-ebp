"""
HTML renderer for mistletoe.
"""

import re
import sys
from textwrap import dedent
from urllib.parse import quote

from mistletoe.renderers.base import BaseRenderer

if sys.version_info < (3, 4):
    from mistletoe import _html as html
else:
    import html


class HTMLRenderer(BaseRenderer):
    """HTML renderer class."""

    def __init__(
        self, find_blocks=None, find_spans=None, as_standalone=False, add_css=None
    ):
        """Initialise the renderer

        :param find_blocks: override the default block tokens (classes or class paths)
        :param find_spans: override the default span tokens (classes or class paths)
        :param as_standalone: return the HTML body within a minmal HTML page
        :param add_css: if as_standalone=True, CSS to add to the header
        """
        super().__init__(find_blocks=find_blocks, find_spans=find_spans)
        self.as_standalone = as_standalone
        self.add_css = add_css
        self._suppress_ptag_stack = [False]
        # html.entities.html5 includes entitydefs not ending with ';',
        # CommonMark seems to hate them, so...
        self._stdlib_charref = html._charref
        _charref = re.compile(
            r"&(#[0-9]+;" r"|#[xX][0-9a-fA-F]+;" r"|[^\t\n\f <&#;]{1,32};)"
        )
        html._charref = _charref
        # TODO when to reset? on every `__enter__` or just in `render_document`?
        self.footnotes_referenced = []

    def __exit__(self, *args):
        super().__exit__(*args)
        html._charref = self._stdlib_charref

    def render_document(self, token):

        self.link_definitions.update(token.link_definitions)
        self.footnotes_referenced = token.footref_order

        inner = "\n".join([self.render(child) for child in token.children])
        body = "{}\n".format(inner) if inner else ""

        if token.footref_order:
            body += '<hr class="footnotes-sep">\n'
            body += '<section class="footnotes">\n'
            body += '<ol class="footnotes-list">\n'
            for index, target in enumerate(token.footref_order, 1):
                footnote = token.footnotes[target]
                body += '<li id="fn{}" class="footnote-item">\n'.format(index)
                body += "\n".join([self.render(child) for child in footnote.children])
                body += "\n</li>\n"
            body += "</ol>\n"
            body += "</section>\n"

        if not self.as_standalone:
            return body
        return minimal_html_page(body, css=self.add_css or "")

    def render_to_plain(self, token):
        if token.children is not None:
            inner = [self.render_to_plain(child) for child in token.children]
            return "".join(inner)
        return self.escape_html(token.content)

    def render_strong(self, token):
        template = "<strong>{}</strong>"
        return template.format(self.render_inner(token))

    def render_emphasis(self, token):
        template = "<em>{}</em>"
        return template.format(self.render_inner(token))

    def render_inline_code(self, token):
        template = "<code>{}</code>"
        inner = html.escape(token.children[0].content)
        return template.format(inner)

    def render_strikethrough(self, token):
        template = "<del>{}</del>"
        return template.format(self.render_inner(token))

    def render_image(self, token):
        template = '<img src="{}" alt="{}"{} />'
        if token.title:
            title = ' title="{}"'.format(self.escape_html(token.title))
        else:
            title = ""
        return template.format(token.src, self.render_to_plain(token), title)

    def render_link(self, token):
        template = '<a href="{target}"{title}>{inner}</a>'
        target = self.escape_url(token.target)
        if token.title:
            title = ' title="{}"'.format(self.escape_html(token.title))
        else:
            title = ""
        inner = self.render_inner(token)
        return template.format(target=target, title=title, inner=inner)

    def render_auto_link(self, token):
        template = '<a href="{target}">{inner}</a>'
        if token.mailto:
            target = "mailto:{}".format(token.target)
        else:
            target = self.escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    def render_raw_text(self, token):
        return self.escape_html(token.content)

    @staticmethod
    def render_html_span(token):
        return token.content

    def render_heading(self, token):
        template = "<h{level}>{inner}</h{level}>"
        inner = self.render_inner(token)
        return template.format(level=token.level, inner=inner)

    def render_quote(self, token):
        elements = ["<blockquote>"]
        self._suppress_ptag_stack.append(False)
        elements.extend([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        elements.append("</blockquote>")
        return "\n".join(elements)

    def render_paragraph(self, token):
        if self._suppress_ptag_stack[-1]:
            return "{}".format(self.render_inner(token))
        return "<p>{}</p>".format(self.render_inner(token))

    def render_block_code(self, token):
        template = "<pre><code{attr}>{inner}</code></pre>"
        if token.language:
            attr = ' class="{}"'.format(
                "language-{}".format(self.escape_html(token.language))
            )
        else:
            attr = ""
        inner = html.escape(token.children[0].content)
        return template.format(attr=attr, inner=inner)

    def render_list(self, token):
        template = "<{tag}{attr}>\n{inner}\n</{tag}>"
        if token.start_at is not None:
            tag = "ol"
            attr = ' start="{}"'.format(token.start_at) if token.start_at != 1 else ""
        else:
            tag = "ul"
            attr = ""
        self._suppress_ptag_stack.append(not token.loose)
        inner = "\n".join([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        return template.format(tag=tag, attr=attr, inner=inner)

    def render_list_item(self, token):
        if len(token.children) == 0:
            return "<li></li>"
        inner = "\n".join([self.render(child) for child in token.children])
        inner_template = "\n{}\n"
        if self._suppress_ptag_stack[-1]:
            if token.children[0].__class__.__name__ == "Paragraph":
                inner_template = inner_template[1:]
            if token.children[-1].__class__.__name__ == "Paragraph":
                inner_template = inner_template[:-1]
        return "<li>{}</li>".format(inner_template.format(inner))

    def render_table(self, token):
        # This is actually gross and I wonder if there's a better way to do it.
        #
        # The primary difficulty seems to be passing down alignment options to
        # reach individual cells.
        template = "<table>\n{inner}</table>"
        if getattr(token, "header", None) is not None:
            head_template = "<thead>\n{inner}</thead>\n"
            head_inner = self.render_table_row(token.header, is_header=True)
            head_rendered = head_template.format(inner=head_inner)
        else:
            head_rendered = ""
        body_template = "<tbody>\n{inner}</tbody>\n"
        body_inner = self.render_inner(token)
        body_rendered = body_template.format(inner=body_inner)
        return template.format(inner=head_rendered + body_rendered)

    def render_table_row(self, token, is_header=False):
        template = "<tr>\n{inner}</tr>\n"
        inner = "".join(
            [self.render_table_cell(child, is_header) for child in token.children]
        )
        return template.format(inner=inner)

    def render_table_cell(self, token, in_header=False):
        template = "<{tag}{attr}>{inner}</{tag}>\n"
        tag = "th" if in_header else "td"
        if token.align is None:
            align = "left"
        elif token.align == 0:
            align = "center"
        elif token.align == 1:
            align = "right"
        attr = ' align="{}"'.format(align)
        inner = self.render_inner(token)
        return template.format(tag=tag, attr=attr, inner=inner)

    @staticmethod
    def render_thematic_break(token):
        return "<hr />"

    @staticmethod
    def render_line_break(token):
        return "\n" if token.soft else "<br />\n"

    @staticmethod
    def render_html_block(token):
        return token.content

    @staticmethod
    def escape_html(raw):
        return html.escape(html.unescape(raw)).replace("&#x27;", "'")

    @staticmethod
    def escape_url(raw):
        """
        Escape urls to prevent code injection craziness. (Hopefully.)
        """
        return html.escape(quote(html.unescape(raw), safe="/#:()*?=%@+,&"))

    def render_foot_reference(self, token):
        index = self.footnotes_referenced.index(token.target) + 1
        return '<sup class="footnote-ref"><a href="#fn{0}">[{0}]</a></sup>'.format(
            index
        )


def minimal_html_page(
    body: str, css: str = "", title: str = "Standalone HTML", lang: str = "en"
):
    """Return a template for a minimal HTML page."""
    return dedent(
        """\
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
    {css}
    </style>
    </head>
    <body>
    {body}
    </body>
    </html>
    """
    ).format(title=title, lang=lang, css=css, body=body)
