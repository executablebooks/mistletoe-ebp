import cProfile
import io
import pstats
from pathlib import Path

from mistletoe import markdown, renderers
import mistletoe

if __name__ == "__main__":

    extended_block_tokens = renderers.get_extended_block_tokens()
    extended_span_tokens = renderers.get_extended_span_tokens()

    text = Path(__file__).parent.joinpath("syntax.md").read_text()

    pr = cProfile.Profile()
    pr.enable()
    for _ in range(1000):
        markdown(
            text, find_blocks=extended_block_tokens, find_spans=extended_span_tokens
        )
    pr.disable()
    # pr.print_stats()
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    stats_string = s.getvalue()
    stats_string = "\n".join(stats_string.splitlines()[:100])
    # print([l.split(None, 6) for l in stats_string.splitlines() if l])
    stats_string = stats_string.replace(
        str(Path(mistletoe.__file__).parent), "mistletoe"
    )
    print(stats_string)
