from mistletoe import block_tokens, block_tokens_ext, span_tokens, span_tokens_ext


def get_commonmark_block_tokens():
    return (
        block_tokens.HTMLBlock,
        block_tokens.BlockCode,
        block_tokens.Heading,
        block_tokens.Quote,
        block_tokens.CodeFence,
        block_tokens.ThematicBreak,
        block_tokens.List,
        block_tokens.LinkDefinition,
        block_tokens.Paragraph,
    )


def get_commonmark_span_tokens():
    return (
        span_tokens.EscapeSequence,
        span_tokens.HTMLSpan,
        span_tokens.AutoLink,
        span_tokens.CoreTokens,
        span_tokens.InlineCode,
        span_tokens.LineBreak,
        span_tokens.RawText,
    )


def get_extended_block_tokens():
    return (
        block_tokens.HTMLBlock,
        block_tokens.BlockCode,
        block_tokens.Heading,
        block_tokens.Quote,
        block_tokens.CodeFence,
        block_tokens.ThematicBreak,
        block_tokens.List,
        block_tokens_ext.Table,
        block_tokens_ext.Footnote,
        block_tokens.LinkDefinition,
        block_tokens.Paragraph,
    )


def get_extended_span_tokens():
    return (
        span_tokens.EscapeSequence,
        span_tokens.HTMLSpan,
        span_tokens.AutoLink,
        span_tokens.CoreTokens,
        span_tokens_ext.FootReference,
        span_tokens_ext.Strikethrough,
        span_tokens_ext.Math,
        span_tokens.InlineCode,
        span_tokens.LineBreak,
        span_tokens.RawText,
    )
