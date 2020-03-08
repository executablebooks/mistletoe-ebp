"""
LaTeX renderer for mistletoe.
"""
from mistletoe import block_tokens, block_tokens_ext, span_tokens, span_tokens_ext
from mistletoe.renderers.base import BaseRenderer


class LaTeXRenderer(BaseRenderer):

    default_block_tokens = (
        # block_tokens.HTMLBlock,
        block_tokens.BlockCode,
        block_tokens.Heading,
        block_tokens.Quote,
        block_tokens.CodeFence,
        block_tokens.ThematicBreak,
        block_tokens.List,
        block_tokens_ext.Table,
        block_tokens.LinkDefinition,
        block_tokens.Paragraph,
    )

    default_span_tokens = (
        span_tokens.EscapeSequence,
        # span_tokens.HTMLSpan,
        span_tokens.AutoLink,
        span_tokens.CoreTokens,
        span_tokens_ext.Math,
        span_tokens_ext.Strikethrough,
        span_tokens.InlineCode,
        span_tokens.LineBreak,
        span_tokens.RawText,
    )

    def __init__(self, find_blocks=None, find_spans=None):
        """Initialise the renderer

        :param find_blocks: override the default block tokens (classes or class paths)
        :param find_spans: override the default span tokens (classes or class paths)
        """
        self.packages = {}
        super().__init__(find_blocks=find_blocks, find_spans=find_spans)

    def render_strong(self, token):
        return "\\textbf{{{}}}".format(self.render_inner(token))

    def render_emphasis(self, token):
        return "\\textit{{{}}}".format(self.render_inner(token))

    def render_inline_code(self, token):
        return "\\verb|{}|".format(self.render_inner(token))

    def render_strikethrough(self, token):
        self.packages["ulem"] = ["normalem"]
        return "\\sout{{{}}}".format(self.render_inner(token))

    def render_image(self, token):
        self.packages["graphicx"] = []
        return "\n\\includegraphics{{{}}}\n".format(token.src)

    def render_link(self, token):
        self.packages["hyperref"] = []
        template = "\\href{{{target}}}{{{inner}}}"
        inner = self.render_inner(token)
        return template.format(target=token.target, inner=inner)

    def render_auto_link(self, token):
        self.packages["hyperref"] = []
        return "\\url{{{}}}".format(token.target)

    @staticmethod
    def render_math(token):
        return token.content

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    def render_raw_text(self, token, escape=True):
        return (
            (
                token.content.replace("$", "\\$")
                .replace("#", "\\#")
                .replace("{", "\\{")
                .replace("}", "\\}")
                .replace("&", "\\&")
            )
            if escape
            else token.content
        )

    def render_heading(self, token):
        inner = self.render_inner(token)
        if token.level == 1:
            return "\n\\section{{{}}}\n".format(inner)
        elif token.level == 2:
            return "\n\\subsection{{{}}}\n".format(inner)
        return "\n\\subsubsection{{{}}}\n".format(inner)

    def render_quote(self, token):
        self.packages["csquotes"] = []
        template = "\\begin{{displayquote}}\n{inner}\\end{{displayquote}}\n"
        return template.format(inner=self.render_inner(token))

    def render_paragraph(self, token):
        return "\n{}\n".format(self.render_inner(token))

    def render_block_code(self, token):
        self.packages["listings"] = []
        template = "\n\\begin{{lstlisting}}[language={}]\n" "{}" "\\end{{lstlisting}}\n"
        inner = self.render_raw_text(token.children[0], False)
        return template.format(token.language, inner)

    def render_list(self, token):
        self.packages["listings"] = []
        template = "\\begin{{{tag}}}\n{inner}\\end{{{tag}}}\n"
        tag = "enumerate" if token.start_at is not None else "itemize"
        inner = self.render_inner(token)
        return template.format(tag=tag, inner=inner)

    def render_list_item(self, token):
        inner = self.render_inner(token)
        return "\\item {}\n".format(inner)

    def render_table(self, token):
        def render_align(column_align):
            if column_align != [None]:
                cols = [get_align(col) for col in token.column_align]
                return "{{{}}}".format(" ".join(cols))
            else:
                return ""

        def get_align(col):
            if col is None:
                return "l"
            elif col == 0:
                return "c"
            elif col == 1:
                return "r"
            raise RuntimeError("Unrecognized align option: " + col)

        template = "\\begin{{tabular}}{align}\n" "{inner}" "\\end{{tabular}}\n"
        if hasattr(token, "header"):
            head_template = "{inner}\\hline\n"
            head_inner = self.render_table_row(token.header)
            head_rendered = head_template.format(inner=head_inner)
        else:
            head_rendered = ""
        inner = self.render_inner(token)
        align = render_align(token.column_align)
        return template.format(inner=head_rendered + inner, align=align)

    def render_table_row(self, token):
        cells = [self.render(child) for child in token.children]
        return " & ".join(cells) + " \\\\\n"

    def render_table_cell(self, token):
        return self.render_inner(token)

    @staticmethod
    def render_thematic_break(token):
        return "\\hrulefill\n"

    @staticmethod
    def render_line_break(token):
        return "\n" if token.soft else "\\newline\n"

    def render_packages(self):
        pattern = "\\usepackage{options}{{{package}}}\n"
        return "".join(
            pattern.format(options=options or "", package=package)
            for package, options in self.packages.items()
        )

    def render_document(self, token):
        template = (
            "\\documentclass{{article}}\n"
            "{packages}"
            "\\begin{{document}}\n"
            "{inner}"
            "\\end{{document}}\n"
        )
        self.link_definitions.update(token.link_definitions)
        return template.format(
            inner=self.render_inner(token), packages=self.render_packages()
        )
