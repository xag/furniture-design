"""The step that cuts the grooves of joints, drawn to IKEA's rules: no sentences, one action a frame, the
parts in the instructions' three-quarter view, the machine and its jig drawn from the 3D models their
makers' packages give them (a tool's payload model), the details in close-up circles.

First the settings, each a close-up on the machine: its depth adjusters and what they are set to, the
spacer (crossed out when none is used), a test groove in an offcut. Then, per kind of joint (the same two
letters, a shelf or not; how many of it before), four frames: 1, the two parts as they will be assembled,
seen from their reference face, a pencil tick across the joint at each groove, the positions measured
from the edge they start at, a blue triangle on the reference face; 2, the part grooved in its edge, lying
reference face up, the machine's front stop folded down on that face, the groove's distance from it in a
close-up; 3, the part grooved in its face, the machine standing on it, its base plate flush with the
reference edge; 4, the edge-grooved part turned over, the jig on its edge, the drill, how many holes. A
shelf is laid top face down on the side at the line of its top face and clamped; its end is cut with the
machine flat on the side, then the side with the machine standing against the shelf's end.

IKEA's rules followed (Schumacher 2011, from IKEA's own manual for assembly instructions, and IKEA's
manuals read): one viewpoint, the parts resting as on the bench; line drawings, outlines heavier than
inner edges, no texture or shadow; the tool drawn realistically and in use; details magnified in a circle
tied to their spot; a part turned over shown by a framed ring arrow; counts as "4 ×"; dimensions rare and
in perspective.
"""
from __future__ import annotations

import math

import numpy as np
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.units import mm

from . import lineart as la
from .scene import Scene, seats
from .sheets import DIM, INK, MARK, THIN, _fmt, _tool_badge

REF = HexColor("#1f6fb2")
WOOD = (0.97, 0.93, 0.85)
WOOD2 = (0.94, 0.88, 0.78)
DARKF = la.DARK
VIEW = la.View.axo(-35, 28)
LINE = 0.28


def fr(v):
    return _fmt(v).replace(".", ",")


def thickness(p):
    return min(p.hi[i] - p.lo[i] for i in range(3))


# --- the props: the machine and the jig from their models, a drill and a clamp ----------------------

def machine(model, pose, R, at):
    """The machine's solids in a pose ('flat' or 'standing'), its frame turned by R and moved to at."""
    if not model:
        return []
    return la.placed(la.solids(model.get("parts", []) + model.get("poses", {}).get(pose, [])), R, at)


def jig(model, at):
    """The jig's solids on a part's edge, its origin at `at` (the edge's top corner at the groove)."""
    if not model:
        return []
    return la.placed(la.solids(model.get("parts", [])), np.eye(3), at)


def drill(at, length=60):
    """A cordless drill held upright over `at`: the bit, the chuck, the body above it, the grip and the
    battery reaching back along +x."""
    x, y, z = at
    W = (1, 1, 1)
    out = [la.cyl(3, length, "z", (x, y, z), n=14, fill=DARKF),
           la.cyl(9, 18, "z", (x, y, z + length), n=24, fill=W),
           la.cyl(14, 10, "z", (x, y, z + length + 18), n=28, fill=DARKF),
           la.cyl(24, 70, "z", (x, y, z + length + 28), n=32, fill=W)]
    top = z + length + 28
    out.append(la.rbox((x + 14, y - 14, top + 18), (x + 110, y + 14, top + 50), 8, axis="x", fill=W))
    out.append(la.rbox((x + 100, y - 30, top - 6), (x + 150, y + 30, top + 26), 6, axis="y", fill=W))
    return out


def clamp(x, y0, z_lo, z_hi, reach=70):
    """An F-clamp seen from its side: the bar outside the parts at y0, jaws under z_lo and over z_hi."""
    return [la.box((x - 4, y0 - 10, z_lo - 10), (x + 4, y0, z_hi + 30), fill=(1, 1, 1)),
            la.box((x - 4, y0 - 10, z_lo - 10), (x + 4, y0 + reach, z_lo), fill=(1, 1, 1)),
            la.box((x - 4, y0 - 10, z_hi + 14), (x + 4, y0 + reach, z_hi + 22), fill=(1, 1, 1)),
            la.cyl(3, 14, "z", (x, y0 + reach - 12, z_hi), n=12, fill=DARKF),
            la.cyl(6, 30, "z", (x, y0 + reach - 12, z_hi + 22), n=20, fill=(1, 1, 1))]


# --- drawing a frame -------------------------------------------------------------------------

def proj(p):
    p = np.asarray(p, float)
    return float(p @ VIEW.right), float(p @ VIEW.up)


def frame(pen, b, n):
    x, y, w, h = b
    pen.c.setStrokeColor(THIN)
    pen.c.setLineWidth(0.25 * mm)
    pen.c.roundRect(x * mm, y * mm, w * mm, h * mm, 2 * mm, stroke=1, fill=0)
    pen.text(x + 2.5, y + h - 5.5, str(n), 4.5, INK, bold=True)


def clip(pen, x, y, w, h):
    pen.c.saveState()
    p = pen.c.beginPath()
    p.roundRect(x * mm, y * mm, w * mm, h * mm, 2 * mm)
    pen.c.clipPath(p, stroke=0, fill=0)


SIDE = 30.0   # mm: the column at a frame's right for its close-up, count and turn-over sign


def scene_box(b):
    x, y, w, h = b
    return (x, y, w - SIDE, h)


def side_spot(b, k=0):
    """The centre of the k-th slot of a frame's side column, from the top."""
    x, y, w, h = b
    return (x + w - SIDE / 2 - 1, y + h - 16 - k * 24)


def scene3d(pen, b, meshes, focus):
    """Draws the meshes in frame b's scene part, fitted to the 3D points `focus`; returns the world ->
    paper map."""
    dr = la.draw(meshes, VIEW, px=1600)
    pts = [proj(q) for q in focus]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    sb = scene_box(b)
    clip(pen, *b)
    P, k = la.render(pen, dr, (sb[0] + 3, sb[1] + 3, sb[2] - 4, sb[3] - 11), line=LINE,
                     fit=(min(xs), min(ys), max(xs), max(ys)))
    pen.c.restoreState()
    return lambda q: P(*proj(q))


def ref_triangle(pen, at, toward, s=3.2):
    """The blue reference triangle at paper point `at`, pointing to paper direction `toward`."""
    dx, dy = toward
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    x, y = at
    pen.poly([(x - px * s / 2 - ux * s, y - py * s / 2 - uy * s), (x + px * s / 2 - ux * s, y + py * s / 2 - uy * s),
              (x, y)], fill=REF, stroke=None)


def letter(pen, at, m, r=3.4):
    """A part's letter in a circle, at paper point `at`."""
    pen.circle(at[0], at[1], r, fill=white, w=0.35)
    pen.text(at[0], at[1] - r * 0.4, m, r * 1.1, INK, "middle", bold=True)


def tick(pen, W, a, b):
    pa, pb = W(a), W(b)
    pen.line(pa[0], pa[1], pb[0], pb[1], 0.45, INK)


def closeup(pen, center, r, spot, draw_inside):
    """A close-up circle at paper `center`, radius r, joined to the paper `spot` by two tapering lines,
    its content drawn by draw_inside(cx, cy, r) under a clip."""
    cx, cy = center
    sx, sy = spot
    d = math.hypot(cx - sx, cy - sy) or 1
    ux, uy = (cx - sx) / d, (cy - sy) / d
    px, py = -uy, ux
    for sgn in (1, -1):
        pen.line(sx, sy, cx + px * r * 0.75 * sgn - ux * r * 0.66, cy + py * r * 0.75 * sgn - uy * r * 0.66, 0.2, INK)
    pen.circle(cx, cy, r, fill=white, stroke=INK, w=0.45)
    pen.c.saveState()
    p = pen.c.beginPath()
    p.circle(cx * mm, cy * mm, r * mm)
    pen.c.clipPath(p, stroke=0, fill=0)
    draw_inside(cx, cy, r)
    pen.c.restoreState()
    pen.circle(sx, sy, 0.7, fill=INK, stroke=INK, w=0.1)


def section_edge(pen, cx, cy, r, t, off, standing=False):
    """Inside a close-up: a part in section, its reference face (blue) on top, the groove `off` under it
    in its edge (right), the machine's front stop on the face (or, standing, its base plate against
    the edge, groove `off` in from it)."""
    k = r * 1.25 / max(t, 22)
    from reportlab.lib.colors import Color as C
    wood = C(*WOOD)
    if not standing:
        xe, top = cx + 2, cy + t * k / 2
        pen.rect(cx - r, top - t * k, xe - (cx - r), t * k, fill=wood, stroke=INK, lw_=0.35)
        pen.line(cx - r, top, xe, top, 1.0, REF)
        gy = top - off * k
        pen.rect(xe - 11 * k, gy - 3.5 * k, 11 * k, 7 * k, fill=MARK, stroke=None)
        pen.rect(xe - 14 * k, top, 14 * k + 1, 1.0, fill=INK, stroke=None)         # the folded stop
        pen.rect(xe, gy - 14 * k, 4, 30 * k, fill=white, stroke=INK, lw_=0.3)      # the machine's front
        pen.dim((xe - 6 * k - 4, top), (xe - 6 * k - 4, gy), -2, fr(off), horizontal=False, size=2.6)
    else:
        xl, bot = cx - t * k * 0.2, cy - t * k / 2
        top = bot + t * k
        pen.rect(xl, bot, cx + r - xl, t * k, fill=wood, stroke=INK, lw_=0.35)
        pen.line(xl, bot, xl, top, 1.0, REF)
        gx = xl + off * k
        pen.rect(gx - 3.5 * k, top - 11 * k, 7 * k, 11 * k, fill=MARK, stroke=None)
        pen.rect(xl, top, 30 * k, 4, fill=white, stroke=INK, lw_=0.3)              # the machine's front
        pen.line(xl, top, xl, top + 12, 0.9, INK)                                  # its base plate
        pen.dim((xl, bot), (gx, bot), -3, fr(off), size=2.6)


# --- the four frames ---------------------------------------------------------------------------

W_SHOW, L_SHOW = 220.0, 420.0


def f_mark(pen, b, sc, e, f):
    """Both parts as they will be assembled, turned so their reference face is seen: a pencil tick across
    the joint at each groove, the positions measured from the start edge in perspective, the blue
    triangle on the reference face."""
    pe, pf = sc.part(e.part), sc.part(f.part)
    al = {"left": 0, "right": 0, "front": 1, "back": 1, "bottom": 2, "top": 2}[e.start]
    across = min(range(3), key=lambda i: pe.hi[i] - pe.lo[i])
    normal = next(i for i in range(3) if i not in (al, across))
    ref_hi = e.reference in ("right", "back", "top")
    rnorm = np.zeros(3)
    rnorm[across] = 1 if ref_hi else -1
    turn = None
    if rnorm @ VIEW.d > 0:          # the reference face looks away: turn the pair about the vertical
        c = (np.asarray(pe.lo) + np.asarray(pe.hi)) / 2
        turn = (la.rot("z", 180), c)
    def T(p):
        p = np.asarray(p, float)
        if turn is None:
            return p
        R, c = turn
        return (p - c) @ R.T + c
    meshes = [la.box(pe.lo, pe.hi, fill=WOOD).moved(by=(0, 0, 0)),
              la.box(pf.lo, pf.hi, fill=WOOD2)]
    if turn is not None:
        R, c = turn
        meshes = [m.moved(R, c - c @ R.T) for m in meshes]
    # the joint plane and the reference face's coordinate
    jv = pe.hi[normal] if pf.lo[normal] >= pe.hi[normal] - 1 else pe.lo[normal]
    into_f = 1 if jv == pe.hi[normal] else -1
    rv = pe.hi[across] if ref_hi else pe.lo[across]
    focus = []
    for q in e.points:
        for dn in (-420 * into_f, 160 * into_f):
            p = np.array(q, float)
            p[normal] = jv + dn
            p[across] = rv
            focus.append(T(p))
    s0 = pe.hi[al] if e.start in ("right", "back", "top") else pe.lo[al]
    for p in (pe.lo, pe.hi):
        q = np.array(e.points[0], float)
        q[al] = p[al]
        q[normal] = jv - 420 * into_f
        q[across] = rv
        focus.append(T(q))
    W = scene3d(pen, b, meshes, focus)
    clip(pen, *b)
    for q in e.points:
        a = np.array(q, float); a[across] = rv; a[normal] = jv - 22 * into_f
        c_ = np.array(q, float); c_[across] = rv; c_[normal] = jv + 22 * into_f
        tick(pen, W, T(a), T(c_))
    for part_, dn in ((pe, -150 * into_f), (pf, 60 * into_f)):
        q = np.mean(np.asarray(e.points, float), axis=0)
        q[normal] = jv + dn
        q[across] = rv if part_ is pe else (pf.hi[across] if ref_hi else pf.lo[across])
        letter(pen, W(T(q)), part_.mark)
    a = np.array(e.points[0], float); a[across] = rv; a[al] = s0
    a1, a2 = a.copy(), a.copy()
    a1[normal] = jv + 10 * into_f
    a2[normal] = jv - (70 + 55 * len(e.points)) * into_f
    pa1, pa2 = W(T(a1)), W(T(a2))
    pen.line(pa1[0], pa1[1], pa2[0], pa2[1], 0.15, DIM)
    m = np.mean(np.asarray(e.points, float), axis=0)
    if len(e.points) == 1:
        m[al] += 40 * (1 if m[al] - s0 > 0 else -1) * -1
    a = m.copy(); a[across] = rv; a[normal] = jv
    a2 = a.copy(); a2[normal] = jv + into_f
    pa, pb = W(T(a)), W(T(a2))
    ref_triangle(pen, pa, (pb[0] - pa[0], pb[1] - pa[1]))
    # positions from the start edge, as dimension lines in perspective on the reference face
    for i, q in enumerate(sorted(e.points, key=lambda q: abs(q[al] - s0))):
        off = -(70 + 55 * i) * into_f
        a = np.array(q, float); a[across] = rv; a[normal] = jv + off; a[al] = s0
        c_ = a.copy(); c_[al] = q[al]
        pa, pc = W(T(a)), W(T(c_))
        pen.line(pa[0], pa[1], pc[0], pc[1], 0.18, DIM)
        pen.arrowhead(pa[0], pa[1], pa[0] - pc[0], pa[1] - pc[1], 1.8, DIM)
        pen.arrowhead(pc[0], pc[1], pc[0] - pa[0], pc[1] - pa[1], 1.8, DIM)
        e0 = np.array(c_); e0[normal] = jv - 8 * into_f
        pe0 = W(T(e0))
        pen.line(pc[0], pc[1], pe0[0], pe0[1], 0.12, DIM)
        tx_, ty_ = pa[0] + (pc[0] - pa[0]) * 0.72, pa[1] + (pc[1] - pa[1]) * 0.72
        pen.text(tx_ - 1.2, ty_ + 1.0, f"{abs(q[al] - s0):.0f}", 2.8, DIM, "end")
    pen.c.restoreState()


def f_edge(pen, b, e, t, letter_, mach_model, offset):
    """The edge-grooved part lying reference face up, its joint edge at x = W_SHOW; the machine's front
    stop folded down on that face, its centre mark on the pencil tick."""
    yg = L_SHOW / 2
    part = la.box((0, 0, 0), (W_SHOW, L_SHOW, t), fill=WOOD)
    R = np.column_stack([(0, -1, 0), (1, 0, 0), (0, 0, 1)])          # machine X, Y, Z in the world
    mach = machine(mach_model, "flat", R, (W_SHOW, yg, t - 2 * offset))
    W = scene3d(pen, b, [part] + mach, [(W_SHOW - 80, yg - 90, 0), (W_SHOW + 320, yg + 70, 170)])
    clip(pen, *b)
    letter(pen, W((W_SHOW - 50, yg - 70, t)), letter_)
    tick(pen, W, (W_SHOW - 110, yg, t), (W_SHOW - 82, yg, t))
    pa, pb = W((W_SHOW - 130, yg - 60, t)), W((W_SHOW - 130, yg - 59, t))
    pen.c.restoreState()
    spot = W((W_SHOW, yg + 40, t - e.offset))
    closeup(pen, side_spot(b), 12.5, spot, lambda cx, cy, r: section_edge(pen, cx, cy, r, t, e.offset))


def f_face(pen, b, f, t, letter_, mach_model):
    """The face-grooved part lying grooved face up, its reference edge at x = 0; the machine standing on
    that face, its base plate flush with the edge, its centre mark on the tick."""
    yg = L_SHOW / 2
    part = la.box((0, 0, 0), (W_SHOW, L_SHOW, t), fill=WOOD2)
    R = np.column_stack([(0, 1, 0), (0, 0, 1), (1, 0, 0)])           # X along y, Y up, Z into the part
    mach = machine(mach_model, "standing", R, (0, yg, t))
    W = scene3d(pen, b, [part] + mach, [(-60, yg - 160, 0), (W_SHOW * 0.8, yg + 110, 340)])
    clip(pen, *b)
    letter(pen, W((W_SHOW * 0.55, yg - 110, t)), letter_)
    tick(pen, W, (60, yg, t), (95, yg, t))
    pen.c.restoreState()
    spot = W((0, yg + 70, t / 2))
    closeup(pen, side_spot(b), 12.5, spot,
            lambda cx, cy, r: section_edge(pen, cx, cy, r, t, f.offset, standing=True))


def f_drill(pen, b, e, t, n, letter_, jig_model):
    """The edge-grooved part turned over, reference face down; the jig on the edge at the groove, the
    bit going in."""
    yg = L_SHOW / 2
    part = la.box((0, 0, 0), (W_SHOW, L_SHOW, t), fill=WOOD)
    d, off = e.hole
    meshes = [part] + jig(jig_model, (W_SHOW, yg, t)) + drill((W_SHOW - off, yg, t + 22), 45)
    W = scene3d(pen, b, meshes, [(W_SHOW - 120, yg - 70, 0), (W_SHOW + 160, yg + 60, t + 230)])
    letter(pen, W((W_SHOW - 70, yg - 50, t)), letter_)
    pa = W((W_SHOW - off - 30, yg, t + 40))
    pen.line(pa[0] - 6, pa[1] + 8, pa[0] - 6, pa[1], 0.6, INK)
    pen.arrowhead(pa[0] - 6, pa[1], 0, -1, 2.4)
    pen.text(pa[0] - 14, pa[1] + 3, f"Ø {fr(d)}", 3.2, INK, "end", bold=True)
    cx, cy = side_spot(b)
    turned_over(pen, (cx - 8, cy - 7, 16, 14))
    pen.text(cx, b[1] + 6, f"{n} ×", 5, INK, "middle", bold=True)


def turned_over(pen, box):
    """IKEA's sign for a part turned over: a framed box, the board with its blue face, a thick ring
    arrow round it."""
    x, y, w, h = box
    pen.c.setStrokeColor(INK)
    pen.c.setLineWidth(0.3 * mm)
    pen.c.roundRect(x * mm, y * mm, w * mm, h * mm, 1.2 * mm, stroke=1, fill=0)
    cx, cy = x + w / 2, y + h / 2
    pen.rect(cx - 4, cy - 0.8, 8, 1.6, fill=Color(*WOOD), stroke=INK, lw_=0.25)
    pen.line(cx - 4, cy + 0.8, cx + 4, cy + 0.8, 0.6, REF)
    r = 4.2
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * 0.8 * math.sin(math.radians(a))) for a in range(150, -151, -12)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        pen.line(x1, y1, x2, y2, 0.7, INK)
    pen.arrowhead(pts[-1][0], pts[-1][1], pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1], 2.0)


def f_shelf(pen, b, e, f, sc, which, mach_model, offset):
    """The side lying inner face up, the line of the shelf's top face at its height; the shelf on it top
    face down, its end on the line, clamped. 'mark': with the ticks; 'shelf': the machine flat on the
    side against the shelf's end; 'side': the machine standing, its base plate against the shelf's end."""
    side, shelf = sc.part(f.part), sc.part(e.part)
    ts, tc = thickness(side), thickness(shelf)
    H = side.hi[2] - side.lo[2]
    D = side.hi[1] - side.lo[1]
    line = f.line
    s_lo, s_hi = shelf.lo[1] - side.lo[1], shelf.hi[1] - side.lo[1]
    meshes = [la.box((0, 0, 0), (H, D, ts), fill=WOOD2),
              la.box((line, s_lo, ts), (line + 260, s_hi, ts + tc), fill=WOOD)]
    meshes += clamp(line + 200, -2, 0, ts + tc)
    yg = e.points[0][1] - side.lo[1]
    if which == "shelf":
        R = np.column_stack([(0, 1, 0), (-1, 0, 0), (0, 0, 1)])
        meshes += machine(mach_model, "flat", R, (line, yg, ts))
        focus = [(line - 330, yg - 80, 0), (line + 120, yg + 90, 170)]
    elif which == "side":
        R = np.column_stack([(0, -1, 0), (0, 0, 1), (-1, 0, 0)])
        meshes += machine(mach_model, "standing", R, (line, yg, ts))
        focus = [(line - 140, yg - 90, 0), (line + 120, yg + 90, 330)]
    else:
        focus = [(0, 0, 0), (H, D, ts + tc + 40)]
    W = scene3d(pen, b, meshes, focus)
    clip(pen, *b)
    letter(pen, W((line * 0.45, D * 0.45, ts)), side.mark)
    letter(pen, W((line + 150, (s_lo + s_hi) / 2, ts + tc)), shelf.mark)
    if which == "mark":
        a, c_ = W((line, -6, ts)), W((line, D + 6, ts))
        pen.line(a[0], a[1], c_[0], c_[1], 0.3, INK, [1.4, 0.9])
        for q in e.points:
            y = q[1] - side.lo[1]
            tick(pen, W, (line - 25, y, ts), (line, y, ts))
            tick(pen, W, (line, y, ts + tc), (line, y, ts))
        pa, pc = W((0, -30, ts)), W((line, -30, ts))
        pen.line(pa[0], pa[1], pc[0], pc[1], 0.18, DIM)
        pen.arrowhead(pa[0], pa[1], pa[0] - pc[0], pa[1] - pc[1], 1.8, DIM)
        pen.arrowhead(pc[0], pc[1], pc[0] - pa[0], pc[1] - pa[1], 1.8, DIM)
        pen.text((pa[0] + pc[0]) / 2, (pa[1] + pc[1]) / 2 + 1, f"{line:.0f}", 2.6, DIM, "middle")
        pt, pt2 = W((line, D * 0.75, ts)), W((line + 1, D * 0.75, ts))
        ref_triangle(pen, pt, (pt2[0] - pt[0], pt2[1] - pt[1]))
    pen.c.restoreState()
    if which == "shelf":
        spot = W((line, yg + 60, ts + e.offset))
        closeup(pen, side_spot(b), 12.5, spot,
                lambda cx, cy, r: section_edge(pen, cx, cy, r, tc, e.offset))
    elif which == "side":
        spot = W((line - f.offset, yg + 60, ts))
        closeup(pen, side_spot(b), 12.5, spot,
                lambda cx, cy, r: section_edge(pen, cx, cy, r, ts, f.offset, standing=True))


# --- the pages ---------------------------------------------------------------------------------

def jt(sc, jid):
    return next(j for j in sc.joints if j.id == jid)


def groups(sc, joint_ids):
    out = []
    for jid in joint_ids:
        e, f = seats(sc, jt(sc, jid))
        key = (sc.part(e.part).mark, sc.part(f.part).mark, f.line is not None)
        for g in out:
            if g["key"] == key:
                g["n"] += 1
                break
        else:
            out.append({"key": key, "e": e, "f": f, "n": 1})
    return out


def settings(pen, b, model, setting, spacer, spacers, recess):
    """The settings, each drawn: the machine with a close-up on each depth adjuster showing what it is set
    to (max, or the joint's setting); the spacer, crossed out when none is used; a test groove in an
    offcut, the connector `recess` under the surface."""
    x, y, w, h = b
    pen.c.setStrokeColor(THIN)
    pen.c.setLineWidth(0.25 * mm)
    pen.c.roundRect(x * mm, y * mm, w * mm, h * mm, 2 * mm, stroke=1, fill=0)
    cx = x + 6
    dials = (model or {}).get("dials", [])
    if model:
        W = scene3d(pen, (x, y - 4, 64 + SIDE, h + 8), machine(model, "standing", np.eye(3), (0, 0, 0)),
                    [(-60, 0, 0), (60, 300, 150)])
        cx = x + 76
        for d in dials:
            label = "max" if d.get("shows") == "max" else "".join(ch for ch in setting if ch.isdigit()) or setting
            sp = W(d["at"])

            def inside(cx_, cy_, r, label=label):
                pen.circle(cx_, cy_, r * 0.75, fill=white, stroke=INK, w=0.4)
                for a in range(0, 360, 30):
                    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                    pen.line(cx_ + ca * r * 0.75, cy_ + sa * r * 0.75, cx_ + ca * r * 0.9, cy_ + sa * r * 0.9, 0.3, INK)
                pen.text(cx_, cy_ - 1.3, label, 3.6 if len(label) < 4 else 2.8, INK, "middle", bold=True)
                pen.arrowhead(cx_ + r * 0.55, cy_ + r * 0.62, -1, 0.2, 2.0)
            closeup(pen, (cx, y + h / 2), 9.5, sp, inside)
            cx += 22
    if spacers:
        sx = cx + 2
        shown = spacer or min(spacers)
        pen.rect(sx, y + h / 2 - 7, 10, 14, fill=white, stroke=INK, lw_=0.3)
        for k in range(4):
            pen.line(sx + 2 + 2 * k, y + h / 2 - 5, sx + 2 + 2 * k, y + h / 2 + 5, 0.2, INK)
        pen.text(sx + 5, y + h / 2 - 11, fr(shown), 3.0, INK, "middle")
        if not spacer:
            pen.line(sx - 2, y + h / 2 - 9, sx + 12, y + h / 2 + 9, 0.7, MARK)
            pen.line(sx - 2, y + h / 2 + 9, sx + 12, y + h / 2 - 9, 0.7, MARK)
        cx = sx + 22
    if recess is not None:
        tx = cx
        pen.rect(tx, y + h / 2 - 5, 30, 8, fill=Color(*WOOD), stroke=INK, lw_=0.3)
        pen.rect(tx + 10, y + h / 2 - 1, 10, 4, fill=MARK, stroke=None)
        pen.rect(tx + 10.5, y + h / 2 - 1.4, 9, 2.8, fill=INK, stroke=None)
        pen.dim((tx + 22, y + h / 2 + 3), (tx + 22, y + h / 2 + 1.6), 4, fr(recess), horizontal=False, size=2.4)


def _tool_model(sc: Scene, path: str):
    for j in sc.joints:
        for t in j.methods:
            if t.path == path:
                return t.model
    return None


def grooving_pages(c, pen, sc: Scene, step, L: dict, W_: float = 210, H_: float = 297,
                   short: bool = False) -> None:
    """The pages of a step that cuts joints' grooves, on new pages of the canvas: the step's number and
    tools, the settings, then a block of four frames per kind of joint. Leaves the last page open.
    `short`, for someone who knows the machine: the settings without the test groove, and per kind of
    joint only the frames of what the piece needs, the marks and the holes."""
    joints = [j for j in sc.joints if j.id in step.joints]
    if not joints:
        return
    j0 = joints[0]
    mach_model, jig_model = _tool_model(sc, j0.machine), _tool_model(sc, j0.jig)
    gs = groups(sc, step.joints)
    c.showPage()
    pen.text(15, H_ - 12, L["prepare"], 3.4, THIN)
    pen.rect(15, H_ - 34, 16, 16, fill=INK, stroke=None)
    pen.text(23, H_ - 30, str(step.number), 9, white, "middle", bold=True)
    tx = 37
    for t in step.tools:
        tx += _tool_badge(pen, tx, H_ - 31, t) + 3
    settings(pen, (15, H_ - 78, 180, 38), mach_model, j0.setting, gs[0]["e"].spacer, j0.spacers,
             None if short else j0.test_recess)
    fw, fh = (W_ - 30 - 4) / 2, 62.0
    y_top = H_ - 84
    rows = 1 if short else 2
    for g in gs:
        need = rows * fh + 2 + 8 + (4 if rows > 1 else 0)
        if y_top - need < 10:
            c.showPage()
            pen.text(15, H_ - 12, L["prepare"], 3.4, THIN)
            pen.rect(15, H_ - 30, 12, 12, fill=INK, stroke=None)
            pen.text(21, H_ - 27, str(step.number), 7, white, "middle", bold=True)
            y_top = H_ - 32
        e, f = g["e"], g["f"]
        pe, pf = sc.part(e.part), sc.part(f.part)
        j = jt(sc, e.joint)
        offset = j.groove_offset or e.offset
        if g["n"] > 1:
            pen.text(15, y_top - 6, f"{g['n']} ×", 5, INK, bold=True)
        boxes = [(15 + (i % 2) * (fw + 4), y_top - 8 - (i // 2 + 1) * fh - (i // 2) * 4, fw, fh) for i in range(4)]
        # each frame's border and number are drawn after what it shows, so a part that reaches the
        # frame's edge does not paint over its border
        if short:
            if f.line is not None:
                f_shelf(pen, boxes[0], e, f, sc, "mark", mach_model, offset)
            else:
                f_mark(pen, boxes[0], sc, e, f)
            frame(pen, boxes[0], 1)
            if e.hole:
                f_drill(pen, boxes[1], e, thickness(pe), len(e.points), pe.mark, jig_model)
                frame(pen, boxes[1], 2)
            y_top -= need
            continue
        if f.line is not None:
            f_shelf(pen, boxes[0], e, f, sc, "mark", mach_model, offset)
            f_shelf(pen, boxes[1], e, f, sc, "shelf", mach_model, offset)
            f_shelf(pen, boxes[2], e, f, sc, "side", mach_model, offset)
        else:
            f_mark(pen, boxes[0], sc, e, f)
            f_edge(pen, boxes[1], e, thickness(pe), pe.mark, mach_model, offset)
            f_face(pen, boxes[2], f, thickness(pf), pf.mark, mach_model)
        if e.hole:
            f_drill(pen, boxes[3], e, thickness(pe), len(e.points), pe.mark, jig_model)
        for i, bx in enumerate(boxes):
            frame(pen, bx, i + 1)
        y_top -= need
