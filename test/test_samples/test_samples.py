import os

from mistletoe import markdown

PATH = os.path.dirname(__file__)


def test_syntax(file_regression):
    with open(os.path.join(PATH, "syntax.md")) as handle:
        file_regression.check(markdown(handle.read()), extension=".html")


def test_jquery(file_regression):
    with open(os.path.join(PATH, "jquery.md")) as handle:
        file_regression.check(markdown(handle.read()), extension=".html")
