from unittest import TestCase, mock
from mistletoe.span_tokenizer import tokenize_span
from mistletoe.parse_context import get_parse_context
from contrib.github_wiki import GithubWiki, GithubWikiRenderer


class TestGithubWiki(TestCase):
    def setUp(self):
        self.renderer = GithubWikiRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_parse(self):
        MockRawText = mock.Mock(autospec="mistletoe.span_tokens.RawText")
        RawText = get_parse_context().span_tokens.pop()
        get_parse_context().span_tokens.append(MockRawText)
        try:
            tokens = tokenize_span("text with [[wiki | target]]")
            token = tokens[1]
            self.assertIsInstance(token, GithubWiki)
            self.assertEqual(token.target, "target")
            MockRawText.assert_has_calls([mock.call("text with "), mock.call("wiki")])
        finally:
            get_parse_context().span_tokens[-1] = RawText

    def test_render(self):
        token = next(iter(tokenize_span("[[wiki|target]]")))
        output = '<a href="target">wiki</a>'
        self.assertEqual(self.renderer.render(token), output)
