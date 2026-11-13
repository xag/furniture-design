"""What a piece is built from, generated from its quern nodes: the cut list, the joint
list and, through documents(), the interactive 3D view (viewer.py), the design document and
the assembly instructions (sheets.py), with the checks in plain words (report.py).

Everything here reads the tree; nothing is typed twice. A part's sizes come from its box
(sizes may be expressions over params), its place from its transform, its name from the node's
`name` (else its id). The piece's payload carries its `steps` (scene.py says how), its
`version`, `authors`, `date` and `description` (design notes, one paragraph each).

The frame is furniture-design's: x across from the left, y from the front to the back, z up
from the floor, mm.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

from quern import Quern, run_rules
from quern.tree import get_node

from .natives import Body, _param, bodies

LABELS = {
    "fr": {"front": "Vue de face", "side": "Coupe au milieu, vue de gauche", "top": "Vue de dessus",
           "cut_list": "Débit", "mark": "Repère", "part": "Pièce", "qty": "Qté",
           "length": "Longueur", "width": "Largeur", "thickness": "Épaisseur",
           "material": "Matériau", "grain": "Fil", "joints": "Assemblages", "joint": "Assemblage",
           "joins": "Pièces", "connector": "Connecteur", "count": "Nombre", "cut": "Fraisage",
           "setting": "Réglage", "tool": "Outil", "steps": "Montage", "checks": "Vérifications",
           "rule": "Règle", "where": "Où", "verdict": "Verdict", "why": "Raison", "overall": "Hors tout",
           "views": "Vues 3D", "plans": "Plans cotés (mm)", "all_hold": "Toutes les règles passent.",
           "units": "Cotes en mm."},
    "en": {"front": "Front view", "side": "Section at mid-width, seen from the left", "top": "Top view",
           "cut_list": "Cut list", "mark": "Mark", "part": "Part", "qty": "Qty",
           "length": "Length", "width": "Width", "thickness": "Thickness",
           "material": "Material", "grain": "Grain", "joints": "Joints", "joint": "Joint",
           "joins": "Parts", "connector": "Connector", "count": "Count", "cut": "Cut",
           "setting": "Setting", "tool": "Tool", "steps": "Assembly", "checks": "Checks",
           "rule": "Rule", "where": "Where", "verdict": "Verdict", "why": "Why", "overall": "Overall",
           "views": "3D views", "plans": "Dimensioned plans (mm)", "all_hold": "Every rule holds.",
           "units": "Dimensions in mm."},
}

# view -> (horizontal axis, vertical axis); y runs front to back, so the side view seen
# from the left puts the front on the left
VIEWS = {"front": (0, 2), "side": (1, 2), "top": (0, 1)}


@dataclass
class Row:
    mark: str
    name: str
    qty: int
    length: float
    width: float
    thickness: float
    material: str
    grain: str
    paths: list[str]


def _name(tree: Quern, path: str) -> str:
    node = get_node(tree, path)
    return node.name or node.id


def _fmt(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def cut_list(tree: Quern, piece: str) -> list[Row]:
    """One row per distinct board to cut: sizes sorted longest first, the material, the way
    its grain runs (the part's `span_along`, when it says), and how many. A part glued up
    from several sheets (payload `sheets`) is that many boards of its thickness over the
    count; parts of the same size, material and grain share a row."""
    groups: OrderedDict[tuple, Row] = OrderedDict()
    for b in bodies(tree, piece):
        node = get_node(tree, b.path)
        dims = sorted((h - lo for lo, h in zip(b.lo, b.hi)), reverse=True)
        sheets = int((node.payload or {}).get("sheets", 1))
        dims[2] = dims[2] / sheets
        uses = (node.links or {}).get("uses", [])
        material = uses[0].rsplit("/", 1)[-1] if uses else ""
        grain = (node.payload or {}).get("span_along", "")
        key = (tuple(round(d, 1) for d in dims), material, grain)
        name = _name(tree, b.path)
        if key in groups:
            row = groups[key]
            row.qty += sheets
            row.paths.append(b.path)
            if name not in row.name.split(", "):
                row.name += f", {name}"
        else:
            groups[key] = Row("", name, sheets, *dims, material, grain, [b.path])
    rows = list(groups.values())
    for i, r in enumerate(rows):
        r.mark = chr(ord("A") + i)
    return rows


def joints(tree: Quern, piece: str) -> list[dict]:
    """Every joint under `piece`: the parts it joins, its connector, how many, the cut, the
    machine setting and the tools."""
    out = []
    prefix = piece.rstrip("/") + "/"
    for path, node in tree.walk(""):
        if node.kind != "joint" or not path.startswith(prefix):
            continue
        links = node.links or {}
        out.append({
            "path": path, "name": node.name or node.id,
            "joins": [_name(tree, t) for t in links.get("joins", [])],
            "connector": ", ".join(_name(tree, c) for c in links.get("uses", [])),
            "count": _param(tree, path, "count"),
            "cut": (node.payload or {}).get("cut", ""),
            "setting": (node.payload or {}).get("setting", ""),
            "tools": [_name(tree, t) for t in links.get("made_with", [])],
        })
    return out


def _chain(bs: list[Body], axis: int) -> list[float]:
    """Every distinct edge position along `axis`: the dimension chain a builder marks out."""
    return sorted({round(v, 1) for b in bs for v in (b.lo[axis], b.hi[axis])})


def plan_svg(tree: Quern, piece: str, view: str, *, scale: float = 0.5, lang: str = "fr") -> str:
    """An orthographic view of the piece's parts with two dimension chains: every edge
    along the horizontal axis below the view, every edge along the vertical axis to its
    left, and the overall size outside them."""
    h_ax, v_ax = VIEWS[view]
    bs = bodies(tree, piece)
    hs, vs = _chain(bs, h_ax), _chain(bs, v_ax)
    h0, h1, v0, v1 = hs[0], hs[-1], vs[0], vs[-1]
    margin_l, margin_b, margin_t, margin_r = 110, 110, 40, 30
    w = max((h1 - h0) * scale + margin_l + margin_r, margin_l + 8 * len(LABELS[lang][view]))
    hgt = (v1 - v0) * scale + margin_b + margin_t

    def X(v: float) -> float:
        return margin_l + (v - h0) * scale

    def Y(v: float) -> float:
        return margin_t + (v1 - v) * scale

    # back to front for this view, so nearer parts are drawn last
    depth_ax = ({0, 1, 2} - {h_ax, v_ax}).pop()
    near_first = view == "side"  # seen from the left: small x is nearest
    order = sorted(bs, key=lambda b: b.lo[depth_ax], reverse=not near_first) \
        if view != "top" else sorted(bs, key=lambda b: b.lo[2])
    if view == "front":
        order = sorted(bs, key=lambda b: -b.lo[1])  # back first, front last
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{hgt:.0f}" '
           f'viewBox="0 0 {w:.0f} {hgt:.0f}" font-family="sans-serif" font-size="11">',
           '<rect width="100%" height="100%" fill="#fbfaf7"/>',
           f'<text x="{margin_l}" y="20" font-size="14" font-weight="bold">'
           f'{LABELS[lang][view]}</text>']
    # the side view is a cut through the middle of the width: what the cut passes through
    # is drawn filled, what lies beyond it (the far side) dashed
    mid = (min(b.lo[0] for b in bs) + max(b.hi[0] for b in bs)) / 2
    for b in order:
        x, y = X(b.lo[h_ax]), Y(b.hi[v_ax])
        bw, bh = (b.hi[h_ax] - b.lo[h_ax]) * scale, (b.hi[v_ax] - b.lo[v_ax]) * scale
        cut = view != "side" or b.lo[0] <= mid <= b.hi[0]
        style = ('fill="#e5c9a0" stroke="#6b4f2a" stroke-width="1"' if cut else
                 'fill="none" stroke="#6b4f2a" stroke-width="0.8" stroke-dasharray="5,3"')
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
                   f'{style}><title>{_name(tree, b.path)}</title></rect>')

    def hdim(a: float, b: float, yy: float, label: str) -> None:
        out.append(f'<line x1="{X(a):.1f}" y1="{yy:.1f}" x2="{X(b):.1f}" y2="{yy:.1f}" '
                   'stroke="#2f5d62" marker-start="url(#t)" marker-end="url(#t)"/>')
        out.append(f'<text x="{(X(a) + X(b)) / 2:.1f}" y="{yy - 3:.1f}" text-anchor="middle" '
                   f'fill="#2f5d62">{label}</text>')

    def vdim(a: float, b: float, xx: float, label: str) -> None:
        out.append(f'<line x1="{xx:.1f}" y1="{Y(a):.1f}" x2="{xx:.1f}" y2="{Y(b):.1f}" '
                   'stroke="#2f5d62" marker-start="url(#t)" marker-end="url(#t)"/>')
        cy = (Y(a) + Y(b)) / 2
        out.append(f'<text x="{xx - 4:.1f}" y="{cy:.1f}" text-anchor="middle" fill="#2f5d62" '
                   f'transform="rotate(-90 {xx - 4:.1f} {cy:.1f})">{label}</text>')

    out.insert(1, '<defs><marker id="t" markerWidth="6" markerHeight="6" refX="3" refY="3" '
                  'orient="auto"><path d="M3,0 L3,6" stroke="#2f5d62"/></marker></defs>')
    base = Y(v0)
    for a, b in zip(hs, hs[1:]):
        hdim(a, b, base + 30, _fmt(b - a))
    hdim(h0, h1, base + 60, _fmt(h1 - h0))
    left = X(h0)
    for a, b in zip(vs, vs[1:]):
        vdim(a, b, left - 30, _fmt(b - a))
    vdim(v0, v1, left - 65, _fmt(v1 - v0))
    for v in hs:
        out.append(f'<line x1="{X(v):.1f}" y1="{base + 4:.1f}" x2="{X(v):.1f}" '
                   f'y2="{base + 64:.1f}" stroke="#9ab" stroke-width="0.5"/>')
    for v in vs:
        out.append(f'<line x1="{left - 4:.1f}" y1="{Y(v):.1f}" x2="{left - 69:.1f}" '
                   f'y2="{Y(v):.1f}" stroke="#9ab" stroke-width="0.5"/>')
    out.append("</svg>")
    return "\n".join(out)


def checks(tree: Quern, piece: str) -> list[tuple[str, str, str, str]]:
    """The rules' verdicts that are not passes, on the piece and everything under it, with
    the reason when the rule could not answer."""
    prefix = piece.rstrip("/")
    return [(r.rule, r.node, r.verdict, r.detail or "") for r in run_rules(tree, prefix)
            if not r.ok and (r.node == prefix or r.node.startswith(prefix + "/"))]


def documents(tree: Quern, piece: str, out_dir: Path, *, lang: str = "fr",
              stem: str | None = None) -> dict[str, Path]:
    """The three things a piece is built from, written into `out_dir`: the interactive 3D
    view (HTML), the design document (PDF, A3) and the assembly instructions (PDF, A4)."""
    from .report import checks as plain_checks
    from .scene import scene
    from .sheets import assembly_instructions, design_document
    from .viewer import viewer_html

    out_dir.mkdir(parents=True, exist_ok=True)
    sc = scene(tree, piece)
    stem = stem or piece.rsplit("/", 1)[-1]
    words = {"fr": ("3d", "plans", "montage"), "en": ("3d", "design", "assembly")}[lang]
    return {
        "viewer": viewer_html(sc, out_dir / f"{stem}-{words[0]}.html", lang),
        "design": design_document(sc, out_dir / f"{stem}-{words[1]}.pdf",
                                  plain_checks(tree, piece, lang), lang),
        "assembly": assembly_instructions(sc, out_dir / f"{stem}-{words[2]}.pdf", lang),
    }
