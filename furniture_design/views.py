"""Pictures of a piece for whoever draws its documents, each doing one thing, to scale, on a page of its own:
a view of the parts asked for, from the side asked for, pulled apart or not, lettered or not; a connector
at its size; a tool at work, as the instructions draw it. Nothing is kept and nothing is judged: a picture
is a part, which whoever draws a page places with marks of their own, or leaves out.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from . import linework as lw
from .natives import away
from .scene import Scene, connector_size
from .sheets import INK, MARK, NEW, SCALES, Pen, _boxes, _extent, _fit, _tone, draw_parts

# The sides a view is drawn from: three-quarter views from the front left (the instructions' own) and from
# the front right, both from above, and the flat views.
SIDES = {"front-left": lw.axonometric(-35.0, 28.0), "front-right": lw.axonometric(35.0, 28.0),
         "back-left": lw.axonometric(-145.0, 28.0), "back-right": lw.axonometric(145.0, 28.0),
         "front": lw.FRONT, "left": lw.LEFT, "top": lw.TOP}
PAGE = landscape(A4)
MARGIN = 12.0   # mm


def _scale(extent: tuple[float, float], room: tuple[float, float]) -> int:
    """The first of the drawings' scales (1:k) at which `extent` (mm) fits `room` (mm on paper)."""
    for k in SCALES:
        if extent[0] / k <= room[0] and extent[1] / k <= room[1]:
            return k
    k = SCALES[-1]
    while extent[0] / k > room[0] or extent[1] / k > room[1]:
        k *= 2
    return k


def view(sc: Scene, path: Path, parts: list[str] | None = None, side: str = "front-left", apart: float = 0.0,
         lettered: bool = True) -> dict:
    """Draw the parts `parts` (ids or paths; every part when empty) as seen from `side` (SIDES), each pulled
    `apart` mm away from the piece along the way it comes in when it is not said (natives.away), with its
    letter beside it when `lettered`, to the first of the drawings' scales it fits at, on one A4 landscape
    page written to `path`. Refused (ValueError) on a part or a side the piece does not have. Returns what was
    drawn: {side, scale "1:k", parts [{id, name, letter}], apart}."""
    if side not in SIDES:
        raise ValueError(f"no side {side!r}: one of {', '.join(SIDES)}")
    every = {p.id: p for p in sc.parts} | {p.path: p for p in sc.parts}
    unknown = [p for p in parts or [] if p not in every]
    if unknown:
        raise ValueError(f"no part {', '.join(map(repr, unknown))} in the piece: its parts are "
                         f"{', '.join(p.id for p in sc.parts)}")
    shown_ids = {every[p].id for p in parts} if parts else {p.id for p in sc.parts}
    shown = [p for p in sc.parts if p.id in shown_ids]   # in the piece's order
    offsets = {p.id: tuple(k * float(apart) for k in away(sc.lo, sc.hi, p.centre)) for p in shown} if apart else {}
    vw = SIDES[side]
    boxes = _boxes(shown, offsets)
    u0, v0, u1, v1 = _extent(boxes, vw)
    w, h = PAGE[0] / mm - 2 * MARGIN, PAGE[1] / mm - 2 * MARGIN - 10
    k = _scale((u1 - u0, v1 - v0), (w, h))
    c = Canvas(str(path), pagesize=PAGE)
    pen = Pen(c)
    placed = _fit(boxes, vw, MARGIN, MARGIN, w, h, scale=1 / k)
    draw_parts(pen, placed, shown, fill_for=lambda key, sh: _tone(sh, NEW), offsets=offsets, line=0.35)
    letters = []
    for p in shown:
        if not lettered or not p.mark or p.mark in letters:
            continue
        u, v = placed(tuple(a + b for a, b in zip(p.centre, offsets.get(p.id, (0, 0, 0)))))
        pen.circle(u + 5, v + 5, 3.2, fill=white, w=0.35)
        pen.text(u + 5, v + 3.8, p.mark, 3.6, INK, "middle", bold=True)
        letters.append(p.mark)
    pen.text(MARGIN, PAGE[1] / mm - MARGIN, f"{side}  1:{k}", 3.2, INK)
    c.showPage()
    c.save()
    return {"side": side, "scale": f"1:{k}", "apart": float(apart),
            "parts": [{"id": p.id, "name": p.name, **({"letter": p.mark} if p.mark else {})} for p in shown]}


def connector(tree, path: Path, connector_path: str, name: str = "") -> dict:
    """Draw a connector (a node of the knowledge, by its path) at its size, length by thickness, as the
    instructions mark one where it goes, at 2:1 with its size beside it, on one A4 landscape page written to
    `path`. Refused (ValueError) when the node states no length and thickness."""
    size = connector_size(tree, {"uses": [connector_path]})
    if size is None:
        raise ValueError(f"{connector_path} states no length and thickness to draw it at")
    length, thickness = size
    k = 2.0
    c = Canvas(str(path), pagesize=PAGE)
    pen = Pen(c)
    x, y = MARGIN + 10, PAGE[1] / mm / 2
    pen.rect(x, y, length * k, thickness * k, fill=MARK, stroke=INK)
    pen.text(x, y + thickness * k + 6, f"{name or connector_path}: {length:g} × {thickness:g} mm", 4, INK)
    pen.text(MARGIN, PAGE[1] / mm - MARGIN, "2:1", 3.2, INK)
    c.showPage()
    c.save()
    return {"connector": connector_path, "length": length, "thickness": thickness, "scale": "2:1"}
