"""What a piece is built from, generated from its quern nodes: the cut list, the joint
list and, through documents(), the interactive 3D view (viewer.py), the design document and
the assembly instructions (sheets.py), with the checks in plain words (report.py).

Everything here reads the tree; nothing is typed twice. A part's sizes come from its box
(sizes may be expressions over params), its place from its transform, its name from the node's
`name` (else its id). The piece's payload carries its `steps` (scene.py says how), its
`version`, `authors`, `date`, and may carry `description` (design notes, one paragraph each),
which the design document prints when the caller gives it no notes of its own.

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
    for path, node in tree.walk(piece, kind="joint"):
        if not path.startswith(prefix):
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


DOCUMENTS = ("viewer", "design", "assembly", "cutting")


def documents(tree: Quern, piece: str, out_dir: Path, *, lang: str = "fr",
              stem: str | None = None, notes: list[tuple[str, list[str]]] | None = None,
              stock: dict[str, list[dict]] | None = None, at_work: set[str] | None = None) -> dict[str, Path]:
    """The four things a piece is built from, written into `out_dir`: the interactive 3D
    view (HTML), the design document (PDF, A3), the assembly instructions (PDF, A4) and the
    cutting sheet for a shop's cutting service (PDF, A4); and the instructions as screens for an
    app (steps.instruction_screens), in a folder named as their PDF, `steps` its screens.json, and
    `pages` the instructions as they were drawn (pages.model), in that folder too; `pages-design` and
    `pages-cutting` the plans and the cutting sheet as drawn, each beside its PDF.
    `notes` are the design document's notes, sections of a heading and its paragraphs, a
    paragraph being a text or (text, [lines under it]) (the piece's payload description when none
    are given). `stock` is what can be bought of each material, the sheets the cutting sheet lays
    the parts on (cutting.cutting_sheet). `at_work`: the tools the instructions draw at work
    (sheets.assembly_instructions)."""
    from .scene import scene

    sc = scene(tree, piece)
    out: dict[str, Path] = {}
    for what in DOCUMENTS:
        made = document(tree, piece, out_dir, what, lang=lang, stem=stem, notes=notes, stock=stock,
                        at_work=at_work, sc=sc)
        if "pages" in made and what != "assembly":    # the plans and the cutting sheet as drawn
            made[f"pages-{what}"] = made.pop("pages")
        out |= made
    return out


def document(tree: Quern, piece: str, out_dir: Path, what: str, *, lang: str = "fr",
             stem: str | None = None, notes: list[tuple[str, list[str]]] | None = None,
             stock: dict[str, list[dict]] | None = None, at_work: set[str] | None = None,
             progress=None, sc=None) -> dict[str, Path]:
    """One of the four (`what`, one of DOCUMENTS), written into `out_dir` as documents() writes it, by the
    names documents() gives: viewer, design or cutting, its one file; assembly, the PDF, its screens
    (steps) and the instructions as drawn (pages). `progress`, when given, is called with a fraction done,
    0 to 1, as the instructions draw their steps then cut their screens. `sc`, the piece's scene when the
    caller has it already."""
    from .cutting import cutting_sheet
    from .pages import DRAWN
    from .pages import model as pages_model
    from .report import checks as plain_checks
    from .scene import scene
    from .sheets import assembly_instructions, design_document
    from .steps import instruction_screens
    from .viewer import viewer_html

    if what not in DOCUMENTS:
        raise ValueError(f"no document {what!r}: one of {', '.join(DOCUMENTS)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    sc = sc or scene(tree, piece)
    stem = stem or piece.rsplit("/", 1)[-1]
    names = {"fr": ("3d", "plans", "montage", "decoupe"), "en": ("3d", "design", "assembly", "cutting")}[lang]
    if what == "viewer":
        return {"viewer": viewer_html(sc, out_dir / f"{stem}-{names[0]}.html", lang)}
    pid = piece.rsplit("/", 1)[-1]

    def kept(doc: Path, regions: list, words: list) -> Path:   # the document as drawn, beside it
        drawn = doc.with_suffix(".json")
        drawn.write_text(pages_model(pid, regions, words, DRAWN[what]).model_dump_json(exclude_defaults=True),
                         encoding="utf-8")
        return drawn

    if what == "design":
        regions, words = [], []
        pdf = design_document(sc, out_dir / f"{stem}-{names[1]}.pdf", plain_checks(tree, piece, lang), lang, notes,
                              regions, words)
        return {"design": pdf, "pages": kept(pdf, regions, words)}
    if what == "cutting":
        words = []
        pdf = cutting_sheet(sc, out_dir / f"{stem}-{names[3]}.pdf", lang, stock, words=words)
        return {"cutting": pdf, "pages": kept(pdf, [], words)}
    regions: list[dict] = []     # where the assembly instructions draw each picture, for their screens
    words: list[dict] = []       # every text they set on a page
    pdf = out_dir / f"{stem}-{names[2]}.pdf"
    half = (lambda d, n: progress(0.5 * d / max(n, 1))) if progress else None
    rest = (lambda d, n: progress(0.5 + 0.5 * d / max(n, 1))) if progress else None
    out = {"assembly": assembly_instructions(sc, pdf, lang, regions, words, at_work, half),
           "steps": instruction_screens(sc, pdf, regions, out_dir / f"{stem}-{names[2]}", lang, rest)}
    # the instructions as drawn (pages.model), for a standard to judge: a tree mounts it under instructions
    drawn = out_dir / f"{stem}-{names[2]}" / "pages.json"
    drawn.write_text(pages_model(piece.rsplit("/", 1)[-1], regions, words).model_dump_json(exclude_defaults=True),
                     encoding="utf-8")
    if progress:
        progress(1.0)
    return {**out, "pages": drawn}


def tool_pages(tree: Quern, piece: str, out_dir: Path, tool: str, *, lang: str = "fr", stem: str | None = None,
               progress=None, sc=None) -> dict[str, Path]:
    """The pages of a piece's assembly instructions where `tool` (a path) is drawn at work, beside the
    instructions drawn without it: the blocks that show it, drawn as document() draws them with at_work
    {tool}, as a PDF of their pages and as screens (screens.json in a folder named as that PDF), each block
    screen carrying `step` and `index`, its place among its step's blocks, which is its place in the
    instructions drawn with any tools at work. {tool: the PDF, steps: screens.json}. Refused (ValueError)
    when no block of the instructions shows the tool."""
    import json
    import shutil
    import tempfile

    import pymupdf

    from .scene import scene
    from .sheets import assembly_instructions
    from .steps import instruction_screens

    out_dir.mkdir(parents=True, exist_ok=True)
    sc = sc or scene(tree, piece)
    stem = stem or piece.rsplit("/", 1)[-1]
    names = {"fr": "montage", "en": "assembly"}[lang]
    name = f"{stem}-{names}-{tool.rsplit('/', 1)[-1]}"
    half = (lambda d, n: progress(0.5 * d / max(n, 1))) if progress else None
    rest = (lambda d, n: progress(0.5 + 0.5 * d / max(n, 1))) if progress else None
    with tempfile.TemporaryDirectory() as tmp:
        regions: list[dict] = []
        full = Path(tmp) / "full.pdf"
        assembly_instructions(sc, full, lang, regions, [], {tool}, half)
        shown = [r for r in regions if r.get("kind") == "block" and r.get("tool") == tool]
        if not shown:
            raise ValueError(f"no block of {piece}'s instructions shows {tool} at work")
        folder = out_dir / name
        listed = json.loads(instruction_screens(sc, full, regions, Path(tmp) / "screens", lang, rest)
                            .read_text(encoding="utf-8"))
        kept, seen = [], {}
        for screen in listed["screens"]:
            if screen["kind"] != "block":
                continue
            index = seen[screen["step"]] = seen.get(screen["step"], -1) + 1
            if screen.get("tool") == tool:
                kept.append({**screen, "index": index})
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        for screen in kept:
            for image in screen["images"]:
                shutil.copyfile(Path(tmp) / "screens" / image["file"], folder / image["file"])
        steps = folder / "screens.json"
        steps.write_text(json.dumps({"tool": tool, "lang": lang, "screens": kept}, ensure_ascii=False, indent=1),
                         encoding="utf-8")
        doc = pymupdf.open(str(full))
        doc.select(sorted({r["page"] for r in shown}))
        pdf = out_dir / f"{name}.pdf"
        doc.save(str(pdf))
        doc.close()
    if progress:
        progress(1.0)
    return {"tool": pdf, "steps": steps}
