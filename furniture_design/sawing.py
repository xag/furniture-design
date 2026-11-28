"""A part's cut, drawn to IKEA's rules as the grooving step is (grooving.py): no sentence, one action a frame,
the instructions' one viewpoint, the saw drawn from the model its tool node gives (payload model,
furniture_design.lineart.solids), a maker's saw that follows tools/crosscut-saw, whose method these frames draw, the details in close-up circles.

1, the marks, on the board as it stands in the step's picture: the cut's outline in pencil on the face seen,
its waste hatched on that face and on the edges it runs through (it goes through the board), its distances
from the edges it starts at in mm, each saw line numbered where it starts with a red arrow along it, the
way it is sawn.
2 to 4, the board laid on the bench, tipped back about its bottom edge so the same face stays up and left
and right stay where they were: 2, the saw's heel on the edge where the first line starts, its toe out past
that edge, a close-up of the thumb against the blade above the teeth and the saw drawn back; 3, the saw at
45 degrees to the face (a dashed line along the face, the angle between it and the teeth), pushed, a
close-up of the blade upright with a try square against it; 4, the saw near the end of the last line, a
hand holding the waste.

A saw tilted toward its toe touches the board only at an edge whose far side is open, so the toe points
out of the board past the edge the line starts at. Short instructions draw frame 1 only, over the whole
slot, as they leave the jointer at work out. The saw's sentences stay knowledge (its tool node's say) and
are not printed.
"""
from __future__ import annotations

import math

import numpy as np
from reportlab.lib.colors import Color, white
from reportlab.lib.units import mm

from . import lineart as la
from .grooving import SIDE, VIEW, WOOD, clip, closeup, frame, letter, proj, scene_box, side_spot
from .scene import Part, cut_plan
from .sheets import DIM, INK, MARK, _fmt

# The general hand saw whose method the frames draw: a saw is drawn at work only when it follows it, from
# its own model (its maker's package gives it, as lamello-unofficial gives the Zeta P2's).
SAW = "tools/crosscut-saw"
HAND = (1.0, 0.97, 0.93)
STEEL = Color(0.62, 0.64, 0.67)
LINE = 0.28


# --- the board, its cuts and its lines, as stood and as laid down ---------------------------------

class Face:
    """A board's face as drawn: 2D coordinates (a, b) on it, the map to 3D, the board's box in 3D, its
    cuts as 2D rectangles with their 3D boxes, and its saw lines in the order sawn (start, end, unit along,
    unit into the waste), the start at the board's edge when the line reaches one."""

    def __init__(self, size2, to3, box, cuts2, cuts3, lines):
        self.size2, self.to3, self.box, self.cuts2, self.cuts3, self.lines = size2, to3, box, cuts2, cuts3, lines

    def P(self, a, b):
        return self.to3(a, b)


def _lines2(p, plan, cut_lo2, cut_hi2, h, v):
    out = []
    for (a0, b0), (a1, b1) in plan.lines:
        q0, q1 = (a0 - p.lo[h], b0 - p.lo[v]), (a1 - p.lo[h], b1 - p.lo[v])
        out.append((q0, q1, cut_lo2, cut_hi2))
    return out


def _with_sides(raw):
    lines = []
    for q0, q1, lo, hi in raw:
        ux, uy = q1[0] - q0[0], q1[1] - q0[1]
        d = math.hypot(ux, uy) or 1
        u = (ux / d, uy / d)
        n = (-u[1], u[0])
        mid = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2)
        if (mid[0] - q0[0]) * n[0] + (mid[1] - q0[1]) * n[1] < 0:
            n = (-n[0], -n[1])
        lines.append((q0, q1, u, n))
    return lines


def _local(p: Part):
    """The board in its own place, from p.lo: its size, the thickness axis, the face axes (h, v) of the
    first cut's plan, the face seen (its coordinate along t), and each cut's box."""
    plan = cut_plan(p, *p.cuts[0])
    h, v, t = plan.h, plan.v, plan.t
    size = tuple(p.hi[i] - p.lo[i] for i in range(3))
    seen = 0.0 if VIEW.d[t] > 0 else size[t]           # the face whose normal looks toward the reader
    boxes = []
    for lo, hi in p.cuts:
        boxes.append((tuple(max(a, b) - c for a, b, c in zip(lo, p.lo, p.lo)),
                      tuple(min(a, b) - c for a, b, c in zip(hi, p.hi, p.lo)), cut_plan(p, lo, hi)))
    return plan, h, v, t, size, seen, boxes


def standing(p: Part) -> Face:
    """The board as it stands in the piece (the step's picture), drawn on the face seen."""
    plan, h, v, t, size, seen, boxes = _local(p)

    def to3(a, b):
        q = [0.0, 0.0, 0.0]
        q[h], q[v], q[t] = a, b, seen
        return tuple(q)
    cuts2 = [((lo[h], lo[v]), (hi[h], hi[v])) for lo, hi, _ in boxes]
    raw = []
    for (lo, hi, pl), (lo2, hi2) in zip(boxes, cuts2):
        raw += _lines2(p, pl, lo2, hi2, h, v)
    return Face((size[h], size[v]), to3, ((0, 0, 0), size), cuts2, [(lo, hi) for lo, hi, _ in boxes],
                _with_sides(raw))


def laid(p: Part) -> Face:
    """The board laid on the bench face up: tipped back about its bottom edge (a quarter turn about the
    horizontal axis in its face), so the face seen stays up and stays seen, left and right unchanged. A
    board already lying flat stays as it is."""
    plan, h, v, t, size, seen, boxes = _local(p)
    n = np.zeros(3)
    n[t] = -1.0 if seen == 0.0 else 1.0
    z = np.array([0.0, 0.0, 1.0])
    if t == 2:
        R = np.eye(3)
    else:
        a = np.zeros(3)
        a[1 - t if t in (0, 1) else 0] = 1.0           # the horizontal axis lying in the face
        R = np.column_stack([a, z, -n]) @ np.linalg.inv(np.column_stack([a, n, z]))
    corners = np.array([[x, y, w] for x in (0, size[0]) for y in (0, size[1]) for w in (0, size[2])])
    rc = corners @ R.T
    off = -rc.min(axis=0)
    dims = rc.max(axis=0) - rc.min(axis=0)

    def go(q):
        return np.asarray(q, float) @ R.T + off

    cuts3 = []
    for lo, hi, _ in boxes:
        c = np.array([[x, y, w] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for w in (lo[2], hi[2])])
        g = go(c)
        cuts3.append((tuple(g.min(axis=0)), tuple(g.max(axis=0))))
    cuts2 = [((lo[0], lo[1]), (hi[0], hi[1])) for lo, hi in cuts3]
    raw = []
    for (lo, hi, pl), (lo2, hi2) in zip(boxes, cuts2):
        for (a0, b0), (a1, b1) in pl.lines:
            q0 = [0.0, 0.0, 0.0]
            q1 = [0.0, 0.0, 0.0]
            q0[h], q0[v], q1[h], q1[v] = a0 - p.lo[h], b0 - p.lo[v], a1 - p.lo[h], b1 - p.lo[v]
            g0, g1 = go(q0), go(q1)
            raw.append(((g0[0], g0[1]), (g1[0], g1[1]), lo2, hi2))
    T = float(dims[2])
    return Face((float(dims[0]), float(dims[1])), lambda a, b: (a, b, T), ((0, 0, 0), tuple(dims)),
                cuts2, cuts3, _with_sides(raw))


def box_minus(lo, hi, clo, chi):
    """The box lo-hi less the box clo-chi, as boxes: slabs cut off along each axis in turn."""
    lo, hi = list(lo), list(hi)
    clo = [max(a, b) for a, b in zip(clo, lo)]
    chi = [min(a, b) for a, b in zip(chi, hi)]
    if any(clo[i] >= chi[i] for i in range(3)):
        return [(tuple(lo), tuple(hi))]
    out = []
    for i in range(3):
        if clo[i] > lo[i]:
            a, b = list(lo), list(hi)
            b[i] = clo[i]
            out.append((tuple(a), tuple(b)))
            lo[i] = clo[i]
        if chi[i] < hi[i]:
            a, b = list(lo), list(hi)
            a[i] = chi[i]
            out.append((tuple(a), tuple(b)))
            hi[i] = chi[i]
    return out


# --- the saw -------------------------------------------------------------------------------------

def _saw_axes(toe, angle):
    """The saw's axes for a cut whose toe points along the face's unit direction `toe`, tilted `angle`
    degrees down from the face: x across the blade, y heel to toe, z up from the teeth."""
    a = math.radians(angle)
    u3 = np.array([toe[0], toe[1], 0.0])
    up = np.array([0.0, 0.0, 1.0])
    ys = math.cos(a) * u3 - math.sin(a) * up
    zs = math.sin(a) * u3 + math.cos(a) * up
    return np.cross(ys, zs), ys, zs


def saw(model, at, toe, n, s, angle, t, side=0.6):
    """The saw's solids, its teeth crossing the face at `at` at its own y = s, its toe along `toe`, tilted
    `angle` degrees down, its blade `side` mm off the line into the waste (n)."""
    if not model:
        return []
    xs, ys, zs = _saw_axes(toe, angle)
    c = np.array([at[0], at[1], t]) + np.array([n[0], n[1], 0.0]) * side
    return la.placed(la.solids(model.get("parts", [])), np.column_stack([xs, ys, zs]), c - s * ys)


def _length(model) -> float:
    """The saw's toothed length, from its model's teeth (heel at its y = 0)."""
    return float(model["teeth"]["to"][0])


def _saw_ends(model, at, toe, s, angle, t):
    xs, ys, zs = _saw_axes(toe, angle)
    c = np.array([at[0], at[1], t])
    return [tuple(c - ys * (s + 140) + zs * 150), tuple(c + ys * min(_length(model) - s, 200)), tuple(c - ys * s)]


def _toe(p0, p1):
    ux, uy = p0[0] - p1[0], p0[1] - p1[1]
    d = math.hypot(ux, uy) or 1
    return ux / d, uy / d


# --- drawing -------------------------------------------------------------------------------------

def _scene(pen, b, meshes, focus, box=None):
    dr = la.draw(meshes, VIEW, px=1800)
    pts = [proj(q) for q in focus]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    sb = box or scene_box(b)
    clip(pen, *b)
    P, k = la.render(pen, dr, (sb[0] + 3, sb[1] + 3, sb[2] - 4, sb[3] - 9), line=LINE,
                     fit=(min(xs), min(ys), max(xs), max(ys)))
    pen.c.restoreState()
    return lambda q: P(*proj(q))


def _poly_fill(pen, poly, fill=None, stroke=INK, w=0.35, hatch=None, step=1.2):
    pen.c.saveState()
    path = pen.c.beginPath()
    path.moveTo(poly[0][0] * mm, poly[0][1] * mm)
    for q in poly[1:]:
        path.lineTo(q[0] * mm, q[1] * mm)
    path.close()
    if fill is not None:
        pen.c.setFillColor(fill)
    if stroke is not None:
        pen.c.setStrokeColor(stroke)
        pen.c.setLineWidth(w * mm)
    pen.c.drawPath(path, stroke=1 if stroke is not None else 0, fill=1 if fill is not None else 0)
    pen.c.restoreState()
    if hatch is not None:
        xs, ys = [q[0] for q in poly], [q[1] for q in poly]
        pen.c.saveState()
        path = pen.c.beginPath()
        path.moveTo(poly[0][0] * mm, poly[0][1] * mm)
        for q in poly[1:]:
            path.lineTo(q[0] * mm, q[1] * mm)
        path.close()
        pen.c.clipPath(path, stroke=0, fill=0)
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        k = x0 - (y1 - y0)
        while k < x1:
            pen.line(k, y0, k + (y1 - y0), y1, 0.12, hatch)
            k += step
        pen.c.restoreState()


def _waste_hatched(pen, W, face: Face):
    """The waste hatched on every face of it the reader sees that is the board's surface: the face, and
    the edges the cut runs through."""
    blo, bhi = face.box
    for lo, hi in face.cuts3:
        for i in range(3):
            for side, val in ((0, lo[i]), (1, hi[i])):
                on = (val <= blo[i] + 0.5) if side == 0 else (val >= bhi[i] - 0.5)
                normal = -1 if side == 0 else 1
                if not on or normal * VIEW.d[i] >= 0:
                    continue
                j, k = [a for a in range(3) if a != i]
                quad = []
                for a, b in ((lo[j], lo[k]), (hi[j], lo[k]), (hi[j], hi[k]), (lo[j], hi[k])):
                    q = [0.0, 0.0, 0.0]
                    q[i], q[j], q[k] = val, a, b
                    quad.append(W(q))
                _poly_fill(pen, quad, stroke=None, hatch=MARK)


def _pencil(pen, W, face: Face, sawn=0, upto=None):
    """The saw lines in pencil on the face, those already sawn as cuts; with `upto` the last one sawn that
    far."""
    blo, bhi = face.box
    for k, (p0, p1, u, n) in enumerate(face.lines):
        a, b = W(face.P(*p0)), W(face.P(*p1))
        pen.line(a[0], a[1], b[0], b[1], 0.9 if k < sawn else 0.45, INK)
        if upto is not None and k == len(face.lines) - 1:
            m = W(face.P(p0[0] + (p1[0] - p0[0]) * upto, p0[1] + (p1[1] - p0[1]) * upto))
            pen.line(a[0], a[1], m[0], m[1], 0.9, INK)


ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]


def _number(pen, at, k, r=2.6):
    """A cut's place in the order, in a red circle: I, II, ..., so the digits stay the step's and the
    frames'."""
    label = ROMAN[k - 1] if k <= len(ROMAN) else str(k)
    pen.circle(at[0], at[1], r, fill=MARK, stroke=MARK, w=0.2)
    pen.text(at[0], at[1] - r * 0.42, label, r * (1.15 if len(label) < 3 else 0.8), white, "middle", bold=True)


def _paper_dir(W, face, q, d):
    """The unit direction on paper of the face direction d at the face point q."""
    a, b = W(face.P(*q)), W(face.P(q[0] + d[0] * 10, q[1] + d[1] * 10))
    x, y = b[0] - a[0], b[1] - a[1]
    k = math.hypot(x, y) or 1
    return x / k, y / k


def _number_items(W, face: Face, only=None):
    """Where each saw line's number goes, just outside the edge it starts at, and its red arrow on the line from
    there, the way it is sawn."""
    out = []
    for k, (p0, p1, u, n) in enumerate(face.lines, 1):
        if only is not None and k not in only:
            continue
        d = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        ux, uy = _paper_dir(W, face, p0, u)
        a0 = W(face.P(*p0))
        b = W(face.P(p0[0] + u[0] * d * 0.6, p0[1] + u[1] * d * 0.6))
        out.append({"k": k, "a": (a0[0] - ux * 1.5, a0[1] - uy * 1.5), "b": b, "at": (a0[0] - ux * 5, a0[1] - uy * 5)})
    return out


def _draw_numbers(pen, items):
    for it in items:
        a, b = it["a"], it["b"]
        pen.line(a[0], a[1], b[0], b[1], 0.7, MARK)
        pen.arrowhead(b[0], b[1], b[0] - a[0], b[1] - a[1], 2.4, MARK)
        _number(pen, it["at"], it["k"])


def _numbers(pen, W, face: Face, only=None):
    """Each saw line's number and arrow (_number_items), drawn."""
    _draw_numbers(pen, _number_items(W, face, only))


TEXT = 3.2     # mm: a distance's size on paper
ROW = 7.0      # mm: between two dimension lines set off the same edge


def _meets(a, b, gap=0.0) -> bool:
    """Whether two boxes (x0, y0, x1, y1) on paper come within `gap` of each other."""
    return a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap


def _text_box(x, y, s, size, anchor):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    long = stringWidth(s, "Helvetica-Bold", size * mm) / mm
    x0 = x + {"start": 0.0, "middle": -long / 2, "end": -long}[anchor]
    return (x0, y - 0.2 * size, x0 + long, y + 0.72 * size)


def _spans(face: Face):
    """Each distance to dimension: (axis along, the other axis, the edge it is set off, start, end), each once,
    from the edges each cut starts at, the cuts' own order."""
    sz = face.size2
    out = []
    for (lo, hi) in face.cuts2:
        for i in (0, 1):
            o = 1 - i
            if lo[i] <= 0.5 and hi[i] >= sz[i] - 0.5:
                continue
            if hi[i] >= sz[i] - 0.5:
                spans = [(lo[i], sz[i])]
            elif lo[i] <= 0.5:
                spans = [(0.0, hi[i])]
            else:
                spans = [(0.0, lo[i]), (lo[i], hi[i])]
            near = lo[o] <= 0.5 or (hi[o] < sz[o] - 0.5 and lo[o] < sz[o] - hi[o])
            for a, b in spans:
                if not any(q[:3] == (i, o, near) and abs(q[3] - a) < 0.05 and abs(q[4] - b) < 0.05 for q in out):
                    out.append((i, o, near, a, b))
    return out


def _dim_items(W, face: Face, taken: list, gap=10.0):
    """The dimension lines of _spans on paper, each distance on its own line, the shortest nearest its edge,
    set off from the board by a fixed distance on paper, and where each one's text goes: beside its line, or,
    for a line that runs up the paper, past the outermost line of its edge; slid along the line until it meets
    no box of `taken` (which it joins)."""
    sz = face.size2
    spans = _spans(face)
    rows: dict = {}
    for q in sorted(spans, key=lambda q: q[4] - q[3]):
        rows.setdefault(q[1:3], []).append(q)
    items = []
    for (o, near), group in rows.items():
        for row, (i, _, _, start, end) in enumerate(group):
            edge = 0.0 if near else sz[o]

            def pt(x, y, i=i, o=o):
                q = [0.0, 0.0]
                q[i], q[o] = x, y
                return q
            out = [0.0, 0.0]
            out[o] = -1.0 if near else 1.0
            ea, eb = W(face.P(*pt(start, edge))), W(face.P(*pt(end, edge)))
            dx, dy = eb[0] - ea[0], eb[1] - ea[1]
            k_ = math.hypot(dx, dy) or 1
            ox, oy = -dy / k_, dx / k_                     # square to the dimension, on paper
            fx, fy = _paper_dir(W, face, pt(start, edge), out)
            if ox * fx + oy * fy < 0:                      # away from the board
                ox, oy = -ox, -oy
            off = gap + row * ROW
            pa, pb = (ea[0] + ox * off, ea[1] + oy * off), (eb[0] + ox * off, eb[1] + oy * off)
            vx, vy = dx / k_, dy / k_
            label = f"{_fmt(end - start)} mm"
            upright = abs(ox) >= 0.5                        # the line runs up the paper: the text beside it
            if upright:
                anchor = "start" if ox > 0 else "end"
                d = gap + len(group) * ROW - ROW + 3.0
            else:
                anchor = "middle"
                d = off + 4.0
            mid = ((ea[0] + eb[0]) / 2, (ea[1] + eb[1]) / 2)
            box = None
            for t in [0.0] + [s_ * k * 3.0 for k in range(1, 16) for s_ in (1, -1)]:
                x, y = mid[0] + ox * d + vx * t, mid[1] + oy * d + vy * t - 1.2
                cand = _text_box(x, y, label, TEXT, anchor)
                if not any(_meets(cand, b, 0.6) for b in taken):
                    box = cand
                    break
            if box is None:
                x, y = mid[0] + ox * d, mid[1] + oy * d - 1.2
                box = _text_box(x, y, label, TEXT, anchor)
            taken.append(box)
            items.append({"ea": ea, "eb": eb, "pa": pa, "pb": pb, "o": (ox, oy), "off": off,
                          "text": (x, y, label, anchor), "box": box})
    return items


def _draw_dims(pen, items):
    for it in items:
        pa, pb, (ox, oy), off = it["pa"], it["pb"], it["o"], it["off"]
        L_ = math.hypot(pb[0] - pa[0], pb[1] - pa[1]) or 1
        vx, vy = (pb[0] - pa[0]) / L_, (pb[1] - pa[1]) / L_
        if L_ >= 9:
            pen.line(pa[0], pa[1], pb[0], pb[1], 0.2, DIM)
            pen.arrowhead(pa[0], pa[1], -vx, -vy, 1.8, DIM)
            pen.arrowhead(pb[0], pb[1], vx, vy, 1.8, DIM)
        else:                   # too short for arrows inside: outside, pointing in
            pen.line(pa[0] - vx * 7, pa[1] - vy * 7, pb[0] + vx * 7, pb[1] + vy * 7, 0.2, DIM)
            pen.arrowhead(pa[0], pa[1], vx, vy, 1.8, DIM)
            pen.arrowhead(pb[0], pb[1], -vx, -vy, 1.8, DIM)
        for e in (it["ea"], it["eb"]):
            pen.line(e[0] + ox * 1.0, e[1] + oy * 1.0, e[0] + ox * (off + 1.8), e[1] + oy * (off + 1.8), 0.12, DIM)
        x, y, label, anchor = it["text"]
        pen.text(x, y, label, TEXT, DIM, anchor, bold=True)


def _dims(pen, W, face: Face, gap=10.0):
    """Each cut's distances from the edges it starts at, in mm (_dim_items), drawn."""
    _draw_dims(pen, _dim_items(W, face, [], gap))


def _region3(face: Face, share=0.5, least=40.0, room=50.0):
    """3D points round the cuts on the face, with room for the dimensions off the board."""
    lo = [min(c[0][i] for c in face.cuts2) for i in range(2)]
    hi = [max(c[1][i] for c in face.cuts2) for i in range(2)]
    pad = max(least, share * max(hi[0] - lo[0], hi[1] - lo[1]))
    a0 = [max(-room, lo[i] - pad) for i in range(2)]
    a1 = [min(face.size2[i] + room, hi[i] + pad) for i in range(2)]
    out = []
    for x in (a0[0], a1[0]):
        for y in (a0[1], a1[1]):
            q = np.array(face.P(x, y), float)
            out.append(tuple(q))
            blo, bhi = face.box
            q2 = q.copy()
            thick = [i for i in range(3) if bhi[i] - blo[i] == min(bhi[j] - blo[j] for j in range(3))][0]
            q2[thick] = bhi[thick] - q[thick]
            out.append(tuple(q2))
    return out


def _board(face: Face, cut=False):
    lo, hi = face.box
    if not cut:
        return [la.box(lo, hi, fill=WOOD)]
    boxes = [(lo, hi)]
    for clo, chi in face.cuts3:
        nb = []
        for blo, bhi in boxes:
            nb += box_minus(blo, bhi, clo, chi)
        boxes = nb
    return [la.box(a, b, fill=WOOD) for a, b in boxes]


# --- the hand, drawn flat as IKEA draws one --------------------------------------------------------

def _rounded(x0, y0, x1, y1, r, seg=5):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def hand_outline():
    """A right hand seen from above, palm down, fingers along +x from the wrist at the origin, mm: the
    shapes drawn back to front (the thumb and fingers, then the palm over their roots, the nails)."""
    shapes = []
    th = _rounded(0, -11, 58, 11, 10)
    c, s = math.cos(math.radians(38)), math.sin(math.radians(38))
    shapes.append([(18 + x * c - y * s, 36 + x * s + y * c) for x, y in th])
    for y, w, L in ((-30, 15, 48), (-11, 17, 60), (8, 18, 66), (27, 17, 58)):
        shapes.append(_rounded(55, y - w / 2, 55 + L, y + w / 2, w / 2 - 0.5))
    shapes.append(_rounded(0, -38, 72, 38, 16))
    return shapes


def draw_hand(pen, W, at, toward, z):
    """The hand laid on the face at `at`, fingers along `toward` (a unit x-y vector), drawn as outlines
    over the scene."""
    c, s = toward
    for shape in hand_outline():
        pts = [W((at[0] + x * c - y * s, at[1] + x * s + y * c, z)) for x, y in shape]
        _poly_fill(pen, pts, fill=Color(*HAND), stroke=INK, w=0.35)


# --- the close-ups -------------------------------------------------------------------------------

def _teeth(pen, x0, y0, x1, y1, pitch=1.4, depth=1.0):
    dx, dy = x1 - x0, y1 - y0
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    nx, ny = uy, -ux
    pts = []
    k = 0.0
    while k <= d:
        pts.append((x0 + ux * k, y0 + uy * k))
        pts.append((x0 + ux * (k + pitch / 2) + nx * depth, y0 + uy * (k + pitch / 2) + ny * depth))
        k += pitch
    for (a, b), (c_, d_) in zip(pts, pts[1:]):
        pen.line(a, b, c_, d_, 0.2, INK)


def _start_inside(pen, cx, cy, r):
    """Seen from the side, across the blade: the board's edge, the saw's heel teeth on its corner at a low
    angle, the toe down past it; the thumb's tip against the blade well above the teeth; drawn back."""
    t_ = r * 0.45
    top = cy - r * 0.08
    ex = cx + r * 0.25
    pen.rect(cx - r, top - t_, ex - (cx - r), t_, fill=Color(*WOOD), stroke=INK, lw_=0.35)
    a = math.radians(22)
    ux, uy = -math.cos(a), math.sin(a)
    nx, ny = uy, -ux
    corner = (ex, top)
    p0 = (corner[0] - ux * r * 0.9, corner[1] - uy * r * 0.9)
    p1 = (corner[0] + ux * r * 1.6, corner[1] + uy * r * 1.6)
    blade_h = r * 0.55
    q1 = (p1[0] + nx * blade_h, p1[1] + ny * blade_h)
    q0 = (p0[0] + nx * blade_h * 0.8, p0[1] + ny * blade_h * 0.8)
    pen.poly([p0, p1, q1, q0], fill=STEEL, stroke=INK)
    _teeth(pen, p1[0], p1[1], p0[0], p0[1])
    w2 = r * 0.17
    tip = (corner[0] + ux * r * 0.15 + nx * blade_h * 0.62, corner[1] + uy * r * 0.15 + ny * blade_h * 0.62)
    ang = math.degrees(math.atan2(uy, ux))
    pen.c.saveState()
    pen.c.translate(tip[0] * mm, tip[1] * mm)
    pen.c.rotate(ang)
    pen.c.setFillColor(Color(*HAND))
    pen.c.setStrokeColor(INK)
    pen.c.setLineWidth(0.35 * mm)
    pen.c.roundRect(0, -w2 * mm, r * 1.4 * mm, 2 * w2 * mm, w2 * mm, stroke=1, fill=1)
    pen.c.setLineWidth(0.25 * mm)
    pen.c.roundRect(r * 0.05 * mm, -w2 * 0.6 * mm, r * 0.32 * mm, w2 * 1.2 * mm, w2 * 0.45 * mm, stroke=1, fill=0)
    pen.c.restoreState()
    s0 = (corner[0] + ux * r * 0.1 + nx * (blade_h + 2.2), corner[1] + uy * r * 0.1 + ny * (blade_h + 2.2))
    s1 = (s0[0] + ux * r * 0.6, s0[1] + uy * r * 0.6)
    pen.line(s0[0], s0[1], s1[0], s1[1], 0.6, INK)
    pen.arrowhead(s1[0], s1[1], ux, uy, 2.0)


def _square_inside(pen, cx, cy, r):
    """Looking along the line: the board in section, the blade upright in its cut, the right angle between
    them marked on each side."""
    t_ = r * 0.5
    top = cy - r * 0.2
    pen.rect(cx - r, top - t_, 2 * r, t_, fill=Color(*WOOD), stroke=INK, lw_=0.35)
    pen.rect(cx - 0.7, top - t_ * 0.5, 1.4, r * 1.3, fill=STEEL, stroke=INK, lw_=0.25)
    q = 3.0
    for sgn in (-1, 1):
        x0 = cx + sgn * 0.7
        pen.line(x0 + sgn * q, top, x0 + sgn * q, top + q, 0.35, DIM)
        pen.line(x0, top + q, x0 + sgn * q, top + q, 0.35, DIM)


def _letter_at(W, face: Face):
    """Where the part's letter goes on the board, on paper: away from the cut."""
    lo = [min(c[0][i] for c in face.cuts2) for i in range(2)]
    hi = [max(c[1][i] for c in face.cuts2) for i in range(2)]
    cm = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2)
    spot = (face.size2[0] - cm[0], face.size2[1] - cm[1])
    reach = max(hi[0] - lo[0], hi[1] - lo[1]) * 1.1 + 40
    d = math.hypot(spot[0] - cm[0], spot[1] - cm[1]) or 1
    lx = cm[0] + (spot[0] - cm[0]) / d * reach
    ly = cm[1] + (spot[1] - cm[1]) / d * reach
    return W(face.P(min(max(lx, 20), face.size2[0] - 20), min(max(ly, 20), face.size2[1] - 20)))


def _letter_far(pen, W, face: Face, mark):
    """The part's letter on the board, away from the cut."""
    letter(pen, _letter_at(W, face), mark)


def _side_inside(pen, cx, cy, r, ang, waste_up, right):
    """Looking down on a line: the pencil line across, the waste hatched on its side, the saw's blade drawn
    wide beside the line: in the waste (right), or on the wood kept (wrong, crossed out)."""
    pen.c.saveState()
    pen.c.translate(cx * mm, cy * mm)
    pen.c.rotate(ang)
    sgn = 1 if waste_up else -1
    pen.rect(-r, -r, 2 * r, 2 * r, fill=Color(*WOOD), stroke=None)
    _poly_fill(pen, [(-r, 0), (r, 0), (r, sgn * r), (-r, sgn * r)], stroke=None, hatch=MARK, step=0.9)
    k = r * 0.38
    side = sgn if right else -sgn
    y0 = 0.0 if side > 0 else -k
    pen.rect(-r, y0, 2 * r, k, fill=STEEL, stroke=INK, lw_=0.35)
    pen.line(-r, 0, r, 0, 0.7, INK)
    pen.c.restoreState()
    if not right:
        q = r * 0.62
        pen.line(cx - q, cy - q, cx + q, cy + q, 1.2, MARK)
        pen.line(cx - q, cy + q, cx + q, cy - q, 1.2, MARK)


def _about(pen, x, y, value, size):
    """'about' and a value, centred at x: the sign drawn as two tildes, as the font has no approximately-equal
    sign."""
    w = size * 0.55 * (len(value) + 1.2)
    x0 = x - w / 2
    pen.text(x0, y + size * 0.16, '~', size, DIM, bold=True)
    pen.text(x0, y - size * 0.16, '~', size, DIM, bold=True)
    pen.text(x0 + size * 0.75, y, value, size, DIM, bold=True)


# --- the frames ----------------------------------------------------------------------------------

def _covers(box, other, axis, lo, hi) -> bool:
    """Whether `other` (a 3D box) takes away all of `box` between lo and hi along `axis`, over box's extent on
    the other two axes."""
    return all(other[0][i] <= box[0][i] + 0.05 and other[1][i] >= box[1][i] - 0.05 for i in range(3) if i != axis) \
        and other[0][axis] <= lo + 0.05 and other[1][axis] >= hi - 0.05


def sections(p: Part) -> list[dict]:
    """The board's end in section where cuts that do not go through it reach that end, one section per end
    whose profile differs: `along` the face axis (0 h, 1 v) the cuts run along, `ends` the ends of that axis (0
    its low end, 1 its high end) that show this profile, `A` the board across, `T` its thickness, `rects` each cut seen there (a0, a1, t0, t1), and
    `steps`: the profile, each stretch across (a0, a1) with the face it is open on (0 or T) and its depth from
    that face, the depth a pass is set to. A cut whose side away from a face opens onto an earlier cut is as
    deep as both."""
    plan, h, v, t, size, seen, boxes = _local(p)
    T = size[t]
    deep = [(lo, hi) for lo, hi, _ in boxes if not (lo[t] <= 0.05 and hi[t] >= T - 0.05)]
    if not deep:
        return []
    every = [(lo, hi) for lo, hi, _ in boxes]
    spans = [sum(1 for lo, hi in deep if lo[ax] <= 0.05 and hi[ax] >= size[ax] - 0.05) for ax in (h, v)]
    out = []
    for along in ((1, 0) if spans[1] >= spans[0] else (0, 1)):   # first along the axis most of them run the length of
        A_ax, L_ax = (h, v)[1 - along], (h, v)[along]
        for end in (0, 1):
            at = 0.0 if end == 0 else size[L_ax]
            here = [(lo, hi) for lo, hi in deep if (lo[L_ax] <= 0.05 if end == 0 else hi[L_ax] >= size[L_ax] - 0.05)]
            if not here:
                continue
            cuts = [(lo[A_ax], hi[A_ax], lo[t], hi[t]) for lo, hi in here]
            edges = sorted({0.0, size[A_ax], *[c[0] for c in cuts], *[c[1] for c in cuts]})
            steps = []
            for a0, a1 in zip(edges, edges[1:]):
                if a1 - a0 < 0.05:
                    continue
                over = [c for c in cuts if c[0] <= (a0 + a1) / 2 <= c[1]]
                if not over:
                    continue
                t0, t1 = min(c[2] for c in over), max(c[3] for c in over)
                lo_b, hi_b = [0.0] * 3, [0.0] * 3
                lo_b[A_ax], hi_b[A_ax] = a0, a1
                lo_b[L_ax] = hi_b[L_ax] = at
                lo_b[t], hi_b[t] = t0, t1
                box = (tuple(lo_b), tuple(hi_b))
                if t1 >= T - 0.05 or any(_covers(box, c, t, t1, T) for c in every):
                    side, depth = T, T - t0
                elif t0 <= 0.05 or any(_covers(box, c, t, 0.0, t0) for c in every):
                    side, depth = 0.0, t1
                else:
                    side, depth = T, t1 - t0
                if steps and abs(steps[-1][1] - a0) < 0.05 and steps[-1][2] == side and abs(steps[-1][3] - depth) < 0.05:
                    steps[-1] = (steps[-1][0], a1, side, depth)
                else:
                    steps.append((a0, a1, side, depth))
            same = next((o for o in out if o["steps"] == steps), None)
            if same:
                same["ends"].append(end)
            elif steps:
                out.append({"along": along, "ends": [end], "A": size[A_ax], "T": T, "rects": cuts, "steps": steps})
        if out:
            return out
    return out


def _section_panel(pen, box, sec, spot) -> float:
    """A section of the board's end in `box` (x, y, w, h on paper), drawn from its top down: the board across, the
    face its cuts are open on up, the cuts hatched, each step of the profile with its depth from that face; a
    line from it to `spot`, the end on the board. Returns the height it took."""
    x, y, w, h = box
    T, A = sec["T"], sec["A"]
    a_lo = min(s_[0] for s_ in sec["steps"])
    a_hi = max(s_[1] for s_ in sec["steps"])
    m = max(6.0, 0.3 * (a_hi - a_lo))
    w0, w1 = max(0.0, a_lo - m), min(A, a_hi + m)
    k = min((w - 2) / ((w1 - w0) or 1), 12.0 / T)
    up = sec["steps"][0][2]                                 # the face the cuts are open on, drawn up
    texts: list = []
    labels = []
    for a0, a1, side, depth in sec["steps"]:
        cx = x + 1 + ((a0 + a1) / 2 - w0) * k
        label = f"{_fmt(depth)} mm"
        for r in range(6):
            ty = y + h - 3.0 - r * 3.6
            bx = _text_box(cx, ty, label, 2.6, "middle")
            shift = max(0.0, x - bx[0]) - max(0.0, bx[2] - (x + w))
            bx = (bx[0] + shift, bx[1], bx[2] + shift, bx[3])
            if not any(_meets(bx, o, 0.5) for o in texts):
                break
        texts.append(bx)
        labels.append((cx, cx + shift, ty, label, depth))
    top = min(bx[1] for bx in texts) - 1.5                 # the open face, under the lowest text
    bottom = top - T * k

    def Y(tt):                                              # a point of the thickness, the open face up
        return top - (T - tt if up == T else tt) * k
    pen.rect(x + 1, bottom, (w1 - w0) * k, T * k, fill=Color(*WOOD), stroke=INK, lw_=0.3)
    for a0, a1, t0, t1 in sec["rects"]:
        c0, c1 = max(a0, w0), min(a1, w1)
        if c1 <= c0:
            continue
        ya, yb = Y(t0), Y(t1)
        _poly_fill(pen, [(x + 1 + (c0 - w0) * k, ya), (x + 1 + (c1 - w0) * k, ya), (x + 1 + (c1 - w0) * k, yb),
                         (x + 1 + (c0 - w0) * k, yb)], fill=white, stroke=INK, w=0.25, hatch=MARK, step=0.8)
    for end, at in ((w0, x + 1), (w1, x + 1 + (w1 - w0) * k)):     # the board goes on past the section
        if 0.05 < end < A - 0.05:
            pen.line(at, bottom - 0.8, at, top + 0.8, 0.5, white)
            pen.line(at, bottom - 0.8, at, top + 0.8, 0.2, INK, [0.8, 0.6])
    for cx, tx, ty, label, depth in labels:
        y1 = top - depth * k
        pen.line(cx, y1, cx, ty + 2.0, 0.18, DIM)
        pen.arrowhead(cx, y1, 0, -1, 1.2, DIM)
        pen.arrowhead(cx, top, 0, 1, 1.2, DIM)
        pen.text(tx, ty, label, 2.6, DIM, "middle", bold=True)
    mid = (x + 1, (top + bottom) / 2)
    pen.line(mid[0], mid[1], spot[0], spot[1], 0.15, INK, [1.0, 0.8])
    pen.circle(spot[0], spot[1], 0.7, fill=INK, stroke=INK, w=0.1)
    return y + h - bottom + 2


def _marks_layout(W, face: Face) -> dict:
    """The numbers, the letter and the distances of the marks frame on paper, each text clear of the others,
    and the box they take together with the board's region drawn."""
    nums = _number_items(W, face)
    taken = [(it["at"][0] - 2.6, it["at"][1] - 2.6, it["at"][0] + 2.6, it["at"][1] + 2.6) for it in nums]
    at = _letter_at(W, face)
    taken.append((at[0] - 3.4, at[1] - 3.4, at[0] + 3.4, at[1] + 3.4))
    dims = _dim_items(W, face, taken)
    pts = [q for b in taken for q in ((b[0], b[1]), (b[2], b[3]))]
    for it in nums:
        pts += [it["a"], it["b"]]
    for it in dims:
        ox, oy = it["o"]
        pts += [it["pa"], it["pb"]] + [(e[0] + ox * (it["off"] + 1.8), e[1] + oy * (it["off"] + 1.8))
                                       for e in (it["ea"], it["eb"])]
        if math.hypot(it["pb"][0] - it["pa"][0], it["pb"][1] - it["pa"][1]) < 9:
            v = ((it["pb"][0] - it["pa"][0]), (it["pb"][1] - it["pa"][1]))
            L_ = math.hypot(*v) or 1
            pts += [(it["pa"][0] - v[0] / L_ * 7, it["pa"][1] - v[1] / L_ * 7),
                    (it["pb"][0] + v[0] / L_ * 7, it["pb"][1] + v[1] / L_ * 7)]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    return {"nums": nums, "letter": at, "dims": dims, "bbox": (min(xs), min(ys), max(xs), max(ys))}


def _fit_marks(face: Face, focus, area):
    """The scale and place of the board in `area` (x, y, w, h on paper) so that its region `focus` (3D points)
    and every mark set round it fit: the marks stand at fixed distances on paper, so the room they take is
    found by laying them out and the board scaled into what is left. Returns the world -> paper map, the scale,
    the drawing's bounds fitted, the board region's corner on paper, and the layout (_marks_layout)."""
    pts = [proj(q) for q in focus]
    x0, y0, x1, y1 = min(q[0] for q in pts), min(q[1] for q in pts), max(q[0] for q in pts), max(q[1] for q in pts)
    dx, dy = (x1 - x0) or 1.0, (y1 - y0) or 1.0
    ax, ay, aw, ah = area
    extra = [0.0, 0.0, 0.0, 0.0]          # room the marks take beyond the region: left, bottom, right, top
    for _ in range(8):
        k = max(1e-4, min((aw - extra[0] - extra[2]) / dx, (ah - extra[1] - extra[3]) / dy))
        ox = ax + extra[0] + (aw - extra[0] - extra[2] - dx * k) / 2
        oy = ay + extra[1] + (ah - extra[1] - extra[3] - dy * k) / 2

        def W(q, ox=ox, oy=oy, k=k):
            u, v = proj(q)
            return ox + (u - x0) * k, oy + (v - y0) * k
        marks = _marks_layout(W, face)
        bb = marks["bbox"]
        took = [max(0.0, ox - bb[0]), max(0.0, oy - bb[1]), max(0.0, bb[2] - ox - dx * k), max(0.0, bb[3] - oy - dy * k)]
        if all(abs(a - b) < 0.2 for a, b in zip(took, extra)):
            break
        extra = [max(a, b) for a, b in zip(took, extra)]
    return W, k, (x0, y0, x1, y1), (ox, oy), marks


def f_marks(pen, b, p: Part, qty: int, box=None, sides=True):
    """The board as it stands in the step's picture, its cut marked, its waste hatched, scaled so that every mark
    and distance set round it is inside the frame; with `sides`, two close-ups: the blade in the waste beside
    the line, and on the side kept, crossed out."""
    face = standing(p)
    sb = box or scene_box(b)
    W, k, fit, (ox, oy), marks = _fit_marks(face, _region3(face, share=0.6, least=60, room=0),
                                            (sb[0] + 3, sb[1] + 3, sb[2] - 4, sb[3] - 9))
    dr = la.draw(_board(face), VIEW, px=1800)
    clip(pen, *b)
    la.render(pen, dr, (ox, oy, (fit[2] - fit[0]) * k, (fit[3] - fit[1]) * k), line=LINE, pad=0, scale=k, fit=fit)
    pen.c.restoreState()
    clip(pen, *b)
    _waste_hatched(pen, W, face)
    _pencil(pen, W, face)
    _draw_dims(pen, marks["dims"])
    _draw_numbers(pen, marks["nums"])
    letter(pen, marks["letter"], p.mark)
    pen.c.restoreState()
    top = b[1] + b[3] - (36 if sides else 9)
    ends = []
    for sec in sections(p):   # an end that shows it, the one nearest the side column
        spots = []
        for end in sec["ends"]:
            pt = [0.0, 0.0]
            pt[sec["along"]] = 0.0 if end == 0 else face.size2[sec["along"]]
            pt[1 - sec["along"]] = (sec["steps"][0][0] + sec["steps"][-1][1]) / 2
            spots.append(W(face.P(*pt)))
        ends.append((max(spots, key=lambda q: q[0]), sec))
    for spot, sec in sorted(ends, key=lambda e: -e[0][1]):   # down the side column, the higher end first
        top -= _section_panel(pen, (b[0] + b[2] - SIDE + 1, b[1], SIDE - 2, top - b[1]), sec, spot) + 2
    if sides:
        p0, p1, u, n = face.lines[0]
        ux, uy = _paper_dir(W, face, p0, u)
        nx, ny = _paper_dir(W, face, p0, n)
        ang = math.degrees(math.atan2(uy, ux))
        waste_up = (-uy * nx + ux * ny) > 0          # the waste on the left of the line's direction on paper
        mid = W(face.P(p0[0] + (p1[0] - p0[0]) * 0.5, p0[1] + (p1[1] - p0[1]) * 0.5))
        for k, right in ((0, True),) + (() if sections(p) else ((1, False),)):   # the sections take the second's place
            closeup(pen, side_spot(b, k), 10.0, mid,
                    lambda cx, cy, r, right=right: _side_inside(pen, cx, cy, r, ang, waste_up, right))
    elif qty > 1:
        cx, cy = side_spot(b)
        pen.text(cx, b[1] + 6, f"{qty} ×", 5, INK, "middle", bold=True)


def f_start(pen, b, p: Part, model):
    """Laid down: the saw's heel on the edge where the first line starts, its toe out past it; a close-up of
    that spot, magnified in the same view: the thumb against the blade above the teeth, the saw drawn back
    toward the heel."""
    face = laid(p)
    p0, p1, u, n = face.lines[0]
    toe = _toe(p0, p1)
    t = face.box[1][2]
    s, angle = 40.0, 24.0
    meshes = _board(face) + saw(model, p0, toe, n, s, angle, t)
    W = _scene(pen, b, meshes, _region3(face, share=0.3, least=40, room=30) + _saw_ends(model, p0, toe, s, angle, t))
    clip(pen, *b)
    _pencil(pen, W, face)
    _numbers(pen, W, face, only=[1])
    _letter_far(pen, W, face, p.mark)
    pen.c.restoreState()
    xs, ys, zs = _saw_axes(toe, angle)
    c = np.array([p0[0], p0[1], t])

    def pdir(v):
        a_, b_ = W(tuple(c)), W(tuple(c + np.asarray(v) * 50))
        x, y = b_[0] - a_[0], b_[1] - a_[1]
        k = math.hypot(x, y) or 1
        return x / k, y / k
    eu = pdir(ys)                                        # along the blade, toward the toe, on paper
    ez = pdir(zs)                                        # up from the teeth, on paper
    ef = pdir((toe[0], toe[1], 0.0))                     # along the face, out past the edge
    ed = pdir((0.0, 0.0, -1.0))                          # down
    mirror = (eu[0] * ez[1] - eu[1] * ez[0]) < 0

    def inside(cx, cy, r):
        """Seen across the blade, turned as the frame is: the board's corner, the blade's heel on it, its
        teeth below; the thumb lying on the blade above the teeth; the saw drawn back toward the heel."""
        ang = math.degrees(math.atan2(eu[1], eu[0]))

        def local(v):                                     # a paper direction in the turned frame
            x = v[0] * eu[0] + v[1] * eu[1]
            y = -v[0] * eu[1] + v[1] * eu[0]
            return x, (-y if mirror else y)
        lf, ld = local(ef), local(ed)
        pen.c.saveState()
        pen.c.translate(cx * mm, cy * mm)
        pen.c.rotate(ang)
        if mirror:
            pen.c.scale(1, -1)
        # the board: its top face from the corner back under the heel, its edge down
        q = 2.2 * r
        board = [(0, 0), (-lf[0] * q, -lf[1] * q), (-lf[0] * q + ld[0] * q * 0.4, -lf[1] * q + ld[1] * q * 0.4),
                 (ld[0] * q * 0.4, ld[1] * q * 0.4)]
        _poly_fill(pen, board, fill=Color(*WOOD), stroke=INK, w=0.35)
        # the blade, from its heel (x < 0) toward its toe, teeth on its lower edge through the corner; the
        # handle on the heel end, its cheek over the blade
        h_ = r * 0.42
        heel = -0.62 * r
        pen.poly([(heel, 0), (2 * r, 0), (2 * r, h_ * 0.85), (heel, h_)], fill=STEEL, stroke=INK)
        _teeth(pen, 2 * r, 0, heel, 0)
        pen.c.setFillColor(white)
        pen.c.setStrokeColor(INK)
        pen.c.setLineWidth(0.45 * mm)
        pen.c.roundRect((heel - 1.2 * r) * mm, (h_ * 0.15) * mm, (1.45 * r) * mm, (h_ + 0.75 * r) * mm,
                        0.25 * r * mm, stroke=1, fill=1)
        for yy in (0.35, 0.75):                                   # the cheek's screws
            pen.circle(heel + 0.1 * r, h_ * 0.15 + (h_ + 0.75 * r) * yy, 0.09 * r, fill=Color(0.55, 0.55, 0.57), w=0.25)
        # drawn back: one arrow outside the blade's back, along it, toward the handle
        y_a = h_ + r * 0.2
        pen.line(0.75 * r, y_a, 0.4 * r + heel + 0.35 * r, y_a, 0.8, INK)
        pen.arrowhead(0.4 * r + heel + 0.35 * r, y_a, -1, 0, 2.4)
        # the thumb: its tip, nail out, against the blade's side above the teeth, its length running down
        # toward the toe and out of the circle, to the hand
        tip = (0.12 * r, h_ * 0.55)
        ang_t = math.radians(-58)
        L_t, w_t = 1.6 * r, 0.27 * r
        ux_, uy_ = math.cos(ang_t), math.sin(ang_t)
        px_, py_ = -uy_, ux_
        arc_ = [math.pi / 2 + math.pi * k / 12 for k in range(13)]

        def put(xy):
            return [(tip[0] + ux_ * x + px_ * y, tip[1] + uy_ * x + py_ * y) for x, y in xy]
        thumb_ = [(w_t / 2 * (1 + math.cos(t_)), w_t / 2 * math.sin(t_)) for t_ in arc_] + [(L_t, -w_t / 2), (L_t, w_t / 2)]
        _poly_fill(pen, put(thumb_), fill=Color(*HAND), stroke=INK, w=0.4)
        rn = 0.27 * w_t
        nail = [(0.1 * w_t + rn * (1 + math.cos(t_)), rn * math.sin(t_)) for t_ in arc_] + [(0.62 * w_t, -rn), (0.62 * w_t, rn)]
        _poly_fill(pen, put(nail), fill=white, stroke=INK, w=0.25)
        pen.c.restoreState()
    closeup(pen, side_spot(b), 12.5, W(tuple(c)), inside)


def f_saw(pen, b, p: Part, model):
    """Sawing the first line at 45 degrees to the face, pushed; a close-up: the blade square to the face."""
    face = laid(p)
    p0, p1, u, n = face.lines[0]
    toe = _toe(p0, p1)
    t = face.box[1][2]
    d = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    at = (p0[0] + u[0] * min(1.2 * t, d * 0.4), p0[1] + u[1] * min(1.2 * t, d * 0.4))
    s = 300.0
    xs, ys, zs = _saw_axes(toe, 45)
    c = np.array([at[0], at[1], t])
    W = _scene(pen, b, _board(face) + saw(model, at, toe, n, s, 45, t),
               _region3(face, share=0.3, least=40, room=30) + _saw_ends(model, at, toe, s, 45, t))
    clip(pen, *b)
    _pencil(pen, W, face)
    _numbers(pen, W, face, only=[1])
    # the angle between the face and the teeth, as an arc from the face up to the blade
    back = -np.array([toe[0], toe[1], 0.0])
    arc = [W(tuple(c + 110 * (math.cos(math.radians(a)) * back + math.sin(math.radians(a)) * np.array([0, 0, 1.0]))))
           for a in range(0, 46, 3)]
    for (x1, y1), (x2, y2) in zip(arc, arc[1:]):
        pen.line(x1, y1, x2, y2, 0.4, DIM)
    m = W(tuple(c + 150 * (math.cos(math.radians(22)) * back + math.sin(math.radians(22)) * np.array([0, 0, 1.0]))))
    _about(pen, m[0], m[1] - 1.2, "45°", 3.2)
    _letter_far(pen, W, face, p.mark)
    s0, s1 = W(tuple(c - ys * 110 + zs * 125)), W(tuple(c - ys * 20 + zs * 125))   # pushed, toward the toe
    pen.line(s0[0], s0[1], s1[0], s1[1], 0.8, INK)
    pen.arrowhead(s1[0], s1[1], s1[0] - s0[0], s1[1] - s0[1], 2.6)
    pen.c.restoreState()
    closeup(pen, side_spot(b), 12.5, W(tuple(c - ys * 20)), lambda cx, cy, r: _square_inside(pen, cx, cy, r))


def f_end(pen, b, p: Part, model):
    """The saw near the end of the last line, the earlier ones sawn, a hand holding the waste."""
    face = laid(p)
    p0, p1, u, n = face.lines[-1]
    toe = _toe(p0, p1)
    t = face.box[1][2]
    d = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    at = (p0[0] + u[0] * d * 0.8, p0[1] + u[1] * d * 0.8)
    s = 300.0
    lo, hi = face.cuts2[-1]
    # the waste runs from the last line, along n, to the board's edge: the hand holds its far end from
    # beyond that edge, fingers toward the line, their tips well short of it
    run = max(abs((hi[0] - p0[0]) * n[0] + (hi[1] - p0[1]) * n[1]), abs((lo[0] - p0[0]) * n[0] + (lo[1] - p0[1]) * n[1]))
    mid_line = (p0[0] + (p1[0] - p0[0]) / 2, p0[1] + (p1[1] - p0[1]) / 2)
    tips = max(run * 0.55, 45.0)
    wrist = (mid_line[0] + n[0] * (tips + 125), mid_line[1] + n[1] * (tips + 125))
    out = n
    W = _scene(pen, b, _board(face) + saw(model, at, toe, n, s, 45, t),
               _region3(face, share=0.7, least=60, room=30)
               + [(wrist[0] + out[0] * 40, wrist[1] + out[1] * 40, t), (at[0], at[1], t + 120)])
    clip(pen, *b)
    _pencil(pen, W, face, sawn=len(face.lines) - 1, upto=0.8)
    draw_hand(pen, W, wrist, (-out[0], -out[1]), t + 2)
    _numbers(pen, W, face, only=[len(face.lines)])
    _letter_far(pen, W, face, p.mark)
    pen.c.restoreState()


def sawing_frames(pen, box, p: Part, qty: int, short: bool = False):
    """A part's cut in a slot of the instructions: four frames, two by two, or, short, the marks alone over
    the whole slot."""
    x, y, w, h = box
    model = next((t.model for t in p.tools if t.model and SAW in t.follows), None)
    if short or not model:
        bx = (x, y, w, h)
        f_marks(pen, bx, p, qty, sides=False)
        frame(pen, bx, 1)
        return
    fw, fh = (w - 4) / 2, (h - 4) / 2
    boxes = [(x + (i % 2) * (fw + 4), y + h - (i // 2 + 1) * fh - (i // 2) * 4, fw, fh) for i in range(4)]
    draw = [lambda bx: f_marks(pen, bx, p, qty), lambda bx: f_start(pen, bx, p, model),
            lambda bx: f_saw(pen, bx, p, model), lambda bx: f_end(pen, bx, p, model)]
    for i, (bx, f) in enumerate(zip(boxes, draw)):
        f(bx)
        frame(pen, bx, i + 1)
