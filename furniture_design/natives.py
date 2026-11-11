"""The calculations a rule reaches with `solve('furniture/...', ...)`.

Each is here because the rule grammar cannot state it: it sums products over the parts of a
piece (mass times lever arm), and the grammar sums one list at a time. Everything a
calculation needs to know comes from the tree (parts, materials, requirements); nothing a
source states is written in this file.

The frame is geometry@'s: a part's `shape` is a box {size [x, y, z]} in mm, a size entry may
name one of the part's params, and `transform.translate` places its minimum corner relative
to the enclosing part (or the piece). For furniture, y runs from the front (smallest y) to
the back and z is up from the floor.

A part is a node of kind `part`. Its mass is its own `mass` param when it has one (hardware,
a mirror), and otherwise its volume times the `density` it reads through `uses` (its
material). A part with `extends` in its payload is an extendible element (a drawer, a
pull-out shelf): opened, it and everything under it move that many mm towards the front.
A part that swings open (payload `hinged`) is refused: doors are not modelled yet.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from quern.cache import OPENS_ONLY
from quern.tree import Quern, _segs, get_node, register_native, resolve_params

from .units import STANDARD_GRAVITY

TOUCH_MM = 0.5  # a part whose bottom is this close to the lowest bottom stands on the floor


@dataclass
class Body:
    path: str
    mass: float          # kg
    lo: list[float]      # min corner, mm, in the piece's frame
    hi: list[float]      # max corner
    opens: float         # mm it moves towards the front when everything is opened
    extendible: str      # path of the outermost extendible element it moves with, or ""


def _param(tree, path: str, name: str) -> float | None:
    q = resolve_params(tree, path).get(name)
    return None if q is None else q.value


def _size(tree, path: str, node) -> list[float]:
    shape = (node.payload or {}).get("shape")
    if not shape or shape.get("op") != "box":
        raise ValueError(f"part '{path}' has no box shape; only boxes are modelled")
    out = []
    for v in shape.get("size", []):
        if isinstance(v, str):
            got = _param(tree, path, v)
            if got is None:
                raise ValueError(f"part '{path}' sizes its shape by '{v}', which it does not carry")
            v = got
        out.append(float(v))
    if len(out) != 3:
        raise ValueError(f"part '{path}' box size must have three entries")
    return out


def _translate(node) -> list[float]:
    t = (node.payload or {}).get("transform") or {}
    if t.get("rotate"):
        raise ValueError(f"part '{node.id}' is rotated; only unrotated boxes are modelled")
    return [float(x) for x in (t.get("translate") or [0, 0, 0])]


def bodies(tree: Quern, piece: str) -> list[Body]:
    """Every part under `piece`, placed in the piece's frame, with its mass."""
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
        lo = [o + t for o, t in zip(origin, _translate(node))]
        size = _size(tree, path, node)
        own = _param(tree, path, "mass")
        if own is None:
            density = _param(tree, path, "density")
            if density is None:
                raise ValueError(f"part '{path}' has no mass and no density to weigh it by")
            own = density * size[0] * size[1] * size[2] * 1e-9
        more = float((node.payload or {}).get("extends") or 0)
        cext = ext or (path if more else "")
        out.append(Body(path, own, lo, [a + s for a, s in zip(lo, size)], opens + more, cext))
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
    reqs = [p for p, n in tree.walk("") if n.kind == "requirement"]
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
    loads = sum(_param(tree, p, "mass") or 0.0 for p, n in tree.walk("")
                if n.kind == "load" and here in [("/".join(_segs(t))) for t in n.links.get("on", [])])
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


NATIVES = {
    "furniture/deflection": deflection,
    "furniture/emc": emc,
    "furniture/mass": mass,
    "furniture/height": height,
    "furniture/overturning_margin": overturning_margin,
    "furniture/tipping_cases": tipping_cases,
    "furniture/unheld": unheld,
}


def register() -> None:
    from .spec import SPEC
    for name, fn in NATIVES.items():
        register_native(name, fn, SPEC[name], reads=OPENS_ONLY)
