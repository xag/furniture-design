"""The cutting sheet: what to hand a shop's cutting service. One A4 page or more, in the piece's
language: the parts as the saw cuts them (rectangles, length along the grain), then, for each
material and thickness, the panels to buy and where each part sits on them, drawn to scale with
the grain of the panel and of every part. A part's own cuts (a notch) are made afterwards, as the
assembly instructions say, so the sheet lists its rectangle.

What can be bought is the caller's: `stock` maps a material (its path, as a part's `uses` names
it, or its id) to the sheets sold of it, each {"length", "width", "ref"} in mm, length along the
face grain. A material with none is listed with
its parts and no panel. The parts are laid in strips across the panel, end to end along its grain,
as a panel saw cuts: every part's grain then runs with the panel's.

A part glued up from several sheets is that many rectangles of the sheet's thickness, and its row
says how many make the part and how thick it is.

A part's grain runs along its length (the longer side of its face), unless its `span_along` says
it bends across the face grain, when it runs across.

The parts are laid apart by the width the saw takes out: for each material and thickness, the widest
kerf of the saws its parts link `sawn_with` (a saw's kerf, else the widest blade it takes). A part
that names no saw, or a saw whose maker states neither, counts the caller's `kerf`, an allowance and
not a measurement; the sheet says which it counted and from which saw.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from .scene import Scene

INK, MUTED, GRAIN, ACCENT, PANEL = (HexColor("#1d1d1b"), HexColor("#5b5b58"), HexColor("#d9c3a0"),
                                    HexColor("#9a4f12"), HexColor("#f6efe4"))

LABELS = {
    "fr": {"title": "Débit pour l'atelier de découpe",
           "sub": "{version} · cotes en mm, longueur dans le sens du fil · échelle 1:{scale}",
           "mark": "Rep.", "name": "Pièce", "qty": "Qté", "length": "Long. (fil)", "width": "Larg.",
           "thickness": "Ép.", "cut_later": "découpe à faire ensuite (notice)",
           "glued": "{n} × {t} collées en {T}",
           "panel": "Panneau {i} — {material}, {t} mm, {L} × {W}", "ref": "réf. {ref}",
           "grain": "sens du fil du panneau et des pièces",
           "choose": "{material}, {t} mm — panneau à choisir : {parts}, fil dans la longueur.",
           "kerf": "Trait de scie compté entre les pièces : {k} mm, celui de la scie {saw}.",
           "kerf_none": "Trait de scie compté entre les pièces : {k} mm par défaut ({parts} : aucune scie nommée ne donne son trait)."},
    "en": {"title": "Cutting list for the cutting service",
           "sub": "{version} · dimensions in mm, length along the grain · scale 1:{scale}",
           "mark": "Mark", "name": "Part", "qty": "Qty", "length": "Length (grain)", "width": "Width",
           "thickness": "Thk.", "cut_later": "cut afterwards (instructions)",
           "glued": "{n} × {t} glued into {T}",
           "panel": "Board {i} — {material}, {t} mm, {L} × {W}", "ref": "ref. {ref}",
           "grain": "grain of the board and of the parts",
           "choose": "{material}, {t} mm — board to choose: {parts}, grain along the length.",
           "kerf": "Saw cut counted between parts: {k} mm, that of the {saw}.",
           "kerf_none": "Saw cut counted between parts: {k} mm by default ({parts}: no saw named states its cut)."},
}


@dataclass
class Cut:
    """One rectangle the saw cuts: length along the grain, width across it, thickness."""
    mark: str
    name: str
    length: float
    width: float
    thickness: float
    material: str
    material_name: str
    cut_later: bool
    glued: int = 1  # how many such sheets are glued into the one part
    kerf: float | None = None  # the widest cut of the saws that cut it out, when they state one
    saw: str = ""              # that saw's name


def cuts(sc: Scene) -> list[Cut]:
    """Every rectangle to cut, one per board: a part glued up from several sheets is that many."""
    out = []
    for p in sc.parts:
        dims = sorted(p.size, reverse=True)
        a, b = dims[0], dims[1]
        if "across" in (p.grain or ""):
            a, b = b, a
        for _ in range(p.sheets):
            known = [(k, n) for n, k in p.saws if k is not None]
            kerf, saw = max(known) if known and len(known) == len(p.saws) else (None, "")
            out.append(Cut(p.mark, p.name, a, b, dims[2] / p.sheets, p.material, p.material_name, bool(p.cuts),
                           p.sheets, kerf, saw))
    return out


def pack(parts: list[Cut], length: float, width: float, kerf: float):
    """Strips across the panel's width, parts end to end along its length, widest first: where
    each part sits, (part, along, across) from a corner, or None when they do not all fit."""
    strips, placed = [], []
    for q in sorted(parts, key=lambda q: (-q.width, -q.length)):
        for s in strips:
            if q.width <= s["w"] and s["used"] + q.length <= length:
                placed.append((q, s["used"], s["y"]))
                s["used"] += q.length + kerf
                break
        else:
            y = sum(s["w"] + kerf for s in strips)
            if y + q.width > width or q.length > length:
                return None
            strips.append({"y": y, "w": q.width, "used": q.length + kerf})
            placed.append((q, 0.0, y))
    return placed


def panels(parts: list[Cut], sheets: list[dict], kerf: float) -> tuple[list, list[Cut]]:
    """The panels to buy: fill the largest sheet sold, then give each panel the smallest sheet its
    parts fit. Returns [(sheet, placed)] and the parts no sheet takes."""
    if not sheets:
        return [], list(parts)
    area = lambda s: s["length"] * s["width"]
    big = max(sheets, key=area)
    left, out = list(parts), []
    while left:
        took = []
        for q in sorted(left, key=lambda q: -q.length * q.width):
            if pack(took + [q], big["length"], big["width"], kerf):
                took.append(q)
        if not took:
            break
        for q in took:
            left.remove(q)
        sheet = min((s for s in sheets if pack(took, s["length"], s["width"], kerf)), key=area)
        out.append((sheet, pack(took, sheet["length"], sheet["width"], kerf)))
    return out, left


def _f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


class _Page:
    def __init__(self, path: Path, sc: Scene, L: dict, scale: int):
        self.c = Canvas(str(path), pagesize=A4)
        self.c.setTitle(f"{sc.title} - {L['title']}")
        self.sc, self.L, self.scale = sc, L, scale
        self.W, self.H = A4
        self.M = 15 * mm

    def head(self) -> float:
        c, L = self.c, self.L
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.M, self.H - self.M - 4 * mm, f"{self.sc.title} — {L['title']}")
        c.setFont("Helvetica", 9)
        c.setFillColor(MUTED)
        c.drawString(self.M, self.H - self.M - 10 * mm,
                     L["sub"].format(version=self.sc.info.get("version", ""), scale=self.scale))
        c.setFillColor(INK)
        return self.H - self.M - 20 * mm

    def room(self, y: float, need: float) -> float:
        if y - need < self.M + 10 * mm:
            self.c.showPage()
            return self.head()
        return y


def _arrow(c: Canvas, x0, y, x1):
    c.setStrokeColor(ACCENT)
    c.line(x0, y, x1, y)
    for xa, d in ((x0, 1), (x1, -1)):
        c.line(xa, y, xa + d * 2 * mm, y + 1.1 * mm)
        c.line(xa, y, xa + d * 2 * mm, y - 1.1 * mm)


def _grain_lines(c: Canvas, x, y, w, h):
    c.setStrokeColor(GRAIN)
    c.setLineWidth(0.35)
    gy = y + 1.2 * mm
    while gy < y + h - 0.5 * mm:
        c.line(x + 0.4, gy, x + w - 0.4, gy)
        gy += 1.8 * mm


def part_name(q: Cut, L: dict) -> str:
    """The part as its row names it: a glued-up part says how many sheets make it and how thick."""
    if q.glued < 2:
        return q.name
    return f"{q.name} ({L['glued'].format(n=q.glued, t=_f(q.thickness), T=_f(q.thickness * q.glued))})"


def _table(pg: _Page, y: float, parts: list[Cut]) -> float:
    c, L, M = pg.c, pg.L, pg.M
    cols = [(L["mark"], 0), (L["name"], 12), (L["qty"], 62), (L["length"], 76), (L["width"], 100),
            (L["thickness"], 118), ("", 132)]
    c.setFont("Helvetica-Bold", 8.5)
    for t, x in cols:
        c.drawString(M + x * mm, y, t)
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.5)
    c.line(M, y - 2 * mm, pg.W - M, y - 2 * mm)
    c.setFont("Helvetica", 8.5)
    rows: OrderedDict[tuple, list] = OrderedDict()
    for q in parts:
        rows.setdefault((q.mark, round(q.length, 1), round(q.width, 1), round(q.thickness, 1)), [q, 0])[1] += 1
    for (_, length, width, t), (q, n) in rows.items():
        y = pg.room(y, 6 * mm) - 5.5 * mm
        vals = [q.mark, part_name(q, L), str(n), _f(length), _f(width), _f(t), L["cut_later"] if q.cut_later else ""]
        for (_, x), v in zip(cols, vals):
            c.drawString(M + x * mm, y, v)
    return y - 9 * mm


def _panel(pg: _Page, y: float, i: int, sheet: dict, placed, q0: Cut) -> float:
    c, L, M = pg.c, pg.L, pg.M
    s = mm / pg.scale
    w, h = sheet["length"] * s, sheet["width"] * s
    y = pg.room(y, h + 22 * mm)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(M, y, L["panel"].format(i=i, material=q0.material_name, t=_f(q0.thickness),
                                         L=_f(sheet["length"]), W=_f(sheet["width"])))
    if sheet.get("ref"):
        c.setFont("Helvetica", 8.5)
        c.setFillColor(MUTED)
        c.drawRightString(pg.W - M, y, L["ref"].format(ref=sheet["ref"]))
    top = y - 6 * mm
    c.setFillColor(PANEL)
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.6)
    c.rect(M, top - h, w, h, stroke=1, fill=1)
    _grain_lines(c, M, top - h, w, h)
    c.setFillColor(INK)
    c.setFont("Helvetica", 8)
    c.drawCentredString(M + w / 2, top + 1.5 * mm, _f(sheet["length"]))
    c.saveState()
    c.translate(M + w + 3 * mm, top - h / 2)
    c.rotate(90)
    c.drawCentredString(0, 0, _f(sheet["width"]))
    c.restoreState()
    for q, along, across in placed:
        rx, rw, rh = M + along * s, q.length * s, q.width * s
        ry = top - across * s - rh
        c.setFillColor(white)
        c.setStrokeColor(INK)
        c.setLineWidth(1)
        c.rect(rx, ry, rw, rh, stroke=1, fill=1)
        _grain_lines(c, rx, ry, rw, rh)
        roomy = rh > 9 * mm
        if roomy:
            c.setLineWidth(0.9)
            _arrow(c, rx + rw * 0.25, ry + rh / 2 - 2.5 * mm, rx + rw * 0.75)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9 if rw > 30 * mm else 7)
        c.drawCentredString(rx + rw / 2, ry + rh / 2 + (0.5 * mm if roomy else -1.2 * mm),
                            f"{q.mark}  {_f(q.length)} × {_f(q.width)}")
    yy = top - h - 5 * mm
    c.setLineWidth(1)
    _arrow(c, M, yy, M + 30 * mm)
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(M + 32 * mm, yy - 1 * mm, L["grain"])
    c.setFillColor(INK)
    return yy - 9 * mm


def group_kerf(group: list[Cut], default: float) -> tuple[float, str, list[Cut]]:
    """The width to leave between a group's parts: the widest its saws take out, and that saw's name;
    the default when a part's saws state none, with those parts."""
    unknown = [q for q in group if q.kerf is None]
    known = sorted(((q.kerf, q.saw) for q in group if q.kerf is not None), reverse=True)
    if unknown:
        return max([default] + [k for k, _ in known]), "", unknown
    return known[0][0], known[0][1], []


def layout(sc: Scene, stock: dict[str, list[dict]] | None = None, kerf: float = 4.0) -> list[tuple]:
    """For each material and thickness, in the order the parts come: (its parts, the panels to
    buy as [(sheet, placed)], the parts no sheet sold takes)."""
    sold_of = {k.rsplit("/", 1)[-1]: v for k, v in (stock or {}).items()}
    groups: OrderedDict[tuple, list[Cut]] = OrderedDict()
    for q in cuts(sc):
        groups.setdefault((q.material, round(q.thickness, 1)), []).append(q)
    out = []
    for (material, t), group in groups.items():
        sold = [s for s in sold_of.get(material.rsplit("/", 1)[-1], []) if abs(s.get("thickness", t) - t) < 0.05]
        done, left = panels(group, sold, group_kerf(group, kerf)[0])
        out.append((group, done, left))
    return out


def cutting_sheet(sc: Scene, path: Path, lang: str = "fr", stock: dict[str, list[dict]] | None = None,
                  kerf: float = 4.0) -> Path:
    """Write the cutting sheet to `path`. `kerf` is the room left between two parts whose saws state
    no cut, an allowance and not a measurement."""
    L = LABELS[lang]
    parts = cuts(sc)
    longest = max((max(q.length for q in parts), *(s["length"] for v in (stock or {}).values() for s in v)),
                  default=1000)
    scale = 10 if longest <= 1800 else 20 if longest <= 3600 else 40
    pg = _Page(path, sc, L, scale)
    y = _table(pg, pg.head(), parts)
    i = 0
    for group, done, left in layout(sc, stock, kerf):
        t = group[0].thickness
        k, saw, unknown = group_kerf(group, kerf)
        y = pg.room(y, 12 * mm)
        pg.c.setFont("Helvetica", 9)
        pg.c.setFillColor(INK)
        marks = ", ".join(dict.fromkeys(q.mark for q in unknown))
        ks = _f(k).replace(".", ",") if lang == "fr" else _f(k)
        pg.c.drawString(pg.M, y, L["kerf_none"].format(k=ks, parts=marks) if unknown
                        else L["kerf"].format(k=ks, saw=saw))
        y -= 7 * mm
        for sheet, placed in done:
            i += 1
            y = _panel(pg, y, i, sheet, placed, group[0])
        if left:
            y = pg.room(y, 12 * mm)
            pg.c.setFont("Helvetica", 9)
            pg.c.setFillColor(INK)
            text = L["choose"].format(material=group[0].material_name, t=_f(t),
                                      parts=", ".join(f"{q.mark} {_f(q.length)} × {_f(q.width)}" for q in left))
            pg.c.drawString(pg.M, y, text)
            y -= 9 * mm
    pg.c.save()
    return path
