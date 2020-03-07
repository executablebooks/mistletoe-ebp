import unittest
from unittest.mock import patch
from mistletoe import span_tokens
from mistletoe.span_tokenizer import tokenize_span
from mistletoe.parse_context import get_parse_context


class TestBranchToken(unittest.TestCase):
    def setUp(self):
        self.addCleanup(
            lambda: get_parse_context().span_tokens.__setitem__(-1, span_tokens.RawText)
        )
        patcher = patch("mistletoe.span_tokens.RawText")
        self.mock = patcher.start()
        get_parse_context().span_tokens[-1] = self.mock
        self.addCleanup(patcher.stop)

    def _test_parse(self, token_cls, raw, arg, **kwargs):
        token = next(iter(tokenize_span(raw)))
        self.assertIsInstance(token, token_cls)
        self._test_token(token, arg, **kwargs)

    def _test_token(self, token, arg, children=True, **kwargs):
        for attr, value in kwargs.items():
            self.assertEqual(getattr(token, attr), value)
        if children:
            self.mock.assert_any_call(arg)


class TestStrong(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_tokens.Strong, "**some text**", "some text")
        self._test_parse(span_tokens.Strong, "__some text__", "some text")


class TestEmphasis(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_tokens.Emphasis, "*some text*", "some text")
        self._test_parse(span_tokens.Emphasis, "_some text_", "some text")


class TestInlineCode(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_tokens.InlineCode, "`some text`", "some text")


class TestStrikethrough(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_tokens.Strikethrough, "~~some text~~", "some text")


class TestLink(TestBranchToken):
    def test_parse(self):
        self._test_parse(
            span_tokens.Link, "[name 1](target1)", "name 1", target="target1", title=""
        )

    def test_parse_multi_links(self):
        tokens = iter(tokenize_span("[n1](t1) & [n2](t2)"))
        self._test_token(next(tokens), "n1", target="t1")
        self._test_token(next(tokens), " & ", children=False)
        self._test_token(next(tokens), "n2", target="t2")

    def test_parse_children(self):
        token = next(iter(tokenize_span("[![alt](src)](target)")))
        child = next(iter(token.children))
        self._test_token(child, "alt", src="src")


class TestAutoLink(TestBranchToken):
    def test_parse(self):
        self._test_parse(
            span_tokens.AutoLink,
            "<ftp://foo.com>",
            "ftp://foo.com",
            target="ftp://foo.com",
        )


class TestImage(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_tokens.Image, "![alt](link)", "alt", src="link")
        self._test_parse(
            span_tokens.Image, '![alt](link "title")', "alt", src="link", title="title"
        )

    def test_no_alternative_text(self):
        self._test_parse(span_tokens.Image, "![](link)", "", children=False, src="link")


class TestEscapeSequence(TestBranchToken):
    def test_parse(self):
        self._test_parse(span_tokens.EscapeSequence, "\\*", "*")

    def test_parse_in_text(self):
        tokens = iter(tokenize_span("some \\*text*"))
        self._test_token(next(tokens), "some ", children=False)
        self._test_token(next(tokens), "*")
        self._test_token(next(tokens), "text*", children=False)


class TestRawText(unittest.TestCase):
    def test_attribute(self):
        token = span_tokens.RawText("some text")
        self.assertEqual(token.content, "some text")

    def test_no_children(self):
        token = span_tokens.RawText("some text")
        assert token.children is None


class TestLineBreak(unittest.TestCase):
    def test_parse(self):
        (token,) = tokenize_span("  \n")
        self.assertIsInstance(token, span_tokens.LineBreak)


class TestContains(unittest.TestCase):
    def test_contains(self):
        token = next(iter(tokenize_span("**with some *emphasis* text**")))
        self.assertTrue("text" in token)
        self.assertTrue("emphasis" in token)
        self.assertFalse("foo" in token)
