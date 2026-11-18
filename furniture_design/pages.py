"""The assembly instructions as they were drawn, as nodes a standard can judge.

sheets.assembly_instructions notes, while it draws, where each picture is (Pen.note: the regions), what
a step's picture shows (the parts already there, the parts it brings in and of how many kinds, which
of them are drawn apart with a line to where they go, the joints it closes and those whose connectors
it draws, how much of each part is left to see) and every text it sets on a page (Pen.text: the
words). model() turns that record into a branch a tree mounts at instructions/<piece id>: one node of
kind page per page, holding its words, and under it a node of kind frame per picture.

Nothing here judges. What a page may carry and how much of a part must show are furniture-standards@'s
rules, resting on clauses of the knowledge; this module only measures what was drawn.
"""
from __future__ import annotations

from quern.tree import Node

from . import linework as lw

INSTRUCTIONS = "instructions"
# each document a piece's version is drawn as, by the key drawings.document makes it by, and the branch its
# record mounts under (model): the assembly instructions, the plans, the cutting sheet
DRAWN = {"assembly": INSTRUCTIONS, "design": "plans", "cutting": "cutting"}


def _paint(faces, keys, size, to_px):
    from PIL import Image, ImageDraw

    im = Image.new("I", size, 0)
    draw = ImageDraw.Draw(im)
    index = {k: i + 1 for i, k in enumerate(keys)}
    for f in faces:
        if f.key in index and len(f.points) >= 3:
            draw.polygon([to_px(p) for p in f.points], fill=index[f.key])
    return im, index


def shares(boxes: dict, view: lw.View, earlier: list[str], px: int = 320) -> tuple[dict[str, float], float]:
    """How much of each solid of a picture is left to see once all are drawn: for each key of `boxes`
    (sheets._boxes: the parts where the picture puts them), the share of what it would show alone
    that nothing in front of it covers; and the same for the solids in `earlier` taken together (1.0
    when there are none). Measured by painting the faces back to front, as the picture is drawn."""
    faces = lw.faces(boxes, view)
    pts = [p for f in faces for p in f.points]
    if not pts:
        return {}, 1.0
    u0, v0 = min(p[0] for p in pts), min(p[1] for p in pts)
    u1, v1 = max(p[0] for p in pts), max(p[1] for p in pts)
    s = (px - 1) / max(u1 - u0, v1 - v0, 1e-9)
    size = (int((u1 - u0) * s) + 2, int((v1 - v0) * s) + 2)
    to_px = lambda p: ((p[0] - u0) * s, (v1 - p[1]) * s)  # noqa: E731
    keys = list(boxes)
    import numpy as np

    together, index = _paint(faces, keys, size, to_px)
    final = np.asarray(together)
    left = {k: int((final == i).sum()) for k, i in index.items()}
    count = lambda im: int((np.asarray(im) > 0).sum())  # noqa: E731
    out = {}
    for k in keys:
        whole = count(_paint([f for f in faces if f.key == k], [k], size, to_px)[0])
        out[k] = round(left[k] / whole, 3) if whole else 0.0
    context = 1.0
    if earlier:
        whole = count(_paint([f for f in faces if f.key in earlier], [k for k in keys if k in earlier], size, to_px)[0])
        context = round(sum(left[k] for k in earlier if k in left) / whole, 3) if whole else 0.0
    return out, context


def model(piece_id: str, regions: list[dict], words: list[dict], branch: str = INSTRUCTIONS) -> Node:
    """A document as drawn, for a tree to mount under `branch` (DRAWN: instructions, plans or cutting): a
    node named as the piece, its pages in order (kind page, payload words: every text set on it, each
    {text, role?, off?: set beyond the paper, says?: what in the model it states}), and under each page its
    pictures (kind frame, payload: what the drawing noted of it, less where it is on the paper)."""
    pages: dict[int, Node] = {}

    def page(n: int) -> Node:
        if n not in pages:
            pages[n] = Node(id=f"page-{n + 1}", kind="page", payload={"number": n + 1, "words": []})
        return pages[n]

    for w in words:
        page(w["page"]).payload["words"].append({k: w[k] for k in ("text", "role", "off", "says") if k in w})
    for i, r in enumerate(regions):
        facts = {k: v for k, v in r.items() if k not in ("page", "box", "blank")}
        page(r["page"]).children.append(Node(id=f"frame-{i + 1}", kind="frame", payload=facts))
    return Node(id=branch, kind="", children=[
        Node(id=piece_id, kind="instructions" if branch == INSTRUCTIONS else "drawn",
             children=[pages[n] for n in sorted(pages)])])
