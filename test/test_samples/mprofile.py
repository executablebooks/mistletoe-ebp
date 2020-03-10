import cProfile
import io
import pstats
from pathlib import Path

from mistletoe import markdown, renderers
from mistletoe.parse_context import ParseContext
import mistletoe

if __name__ == "__main__":

    text = Path(__file__).parent.joinpath("syntax.md").read_text()

    pr = cProfile.Profile()
    pr.enable()
    for _ in range(1000):
        markdown(
            text,
            parse_context=ParseContext(
                find_blocks=renderers.get_extended_block_tokens(),
                find_spans=renderers.get_extended_span_tokens(),
            ),
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
