from mistletoe.base_elements import serialize_tokens
from mistletoe.span_tokenizer import tokenize_span
from contrib.github_wiki import GithubWikiRenderer


def test_parse(data_regression):
    with GithubWikiRenderer():
        source = "text with [[wiki | target]]"
        data_regression.check(serialize_tokens(tokenize_span(source), as_dict=True))


def test_parse_with_children(data_regression):
    with GithubWikiRenderer():
        source = "[[*alt*|link]]"
        data_regression.check(serialize_tokens(tokenize_span(source), as_dict=True))


def test_render(file_regression):
    with GithubWikiRenderer() as renderer:
        token = tokenize_span("[[wiki|target]]")[0]
        file_regression.check(renderer.render(token), extension=".html")
