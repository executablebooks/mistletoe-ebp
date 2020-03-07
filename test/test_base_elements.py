from textwrap import dedent

from mistletoe import Document


def test_walk():
    doc = Document.read(
        dedent(
            """\
        a **b**

        c [*d*](link)
        """
        )
    )
    tree = [
        (t.node.name, t.parent.name if t.parent else None, t.depth)
        for t in doc.walk(include_self=True)
    ]
    assert tree == [
        ("Document", None, 0),
        ("Paragraph", "Document", 1),
        ("Paragraph", "Document", 1),
        ("RawText", "Paragraph", 2),
        ("Strong", "Paragraph", 2),
        ("RawText", "Paragraph", 2),
        ("Link", "Paragraph", 2),
        ("RawText", "Strong", 3),
        ("Emphasis", "Link", 3),
        ("RawText", "Emphasis", 4),
    ]
