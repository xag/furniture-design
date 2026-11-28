"""The calculations a rule reaches with `solve('furniture/...', ...)`.

Each is here because the rule grammar cannot state it: it sums products over the parts of a
piece (mass times lever arm), and the grammar sums one list at a time. Everything a
calculation needs to know comes from the tree (parts, materials, requirements); nothing a
source states is written in this file.

The frame is geometry@'s: a part's `shape` is a box {size [x, y, z]} in mm, and
`transform.translate` places its minimum corner relative to the enclosing part (or the
piece). Each entry of either is a number or an expression in quern's rule grammar over
params: the part's own, then those of the parts and the piece it sits in, the nearest first
(`"height - top"`, or a single name). So a piece states a dimension once and every part that
depends on it follows. For furniture, y runs from the front (smallest y) to
the back and z is up from the floor.

A part is a node of kind `part`. Its mass is its own `mass` param when it has one (hardware,
a mirror), and otherwise its volume times the `density` it reads through `uses` (its
material). A part with `extends` in its payload is an extendible element (a drawer, a
pull-out shelf): opened, it and everything under it move that many mm towards the front.
A part that swings open (payload `hinged`) is refused: doors are not modelled yet.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from quern.cache import OPENS_ONLY
from quern.expr import Absent, compile_expr
from quern.tree import Node, Quern, _segs, get_node, register_native, resolve_params

from .units import STANDARD_GRAVITY

STOCK_MM = 0.05  # a side this near a part's stock thickness is that thickness: the documents print tenths
TOUCH_MM = 0.5  # a part whose bottom is this close to the lowest bottom stands on the floor
# The side an assembly step brings a part in from (a step's `direction`): "up", lowered from
# above, moves it down; "front", slid in from the front, moves it towards the back.
DIRECTIONS = {"up": (0, 0, 1), "down": (0, 0, -1), "left": (-1, 0, 0), "right": (1, 0, 0),
              "front": (0, -1, 0), "back": (0, 1, 0)}


# How far back from its place the assembly instructions draw a part a step brings in, as a share of the
# piece's largest dimension: the picture claims the part comes straight in over that distance, and the
# standards judge the same distance (standards_piece: a part reaches its place).
DRAWN_APART = 0.28


def drawn_apart(lo, hi) -> float:
    """mm: how far back along the way it comes in a step's picture draws a part, for a piece that
    spans lo to hi."""
    return max(h - l for l, h in zip(lo, hi)) * DRAWN_APART


def away(lo, hi, centre) -> tuple[int, int, int]:
    """The side a part comes in from when its step does not say (a direction of DIRECTIONS' values): out
    along the axis its centre is farthest from the middle of the piece (lo to hi), by the piece's own
    size."""
    mid = [(a + b) / 2 for a, b in zip(lo, hi)]
    span = [b - a for a, b in zip(lo, hi)]
    rel = [(centre[i] - mid[i]) / (span[i] or 1) for i in range(3)]
    i = max(range(3), key=lambda k: abs(rel[k]))
    d = [0, 0, 0]
    d[i] = 1 if rel[i] >= 0 else -1
    return tuple(d)


@dataclass
class Body:
    path: str
    mass: float          # kg
    lo: list[float]      # min corner, mm, in the piece's frame
    hi: list[float]      # max corner
    opens: float         # mm it moves towards the front when everything is opened
    extendible: str      # path of the outermost extendible element it moves with, or ""
    section: list = field(default_factory=list)  # a profile's outline across its length (natives.section)
    existing: str = ""   # what it is, when it is already there (payload existing): not made, weighed or brought in


def _param(tree, path: str, name: str) -> float | None:
    q = resolve_params(tree, path).get(name)
    return None if q is None else q.value


@dataclass
class Layout:
    """Where a joint's connectors sit, in the piece's frame: the face its two parts meet on
    (lo, hi, the axis it is perpendicular to), the axis along it the connectors follow, and
    each connector's centre. `stated` when the joint gives the positions itself."""
    lo: tuple[float, float, float]
    hi: tuple[float, float, float]
    normal: int
    along: int
    positions: list[tuple[float, float, float]]
    stated: bool


def _face(alo, ahi, blo, bhi):
    """The face where boxes (alo, ahi) and (blo, bhi) touch: (lo, hi, normal); None when they are
    apart, and "inside" when one runs into the other."""
    lo, hi, normal = [], [], None
    for i in range(3):
        low, high = max(alo[i], blo[i]), min(ahi[i], bhi[i])
        if high < low - TOUCH_MM:
            return None
        if high - low <= TOUCH_MM:
            normal = i
            low = high = (low + high) / 2
        lo.append(low)
        hi.append(high)
    return (tuple(lo), tuple(hi), normal) if normal is not None else "inside"


def _inside(pts, a: float, b: float) -> bool:
    """Whether the point (a, b) lies inside the outline `pts`."""
    hit = False
    for (a0, b0), (a1, b1) in zip(pts, pts[1:] + pts[:1]):
        if (b0 > b) != (b1 > b) and a < a0 + (b - b0) * (a1 - a0) / (b1 - b0):
            hit = not hit
    return hit


def cells(x) -> list[tuple[list[float], list[float]]]:
    """What a part is made of, as boxes (lo, hi) in the piece's frame: its box, or for a profile whose
    section's sides all run square to its box (an angle, a channel, a tube), the cells of the grid its
    section's corners draw that lie inside the section, run along its length. A section with a slanted
    side stays its box."""
    lo, hi = list(x.lo), list(x.hi)
    pts = list(getattr(x, "section", None) or [])
    if not pts or any(abs(a - c) > 1e-9 and abs(b - d) > 1e-9
                      for (a, b), (c, d) in zip(pts, pts[1:] + pts[:1])):
        return [(lo, hi)]
    t = max(range(3), key=lambda i: hi[i] - lo[i])
    u, v = [i for i in range(3) if i != t]
    us, vs = sorted({a for a, _ in pts}), sorted({b for _, b in pts})
    out = []
    for a0, a1 in zip(us, us[1:]):
        for b0, b1 in zip(vs, vs[1:]):
            if _inside(pts, (a0 + a1) / 2, (b0 + b1) / 2):
                clo, chi = lo[:], hi[:]
                clo[u], chi[u], clo[v], chi[v] = lo[u] + a0, lo[u] + a1, lo[v] + b0, lo[v] + b1
                out.append((clo, chi))
    return out


def contact(a, b):
    """The face where parts a and b (each with lo and hi, and a profile's section) touch:
    (lo, hi, normal), or None when they are apart or one runs into the other. Each part is what
    `cells` makes it, so a channel laid on an angle's flange, inside the angle's box, touches the
    angle where their walls meet. Where they meet on several faces, the largest: the faces in one
    plane are taken together."""
    faces = []
    for alo, ahi in cells(a):
        for blo, bhi in cells(b):
            f = _face(alo, ahi, blo, bhi)
            if f == "inside":
                return None
            if f is not None:
                faces.append(f)
    if not faces:
        return None

    def area(f):
        flo, fhi, n = f
        return (lambda i, j: (fhi[i] - flo[i]) * (fhi[j] - flo[j]))(*[i for i in range(3) if i != n])

    flat = [f for f in faces if area(f) > 0] or faces
    planes: dict[tuple, tuple] = {}
    for flo, fhi, n in flat:
        key = (n, round(flo[n], 3))
        if key in planes:
            plo, phi, _ = planes[key]
            flo, fhi = tuple(map(min, plo, flo)), tuple(map(max, phi, fhi))
        planes[key] = (tuple(flo), tuple(fhi), n)
    return max(planes.values(), key=area)


def joint_layout(tree: Quern, jpath: str, node: Node, boxes: dict) -> Layout | None:
    """The one place a joint's connectors are placed, for the checks and the documents alike:
    along the longer side of the face its parts meet on, at the middle across it, at the
    offsets the joint states (`positions`, mm from the start of that side) or else spread
    evenly, count of them. A joint of more than two parts (a rail screwed through its two profiles
    into a lintel) places them on the face its first two meet on. None when the joint does not join
    two of `boxes`."""
    ends = [boxes.get("/".join(_segs(t))) for t in (node.links or {}).get("joins", [])][:2]
    if len(ends) != 2 or None in ends:
        return None
    touch = contact(*ends)
    if touch is None:
        raise ValueError(f"joint '{jpath}' joins parts that do not touch")
    lo, hi, normal = touch
    in_plane = [i for i in range(3) if i != normal]
    along = max(in_plane, key=lambda i: hi[i] - lo[i])
    across = next(i for i in in_plane if i != along)
    count = int(_param(tree, jpath, "count") or 0)
    length = hi[along] - lo[along]
    stated = (node.payload or {}).get("positions")
    offsets = stated or [length * (k + 1) / (count + 1) for k in range(count)]
    positions = []
    for o in offsets:
        p = [0.0, 0.0, 0.0]
        p[normal] = lo[normal]
        p[along] = lo[along] + float(o)
        p[across] = (lo[across] + hi[across]) / 2
        positions.append(tuple(p))
    return Layout(lo, hi, normal, along, positions, bool(stated))


def _in_scope(tree, path: str) -> dict[str, float]:
    """The params a part's shape may name: its own, then each enclosing node's, nearest first."""
    out: dict[str, float] = {}
    segs = _segs(path)
    for k in range(len(segs), 0, -1):
        for name, q in resolve_params(tree, "/".join(segs[:k])).items():
            out.setdefault(name, q.value)
    return out


def number(tree, path: str, v, what: str) -> float:
    """A number as written in a part's payload: a number, or an expression over the params in
    scope at `path` (_in_scope). `what` names the entry in a refusal."""
    if not isinstance(v, str):
        return float(v)
    expr = compile_expr(v)
    scope = _in_scope(tree, path)
    missing = [n for n in expr.reads.names if n not in scope]
    if missing or expr.reads.functions:
        raise ValueError(f"part '{path}' gives its {what} as '{v}', and "
                         + (f"{', '.join(missing)} is not a param of it or of what holds it"
                            if missing else "calls a function, which a dimension may not"))
    return float(expr.evaluate({}, scope))


def _size(tree, path: str, node) -> list[float]:
    shape = (node.payload or {}).get("shape")
    if not shape or shape.get("op") != "box":
        raise ValueError(f"part '{path}' has no box shape; only boxes are modelled")
    out = [number(tree, path, v, "size") for v in shape.get("size", [])]
    if len(out) != 3:
        raise ValueError(f"part '{path}' box size must have three entries")
    return out


def section(tree, path: str, node) -> list[tuple[float, float]]:
    """A profile's section: payload section, the outline of what the part is across its length, as
    points [a, b] in mm from the part's minimum corner, a and b along the two shorter sides of its
    box in the order of the axes (x, y, z). None for a part that is its whole box."""
    points = (node.payload or {}).get("section")
    if not points:
        return []
    size = _size(tree, path, node)
    long = max(range(3), key=lambda i: size[i])
    across = [size[i] for i in range(3) if i != long]
    out = [(number(tree, path, a, "section"), number(tree, path, b, "section")) for a, b in points]
    if len(out) < 3:
        raise ValueError(f"part '{path}' section must have at least three points")
    for a, b in out:
        if not (-1e-6 <= a <= across[0] + 1e-6 and -1e-6 <= b <= across[1] + 1e-6):
            raise ValueError(f"part '{path}' section point ({a:g}, {b:g}) lies outside its box, "
                             f"{across[0]:g} by {across[1]:g} mm across its length")
    return out


def stock_thickness(tree, path: str, node) -> float | None:
    """mm: the thickness of the board a part's sheets are cut from (payload stock_thickness, a number or an
    expression over params), when it says; None when its box's smallest side is that thickness."""
    v = (node.payload or {}).get("stock_thickness")
    return None if v is None else number(tree, path, v, "stock thickness")


def board(size, sheets: int = 1, stock: float | None = None, path: str = "") -> tuple[float, float, float]:
    """A part as the board it is cut from: the two sides of its face, longest first, then the thickness of
    one of its sheets. Its thickness is its box's smallest side over its sheets, unless it states the stock
    it is cut from (stock_thickness): then it is that, and its face is its two other sides, so a shim
    18 x 22 x 35 cut from 22 mm stock is 35 by 18 by 22. Refused when no side is its sheets times its stock."""
    dims = sorted(size, reverse=True)
    if stock is None:
        return dims[0], dims[1], dims[2] / sheets
    i = min(range(3), key=lambda k: abs(dims[k] - stock * sheets))
    if abs(dims[i] - stock * sheets) > STOCK_MM:
        raise ValueError(f"part '{path}' is cut from stock {stock:g} mm thick"
                         + (f", {sheets} sheets glued" if sheets > 1 else "")
                         + f", and none of its sides ({' x '.join(f'{d:g}' for d in dims)}) is {stock * sheets:g}")
    face = [d for k, d in enumerate(dims) if k != i]
    return face[0], face[1], stock


def off_stock(tree: Quern, part: str) -> float:
    """mm: how far the nearest of a part's box sides is from the thickness of the stock it says it is cut
    from (payload stock_thickness) times its sheets; 0 when one is within STOCK_MM of it, or when it states
    no stock."""
    node = get_node(tree, part)
    if node is None:
        raise ValueError(f"no part at '{part}'")
    stock = stock_thickness(tree, part, node)
    if stock is None:
        return 0.0
    t = stock * int((node.payload or {}).get("sheets", 1))
    gap = min(abs(d - t) for d in _size(tree, part, node))
    return 0.0 if gap <= STOCK_MM else gap


def _share(tree, path: str, node, size) -> float:
    """The share of its box a part fills: its section's area over the box's, 1 for a whole box."""
    pts = section(tree, path, node)
    if not pts:
        return 1.0
    long = max(range(3), key=lambda i: size[i])
    across = [size[i] for i in range(3) if i != long]
    area = abs(sum(a * d - c * b for (a, b), (c, d) in zip(pts, pts[1:] + pts[:1]))) / 2
    return area / (across[0] * across[1])


def _translate(tree, path: str, node) -> list[float]:
    t = (node.payload or {}).get("transform") or {}
    if t.get("rotate"):
        raise ValueError(f"part '{node.id}' is rotated; only unrotated boxes are modelled")
    return [number(tree, path, x, "position") for x in (t.get("translate") or [0, 0, 0])]


def bodies(tree: Quern, piece: str, existing: bool = False) -> list[Body]:
    """Every part under `piece`, placed in the piece's frame, with its mass. A part that is already
    there (payload existing: a wall, a lintel, the top of the chest the piece stands on) is no part
    of what is made, weighed, cut or brought in: it is left out, with what it holds, unless
    `existing`, which gives it too (mass 0 when it states none), for what judges where the parts
    are and what they are fixed to."""
    root = get_node(tree, piece)
    if root is None:
        raise ValueError(f"no node at '{piece}'")
    out: list[Body] = []

    def visit(node, path: str, origin: list[float], opens: float, ext: str) -> None:
        if node.kind != "part":
            for child in node.children:
                visit(child, f"{path}/{child.id}", origin, opens, ext)
            return
        if (node.payload or {}).get("hinged"):
            raise ValueError(f"part '{path}' is hinged; doors are not modelled yet")
        there = str((node.payload or {}).get("existing") or "")
        if there and not existing:
            return
        lo = [o + t for o, t in zip(origin, _translate(tree, path, node))]
        size = _size(tree, path, node)
        own = _param(tree, path, "mass")
        if own is None and there:
            own = 0.0
        if own is None:
            density = _param(tree, path, "density")
            if density is None:
                raise ValueError(f"part '{path}' has no mass and no density to weigh it by")
            own = density * size[0] * size[1] * size[2] * 1e-9 * _share(tree, path, node, size)
        more = float((node.payload or {}).get("extends") or 0)
        cext = ext or (path if more else "")
        out.append(Body(path, own, lo, [a + s for a, s in zip(lo, size)], opens + more, cext,
                        section(tree, path, node), there))
        for child in node.children:
            visit(child, f"{path}/{child.id}", lo, opens + more, cext)

    path = "/".join(_segs(piece))
    if root.kind == "part":   # a part on its own: itself and what it holds
        visit(root, path, [0.0, 0.0, 0.0], 0.0, "")
    else:
        for child in root.children:
            visit(child, f"{path}/{child.id}", [0.0, 0.0, 0.0], 0.0, "")
    if not out:
        raise ValueError(f"'{piece}' has no parts")
    return out


def mass(tree: Quern, piece: str) -> float:
    """kg: the parts' masses summed."""
    return sum(b.mass for b in bodies(tree, piece))


def height(tree: Quern, piece: str) -> float:
    """mm: from the floor to the top of the highest part."""
    bs = bodies(tree, piece)
    floor = min(b.lo[2] for b in bs)
    return max(b.hi[2] for b in bs) - floor


def overturning_margin(tree: Quern, piece: str, case: str) -> float:
    """N·mm: the moment holding the piece down about its front tipping edge, minus the one
    tipping it, under the test conditions the requirement `case` states — its params
    `tilt_block` (mm, the rear supports raised so the piece leans forward), `point_mass`
    (kg on the front top edge of an open extendible element, each in turn, the worst one
    kept), and `fill_density` with `fill_share` (kg/m3 of storage volume in every
    extendible element, when they hold at least that share of the piece's
    `storage_volume`). Every extendible element is open. Positive: it stays standing."""
    req = get_node(tree, case)
    if req is None:
        raise ValueError(f"no requirement at '{case}'")
    bs = bodies(tree, piece)
    floor = min(b.lo[2] for b in bs)
    feet = [b for b in bs if b.lo[2] - floor <= TOUCH_MM]
    front = min(b.lo[1] - b.opens for b in feet)
    back = max(b.hi[1] - b.opens for b in feet)
    if back <= front:
        raise ValueError(f"'{piece}' has no depth to stand on")
    block = _param(tree, case, "tilt_block") or 0.0
    theta = math.atan2(block, back - front)

    def arm(y: float, z: float) -> float:
        # horizontal distance behind the front edge once the rear is raised by `block`
        return (y - front) * math.cos(theta) - (z - floor) * math.sin(theta)

    def centre(b: Body) -> tuple[float, float]:
        return ((b.lo[1] + b.hi[1]) / 2 - b.opens, (b.lo[2] + b.hi[2]) / 2)

    standing = sum(b.mass * arm(*centre(b)) for b in bs)

    fill_density = _param(tree, case, "fill_density")
    if fill_density:
        share = _param(tree, case, "fill_share") or 0.0
        drawers = [b for b in bs if b.path == b.extendible]
        held = {b.path: _param(tree, b.path, "storage_volume") or 0.0 for b in drawers}
        total = _param(tree, piece, "storage_volume")
        if total is None:
            raise ValueError(f"'{piece}' states no storage_volume to weigh the fill share against")
        if total > 0 and sum(held.values()) >= share * total:
            standing += sum(fill_density * held[b.path] * 1e-9 * arm(*centre(b)) for b in drawers)

    point = _param(tree, case, "point_mass") or 0.0
    worst = 0.0
    if point:
        for top in {b.extendible for b in bs if b.extendible}:
            moving = [b for b in bs if b.extendible == top]
            y = min(b.lo[1] - b.opens for b in moving)
            z = max(b.hi[2] for b in moving)
            worst = min(worst, point * arm(y, z))
    return STANDARD_GRAVITY * (standing + worst)


def tipping_cases(tree: Quern, piece: str) -> float:
    """How many of the requirements `piece` links as `stability_case` it is predicted to
    tip under."""
    node = get_node(tree, piece)
    if node is None:
        raise ValueError(f"no node at '{piece}'")
    return float(sum(1 for case in node.links.get("stability_case", [])
                     if overturning_margin(tree, piece, case) <= 0))


_MEASURES = {"height": height, "mass": mass}


def in_scope(tree: Quern, piece: str, req: str) -> bool:
    """Whether requirement `req` applies to `piece`: its payload scope's category is the
    piece's, and for every param `min_<x>` the requirement carries, the piece's x reaches
    it — x measured (height, mass) or read from the piece's own params."""
    node, r = get_node(tree, piece), get_node(tree, req)
    category = ((r.payload or {}).get("scope") or {}).get("category")
    if not category or category != (node.payload or {}).get("category"):
        return False
    for name, limit in resolve_params(tree, req).items():
        if not name.startswith("min_"):
            continue
        what = name[4:]
        value = (_MEASURES[what](tree, piece) if what in _MEASURES
                 else _param(tree, piece, what))
        if value is None:
            raise ValueError(f"'{piece}' states no {what}, so whether '{req}' applies is unknown")
        if value < limit.value:
            return False
    return True


def unheld(tree: Quern, piece: str) -> float:
    """How many requirements apply to `piece` (in_scope) that it does not link to."""
    node = get_node(tree, piece)
    if node is None:
        raise ValueError(f"no node at '{piece}'")
    linked = {t for targets in node.links.values() for t in targets}
    reqs = [p for p, _ in tree.walk("", kind="requirement")]
    return float(sum(1 for r in reqs if r not in linked and in_scope(tree, piece, r)))


def emc(tree: Quern, climate: str, end: str) -> float:
    """%: the moisture content wood settles at in `climate` at its `end` ('min' or 'max'):
    the climate's `temperature` (°C) and `rh_<end>` (relative humidity, a decimal), through
    the equation of the clause it links as `emc_per`, whose params are W, K, K1 and K2 as
    polynomials in T (`W_0`, `W_1`, `W_2`, ...). Wood Handbook Equation (4-5)."""
    node = get_node(tree, climate)
    if node is None:
        raise ValueError(f"no climate at '{climate}'")
    per = node.links.get("emc_per", [])
    if len(per) != 1:
        raise ValueError(f"climate '{climate}' must link one equation as emc_per")
    t = _param(tree, climate, "temperature")
    h = _param(tree, climate, f"rh_{end}")
    if t is None or h is None:
        raise ValueError(f"climate '{climate}' states no temperature or rh_{end}")
    if not 0 <= h < 1:
        raise ValueError(f"rh_{end} of '{climate}' is {h}; it is a decimal below 1")

    def term(name: str) -> float:
        c = [_param(tree, per[0], f"{name}_{i}") for i in range(3)]
        if None in c:
            raise ValueError(f"'{per[0]}' does not state {name} as a polynomial in T")
        return c[0] + c[1] * t + c[2] * t * t

    w, k, k1, k2 = term("W"), term("K"), term("K1"), term("K2")
    kh = k * h
    return 1800 / w * (kh / (1 - kh) + (k1 * kh + 2 * k1 * k2 * kh * kh)
                       / (1 + k1 * kh + k1 * k2 * kh * kh))


def deflection(tree: Quern, part: str) -> float:
    """mm: the initial deflection of `part` under its own weight and every load `on` it,
    Wood Handbook Equation (9-2) with (9-3) and (9-4): kb W L³/(E I) + ks W L/(G A′), I =
    b h³/12, A′ = 5 b h/6, kb and ks from the one Table 9-1 clause the part links as
    `bends_as`, L, b, h its `span`, `depth` and `thickness`, E its material's
    `modulus_of_elasticity`. The shear term's G is the material property the part names in
    payload `shear_modulus`. A material whose payload says its modulus is `apparent` (a
    panel's bending modulus, measured on the panel with its shear deflection in it) takes no
    shear term: adding one would count that deflection twice."""
    node = get_node(tree, part)
    if node is None:
        raise ValueError(f"no part at '{part}'")
    cases = node.links.get("bends_as", [])
    if len(cases) != 1:
        raise ValueError(f"part '{part}' must link one Table 9-1 case as bends_as")
    need = {n: _param(tree, part, n) for n in ("span", "depth", "thickness", "modulus_of_elasticity")}
    need.update({n: _param(tree, cases[0], n) for n in ("kb", "ks")})
    missing = [n for n, v in need.items() if v is None]
    if missing:
        raise ValueError(f"part '{part}' or its case states no {', '.join(missing)}")
    uses = node.links.get("uses", [])
    material = get_node(tree, uses[0]) if uses else None
    apparent = material is not None and (material.payload or {}).get("modulus") == "apparent"
    here = "/".join(_segs(part))
    loads = sum(_param(tree, p, "mass") or 0.0 for p, n in tree.walk("", kind="load")
                if here in [("/".join(_segs(t))) for t in n.links.get("on", [])])
    w = STANDARD_GRAVITY * (mass(tree, part) + loads)
    span, b, h, e = need["span"], need["depth"], need["thickness"], need["modulus_of_elasticity"]
    bending = need["kb"] * w * span ** 3 * 12 / (e * b * h ** 3)
    if apparent:
        return bending
    name = (node.payload or {}).get("shear_modulus")
    g = _param(tree, part, name) if name else None
    if g is None:
        raise ValueError(f"part '{part}' names no shear modulus its material carries, and its "
                         "material's modulus is not an apparent one")
    return bending + need["ks"] * w * span * 6 / (5 * g * b * h)


def narrow_margin(tree: Quern, part: str) -> float:
    """mm: how much wider than its saws' narrowest cut a part is. The part's cut width is the
    middle of its three box sides (the narrower side of its face, its thickness being the
    smallest); from it is taken the largest min_part_width of the saws it links `sawn_with`
    that state one. A part none of whose saws states a narrowest cut answers its cut width."""
    node = get_node(tree, part)
    if node is None:
        raise ValueError(f"no part at '{part}'")
    width = sorted(_size(tree, part, node))[1]
    limits = [v for v in (_param(tree, t, "min_part_width") for t in (node.links or {}).get("sawn_with", []))
              if v is not None]
    return width - max(limits, default=0.0)


def misfit_closings(tree: Quern, piece: str) -> float:
    """Count: the joints the piece's assembly steps close against their connector. A step (its
    payload `steps`, a `prepare` step aside) that closes a joint and brings one of its parts in
    from a side (`direction`) moves that part straight in from there; a connector that engages
    square (payload engages: square) takes its two parts only brought together square to the
    face they meet on, the moving part coming from its own side of that face. Each joint a moving
    part closes otherwise counts one: slid along the face, or brought from the far side (a shelf
    pushed in from the right between two sides already up closes the left joint and not the
    right one). A joint closed by a moving part whose connector does not say how it engages
    leaves the count absent."""
    return float(sum(1 for *_, ok in closings(tree, piece) if not ok))


def closings(tree: Quern, piece: str) -> list[tuple[int, str, str, bool]]:
    """Each joint an assembly step closes by bringing a part in, whose connector engages
    square: (step number, joint id, the moving part's id, whether it comes straight at the
    face from its own side). misfit_closings counts the ones that do not; the documents name
    them."""
    root = get_node(tree, piece)
    if root is None:
        raise ValueError(f"no node at '{piece}'")
    base = "/".join(_segs(piece))
    boxes = {b.path: b for b in bodies(tree, piece, existing=True)}
    out: list[tuple[int, str, str, bool]] = []
    for n, step in enumerate((root.payload or {}).get("steps") or [], 1):
        if step.get("prepare"):
            continue
        moving = step.get("direction") or {}
        for key, side in moving.items():
            if side not in DIRECTIONS:
                raise ValueError(f"step {n} brings '{key}' in from '{side}', which is not one of "
                                 f"{', '.join(DIRECTIONS)}")
        for jid in step.get("joints") or []:
            jpath = f"{base}/{jid}"
            joint = get_node(tree, jpath)
            if joint is None:
                raise ValueError(f"step {n} closes '{jid}', which is not a joint of '{base}'")
            ends = ["/".join(_segs(t)) for t in (joint.links or {}).get("joins", [])]
            movers = [e for e in ends if e.startswith(base + "/") and e[len(base) + 1:] in moving]
            if not movers:
                continue
            uses = (joint.links or {}).get("uses", [])
            connector = get_node(tree, uses[0]) if uses else None
            engages = ((connector.payload if connector else None) or {}).get("engages")
            if engages is None:
                raise Absent(f"the connector of '{jpath}' does not say how its parts come "
                             f"together (engages)")
            if engages != "square":
                continue
            if len(ends) != 2 or any(e not in boxes for e in ends):
                raise ValueError(f"joint '{jpath}' does not join two parts of '{base}'")
            touch = contact(boxes[ends[0]], boxes[ends[1]])
            if touch is None:
                raise ValueError(f"joint '{jpath}' joins parts that do not touch")
            axis = touch[2]
            for m in movers:
                mine, other = boxes[m], boxes[ends[1] if m == ends[0] else ends[0]]
                want = [0, 0, 0]
                want[axis] = 1 if mine.lo[axis] >= other.hi[axis] - TOUCH_MM else -1
                key = m[len(base) + 1:]
                out.append((n, jid, key, DIRECTIONS[moving[key]] == tuple(want)))
    return out


def _material(tree: Quern, path: str):
    uses = (get_node(tree, path).links or {}).get("uses", [])
    return get_node(tree, uses[0]) if uses else None


def _rated(tree: Quern, jpath: str, mode: str, parts: tuple[str, ...]) -> float:
    """What a joint's connector is rated for in `mode` (shear, pull_out, moment_opening,
    ...), in the weaker of the joined parts' materials (their `connector_key`)."""
    out = []
    for part in parts:
        key = ((_material(tree, part) or Node(id="x", kind="")).payload or {}).get(
            "connector_key")
        got = _param(tree, jpath, f"{mode}_{key}") if key else None
        if got is None:
            raise Absent(f"the connector of '{jpath}' states no {mode} strength in "
                         f"{key or 'the material of ' + part}")
        out.append(got)
    return min(out)


def _count(tree: Quern, jpath: str) -> float:
    n = _param(tree, jpath, "count")
    if n is None:
        raise Absent(f"joint '{jpath}' states no count of connectors")
    return n


def sideways_margin(tree: Quern, piece: str, case: str) -> float:
    """N: whether `piece` takes the requirement `case`'s `side_force` F across it at the
    height of its top, by either of the two ways a piece of furniture does, the better
    one answering:

    - its braces (_brace_margin): panels standing in the plane of the push, held at their
      edges by connectors working in shear and pull-out;
    - its frame (_frame_margin): for the piece to lean over, every joint between an upright
      (a part thin across, like a side) and a part across it (a top, a shelf, a rail) has
      to turn; the joints resist with their connectors' resistance to being bent open or
      shut, and the piece holds if together they resist more than F times its height.

    Whichever holds answers. If neither does, a way that could not be judged (a connector
    not rated in a material) leaves the check absent, since it might have held; if both
    were judged, the better shortfall is the answer."""
    node = get_node(tree, piece)
    if node is None:
        raise ValueError(f"no piece at '{piece}'")
    force = _param(tree, case, "side_force")
    if force is None:
        raise ValueError(f"requirement '{case}' states no side_force")
    judged, unknown = [], None
    for way in (_brace_margin, _frame_margin):
        try:
            judged.append(way(tree, piece, force))
        except Absent as e:
            unknown = unknown or e
    best = max(judged) if judged else None
    if best is not None and best >= 0:
        return best
    if unknown is not None:
        raise unknown
    return best


def _frame_margin(tree: Quern, piece: str, force: float) -> float:
    """N: what the frame's joints resist, as a force at the top, less F. For the piece to
    lean by an angle, each joint between an upright and a part across it turns by that
    angle while the top moves sideways by its height times the angle; so the joints hold
    the top against a force of the sum of their resisting moments over the height. One end
    of each cross part is bent shut as the other is bent open, so a joint is counted at the
    mean of its connectors' `moment_opening_<key>` and `moment_closing_<key>`, times its
    count. A piece with no such joint: -F."""
    bs = bodies(tree, piece)
    box = {b.path: b for b in bs}
    floor = min(b.lo[2] for b in bs)
    height = max(b.hi[2] for b in bs) - floor

    def upright(b) -> bool:
        size = [h - lo for lo, h in zip(b.lo, b.hi)]
        return size[0] < min(size[1], size[2])

    total, found = 0.0, False
    for jpath, j in tree.walk("", kind="joint"):
        joined = ["/".join(_segs(t)) for t in j.links.get("joins", [])]
        if len(joined) != 2 or not all(p in box for p in joined):
            continue
        if upright(box[joined[0]]) == upright(box[joined[1]]):
            continue
        found = True
        n = _count(tree, jpath)
        opening = _rated(tree, jpath, "moment_opening", tuple(joined))
        closing = _rated(tree, jpath, "moment_closing", tuple(joined))
        total += n * (opening + closing) / 2
    if not found:
        return -force
    return total / height - force


def _brace_margin(tree: Quern, piece: str, force: float) -> float:
    """N: the smallest margin, connector by connector, between what the connectors around
    the panels that brace `piece` across (the parts it links as `braced_by`) are rated for
    and what F asks of them; and between what the sides below a brace can take in bending
    and what they are asked.

    A brace is a panel standing in the plane of the push (x across, z up), as a back or a
    rail does, held along its two side edges by the parts beside it. The push enters along
    its top edge and goes down through the sides to the floor. Asked, without crediting any
    bearing of one part on another:
    - of each connector along the top edge, F shared among them, in shear;
    - of each connector along a side edge, in pull-out, F shared among that edge's
      connectors (pushed one way, one side's connectors are pulled), plus its part of the
      pair of forces that holds the side square to the brace: each side carries F/2 down to
      the floor, so at the brace's bottom edge it bends by F/2 times the brace's height
      above the floor, and that moment is passed by the edge's outermost connectors, as far
      apart in height as the joint places them (joint_layout: where it states, else spread
      evenly, the edge's length times (n - 1)/(n + 1));
    - of each connector along a side edge, in shear, F times the brace's height over its
      width, shared (the vertical pair that keeps the brace from turning);
    - of each side, that same bending moment at most its material's design bending stress
      times its section (its depth times its thickness squared over 6), given here as the
      force at the floor it leaves to spare.
    A side edge whose connectors sit at one height (a single one) cannot pass a moment: if the brace stops above the
    floor, half the push has no way down by this path, and the margin is -F/2. A piece with
    no brace carries nothing across by this path: -F.

    Absent, rather than answered: a joint with no count, a connector that states no
    strength in a joined material, a side with no design bending stress. Refused: a brace
    whose top edge or a side edge is joined to nothing."""
    node = get_node(tree, piece)
    braces = node.links.get("braced_by", [])
    if not braces:
        return -force
    bs = bodies(tree, piece)
    box = {b.path: b for b in bs}
    floor = min(b.lo[2] for b in bs)
    joints = list(tree.walk("", kind="joint"))
    nodes = dict(joints)

    def rated(jpath: str, mode: str, parts: tuple[str, str]) -> float:
        return _rated(tree, jpath, mode, parts)

    def count(jpath: str) -> float:
        return _count(tree, jpath)

    worst = math.inf
    for brace in braces:
        bpath = "/".join(_segs(brace))
        b = box.get(bpath)
        if b is None:
            raise ValueError(f"brace '{brace}' is not a part of '{piece}'")
        width, height = b.hi[0] - b.lo[0], b.hi[2] - b.lo[2]
        drop = b.lo[2] - floor
        top, side = [], []
        for jpath, j in joints:
            joined = ["/".join(_segs(t)) for t in j.links.get("joins", [])]
            if bpath not in joined:
                continue
            for other in joined:
                o = box.get(other)
                if o is None or other == bpath:
                    continue
                if abs(o.lo[2] - b.hi[2]) <= TOUCH_MM:
                    top.append((jpath, other))
                elif abs(o.hi[0] - b.lo[0]) <= TOUCH_MM or abs(o.lo[0] - b.hi[0]) <= TOUCH_MM:
                    side.append((jpath, other))
        if not top or len(side) < 2:
            raise ValueError(f"brace '{brace}' must be joined along its top edge and both "
                             "side edges to carry a sideways force")
        moment = force / 2 * drop
        arm = {}
        for jp, _ in side:
            lay = joint_layout(tree, jp, nodes[jp], box)
            zs = [p[2] for p in lay.positions] if lay else []
            arm[jp] = max(zs) - min(zs) if len(zs) > 1 else 0.0
        if moment > 0 and any(arm[jp] <= 0 for jp, _ in side):
            # a shortfall no rating can make up, so it is answered before any rating is read
            return -force / 2
        n_top = sum(count(jp) for jp, _ in top)
        for jpath, other in top:
            worst = min(worst, rated(jpath, "shear", (bpath, other)) - force / n_top)
        for jpath, other in side:
            n = count(jpath)
            couple = moment / arm[jpath] if moment > 0 else 0.0
            worst = min(worst, rated(jpath, "pull_out", (bpath, other)) - (force / n + couple))
            worst = min(worst, rated(jpath, "shear", (bpath, other)) - force * height / width / n)
            o = box[other]
            if drop > 0:
                stress = _param(tree, other, "design_bending_stress")
                if stress is None:
                    raise Absent(f"'{other}' states no design bending stress")
                section = (o.hi[1] - o.lo[1]) * (o.hi[0] - o.lo[0]) ** 2 / 6
                worst = min(worst, (stress * section - moment) / drop)
    return worst


NATIVES = {
    "furniture/deflection": deflection,
    "furniture/sideways_margin": sideways_margin,
    "furniture/emc": emc,
    "furniture/mass": mass,
    "furniture/height": height,
    "furniture/overturning_margin": overturning_margin,
    "furniture/tipping_cases": tipping_cases,
    "furniture/unheld": unheld,
    "furniture/narrow_margin": narrow_margin,
    "furniture/off_stock": off_stock,
    "furniture/misfit_closings": misfit_closings,
}


def register() -> None:
    from .spec import SPEC
    for name, fn in NATIVES.items():
        register_native(name, fn, SPEC[name], reads=OPENS_ONLY)
