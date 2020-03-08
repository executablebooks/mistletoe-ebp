import pytest

from mistletoe.base_elements import serialize_tokens
from mistletoe.block_tokenizer import tokenize_main
from contrib.scheme import Scheme


@pytest.mark.parametrize(
    "name,source",
    [
        ("basic", [" (lambda (arg) (+ arg 1)\n"]),
        ("operators", ['(or (and "zero" nil "never") "James")\n']),
    ],
)
def test_tokenize(name, source, data_regression):
    with Scheme():
        data_regression.check(
            serialize_tokens(tokenize_main(source), as_dict=True),
            basename=f"test_tokenize_{name}",
        )


@pytest.mark.parametrize(
    "name,source,result",
    [
        ("basic", ["(define x (* 2 21))\n", "x\n"], 42),
        ("operators", ["(or (and 1 and 0))\n"], False),
    ],
)
def test_render(name, source, result, file_regression):
    with Scheme() as renderer:
        token = tokenize_main(source)[0]
        assert renderer.render(token) == result
