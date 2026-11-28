"""PDF documents for the people who build a piece, drawn from its scene (scene.py):

- design_document(): the design file, A3 landscape, as a drawing office lays it out: a
  general arrangement sheet (front view, view from the left placed on its right and top
  view below it, first-angle projection as in Europe, dimensioned, with a three-quarter
  view whose parts carry their letters), a sheet of parts (the parts list and one drawing
  per board, with its connector grooves, cuts and grain), and a sheet of checks and design
  notes in plain words; each sheet framed, with its title block.
- assembly_instructions(): A4 portrait, picture first: a cover, what is in the box (each
  board with its letter and number, the connectors, the tools), then one picture per step,
  the parts it brings in drawn darker and pulled back along the way they come in, arrows
  showing where they go, the connectors of the step marked, and one short sentence.

French by default (`lang`), since the people building read French; the words are in LABELS.
"""

from __future__ import annotations

import datetime as dt
import math
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.pagesizes import A3, A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab import rl_config

# Streams written as binary, not as ASCII85 text: a picture is then one copy less to hold while it
# is put in, and the file a fifth smaller.
rl_config.useA85 = 0

from . import linework as lw
from .natives import away, drawn_apart
from .scene import TOUCH, Part, Scene, cut_plan, place_of

INK = HexColor("#1d1d1b")
THIN = HexColor("#5b5b58")
DIM = HexColor("#1f4e5a")
# A part is drawn in a plain tone and a part a step brings in in a deeper one: no colour says what a part
# is made of, which only its material does.
PLAIN = HexColor("#ecebe8")
NEW = HexColor("#b4c2ce")
MARK = HexColor("#c0392b")
# the most a part's fill may spread between its red, green and blue and still be a grey (draw_parts): PLAIN
# and NEW, the tones of a part there and of one brought in, say nothing of what it is made of; a wood's
# colour spreads more than twice as far
GREY = 0.12
OK = HexColor("#2e7d32")
OPEN = HexColor("#b26a00")

LABELS = {
    "fr": {
        "general": "Vue d'ensemble", "parts": "Pièces", "checks": "Vérifications et notes",
        "front": "Face", "left": "Gauche", "top": "Dessus", "axo": "Vue 3/4",
        "title": "Titre", "version": "Version", "drawn": "Dessiné par", "date": "Date",
        "scale": "Échelle", "sheet": "Feuille", "units": "Cotes en mm", "material": "Matériau",
        "see_parts": "voir la liste des pièces, feuille 2",
        "projection": "Projection européenne (1er dièdre)",
        "mark": "Rep.", "name": "Désignation", "qty": "Qté", "length": "Long.", "width": "Larg.",
        "thickness": "Ép.", "grain": "Fil", "connectors": "Assemblages",
        "joint": "Assemblage", "joins": "Pièces", "count": "Nb", "setting": "Réglage",
        "tool": "Outil", "requirement": "Exigence", "result": "Résultat", "verdict": "Verdict",
        "ok": "OK", "fail": "NON", "open": "OUVERT", "info": "INFO",
        "notes": "Notes de conception",
        "slots": "rainures", "grain_along": "fil", "thick": "ép.", "glued_from": "collé de",
        "sheets_of": "feuilles de", "positions_note": "Positions des rainures indicatives, "
        "réparties régulièrement : à confirmer au traçage.",
        "inbox": "Avant de commencer", "boards": "Pièces", "hardware": "Fixations",
        "unstated": "Fixation non précisée",
        "tools": "Outils", "other_tools": "Autres outils", "prepare": "Préparation", "assemble": "Montage",
        "overall": "Encombrement", "step": "Étape",
        "cutting": "Découpe", "sources": "Sources", "mark_out": "Tracer", "from": "depuis", "to": "à",
        "edge": {"bottom": "le chant du bas", "top": "le chant du haut",
                 "front": "le chant avant", "back": "le chant arrière",
                 "left": "le chant gauche", "right": "le chant droit"},
        "deep": "sur {d} de profondeur",
        "saw_from_edge": "Scier les traits dans l'ordre des numéros, chacun depuis le bord où "
                         "il commence.",
        "saw_from_hole": "Scier les traits dans l'ordre des numéros, en partant d'un trou "
                         "percé dans la chute.",
        "saw_mixed": "Scier d'abord les traits qui partent d'un bord, chacun depuis ce bord, "
                     "puis les autres en partant d'un trou percé dans la chute.",
        "sources": "Sources",
    },
    "en": {
        "general": "General arrangement", "parts": "Parts", "checks": "Checks and notes",
        "front": "Front", "left": "Left", "top": "Top", "axo": "3/4 view",
        "title": "Title", "version": "Version", "drawn": "Drawn by", "date": "Date",
        "scale": "Scale", "sheet": "Sheet", "units": "Dimensions in mm", "material": "Material",
        "see_parts": "see the parts list, sheet 2",
        "projection": "First-angle projection",
        "mark": "Mark", "name": "Part", "qty": "Qty", "length": "Length", "width": "Width",
        "thickness": "Thk.", "grain": "Grain", "connectors": "Joints",
        "joint": "Joint", "joins": "Parts", "count": "No.", "setting": "Setting",
        "tool": "Tool", "requirement": "Requirement", "result": "Result", "verdict": "Verdict",
        "ok": "OK", "fail": "NO", "open": "OPEN", "info": "INFO", "notes": "Design notes",
        "slots": "grooves", "grain_along": "grain", "thick": "thk.", "glued_from": "glued from",
        "sheets_of": "sheets of", "positions_note": "Groove positions indicative, evenly "
        "spread: to be confirmed when marking out.",
        "inbox": "Before you start", "boards": "Parts", "hardware": "Fixings",
        "unstated": "Fastening not stated",
        "tools": "Tools", "other_tools": "Other tools", "prepare": "Preparation", "assemble": "Assembly",
        "overall": "Overall size", "step": "Step",
        "cutting": "Cutting", "sources": "Sources", "mark_out": "Mark out", "from": "from", "to": "to",
        "edge": {"bottom": "the bottom edge", "top": "the top edge", "front": "the front edge",
                 "back": "the back edge", "left": "the left edge", "right": "the right edge"},
        "deep": "{d} deep",
        "saw_from_edge": "Saw the lines in the order of their numbers, each from the edge "
                         "where it starts.",
        "saw_from_hole": "Saw the lines in the order of their numbers, starting from a hole "
                         "drilled in the waste.",
        "saw_mixed": "First saw the lines that start at an edge, each from that edge, then "
                     "the others starting from a hole drilled in the waste.",
        "sources": "Sources",
    },
}

SCALES = [1, 2, 2.5, 5, 10, 20]
DOT = 0.8  # mm on paper: a connector whose node states no size is drawn as a dot


def _fmt(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


# --- drawing primitives ---------------------------------------------------------------

class Pen:
    """Draws on a reportlab canvas in millimetres."""

    def __init__(self, c: Canvas):
        self.c = c
        # a list to note where each picture is drawn in (note()), and one to note every text set on a page
        # (text()), or None; a canvas that carries them (drawn_regions, drawn_words) gives them to its pens
        self.regions = getattr(c, "drawn_regions", None)
        self.words = getattr(c, "drawn_words", None)

    def note(self, kind: str, box, blank=None, **info):
        """When regions are kept, note that a picture of `kind` is drawn in `box` (x, y, w, h in mm from the
        page's bottom left) on the current page, as [x0, y0, x1, y1] from the page's top left, the way a
        page is cut; `blank` an area within it to leave out (a letter the screen sets as text)."""
        if self.regions is None:
            return
        top = self.c._pagesize[1] / mm
        flip = lambda x, y, w, h: [round(x, 2), round(top - (y + h), 2), round(x + w, 2), round(top - y, 2)]
        self.regions.append({"kind": kind, "page": self.c.getPageNumber() - 1, "box": flip(*box),
                             **({"blank": flip(*blank)} if blank else {}), **info})

    def _seen(self, *pts) -> bool:
        """Whether every point (mm) is on the paper. When regions are kept and one is not, note it once
        for the page (a region of kind spill): something is drawn beyond the edge."""
        w, h = (v / mm for v in self.c._pagesize)
        if all(-0.5 <= x <= w + 0.5 and -0.5 <= y <= h + 0.5 for x, y in pts):
            return True
        page = self.c.getPageNumber() - 1
        if self.regions is not None and not any(r["kind"] == "spill" and r["page"] == page for r in self.regions):
            self.regions.append({"kind": "spill", "page": page, "box": [0, 0, 0, 0]})
        return False

    def line(self, x1, y1, x2, y2, w=0.25, color=INK, dash=None):
        self._seen((x1, y1), (x2, y2))
        c = self.c
        c.setStrokeColor(color)
        c.setLineWidth(w * mm)
        c.setDash(*(dash or ([],)))
        c.line(x1 * mm, y1 * mm, x2 * mm, y2 * mm)
        c.setDash([])

    def poly(self, pts, fill=None, stroke=INK, w=0.35):
        self._seen(*pts)
        c = self.c
        p = c.beginPath()
        p.moveTo(pts[0][0] * mm, pts[0][1] * mm)
        for x, y in pts[1:]:
            p.lineTo(x * mm, y * mm)
        p.close()
        if fill is not None:
            c.setFillColor(fill)
        if stroke is not None:
            c.setStrokeColor(stroke)
            c.setLineWidth(w * mm)
        c.setLineJoin(1)
        c.drawPath(p, fill=fill is not None, stroke=stroke is not None)

    def rect(self, x, y, w, h, fill=None, stroke=INK, lw_=0.35):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], fill, stroke, lw_)

    def text(self, x, y, s, size=3.0, color=INK, anchor="start", bold=False, angle=0, role="", says=None, step=None):
        """Set a text. When words are kept, note it with its page; `role` says what it is where that
        is not a thing to read as a sentence: "name", the piece's own name; "heading", a heading the
        drawing sets; "label", the name of a thing (a tool, the hardware) or a size; "note", the
        sentence of a step that brings in, cuts and closes nothing, so that no picture can say it. A text
        set beyond the paper is noted so (off). `says` is what in the model the text states, for a standard
        to hold it to (standards_pages.printed_unsupported): {"size": the paths of the parts it measures
        across}, {"material": the parts whose materials it names}, {"name": the node whose name it is},
        {"connector": the joints whose connectors it names}. `step` is the number of the step whose sentence
        it is (a line of it), so a reader can show a case of it on that step."""
        c = self.c
        from reportlab.pdfbase.pdfmetrics import stringWidth
        long = stringWidth(str(s), "Helvetica-Bold" if bold else "Helvetica", size * mm) / mm if not angle else 0
        start = {"start": 0, "middle": -long / 2, "end": -long}[anchor]
        on = self._seen((x + start, y), (x + start + long, y))
        if self.words is not None and str(s).strip():
            self.words.append({"page": c.getPageNumber() - 1, "text": str(s), **({"role": role} if role else {}),
                               **({} if on else {"off": True}), **({"says": says} if says else {}),
                               **({"step": step} if step is not None else {})})
        c.saveState()
        c.setFillColor(color)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size * mm / 0.3528 * 0.3528)
        c.translate(x * mm, y * mm)
        c.rotate(angle)
        fn = {"start": c.drawString, "middle": c.drawCentredString,
              "end": c.drawRightString}[anchor]
        fn(0, 0, s)
        c.restoreState()

    def arrowhead(self, x, y, dx, dy, size=2.2, color=INK):
        n = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / n, dy / n
        px, py = -uy, ux
        self.poly([(x, y), (x - ux * size + px * size * 0.33, y - uy * size + py * size * 0.33),
                   (x - ux * size - px * size * 0.33, y - uy * size - py * size * 0.33)],
                  fill=color, stroke=None)

    def circle(self, x, y, r, fill=white, stroke=INK, w=0.3):
        self._seen((x - r, y - r), (x + r, y + r))
        c = self.c
        c.setFillColor(fill)
        c.setStrokeColor(stroke)
        c.setLineWidth(w * mm)
        c.circle(x * mm, y * mm, r * mm, fill=1, stroke=1)

    def dim(self, a, b, offset, label, horizontal=True, size=2.6, *, of: list[str]):
        """An ISO-style dimension between points a and b (paper mm), the dimension line
        `offset` mm away (positive: above / to the right). `of`: the paths of the parts whose edges it
        runs between, or of the thing it spans: what in the model it measures (Pen.text's says)."""
        (ax, ay), (bx, by) = a, b
        says = {"size": list(of)}
        if horizontal:
            y = (ay if offset > 0 else min(ay, by)) + offset
            y = max(ay, by) + offset if offset > 0 else min(ay, by) + offset
            for px, py in (a, b):
                self.line(px, py + (1 if offset > 0 else -1), px, y + (1.5 if offset > 0 else -1.5),
                          0.13, DIM)
            self.line(ax, y, bx, y, 0.18, DIM)
            self.arrowhead(ax, y, ax - bx, 0, 2.0, DIM)
            self.arrowhead(bx, y, bx - ax, 0, 2.0, DIM)
            room = abs(bx - ax)
            if room >= len(label) * size * 0.55 + 1:
                self.text((ax + bx) / 2, y + 0.8, label, size, DIM, "middle", says=says)
            else:  # too short to hold its figure: write it beside, past the right end
                self.text(max(ax, bx) + 1.2, y + 0.8, label, size * 0.9, DIM, says=says)
        else:
            x = max(ax, bx) + offset if offset > 0 else min(ax, bx) + offset
            for px, py in (a, b):
                self.line(px + (1 if offset > 0 else -1), py, x + (1.5 if offset > 0 else -1.5), py,
                          0.13, DIM)
            self.line(x, ay, x, by, 0.18, DIM)
            self.arrowhead(x, ay, 0, ay - by, 2.0, DIM)
            self.arrowhead(x, by, 0, by - ay, 2.0, DIM)
            room = abs(by - ay)
            if room >= len(label) * size * 0.55 + 1:
                self.text(x - 0.8, (ay + by) / 2, label, size, DIM, "middle", angle=90, says=says)
            else:
                self.text(x - 0.8, max(ay, by) + 1.2, label, size * 0.9, DIM, angle=90, says=says)


class Placed:
    """A view placed on paper: piece mm -> paper mm, by scale and offset."""

    def __init__(self, view: lw.View, scale: float, ox: float, oy: float, origin=(0.0, 0.0)):
        self.view, self.s, self.ox, self.oy, self.origin = view, scale, ox, oy, origin

    def __call__(self, p) -> tuple[float, float]:
        u, v = self.view.to2d(p)
        return (self.ox + (u - self.origin[0]) * self.s, self.oy + (v - self.origin[1]) * self.s)

    def pt(self, uv):
        return (self.ox + (uv[0] - self.origin[0]) * self.s, self.oy + (uv[1] - self.origin[1]) * self.s)


def _boxes(parts: list[Part], offsets: dict[str, tuple] | None = None) -> dict:
    out = {}
    for p in parts:
        o = (offsets or {}).get(p.id, (0, 0, 0))
        out[p.id] = (tuple(a + b for a, b in zip(p.lo, o)), tuple(a + b for a, b in zip(p.hi, o)),
                     p.profile(o))
    return out


def _extent(boxes: dict, view: lw.View):
    pts = [view.to2d(c) for entry in boxes.values() for c in _box_corners(entry[0], entry[1])]
    return lw.bounds(pts)


def _box_corners(lo, hi):
    return [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]


def _fit(boxes, view, x, y, w, h, scale=None, pad=0.0):
    """A Placed that fits `boxes` in the paper rectangle, centred, at `scale` (or the
    largest that fits)."""
    u0, v0, u1, v1 = _extent(boxes, view)
    s = scale or min((w - 2 * pad) / max(u1 - u0, 1), (h - 2 * pad) / max(v1 - v0, 1))
    ox = x + (w - (u1 - u0) * s) / 2
    oy = y + (h - (v1 - v0) * s) / 2
    return Placed(view, s, ox, oy, (u0, v0))


def draw_parts(pen: Pen, placed: Placed, parts: list[Part], *, fill_for=None, offsets=None,
               line=0.3, shaded=True):
    """Fill and stroke each part's visible faces, back to front. `fill_for(part_id, shade)`
    gives the face colour. A part filled in a colour that is not a grey is noted (a region of kind
    colour, when regions are kept): a colour says what a part is made of."""
    boxes = _boxes(parts, offsets)
    paths, coloured = {p.id: p.path for p in parts}, set()
    for f in lw.faces(boxes, placed.view):
        pts = [placed.pt(p) for p in f.points]
        if fill_for:
            fill = fill_for(f.key, f.shade)
        else:
            g = 1 - (0.12 * f.shade if shaded else 0)
            fill = Color(g, g, g)
        if (pen.regions is not None and f.key not in coloured and fill is not None
                and max(fill.red, fill.green, fill.blue) - min(fill.red, fill.green, fill.blue) > GREY):
            coloured.add(f.key)
            pen.regions.append({"kind": "colour", "page": pen.c.getPageNumber() - 1, "box": [0, 0, 0, 0],
                                "part": paths.get(f.key, f.key), "colour": fill.hexval()})
        pen.poly(pts, fill=fill, stroke=INK, w=line)
    return boxes


def overall(sc: Scene, L: dict) -> list[str]:
    """The overall size as the instructions print it: the piece's, or, when it is made of things that stand
    apart (Scene.apart), each one's with its name, so that no gap the model chose is printed as a size."""
    return [line for line, _ in overall_said(sc, L)]


def overall_said(sc: Scene, L: dict) -> list[tuple[str, list[str]]]:
    """overall's lines, each with the paths of the parts it measures across."""
    things = sc.apart()
    say = lambda lo, hi: " × ".join(_fmt(b - a) for a, b in zip(lo, hi)) + " mm"  # noqa: E731
    if len(things) == 1:
        return [(f"{L['overall']} : {say(*things[0][1:3])}", things[0][3])]
    return [(f"{L['overall']}, {name} : {say(lo, hi)}", paths) for name, lo, hi, paths in things]


def _tone(shade: float, base=PLAIN) -> Color:
    k = 1 - 0.22 * shade
    return Color(base.red * k, base.green * k, base.blue * k)


def _reaches_view(part: Part, lo, hi, view: lw.View) -> bool:
    """Whether a cut reaches the face of its part that the viewer looks at."""
    for k in range(3):
        d = view.direction[k]
        if abs(d) < 1e-9:
            continue
        if d > 0 and lo[k] > part.lo[k] + 0.5:
            return False
        if d < 0 and hi[k] < part.hi[k] - 0.5:
            return False
    return True


def draw_cuts(pen: Pen, placed: Placed, part: Part, offset=(0, 0, 0), color=MARK,
              hatch: bool = True):
    """A part's cuts (a notch), where the view can see them: hatched in the instructions,
    in a drawing as the missing corner it is (blank, its inner edges drawn)."""
    for lo0, hi0 in part.cuts:
        if not _reaches_view(part, lo0, hi0, placed.view):
            continue
        lo = tuple(a + o for a, o in zip(lo0, offset))
        hi = tuple(a + o for a, o in zip(hi0, offset))
        for f in lw.faces({"cut": (lo, hi)}, placed.view):
            pts = [placed.pt(p) for p in f.points]
            if not hatch:
                pen.poly(pts, fill=white, stroke=None)
                plo = [a + o for a, o in zip(part.lo, offset)]
                phi = [a + o for a, o in zip(part.hi, offset)]
                outline = lw.bounds([placed.pt(placed.view.to2d(c))
                                     for c in _box_corners(plo, phi)])
                for a, b in zip(pts, pts[1:] + pts[:1]):
                    vertical_edge = abs(a[0] - b[0]) < 0.05 and min(
                        abs(a[0] - outline[0]), abs(a[0] - outline[2])) < 0.05
                    horizontal_edge = abs(a[1] - b[1]) < 0.05 and min(
                        abs(a[1] - outline[1]), abs(a[1] - outline[3])) < 0.05
                    if not (vertical_edge or horizontal_edge):
                        pen.line(a[0], a[1], b[0], b[1], 0.35, INK)
                continue
            pen.poly(pts, fill=white, stroke=color, w=0.3)
            x0, y0, x1, y1 = lw.bounds(pts)
            c = pen.c
            c.saveState()
            clip = c.beginPath()
            clip.moveTo(pts[0][0] * mm, pts[0][1] * mm)
            for x, y in pts[1:]:
                clip.lineTo(x * mm, y * mm)
            clip.close()
            c.clipPath(clip, stroke=0, fill=0)
            k = -(y1 - y0)
            while k < x1 - x0:
                pen.line(x0 + k, y0, x0 + k + (y1 - y0), y1, 0.12, color)
                k += 1.6
            c.restoreState()


def draw_slots(pen: Pen, placed: Placed, positions, along_axis: int, normal_axis: int,
               offset=(0, 0, 0), color=MARK, size=None):
    """Connectors at `positions`, flat on the face they sit in, at the size their node states
    (length along, thickness across), or a dot where it states none."""
    across = ({0, 1, 2} - {along_axis, normal_axis}).pop()
    for p in positions:
        p = tuple(a + o for a, o in zip(p, offset))
        if size is None:
            x, y = placed(p)
            pen.circle(x, y, DOT, fill=color, stroke=color, w=0)
            continue
        corners = []
        for du, dv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            q = list(p)
            q[along_axis] += du * size[0] / 2
            q[across] += dv * size[1] / 2
            corners.append(placed(tuple(q)))
        pen.poly(corners, fill=color, stroke=None)


def draw_bond(pen: Pen, placed: Placed, joint, offset=(0, 0, 0), color=MARK):
    """The face a joint's glue bonds (the face its parts meet on), hatched, where the glue goes."""
    lo, hi, n = joint.face_lo, joint.face_hi, joint.normal_axis
    u, v = [i for i in range(3) if i != n]
    pts = []
    for a, b in ((lo[u], lo[v]), (hi[u], lo[v]), (hi[u], hi[v]), (lo[u], hi[v])):
        q = [0.0, 0.0, 0.0]
        q[n], q[u], q[v] = lo[n], a, b
        pts.append(placed(tuple(c + o for c, o in zip(q, offset))))
    pen.poly(pts, stroke=color, w=0.3)
    x0, y0, x1, y1 = lw.bounds(pts)
    c = pen.c
    c.saveState()
    clip = c.beginPath()
    clip.moveTo(pts[0][0] * mm, pts[0][1] * mm)
    for x, y in pts[1:]:
        clip.lineTo(x * mm, y * mm)
    clip.close()
    c.clipPath(clip, stroke=0, fill=0)
    k = -(y1 - y0)
    while k < x1 - x0:
        pen.line(x0 + k, y0, x0 + k + (y1 - y0), y1, 0.15, color)
        k += 1.2
    c.restoreState()


# --- the design document ---------------------------------------------------------------

def _frame(pen: Pen, W: float, H: float, sc: Scene, sheet: int, sheets: int, title: str,
           scale: float | None, L: dict):
    pen.rect(10, 10, W - 20, H - 20, stroke=INK, lw_=0.7)
    bw, bh = 180, 36
    x0, y0 = W - 10 - bw, 10
    pen.rect(x0, y0, bw, bh, fill=white, stroke=INK, lw_=0.5)
    pen.line(x0, y0 + 24, x0 + bw, y0 + 24, 0.3)
    pen.line(x0, y0 + 12, x0 + bw, y0 + 12, 0.3)
    for x in (60, 105, 140):
        pen.line(x0 + x, y0, x0 + x, y0 + 24, 0.3)
    pen.text(x0 + 3, y0 + 31, sc.title, 5.2, INK, bold=True)
    pen.text(x0 + 3, y0 + 26.3, title, 3.0, THIN)
    pen.text(x0 + bw - 3, y0 + 26.3, f"{L['version']} {sc.info.get('version', '')}", 3.0, THIN,
             "end")
    materials = sorted({p.material_name for p in sc.parts if p.material_name})
    cells = [
        (0, 12, L["drawn"], ", ".join(sc.info.get("authors", [])) or "-"),
        (60, 12, L["date"], sc.info.get("date") or dt.date.today().isoformat()),
        (105, 12, L["scale"], f"1:{_fmt(1 / scale)}" if scale else "-"),
        (140, 12, L["sheet"], f"{sheet}/{sheets}"),
        (0, 0, L["material"], materials[0] if len(materials) == 1 else L["see_parts"]),
        (105, 0, L["units"], ""),
        (140, 0, "", ""),
    ]
    for x, y, k, v in cells:
        pen.text(x0 + x + 2, y0 + y + 8.6, k, 2.2, THIN)
        pen.text(x0 + x + 2, y0 + y + 3.2, v, _fitted(v, 3.0, (105 if k == L["material"] else 45) - 4), INK,
                 says={"material": [p.path for p in sc.parts]} if k == L["material"] and len(materials) == 1 else None)
    # first-angle projection symbol
    sx, sy = x0 + 152, y0 + 6
    pen.poly([(sx, sy - 3), (sx + 9, sy - 1.5), (sx + 9, sy + 1.5), (sx, sy + 3)], fill=None, w=0.25)
    pen.line(sx - 2, sy, sx + 11, sy, 0.13, THIN, [1, 1])
    pen.circle(sx + 21, sy, 3, fill=white, w=0.25)
    pen.circle(sx + 21, sy, 1.5, fill=white, w=0.25)
    pen.text(x0 + 2, y0 - 4, L["projection"], 2.2, THIN)


def _chain(values):
    return sorted({round(v, 1) for v in values})


def _view_dims(pen: Pen, placed: Placed, sc: Scene, h_axis: int, v_axis: int,
               h_sign: int = 1, chain_h=True, chain_v=True, side_v="left"):
    """A view's dimension chains and overall sizes. The things that stand apart along the view's width
    (Scene.apart) are dimensioned each on its own, the first on side_v and the others on the right: the
    model gives no distance between them (standards_pages.printed_unsupported)."""
    things = [ps for _, _, _, ps in sc.apart()]
    thing = {q: i for i, ps in enumerate(things) for q in ps}
    spans: list[list] = []     # along the width: [lo, hi, the things], things that overlap in the view together
    for ps in sorted(things, key=lambda ps: min(sc.part_at(q).lo[h_axis] for q in ps)):
        lo, hi = min(sc.part_at(q).lo[h_axis] for q in ps), max(sc.part_at(q).hi[h_axis] for q in ps)
        if spans and lo <= spans[-1][1] + TOUCH:
            spans[-1][1] = max(spans[-1][1], hi)
            spans[-1][2].append(ps)
        else:
            spans.append([lo, hi, [ps]])
    size = lambda ps: sum(sc.part_at(q).hi[i] - sc.part_at(q).lo[i] for q in ps for i in range(3))  # noqa: E731
    for k, (_, _, overlapping) in enumerate(spans):
        # things one behind the other in this view: the largest is dimensioned, the others where they stand apart
        ps = max(overlapping, key=size)
        _dims_of(pen, placed, sc, [sc.part_at(q) for q in ps], thing, h_axis, v_axis, chain_h, chain_v,
                 side_v if k == 0 else "right")


def _dims_of(pen: Pen, placed: Placed, sc: Scene, parts: list, thing: dict, h_axis: int, v_axis: int,
             chain_h: bool, chain_v: bool, side_v: str):
    """The chains and overall sizes of `parts`, each dimension saying the parts it measures (Pen.dim's of):
    two of one thing when one thing has both its edges, and one thing's when one spans it."""
    hs = _chain(v for p in parts for v in (p.lo[h_axis], p.hi[h_axis]))
    vs = _chain(v for p in parts for v in (p.lo[v_axis], p.hi[v_axis]))
    lo, hi = sc.lo, sc.hi

    def between(va, vb, axis) -> list[str]:
        at = lambda v: [p.path for p in parts if round(p.lo[axis], 1) == v or round(p.hi[axis], 1) == v]  # noqa: E731
        a, b = at(va), at(vb)
        return next(([x, y] for x in a for y in b if thing[x] == thing[y]), [a[0], b[0]])

    def spanning(v0, v1, axis) -> list[str]:
        groups: dict[int, list] = {}
        for p in parts:
            groups.setdefault(thing[p.path], []).append(p)
        return next(([p.path for p in ps] for ps in groups.values() if round(min(p.lo[axis] for p in ps), 1) == v0
                     and round(max(p.hi[axis] for p in ps), 1) == v1), [p.path for p in parts])

    def at(hv, vv):
        p = [(lo[i] + hi[i]) / 2 for i in range(3)]
        p[h_axis], p[v_axis] = hv, vv
        return placed(tuple(p))

    base = min(at(h, vs[0])[1] for h in hs)
    xs = sorted(at(h, vs[0])[0] for h in hs)
    if chain_h and len(hs) > 2:
        pts = sorted((at(h, vs[0])[0], h) for h in hs)
        for (xa, ha), (xb, hb) in zip(pts, pts[1:]):
            pen.dim((xa, base), (xb, base), -7, _fmt(abs(hb - ha)), of=between(ha, hb, h_axis))
    pen.dim((xs[0], base), (xs[-1], base), -15 if chain_h and len(hs) > 2 else -7,
            _fmt(hs[-1] - hs[0]), of=spanning(hs[0], hs[-1], h_axis))
    ys = sorted(at(hs[0], v)[1] for v in vs)
    if side_v == "left":
        edge = min(at(h, vs[0])[0] for h in hs)
        off1, off2 = -7, -15
    else:
        edge = max(at(h, vs[0])[0] for h in hs)
        off1, off2 = 7, 15
    if chain_v and len(vs) > 2:
        for a, b, va, vb in zip(ys, ys[1:], vs, vs[1:]):
            pen.dim((edge, a), (edge, b), off1, _fmt(vb - va), horizontal=False,
                    of=between(va, vb, v_axis))
    pen.dim((edge, ys[0]), (edge, ys[-1]), off2 if chain_v and len(vs) > 2 else off1,
            _fmt(vs[-1] - vs[0]), horizontal=False, of=spanning(vs[0], vs[-1], v_axis))


def _scale_for(extent_mm: float, room_mm: float) -> float:
    for k in SCALES:
        if extent_mm / k <= room_mm:
            return 1 / k
    return 1 / SCALES[-1]


def _sheet_general(c: Canvas, sc: Scene, L: dict, sheets: int):
    W, H = 420, 297
    pen = Pen(c)
    size = [h - l for l, h in zip(sc.lo, sc.hi)]
    s = _scale_for(max(size[0] + size[1], size[2] + size[1]), 230)
    boxes = _boxes(sc.parts)
    white_faces = lambda k, sh: Color(1, 1, 1)  # noqa: E731
    # front view, top left; the view from the left to its right; the top view below it
    fx, fy = 45, H - 30 - size[2] * s
    front = Placed(lw.FRONT, s, fx, fy, (sc.lo[0], sc.lo[2]))
    left = Placed(lw.LEFT, s, fx + size[0] * s + 40, fy, (-sc.hi[1], sc.lo[2]))
    top = Placed(lw.TOP, s, fx, fy - 40 - size[1] * s, (sc.lo[0], sc.lo[1]))
    for placed, name in ((front, "front"), (left, "left"), (top, "top")):
        draw_parts(pen, placed, sc.parts, fill_for=white_faces, line=0.35)
        u0, v0, u1, v1 = _extent(boxes, placed.view)
        pen.text(placed.pt((u0, v1))[0], placed.pt((u0, v1))[1] + 4, L[name], 3.2, INK, bold=True)
    _view_dims(pen, front, sc, 0, 2)
    _view_dims(pen, left, sc, 1, 2, side_v="right")
    _view_dims(pen, top, sc, 0, 1, chain_h=False, chain_v=False)
    # three-quarter view with the parts' letters
    axo = lw.axonometric()
    ax_box = (240, 50, 165, 88)
    placed = _fit(boxes, axo, *ax_box, pad=18)
    draw_parts(pen, placed, sc.parts, fill_for=lambda k, sh: _tone(sh), line=0.3)
    pen.text(ax_box[0] + 4, ax_box[1] + ax_box[3] - 2, L["axo"], 3.2, INK, bold=True)
    _balloons(pen, placed, sc)
    _frame(pen, W, H, sc, 1, sheets, L["general"], s, L)


def _balloons(pen: Pen, placed: Placed, sc: Scene):
    seen = set()
    cx = sum(placed(p.centre)[0] for p in sc.parts) / len(sc.parts)
    cy = sum(placed(p.centre)[1] for p in sc.parts) / len(sc.parts)
    for p in sc.parts:
        if p.mark in seen:
            continue
        seen.add(p.mark)
        # aim at the middle of the face the part shows most: its top if it has one in view
        tip = placed((p.centre[0], p.centre[1], p.hi[2])) if p.size[2] < min(p.size[:2]) else \
            placed((p.centre[0], p.lo[1], p.centre[2])) if p.size[1] < min(p.size[0], p.size[2]) \
            else placed((p.lo[0], p.centre[1], p.centre[2]))
        dx, dy = tip[0] - cx, tip[1] - cy
        n = (dx * dx + dy * dy) ** 0.5 or 1
        bx, by = tip[0] + dx / n * 22, tip[1] + dy / n * 22
        pen.line(tip[0], tip[1], bx, by, 0.2, INK)
        pen.circle(tip[0], tip[1], 0.6, fill=INK)
        pen.circle(bx, by, 4, fill=white, w=0.35)
        pen.text(bx, by - 1.4, p.mark, 4, INK, "middle", bold=True)


def _fitted(text: str, size: float, width: float, bold: bool = False) -> float:
    """The size (Pen.text's) at which `text` fits `width` mm: `size`, or smaller; never cut short."""
    from reportlab.pdfbase.pdfmetrics import stringWidth

    w = stringWidth(text, "Helvetica-Bold" if bold else "Helvetica", size * mm) / mm
    return size if w <= width else size * width / w


def _parts_table(pen: Pen, x: float, y: float, rows: list[list[str]], widths: list[float],
                 header: list[str], row_h=7.0, size=3.0):
    pen.rect(x, y - row_h, sum(widths), row_h, fill=HexColor("#ece7dd"), stroke=INK, lw_=0.3)
    cx = x
    for h, w in zip(header, widths):
        pen.text(cx + 2, y - row_h + 2.2, h, size, INK, bold=True)
        cx += w
    for i, row in enumerate(rows, 1):
        yy = y - row_h * (i + 1)
        pen.rect(x, yy, sum(widths), row_h, fill=None, stroke=THIN, lw_=0.15)
        cx = x
        for v, w in zip(row, widths):
            text, says = v if isinstance(v, tuple) else (v, None)
            pen.text(cx + 2, yy + 2.2, text, _fitted(text, size, w - 3), INK, says=says)
            cx += w
    return y - row_h * (len(rows) + 1)


def _part_face_axes(p: Part):
    order = sorted(range(3), key=lambda i: p.size[i], reverse=True)
    return order[0], order[1], order[2]   # length, width, thickness axes


def _part_drawing(pen: Pen, sc: Scene, p: Part, x, y, w, h, L: dict):
    """One board, seen on its face: its length and width dimensioned, its thickness and
    grain written, its grooves and cuts drawn where they are."""
    u, v, t = _part_face_axes(p)
    lu, lv = p.size[u], p.size[v]
    s = min((w - 30) / lu, (h - 30) / lv)
    ox, oy = x + (w - lu * s) / 2, y + (h - lv * s) / 2 + 2

    def P(q):  # piece frame -> paper, on this face
        return ox + (q[u] - p.lo[u]) * s, oy + (q[v] - p.lo[v]) * s

    pen.rect(ox, oy, lu * s, lv * s, fill=_tone(0.1), stroke=INK, lw_=0.35)
    for lo, hi in p.cuts:
        a, b = P(lo), P(hi)
        x0, y0, x1, y1 = min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])
        pen.rect(x0, y0, x1 - x0, y1 - y0, fill=white, stroke=INK, lw_=0.3)
        # each side measured on the side of the cut that is inside the board
        top = y1 < oy + lv * s - 0.5
        right = x1 < ox + lu * s - 0.5
        pen.dim((x0, y1 if top else y0), (x1, y1 if top else y0), 4 if top else -4,
                _fmt(abs(hi[u] - lo[u])), size=2.2, of=[p.path])
        pen.dim((x1 if right else x0, y0), (x1 if right else x0, y1), 4 if right else -4,
                _fmt(abs(hi[v] - lo[v])), horizontal=False, size=2.2, of=[p.path])
    # grooves of every joint this part is in
    for j in sc.joints:
        if p.id not in j.parts:
            continue
        on_face = j.normal_axis == t
        for q in j.positions:
            cu, cv = P(q)
            if j.size is None:
                pen.circle(cu, cv, DOT, fill=MARK, stroke=MARK, w=0)
                continue
            length, thickness = j.size
            if on_face:
                du = length / 2 * s if j.along_axis == u else thickness / 2 * s
                dv = thickness / 2 * s if j.along_axis == u else length / 2 * s
                pen.rect(cu - du, cv - dv, 2 * du, 2 * dv, fill=MARK, stroke=None)
            else:  # in the edge: a tick across the outline
                if j.along_axis == u:
                    pen.rect(cu - length / 2 * s, cv - 1.2, length * s, 2.4, fill=MARK, stroke=None)
                else:
                    pen.rect(cu - 1.2, cv - length / 2 * s, 2.4, length * s, fill=MARK, stroke=None)
    pen.dim((ox, oy), (ox + lu * s, oy), -6, _fmt(lu), of=[p.path])
    pen.dim((ox, oy), (ox, oy + lv * s), -6, _fmt(lv), horizontal=False, of=[p.path])
    thick = p.size[t] / p.sheets
    label = f"{p.mark}  {p.name}"
    pen.text(x + 2, y + h - 4, label, 3.4, INK, bold=True, says={"name": p.path})
    extra = f"{L['thick']} {_fmt(p.size[t])}" if p.sheets == 1 else \
        f"{L['thick']} {_fmt(p.size[t])} ({L['glued_from']} {p.sheets} {L['sheets_of']} {_fmt(thick)})"
    pen.text(x + 2, y + h - 8.5, extra, 2.6, THIN, says={"size": [p.path]})
    if p.grain:
        gx, gy = ox + lu * s * 0.2, oy + lv * s / 2
        pen.line(gx, gy, gx + lu * s * 0.6, gy, 0.25, THIN)
        pen.arrowhead(gx + lu * s * 0.6, gy, 1, 0, 2.2, THIN)
        pen.arrowhead(gx, gy, -1, 0, 2.2, THIN)
        pen.text(gx + lu * s * 0.3, gy + 1.2, L["grain_along"], 2.4, THIN, "middle")


PART_ROW = 45.0   # mm: the least height a part's drawing takes on the parts sheets
PARTS_FOOT = 52.0  # mm: where the part drawings stop, above the title block


def _distinct(sc: Scene) -> list[Part]:
    distinct = []
    for p in sc.parts:
        if p.mark not in [d.mark for d in distinct]:
            distinct.append(p)
    return distinct


def _part_sheets(sc: Scene) -> list[tuple[float, list[Part]]]:
    """The part drawings by sheet, each (where its grid starts, its parts): under the parts and joints tables
    on the first, as many rows as fit PART_ROW high, then on sheets of their own; never smaller."""
    H = 297
    distinct = _distinct(sc)
    bottom = H - 26 - 7.0 * (len(distinct) + 1)    # under the parts table, and the joints table (_sheet_parts)
    if sc.joints:
        bottom = min(bottom, H - 26 - 6.0 * (len(sc.joints) + 1) - (6 if any(not j.stated for j in sc.joints) else 0))
    top = bottom - 6
    out, i = [], 0
    while True:
        n = 3 * max(0, int((top - PARTS_FOOT) // PART_ROW))
        out.append((top, distinct[i:i + n]))
        i += n
        if i >= len(distinct):
            return out
        top = H - 30


def _sheet_parts(c: Canvas, sc: Scene, L: dict, sheets: int) -> int:
    """The parts sheets: the parts and joints tables, and a drawing of each part (_part_sheets); returns how
    many sheets they took, numbered from 2."""
    W, H = 420, 297
    pen = Pen(c)
    distinct = _distinct(sc)
    qty = {m: sum(pp.sheets for pp in sc.parts if pp.mark == m) for m in {p.mark for p in sc.parts}}
    rows = []
    for p in distinct:
        dims = sorted(p.size, reverse=True)
        size = {"size": [p.path]}
        rows.append([p.mark, (p.name, {"name": p.path}), str(qty[p.mark]), (_fmt(dims[0]), size),
                     (_fmt(dims[1]), size), (_fmt(dims[2] / p.sheets), size),
                     (p.material_name, {"material": [p.path]}),
                     L["grain_along"] if p.grain else ""])
    pen.text(18, H - 22, L["parts"], 5, INK, bold=True)
    bottom = _parts_table(pen, 18, H - 26, rows, [12, 66, 10, 18, 18, 12, 60, 12],
                          [L["mark"], L["name"], L["qty"], L["length"], L["width"],
                           L["thickness"], L["material"], L["grain"]])
    jrows = [[" + ".join(sc.part(i).mark for i in j.parts), (j.connector, {"connector": [j.path]}),
              "" if j.fasteners and len(j.uncounted) == len(j.fasteners) else str(j.count),   # a glue: no count
              j.setting, ", ".join(j.tools)] for j in sc.joints]
    jbottom = bottom
    if jrows:
        pen.text(238, H - 22, L["connectors"], 5, INK, bold=True)
        jbottom = _parts_table(pen, 238, H - 26, jrows, [16, 50, 10, 16, 72],
                               [L["joins"], "", L["count"], L["setting"], L["tool"]],
                               row_h=6.0, size=2.6)
        if any(not j.stated for j in sc.joints):
            pen.text(238, jbottom - 4, L["positions_note"], 2.4, THIN)
            jbottom -= 6
    # one drawing per distinct board, in a grid, over as many sheets as they take
    cols = 3
    for n, (top, shown) in enumerate(_part_sheets(sc)):
        if n:
            _frame(pen, W, H, sc, 1 + n, sheets, L["parts"], None, L)
            c.showPage()
            pen.text(18, H - 22, L["parts"], 5, INK, bold=True, role="heading")
        cw, ch = (W - 36) / cols, (top - PARTS_FOOT) / max(1, (len(shown) + cols - 1) // cols)
        ch = min(ch, 95)
        for i, p in enumerate(shown):
            r, k = divmod(i, cols)
            x, y = 18 + k * cw, top - (r + 1) * ch
            pen.rect(x, y, cw - 4, ch - 4, fill=None, stroke=THIN, lw_=0.15)
            _part_drawing(pen, sc, p, x, y, cw - 4, ch - 4, L)
    _frame(pen, W, H, sc, 1 + len(_part_sheets(sc)), sheets, L["parts"], None, L)
    return len(_part_sheets(sc))


def _wrap(text: str, width_chars: int) -> list[str]:
    out, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > width_chars:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out


# The design notes: sections, each a heading and its paragraphs; a paragraph is a text, or a text
# and the lines under it (an open point and what would settle it)
Notes = list[tuple[str, list]]


def _paragraphs(texts: list) -> list[tuple[int, str]]:
    """(depth, text) for each paragraph of a section and each line under one."""
    out = []
    for t in texts:
        text, under = (t, []) if isinstance(t, str) else (t[0], list(t[1]))
        out.append((0, text))
        out += [(1, u) for u in under]
    return out
NOTES_FLOOR = 52  # mm: the lowest a line of notes goes, above the title block
NOTES_TOP = 297 - 22  # mm: where the notes start on a sheet of their own


def _check_height(row: dict) -> float:
    return 5 + 4.2 * max(len(_wrap(row["requirement"], 70)), len(_wrap(row["result"], 80)))


def _note_lines(notes: Notes, L: dict) -> list[tuple]:
    """The notes as lines to set one under the other: (x, text, size, colour, bold, step, keep),
    step being the space the line takes, keep that it goes on the sheet of the line after it (a
    title or a heading is never left at the foot of a sheet)."""
    out = [(18, L["notes"], 4.2, INK, True, 8, True)]
    for heading, texts in notes:
        if heading:
            out.append((18, heading, 3.4, INK, True, 5.5, True))
        for depth, text in _paragraphs(texts):
            x = 18 + 8 * depth
            lines = _wrap(text, 150 - 6 * depth)
            for i, line in enumerate(lines):
                last = i == len(lines) - 1
                out.append((x + 4 if i else x, (("- ", "· ")[depth] if i == 0 else "") + line, 3.0,
                            INK if depth == 0 else THIN, False,
                            4.4 + ((1.5 if depth == 0 else 0.5) if last else 0), False))
        x, text, size, colour, bold, step, keep = out[-1]
        out[-1] = (x, text, size, colour, bold, step + 3, keep)
    return out


def _flow(lines: list[tuple], first_top: float) -> list[tuple[float, list[tuple]]]:
    """The notes' lines cut into sheets: the first starts at `first_top` under the checks, each
    next at the top of a sheet of its own, the notes' title said again at its head."""
    pages, y, page = [], first_top, []
    for i, line in enumerate(lines):
        need = line[5] + (lines[i + 1][5] if line[6] and i + 1 < len(lines) else 0)
        if page and y - need < NOTES_FLOOR:
            pages.append((first_top if not pages else NOTES_TOP, page))
            y, page = NOTES_TOP - 8, [lines[0]]
        page.append(line)
        y -= line[5]
    if page:
        pages.append((first_top if not pages else NOTES_TOP, page))
    if pages and len(pages[0][1]) == 1:  # only the title fitted under the checks
        pages[0] = (pages[0][0], [])
    return pages


def _set_lines(pen: Pen, lines: list[tuple], y: float) -> None:
    for x, text, size, colour, bold, step, _ in lines:
        pen.text(x, y, text, size, colour, bold=bold)
        y -= step


def _sheet_notes(c: Canvas, sc: Scene, lines: list[tuple], L: dict, sheet: int, sheets: int):
    W, H = 420, 297
    pen = Pen(c)
    _set_lines(pen, lines, NOTES_TOP)
    _frame(pen, W, H, sc, sheet, sheets, L["notes"], None, L)


def _sheet_checks(c: Canvas, sc: Scene, checks: list[dict], L: dict, sheets: int,
                  notes: tuple[float, list[tuple]] | None = None, sheet: int = 3):
    W, H = 420, 297
    pen = Pen(c)
    pen.text(18, H - 22, L["checks"], 5, INK, bold=True)
    y = H - 30
    colours = {"ok": OK, "fail": MARK, "open": OPEN, "info": THIN}
    for row in checks:
        lines = _wrap(row["requirement"], 70)
        res = _wrap(row["result"], 80)
        n = max(len(lines), len(res))
        hgt = _check_height(row)
        pen.rect(18, y - hgt, 384, hgt, fill=None, stroke=THIN, lw_=0.15)
        col = colours[row["verdict"]]
        pen.rect(20, y - hgt + 1.5, 22, hgt - 3, fill=col, stroke=None)
        pen.text(31, y - hgt / 2 - 1.2, L[row["verdict"]], 3.2, white, "middle", bold=True)
        for i, s in enumerate(lines):
            pen.text(46, y - 5 - 4.2 * i, s, 3.0, INK, bold=i == 0)
        for i, s in enumerate(res):
            pen.text(205, y - 5 - 4.2 * i, s, 3.0, INK)
        y -= hgt
    if notes and notes[1]:
        _set_lines(pen, notes[1], notes[0])
    _frame(pen, W, H, sc, sheet, sheets, L["checks"], None, L)


def design_document(sc: Scene, path: Path, checks: list[dict], lang: str = "fr",
                    notes: Notes | None = None, regions: list | None = None, words: list | None = None) -> Path:
    """The design file of a piece, A3 landscape: the general views, the parts, the checks with
    the design notes under them, the notes going on over as many sheets of their own as they
    need. `notes` are the caller's sections (a heading and its paragraphs each); given none, the
    piece's payload description is the notes, one paragraph each, under no heading. `regions` and `words`,
    lists, get what its pens note (Pen.note, Pen.text), which pages.model makes the plans as drawn."""
    L = LABELS[lang]
    if notes is None:
        notes = [("", list(sc.info.get("description") or []))] if sc.info.get("description") else []
    pages = _flow(_note_lines(notes, L), 297 - 30 - sum(_check_height(r) for r in checks) - 10) if notes else []
    parts = len(_part_sheets(sc))
    sheets = 2 + parts + max(0, len(pages) - 1)
    c = Canvas(str(path), pagesize=landscape(A3))
    c.drawn_regions, c.drawn_words = regions, words
    c.setTitle(f"{sc.title} - {sc.info.get('version', '')}")
    _sheet_general(c, sc, L, sheets)
    c.showPage()
    _sheet_parts(c, sc, L, sheets)
    c.showPage()
    _sheet_checks(c, sc, checks, L, sheets, pages[0] if pages else None, sheet=2 + parts)
    c.showPage()
    for sheet, (_, lines) in enumerate(pages[1:], start=3 + parts):
        _sheet_notes(c, sc, lines, L, sheet, sheets)
        c.showPage()
    c.save()
    return path


# --- the assembly instructions ----------------------------------------------------------

def _fastening(pen: Pen, x, y, n: int | None = None, size=None, scale=1.0, joints: list[str] = (), fastener: str = ""):
    """What fastens a joint, as the steps' pictures mark it where it goes (draw_slots): a bar of the
    connector's own proportions when its node states its size (length, thickness), else the dot; and how
    many. It claims no kind of connector the model does not state. When regions are kept it notes what it
    drew and for which `joints` (a region of kind fastening: drawn, the bar's length and thickness, or
    none for the dot), for a standard to hold the drawing to their connectors, or to `fastener` (a path) when it
    marks that one of the things they use."""
    if size and size[0] > 0:
        w = 16 * scale
        h = max(1.2 * scale, min(6 * scale, w * size[1] / size[0]))
        pen.rect(x, y + (6 * scale - h) / 2, w, h, fill=MARK, stroke=None)
        drawn = [round(w, 3), round(h, 3)]
    else:
        pen.circle(x + 8 * scale, y + 3 * scale, 1.8 * scale, fill=MARK, stroke=MARK, w=0)
        drawn = None
    if pen.regions is not None:
        pen.regions.append({"kind": "fastening", "page": pen.c.getPageNumber() - 1, "box": [0, 0, 0, 0],
                            "joints": list(joints), "drawn": drawn, **({"fastener": fastener} if fastener else {})})
    if n is not None:
        pen.text(x + 19 * scale, y + 1.2 * scale, f"{n} ×", 5 * scale, INK, bold=True)


def _pin(pen: Pen, x, y, size: float = 1.0) -> float:
    """A place's mark, a map pin (a round head over a point), its foot at (x, y) mm; returns its width."""
    pen.poly([(x + 1.5 * size, y + 4 * size), (x + 3.5 * size, y + 4 * size), (x + 2.5 * size, y)], fill=INK, stroke=None)
    pen.circle(x + 2.5 * size, y + 5.2 * size, 1.9 * size, fill=INK, stroke=INK)
    pen.circle(x + 2.5 * size, y + 5.2 * size, 0.7 * size, fill=white, stroke=white)
    return 5 * size


def _place_mark(pen: Pen, x, y, place: str) -> float:
    """A place's pin and name, as a tool badge's height; returns the width drawn."""
    w = _pin(pen, x, y)
    pen.text(x + w + 1, y + 2.6, place, 3.2, INK, bold=True, role="label")
    return w + 1 + len(place) * 1.9


def _tool_badge(pen: Pen, x, y, name: str) -> float:
    w = 4 + len(name) * 1.9
    pen._seen((x, y), (x + w, y + 8))
    pen.c.setStrokeColor(INK)
    pen.c.setLineWidth(0.3 * mm)
    pen.c.roundRect(x * mm, y * mm, w * mm, 8 * mm, 2 * mm, stroke=1, fill=0)
    pen.text(x + 2, y + 2.6, name, 3.2, INK, role="label")
    return w


def _assembly_picture(pen: Pen, sc: Scene, placed_ids: list[str], new_ids: list[str],
                      joints: list, directions: dict, box, explode: float, aside: bool = False,
                      wholes: dict | None = None):
    """The state after this step: what was already there in white (the parts earlier steps brought in, and
    what the piece is fixed to: sc.existing), the new parts darker,
    pulled back along the way they come in, arrows to where they go, and the connectors
    of the joints the step closes. Returns where it was placed and what it shows: the parts
    already there (shows), those brought in (brings) and the letters they carry (kinds), the letters drawn
    beside them (lettered), the assemblies brought in whole (wholes), those of
    them drawn with a line to where they go (guided), the joints the step closes (closes) and those
    whose connectors are drawn (fastened), how much of each part brought in is left to see (visible)
    and of the parts already there taken together (context). `aside`: the step puts an assembly together
    away from the piece, so what the piece is fixed to is not in the picture. `wholes` (part id -> the
    assembly it comes in with): those parts come in as one thing, of one kind, the assembly's, with one
    line to where it goes, and each shows as much as the one of them that shows most."""
    wholes = wholes or {}
    view = lw.axonometric()
    moving_ids = [i for i in new_ids if i in directions] or list(new_ids)
    old = ([] if aside else sc.existing) + [p for p in sc.parts
                                            if p.id in placed_ids or (p.id in new_ids and p.id not in moving_ids)]
    new = [p for p in sc.parts if p.id in moving_ids]
    new_ids = moving_ids
    offsets = {}
    for p in new:
        d = directions.get(p.id) or _away(sc, p)
        offsets[p.id] = tuple(k * explode for k in d)
    shown = old + new
    boxes = _boxes(shown, offsets)
    placed = _fit(boxes, view, *box, pad=10)
    fill = lambda k, sh: _tone(sh, NEW) if k in new_ids else Color(1 - 0.1 * sh, 1 - 0.1 * sh, 1 - 0.1 * sh)  # noqa: E731
    draw_parts(pen, placed, shown, fill_for=fill, offsets=offsets, line=0.35)
    for j in joints:
        moving = next((i for i in j.parts if i in new_ids), None)
        fixed = next((i for i in j.parts if i not in new_ids), None)
        off = (0, 0, 0) if fixed in placed_ids or fixed is None else offsets.get(fixed, (0, 0, 0))
        draw_slots(pen, placed, j.positions, j.along_axis, j.normal_axis, off, size=j.size)
        if j.bonded:
            draw_bond(pen, placed, j, off)
    guided = []
    lined = set()
    for p in new:
        o = offsets[p.id]
        centre = p.centre
        if p.id in wholes:     # one line for the whole, from its middle
            mates = [q for q in new if wholes.get(q.id) == wholes[p.id]]
            centre = tuple((min(q.lo[i] for q in mates) + max(q.hi[i] for q in mates)) / 2 for i in range(3))
        a = placed(tuple(c + k for c, k in zip(centre, o)))
        b = placed(centre)
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) < 3:
            continue
        if p.id in wholes and wholes[p.id] in lined:
            guided.append(p.id)
            continue
        lined.add(wholes.get(p.id))
        pen.line(a[0], a[1], b[0] + (a[0] - b[0]) * 0.25, b[1] + (a[1] - b[1]) * 0.25, 0.4, INK,
                 [2, 1.2])
        pen.arrowhead(b[0] + (a[0] - b[0]) * 0.25, b[1] + (a[1] - b[1]) * 0.25,
                      b[0] - a[0], b[1] - a[1], 3.2)
        guided.append(p.id)
    lettered, spots = [], []
    for p in new:      # each kind of part brought in carries its letter, as on the page of what is needed
        if p.id in wholes or not p.mark or p.mark in lettered:
            continue
        u, v = placed(tuple(c + k for c, k in zip(p.centre, offsets[p.id])))
        u += 5
        while any(math.dist((u, v), q) < 2 * 3.2 + 0.8 for q in spots):
            u += 2 * 3.2 + 1.0                             # beside a letter already there, clear of it
        spots.append((u, v))
        pen.circle(u, v + 5, 3.2, fill=white, w=0.35)
        pen.text(u, v + 3.8, p.mark, 3.6, INK, "middle", bold=True)
        lettered.append(p.mark)
    from .pages import shares
    left, context = shares(boxes, view, [p.id for p in old])
    return placed, {"shows": [p.id for p in old], "brings": [p.id for p in new],
                    "kinds": sorted({wholes.get(p.id) or p.mark for p in new}), "guided": guided,
                    "lettered": lettered, "wholes": sorted({wholes[p.id] for p in new if p.id in wholes}),
                    "closes": [j.id for j in joints], "fastened": [j.id for j in joints if j.positions or j.bonded],
                    "visible": {p.id: max(left.get(q.id, 0.0) for q in new if wholes.get(q.id, q.id) == wholes.get(p.id, p.id))
                                for p in new}, "context": context}


def _away(sc: Scene, p: Part):
    """The way a part comes in when the step does not say (natives.away, which the standards judge too)."""
    return away(sc.lo, sc.hi, p.centre)


def _prepare_picture(pen: Pen, sc: Scene, step, box):
    """The boards a preparation step works on, side by side: glued-up boards split into
    their sheets, cuts hatched, the grooves of the step's joints marked."""
    view = lw.axonometric()
    parts = [sc.part(i) for i in step.add] or sc.parts
    gap = 120.0
    x = 0.0
    shown, offsets, extra = [], {}, []
    for p in parts:
        shift = (x - p.lo[0], -p.lo[1], -p.lo[2])
        if p.sheets > 1 and p.id in step.split:
            t = p.size[2] / p.sheets
            for s in range(p.sheets):
                q = Part(f"{p.path}#{s}", f"{p.id}#{s}", p.name, p.mark,
                         (p.lo[0], p.lo[1], p.lo[2] + s * t), (p.hi[0], p.hi[1], p.lo[2] + (s + 1) * t),
                         p.material, p.material_name)
                shown.append(q)
                offsets[q.id] = (shift[0], shift[1], shift[2] + s * 90)
                if s:
                    extra.append((q, offsets[q.id], (shift[0], shift[1], shift[2] + s * t)))
        else:
            shown.append(p)
            offsets[p.id] = shift
        x += p.size[0] + gap
    boxes = _boxes(shown, offsets)
    placed = _fit(boxes, view, *box, pad=12)
    draw_parts(pen, placed, shown, fill_for=lambda k, sh: _tone(sh), offsets=offsets, line=0.35)
    for p in parts:
        if p.cuts and p.id in step.cuts:
            draw_cuts(pen, placed, p, offsets.get(p.id, (0, 0, 0)))
    for j in sc.joints:
        if j.id not in step.joints:
            continue
        for pid in j.parts:
            if pid in offsets:
                draw_slots(pen, placed, j.positions, j.along_axis, j.normal_axis, offsets[pid],
                           size=j.size)
    for q, at, home in extra:
        a = placed(tuple(c + k for c, k in zip(q.centre, at)))
        b = placed(tuple(c + k for c, k in zip(q.centre, home)))
        pen.line(a[0], a[1], b[0], b[1] + 6, 0.4, INK, [2, 1.2])
        pen.arrowhead(b[0], b[1] + 6, b[0] - a[0], b[1] + 6 - a[1], 3.2)
    for p in parts:
        c = placed(tuple(a + b for a, b in zip((p.centre[0], p.lo[1], p.hi[2]), offsets.get(p.id, (0, 0, 0)))))
        pen.circle(c[0], c[1] + 9, 3.6, fill=white, w=0.35)
        pen.text(c[0], c[1] + 7.7, p.mark, 3.8, INK, "middle", bold=True)




def cut_sentences(p: Part, L: dict, lang: str) -> list[str]:
    """What the card says beside a board: where to mark each cut, measured from the edges
    it touches, and the order to saw its lines in."""
    marks, starts, total = [], 0, 0
    for lo, hi in p.cuts:
        plan = cut_plan(p, lo, hi)
        said = []
        for _axis, edge, dist, off in plan.measures:
            if off:
                said.append(f"{_fmt(off)} {L['to']} {_fmt(off + dist)} {L['from']} "
                            f"{L['edge'][edge]}")
            else:
                said.append(f"{_fmt(dist)} {L['from']} {L['edge'][edge]}")
        if plan.depth is not None:
            said.append(L["deep"].format(d=_fmt(plan.depth)))
        marks.append(", ".join(said))
        starts += plan.from_edge
        total += len(plan.lines)
    colon = " : " if lang == "fr" else ": "
    sep = " ; " if lang == "fr" else "; "
    return [f"{L['mark_out']}{colon}{sep.join(marks)}.",
            L["saw_from_edge"] if starts == total else
            L["saw_from_hole"] if starts == 0 else L["saw_mixed"]]


def tool_groups(sc: Scene, tools: list[str], places: dict[str, str] | None) -> list[tuple[str | None, list[str]]]:
    """What is needed's tools by place: [(place name, its tools)] in the order of `places` (where the person has
    each tool, {path: place}), then (None, the others) when a place is drawn. Without `places`, or when none
    of the tools is at a place of the person's, the one group (None, every tool): the tools under "Tools"."""
    at = {name: (places or {}).get(path) for name, path in sc.tool_paths.items()}
    order = list(dict.fromkeys(v for v in (places or {}).values()))
    named = [p for p in order if any(at.get(t) == p for t in tools)]
    if not named:
        return [(None, list(tools))]
    rest = [t for t in tools if at.get(t) not in named]
    return [(p, [t for t in tools if at.get(t) == p]) for p in named] + ([(None, rest)] if rest else [])


def _cut_block(pen: Pen, box, step, p, qty: int, brief) -> None:
    """A part's cut drawn in `box` as its own block of the step (sawing.sawing_frames), noted with the part, how
    many when more than one, and the saw it shows at work when there is one."""
    from .sawing import SAW, sawing_frames
    saw = next((t for t in p.tools if t.model and SAW in t.follows), None)
    pen.note("block", box, step=step.number, part=p.id, count=qty, **({"tool": saw.path} if saw else {}))
    sawing_frames(pen, box, p, qty, brief(saw))


def assembly_instructions(sc: Scene, path: Path, lang: str = "fr", regions: list | None = None,
                          words: list | None = None, at_work: set[str] | None = None, progress=None,
                          places: dict[str, str] | None = None) -> Path:
    """Picture-first assembly instructions, A4 portrait. A piece whose payload instructions is short
    leaves out how its tools are used: the saw and the jointer drawn at work and the test groove;
    what the piece needs (the cuts, the marks, the settings, the holes) stays. A cut is drawn by
    sawing.sawing_frames, a joint's grooves by grooving.grooving_pages; neither prints a sentence.
    `regions`, a list, gets where each picture is drawn (Pen.note): the cover, each board, each step's
    picture, each block of a step drawn on its own (a cut's frames, the grooving settings and each kind of
    joint) and the frames and drawings in it, in the order drawn; steps.instruction_screens cuts them out.
    A step's picture is noted with what it shows (_assembly_picture), and `words`, a list, gets every text
    set on a page: pages.model makes of both the instructions as drawn, which a standard judges.
    `at_work`, when given, overrides the payload's choice tool by tool: a block draws its tool at work when
    the tool's path is in it, and leaves it out otherwise (an empty set: no tool at work). `progress`, when
    given, is called with (steps drawn, steps) before each step. `places`, when given, is where the person
    making the document has each tool ({tool path: the place's name}, the places in their order): a step's head
    ends with the place that holds every tool it names by path (scene.place_of), and what is needed lists each
    place's tools under its pin and name, then the others under "Other tools"."""
    L = LABELS[lang]
    short = sc.info.get("instructions") == "short"

    def brief(tool) -> bool:
        """Whether a block leaves out how its tool is used: the payload's choice for every tool, or, with
        `at_work` given, every tool but those it names (by path)."""
        return short if at_work is None else not (tool and tool.path in at_work)
    W, H = 210, 297
    c = Canvas(str(path), pagesize=A4)
    c.setTitle(f"{sc.title} - {L['assemble']}")
    pen = Pen(c)
    pen.regions = regions
    pen.words = words
    view = lw.axonometric()
    boxes = _boxes(sc.parts)
    # cover
    pen.text(W / 2, H - 40, sc.title, 11, INK, "middle", bold=True, role="name")
    pen.text(W / 2, H - 50, f"{L['version']} {sc.info.get('version', '')}", 4, THIN, "middle")
    pen.note("cover", (20, 70, W - 40, 150))
    placed = _fit(boxes, view, 20, 70, W - 40, 150, pad=10)
    draw_parts(pen, placed, sc.parts, fill_for=lambda k, sh: _tone(sh), line=0.4)
    size = [h - l for l, h in zip(sc.lo, sc.hi)]
    for k, (line, paths) in enumerate(overall_said(sc, L)):     # one size for each thing that stands apart
        pen.text(W / 2, 50 - 6 * k, line, 4, INK, "middle", role="label", says={"size": paths})
    c.showPage()
    # what is needed
    pen.text(15, H - 20, L["inbox"], 7, INK, bold=True, role="heading")
    pen.text(15, H - 32, L["boards"], 4.5, INK, bold=True, role="heading")
    distinct = []
    for p in sc.parts:
        if p.mark not in [d.mark for d in distinct]:
            distinct.append(p)
    qty = {m: sum(pp.sheets for pp in sc.parts if pp.mark == m) for m in {p.mark for p in sc.parts}}
    cw, ch = (W - 30) / 3, 52
    FOOT = 14            # mm: nothing of what is needed is set lower on a page
    top, first = H - 40, 0   # where the grid starts on this page, and the row it starts with
    for i, p in enumerate(distinct):
        r, k = divmod(i, 3)
        if top - (r - first + 1) * ch - 2 < FOOT:    # this row would run off the page: it starts the next
            c.showPage()
            top, first = H - 20, r
        x, y = 15 + k * cw, top - (r - first + 1) * ch
        if p.sheets > 1:  # a glued-up part comes as its sheets: draw one, lying flat
            board = Part(p.path, p.id, p.name, p.mark, (0, 0, 0),
                         tuple(sorted(p.size, reverse=True)[:2]) + (sorted(p.size)[0] / p.sheets,),
                         p.material, p.material_name)
            shift = (0, 0, 0)
        else:             # as it stands in the piece, with its cuts
            board, shift = p, tuple(-a for a in p.lo)
        pen.note("board", (x, y + 10, cw - 6, ch - 14), blank=(x + 1.2, y + ch - 13, 10, 10), mark=p.mark)
        shown = _boxes([board], {board.id: shift})
        bplaced = _fit(shown, view, x, y + 10, cw - 6, ch - 14, pad=4)
        draw_parts(pen, bplaced, [board], fill_for=lambda k, sh: _tone(sh), offsets={board.id: shift},
                   line=0.35)
        pen.circle(x + 6, y + ch - 8, 4.2, fill=white, w=0.4)
        pen.text(x + 6, y + ch - 9.6, p.mark, 4.6, INK, "middle", bold=True)
        pen.text(x + cw / 2, y + 3, f"{qty[p.mark]} ×", 5, INK, "middle", bold=True)
        dims = p.board()
        pen.text(x + cw / 2, y - 2, f"{_fmt(dims[0])} × {_fmt(dims[1])} × {_fmt(dims[2])}",
                 2.8, THIN, "middle", says={"size": [p.path]})
    yy = top - ((len(distinct) + 2) // 3 - first) * ch - 16
    fastenings: dict[str, list] = {}     # each thing that fastens: how many, its size when it states one, its joints,
    for j in sc.joints:                  # its path; a joint that uses two (plugs and screws) counts each, and
        for used, name, size in j.fasteners or [("", "", None)]:   # what is not counted in pieces has no count
            kind = fastenings.setdefault(name, [None if used in j.uncounted else 0, size, [], used])
            if kind[0] is not None:
                kind[0] += j.count
            kind[2].append(j.path)
    if fastenings and yy - 14 * len(fastenings) - 4 < FOOT:
        c.showPage()
        yy = H - 20
    if fastenings:
        pen.text(15, yy, L["hardware"], 4.5, INK, bold=True, role="heading")
    for name in sorted(fastenings):
        yy -= 14
        _fastening(pen, 18, yy, fastenings[name][0], fastenings[name][1], 1.2, joints=fastenings[name][2],
                   fastener=fastenings[name][3])
        label = name or L["unstated"]
        pen.text(65, yy + 3, label, _fitted(label, 3.4, W - 15 - 65), INK, role="label",
                 says={"connector": fastenings[name][2], **({"fastener": fastenings[name][3]} if name else {})})
    yy -= 14
    tools = []
    for s in sc.steps:
        for t in s.tools:
            if t not in tools:
                tools.append(t)
    for j in sc.joints:
        for t in j.tools:
            if t not in tools:
                tools.append(t)
    if tools and yy - 13 < FOOT:
        c.showPage()
        yy = H - 20
    if tools:
        pen.text(15, yy, L["tools"], 4.5, INK, bold=True, role="heading")
    x = 15
    row = yy - 13
    groups = tool_groups(sc, tools, places)
    for place, group in groups:
        if place is not None or len(groups) > 1:     # a heading only once the tools are told apart by place
            if x > 15:
                x, row = 15, row - 11
            if row < FOOT:
                c.showPage()
                x, row = 15, H - 30
            if place is not None:
                _place_mark(pen, 15, row, place)
            else:
                pen.text(15, row + 2.6, L["other_tools"], 3.2, INK, bold=True, role="heading")
            x, row = 15, row - 11
        for t in group:
            w = 4 + len(t) * 1.9
            if x > 15 and x + w > W - 15:
                x, row = 15, row - 11
            if row < FOOT:
                c.showPage()
                x, row = 15, H - 30
            x += _tool_badge(pen, x, row, t) + 4
    c.showPage()
    # the steps, two to a page
    explode = drawn_apart(sc.lo, sc.hi)
    placed_ids: list[str] = []
    built: dict[str, list[str]] = {}   # assembly id -> its parts put together aside so far
    slots = [(15, 158, W - 30, 118), (15, 22, W - 30, 118)]
    slot = 0   # the next free half page, counted from the first page of steps
    band = None   # the top of the next band free in the half page of steps said in a sentence alone, if one is open
    BAND = 23     # mm: a step said in a sentence alone, its number and up to four lines
    for done, step in enumerate(sc.steps):
        if progress:
            progress(done, len(sc.steps))
        if not (step.add or step.joints or step.cuts or step.prepare):
            # it brings in, closes and cuts nothing: no picture says it (it would draw the one before again),
            # so its number and its sentence, in a band; such steps one after the other share a half page
            x, y, w, h = slots[slot % 2] if band is None else slots[(slot - 1) % 2]
            if band is None or band - BAND < y:
                x, y, w, h = slots[slot % 2]
                if slot % 2 == 0 and slot:
                    c.showPage()
                if slot % 2 == 0:
                    pen.text(15, H - 12, L["assemble"], 3.4, THIN, role="heading")
                else:
                    pen.line(15, 148, W - 15, 148, 0.2, THIN, [1.5, 1.5])
                band = y + h
                slot += 1
            top = band
            pen.rect(x, top - 12, 12, 12, fill=INK, stroke=None)
            pen.text(x + 6, top - 9, str(step.number), 7, white, "middle", bold=True)
            tx = x + 17
            for t in step.tools:
                tx += _tool_badge(pen, tx, top - 10, t) + 3
            place = place_of(step.keys, places)
            if place and tx + 6 + len(place) * 1.9 <= x + w:
                _place_mark(pen, tx + 1, top - 10, place)
            lines = _wrap(step.text, 88)[:4]
            for k, line in enumerate(lines):
                pen.text(x + 17, top - (17 if step.tools or place else 4.5) - 4.6 * k, line, 3.6, INK, role="note",
                         step=step.number)
            pen.note("step", (x, top - BAND, w, BAND), step=step.number, picture=False)
            band = top - BAND
            continue
        band = None
        cut = []   # one board per letter among the parts the step cuts, with how many
        for p in sc.parts:
            if p.id in step.cuts and p.cuts and p.mark not in [q.mark for q, _ in cut]:
                cut.append((p, sum(1 for q in sc.parts
                                   if q.mark == p.mark and q.id in step.cuts)))
        grooved = step.prepare and any(j.id in step.joints and j.groove_offset is not None for j in sc.joints)
        only_cuts = bool(cut) and not (step.add or step.joints or step.prepare)
        if (cut or grooved) and slot % 2 and not only_cuts:
            slot += 1    # a step with cuts starts a page: its picture, then its cards
        x, y, w, h = slots[slot % 2]
        if slot % 2 == 0 and slot:
            c.showPage()
        if slot % 2 == 0:
            pen.text(15, H - 12, L["prepare"] if step.prepare else L["assemble"], 3.4, THIN, role="heading")
        else:
            pen.line(15, 148, W - 15, 148, 0.2, THIN, [1.5, 1.5])
        pen.rect(x, y + h - 16, 16, 16, fill=INK, stroke=None)
        pen.text(x + 8, y + h - 12, str(step.number), 9, white, "middle", bold=True)
        joints = [j for j in sc.joints if j.id in step.joints]
        n = sum(j.count for j in joints)
        if n and not step.prepare:
            _fastening(pen, x + w - 46, y + h - 12, n, next((j.size for j in joints if j.size), None), 1.0,
                       joints=[j.path for j in joints])
        tx = x + 22
        for t in step.tools:
            tx += _tool_badge(pen, tx, y + h - 13, t) + 3
        place = place_of(step.keys, places)
        if place and tx + 6 + len(place) * 1.9 <= x + w - (46 if n and not step.prepare else 0):
            _place_mark(pen, tx + 1, y + h - 13, place)   # where the person has every tool the step names
        pic = (x, y + 14, w, h - 32)
        if only_cuts:
            # it only cuts: a picture of the piece would show it as the step before left it, and say nothing of
            # the cut; its number heads the half page its first cut is drawn in, and its screen has no picture
            lines = _wrap(step.text, 95)[:3]
            for k, s in enumerate(lines):
                pen.text(x + 2, y + h - 22 - 4.6 * k, s, 3.6, INK, step=step.number)
            under = 18 + 4.6 * len(lines)
            pen.note("step", (x, y + h - under, w, under), step=step.number, picture=False)
            first = (x, y, w, h - under - 2)
            for p, qty in cut:
                if first is None:
                    if slot % 2 == 0:
                        c.showPage()
                    else:
                        pen.line(15, 148, W - 15, 148, 0.2, THIN, [1.5, 1.5])
                box = first or slots[slot % 2]
                _cut_block(pen, box, step, p, qty, brief)
                first = None
                slot += 1
            continue
        if step.prepare:
            pen.note("step", pic, step=step.number, prepare=True)
            _prepare_picture(pen, sc, step, pic)
        else:
            if step.builds:    # an assembly put together aside: only its own parts are in the picture
                _placed, shown = _assembly_picture(pen, sc, built.setdefault(step.builds, []), step.add, joints,
                                                   step.direction, pic, explode, aside=True)
                built[step.builds] += step.add
            else:
                _placed, shown = _assembly_picture(pen, sc, placed_ids, step.add, joints, step.direction, pic, explode,
                                                   wholes=step.wholes)
                placed_ids += step.add
            pen.note("step", pic, step=step.number, **shown)
        drawn = step.add or step.joints or step.cuts or step.prepare
        for k, s in enumerate(_wrap(step.text, 95)[:3]):
            pen.text(x + 2, y + 8 - 4.6 * k, s, 3.6, INK, role="" if drawn else "note", step=step.number)
        slot += 1
        for p, qty in cut:
            if slot % 2 == 0:
                c.showPage()
            else:
                pen.line(15, 148, W - 15, 148, 0.2, THIN, [1.5, 1.5])
            _cut_block(pen, slots[slot % 2], step, p, qty, brief)
            slot += 1
        if grooved:            # the grooving step's pages, drawn to IKEA's rules, after its picture
            from .grooving import grooving_pages
            machine = next((j.machine for j in sc.joints if j.id in step.joints and j.machine), "")
            grooving_pages(c, pen, sc, step, L, W, H, brief(next((t for j in sc.joints for t in j.methods
                                                                   if t.path == machine), None)))
            slot += (slot % 2) + 2
        if (cut or grooved) and slot % 2:
            slot += 1    # and the next step starts a page too
    c.showPage()
    c.save()
    return path
