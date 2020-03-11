#!/usr/bin/env python
import argparse
from importlib import import_module
import os
import re
import sys
from time import perf_counter

from mistletoe import token_sets, parse_context

commonmark_context = parse_context.ParseContext(
    find_blocks=token_sets.get_commonmark_block_tokens(),
    find_spans=token_sets.get_commonmark_span_tokens(),
)
extended_context = parse_context.ParseContext(
    find_blocks=token_sets.get_extended_block_tokens(),
    find_spans=token_sets.get_extended_span_tokens(),
)


ALL_PACKAGES = (
    "markdown",
    "markdown:extra",
    "mistune",
    "commonmark",
    "mistletoe",
    "mistletoe:extra",
    "panflute",
)


def benchmark(package_name):
    def decorator(func):
        def inner(text, num_parses):
            try:
                package = import_module(package_name)
                try:
                    print("(" + (package.__version__) + ")", end=": ")
                except AttributeError:
                    print("(x.x.x)", end=": ")
            except ImportError:
                return "not available."
            start = perf_counter()
            for i in range(num_parses):
                func(package, text)
            end = perf_counter()

            return end - start

        return inner

    return decorator


@benchmark("markdown")
def run_markdown(package, text):
    return package.markdown(text)


@benchmark("markdown")
def run_markdown_extra(package, text):
    # https://python-markdown.github.io/extensions/#officially-supported-extensions
    return package.markdown(text, extensions=["extra"])


@benchmark("mistune")
def run_mistune(package, text):
    return package.markdown(text)


@benchmark("commonmark")
def run_commonmark(package, text):
    return package.commonmark(text)


@benchmark("mistletoe")
def run_mistletoe(package, text):
    return package.markdown(text, parse_context=commonmark_context)


@benchmark("mistletoe")
def run_mistletoe_extra(package, text):
    return package.markdown(text, parse_context=extended_context)


@benchmark("panflute")
def run_panflute(package, text):
    return package.convert_text(text, input_format="markdown", output_format="html")


def run_all(package_names, text, num_parses):
    prompt = "Running {} test(s) ...".format(len(package_names))
    print(prompt)
    print("=" * len(prompt))
    max_len = max(len(p) for p in package_names)
    for package_name in package_names:
        print(package_name + " " * (max_len - len(package_name)), end=" ")
        func_name = re.sub(r"[\.\-\:]", "_", package_name.lower())
        print(
            "{:.2f} s".format(globals()["run_{}".format(func_name)](text, num_parses))
        )
    return True


def main(args=None):
    parser = argparse.ArgumentParser(description="Run benchmark test.")
    parser.add_argument("path", type=str, help="the path to the file to parse")
    parser.add_argument(
        "-n",
        "--num-parses",
        metavar="NPARSES",
        default=1000,
        type=int,
        help="The number of parse iterations (default: 1000)",
    )
    parser.add_argument(
        "-p",
        dest="package",
        action="append",
        default=[],
        help="The package(s) to run (use -p multiple times).",
        choices=ALL_PACKAGES,
        # metavar="PACKAGE_NAME",
    )
    args = parser.parse_args(args)

    assert os.path.exists(args.path), "path does not exist"
    print("Test document: {}".format(os.path.basename(args.path)))
    print("Test iterations: {}".format(args.num_parses))
    with open(args.path, "r") as handle:
        text = handle.read()
    return run_all(args.package or ALL_PACKAGES, text, args.num_parses)


if __name__ == "__main__":
    main(sys.argv[1:])
