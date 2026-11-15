"""What a piece's design is held to, as part of furniture-standards@ (furniture_design/standards.py).

A design can pass every structural rule and still be wrong in ways nobody stated: a door that slides
in no channel, a part held by nothing, a number in the piece's ledger that the model contradicts, a
purpose no decision answers. These are the rules that say so. They read three things:

- the piece's parts and their profiles' sections (natives.bodies, natives.section);
- its `joint` nodes, which say what is fixed to what, and its `motion` nodes, which say what moves:
  payload type ("slide" or "turn"), axis ("x", "y" or "z": the way it slides, or the line it turns
  about) and travel ([from, to] from where the parts are modelled, in mm for a slide and in degrees
  for a turn, numbers or expressions over the piece's params), for a turn its pivot (where that line
  is, two numbers in the plane across the axis), the link moves to the parts or assemblies that
  move, and the link guided_by to the parts that guide or carry them;
- the piece's ledger, mounted at ledgers/<piece id>: its `purpose` entries and its `decision`
  entries, each decision saying which words of the purpose it answers (payload answers: fragments of
  it, verbatim), what in the piece realises it (the link realised_by) and the figures it states
  (payload figures: [{"says", "value", "is"}], `is` an expression over the piece's params that the
  model must give `value` for, within `tolerance` when stated).

A sliding part is judged in the plane across its axis: its outline, moved sideways, must meet a guide
in both directions before it has moved its own thickness (it is held), and, slid along its travel,
it must cross no other part (it has room). A turning part is judged in the plane across the line it
turns about: that line must lie on what moves and on what carries it, within the moving part's own
thickness (it is carried), and, turned through its travel, it must cross no other part.
"""

from __future__ import annotations

import re

from quern.grounding import agree
from quern.provenance import Quantity
from quern.tree import Node, Quern, get_node

from . import natives

AXES = {"x": 0, "y": 1, "z": 2}
LEDGERS = "ledgers"
_EPS = 1e-3       # mm2: two outlines that only touch do not cross
_STEP = 0.25      # mm: the step a part is moved sideways by to find what holds it


# --- the piece, its bodies and their outlines --------------------------------------------------

def _piece(tree: Quern, piece: str) -> Node:
    node = get_node(tree, piece)
    if node is None:
        raise ValueError(f"no node at '{piece}'")
    return node


def _under(path: str, roots: list[str]) -> bool:
    return any(path == r or path.startswith(r + "/") for r in roots)


def _nodes(node: Node, path: str, kind: str):
    for c in node.children:
        p = f"{path}/{c.id}"
        if c.kind == kind:
            yield p, c
        if c.kind != "part":
            yield from _nodes(c, p, kind)


def _outline(tree: Quern, body, axis: int):
    """A body's outline in the plane across `axis` (a shapely polygon, in the piece's frame): its
    section when it is a profile running along that axis, else its box's rectangle."""
    from shapely.geometry import Polygon, box

    u, v = [i for i in range(3) if i != axis]
    node = get_node(tree, body.path)
    size = [h - lo for lo, h in zip(body.lo, body.hi)]
    pts = natives.section(tree, body.path, node)
    if pts and max(range(3), key=lambda i: size[i]) == axis:
        return Polygon([(body.lo[u] + a, body.lo[v] + b) for a, b in pts])
    return box(body.lo[u], body.lo[v], body.hi[u], body.hi[v])


class _Slide:
    """A motion read: the bodies that move, those that guide, the axis and the travel."""

    def __init__(self, tree: Quern, piece: str, path: str, node: Node) -> None:
        self.path, self.node, self.faults = path, node, []
        payload = node.payload or {}
        self.axis = AXES.get(str(payload.get("axis", "")).lower())
        self.type = payload.get("type")
        if self.type not in ("slide", "turn"):
            self.faults.append(f"{path}: its type is {self.type!r}; a motion is a slide or a turn")
        if self.axis is None:
            self.faults.append(f"{path}: its axis is not x, y or z")
        unit = "degrees" if self.type == "turn" else "mm"
        try:
            a, b = (natives.number(tree, piece, t, "travel") for t in payload.get("travel") or [])
            self.travel = (min(a, b), max(a, b))
        except (ValueError, TypeError):
            self.travel = (0.0, 0.0)
            self.faults.append(f"{path}: its travel is not [from, to] in {unit}")
        self.pivot = (0.0, 0.0)
        if self.type == "turn":
            try:
                u, v = (natives.number(tree, piece, t, "pivot") for t in payload.get("pivot") or [])
                self.pivot = (u, v)
            except (ValueError, TypeError):
                self.faults.append(f"{path}: its pivot is not two numbers, where the line it turns about is in "
                                   "the plane across its axis")
        everything = natives.bodies(tree, piece)
        self.movers = [b for b in everything if _under(b.path, node.links.get("moves", []))]
        self.guides = [b for b in everything if _under(b.path, node.links.get("guided_by", []))]
        self.others = [b for b in everything if b not in self.movers]
        for rel, found in (("moves", self.movers), ("guided_by", self.guides)):
            if not found:
                self.faults.append(f"{path}: {rel} names no part of the piece")


def _motions(tree: Quern, piece: str) -> list[_Slide]:
    return [_Slide(tree, piece, p, n) for p, n in _nodes(_piece(tree, piece), piece, "motion")]


def _slides(tree: Quern, piece: str) -> list[_Slide]:
    return [m for m in _motions(tree, piece) if m.type != "turn"]


def _turns(tree: Quern, piece: str) -> list[_Slide]:
    return [m for m in _motions(tree, piece) if m.type == "turn"]


def _unstated(tree: Quern, piece: str) -> list[str]:
    return [f for s in _motions(tree, piece) for f in s.faults]


def motions_unstated(tree: Quern, piece: str) -> float:
    """How many faults the piece's motions have in what they state: a type that is neither slide nor
    turn, an axis that is not x, y or z, a travel that is not [from, to], a turn whose pivot is not
    two numbers, moves or guided_by naming no part."""
    return float(len(_unstated(tree, piece)))


def _uncarried(tree: Quern, piece: str) -> list[str]:
    from shapely.geometry import Point
    from shapely.ops import unary_union

    out = []
    for s in _turns(tree, piece):
        if s.faults:
            continue
        mover = unary_union([_outline(tree, b, s.axis) for b in s.movers])
        guide = unary_union([_outline(tree, b, s.axis) for b in s.guides])
        x0, y0, x1, y1 = mover.bounds
        thick = min(x1 - x0, y1 - y0)
        at = Point(*s.pivot)
        for what, shape in (("what moves", mover), ("what carries it", guide)):
            far = at.distance(shape)
            if far > thick + _EPS:
                out.append(f"{s.path}: the line it turns about is {far:.1f} mm from {what}, more than the moving "
                           f"part's own {thick:g} mm")
    return out


def unheld_turns(tree: Quern, piece: str) -> float:
    """How many of the piece's turning parts are not carried: the line a part turns about (its pivot,
    in the plane across its axis) lies farther from what moves, or from the parts it is guided by,
    than the moving part's own thickness."""
    return float(len(_uncarried(tree, piece)))


_SWEEP = 2.0    # degrees: the step a turning part is turned by to find what it crosses


def _swept(tree: Quern, piece: str) -> list[str]:
    from shapely.affinity import rotate
    from shapely.ops import unary_union

    out = []
    for s in _turns(tree, piece):
        if s.faults:
            continue
        mover = unary_union([_outline(tree, b, s.axis) for b in s.movers])
        lo, hi = min(b.lo[s.axis] for b in s.movers), max(b.hi[s.axis] for b in s.movers)
        steps = max(1, int((s.travel[1] - s.travel[0]) / _SWEEP))
        angles = [s.travel[0] + (s.travel[1] - s.travel[0]) * k / steps for k in range(steps + 1)]
        for o in s.others:
            if o.hi[s.axis] <= lo or o.lo[s.axis] >= hi:
                continue
            shape = _outline(tree, o, s.axis)
            worst = max(((rotate(mover, a, origin=s.pivot).intersection(shape).area, a) for a in angles),
                        default=(0.0, 0.0))
            if worst[0] > _EPS:
                out.append(f"{s.path}: turned {worst[1]:g} degrees it crosses {o.path} ({worst[0]:.1f} mm2 of their "
                           "outlines overlap)")
    return out


def turn_crossings(tree: Quern, piece: str) -> float:
    """How many parts the piece's turning parts cross through their travel: parts that do not move
    with them, beside them along the axis, whose outlines across the axis theirs overlap at some
    angle of the travel (turned about the pivot, anticlockwise for a positive angle seen with the
    two other axes in their order)."""
    return float(len(_swept(tree, piece)))


def _unheld(tree: Quern, piece: str) -> list[str]:
    from shapely.affinity import translate
    from shapely.ops import unary_union

    out = []
    for s in _slides(tree, piece):
        if s.faults:
            continue
        mover = unary_union([_outline(tree, b, s.axis) for b in s.movers])
        guide = unary_union([_outline(tree, b, s.axis) for b in s.guides])
        x0, y0, x1, y1 = mover.bounds
        side = 0 if (x1 - x0) <= (y1 - y0) else 1        # sideways: across the thin way of what moves
        thick = (x1 - x0, y1 - y0)[side]
        name = [a for a in "xyz" if AXES[a] != s.axis][side]
        for sign, word in ((1, f"+{name}"), (-1, f"-{name}")):
            d, held = _STEP, False
            while d <= thick + _STEP:
                moved = translate(mover, *((sign * d, 0) if side == 0 else (0, sign * d)))
                if moved.intersection(guide).area > _EPS:
                    held = True
                    break
                d += _STEP
            if not held:
                out.append(f"{s.path}: nothing it is guided by stops it towards {word} within its own "
                           f"{thick:g} mm")
    return out


def unheld_slides(tree: Quern, piece: str) -> float:
    """How many sides of the piece's sliding parts nothing holds: moved sideways (across the thin way
    of what moves, in the plane across the slide's axis), the moving parts meet none of the parts
    they are guided by before they have moved their own thickness."""
    return float(len(_unheld(tree, piece)))


def _crossings(tree: Quern, piece: str) -> list[str]:
    from shapely.ops import unary_union

    out = []
    for s in _slides(tree, piece):
        if s.faults:
            continue
        mover = unary_union([_outline(tree, b, s.axis) for b in s.movers])
        lo = min(b.lo[s.axis] for b in s.movers) + s.travel[0]
        hi = max(b.hi[s.axis] for b in s.movers) + s.travel[1]
        for o in s.others:
            if o.hi[s.axis] <= lo or o.lo[s.axis] >= hi:
                continue
            area = mover.intersection(_outline(tree, o, s.axis)).area
            if area > _EPS:
                out.append(f"{s.path}: along its travel it crosses {o.path} ({area:.1f} mm2 of their outlines "
                           "overlap)")
    return out


def slide_crossings(tree: Quern, piece: str) -> float:
    """How many parts the piece's sliding parts cross along their travel: parts that do not move with
    them, that they pass (their extents along the axis meet over the travel), and whose outlines
    across the axis overlap theirs."""
    return float(len(_crossings(tree, piece)))


def _loose(tree: Quern, piece: str) -> list[str]:
    root = _piece(tree, piece)
    joined = [t.rstrip("/") for _, j in _nodes(root, piece, "joint") for t in j.links.get("joins", [])]
    moved = [t for _, m in _nodes(root, piece, "motion") for t in m.links.get("moves", [])]
    return [f"{b.path}: no joint joins it, and no motion moves it" for b in natives.bodies(tree, piece)
            if not _under(b.path, moved) and not any(b.path == j or j.startswith(b.path + "/") or b.path.startswith(j + "/")
                                                     for j in joined)]


def loose_parts(tree: Quern, piece: str) -> float:
    """How many parts of the piece nothing holds: a part no joint joins (itself, or an assembly it is
    in) and no motion moves."""
    return float(len(_loose(tree, piece)))


# --- the piece's ledger ------------------------------------------------------------------------

def _ledger(tree: Quern, piece: str) -> tuple[list[Node], list[Node]]:
    """(the purposes, the decisions) of the piece's ledger still current, [] when it has none."""
    node = get_node(tree, f"{LEDGERS}/{piece.rstrip('/').rpartition('/')[2]}")
    entries = list(node.children) if node is not None else []
    gone = {t.rpartition("/")[2] for e in entries for t in e.links.get("supersedes", [])}
    live = [e for e in entries if e.id not in gone]
    return [e for e in live if e.kind == "purpose"], [e for e in live if e.kind == "decision"]


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.;:!?])\s+", str(text)) if len(s.split()) >= 3]


def _answers(decisions: list[Node]) -> list[str]:
    return [_flat(a) for d in decisions for a in (d.payload or {}).get("answers") or [] if len(str(a).split()) >= 3]


def _uncovered(tree: Quern, piece: str) -> list[str]:
    purposes, decisions = _ledger(tree, piece)
    if not purposes:
        return ["the piece's ledger states no purpose"]
    quoted = _answers(decisions)
    return [f"no decision answers: “{s}”" for p in purposes for s in _sentences(p.name)
            if not any(q in _flat(s) for q in quoted)]


def purpose_uncovered(tree: Quern, piece: str) -> float:
    """How many sentences of the piece's purpose no decision of its ledger answers: a decision answers
    a sentence when its payload answers quotes, word for word, at least three words of it. 1 when the
    ledger states no purpose."""
    return float(len(_uncovered(tree, piece)))


def _unrealised(tree: Quern, piece: str) -> list[str]:
    _, decisions = _ledger(tree, piece)
    out = []
    for d in decisions:
        targets = d.links.get("realised_by", [])
        if not targets:
            out.append(f"{d.id}: it names nothing in the piece that realises it (realised_by)")
        out += [f"{d.id}: {t} is not in the piece" for t in targets
                if not _under(t.rstrip("/"), [piece.rstrip("/")]) or get_node(tree, t) is None]
    return out


def unrealised_decisions(tree: Quern, piece: str) -> float:
    """How many of the piece's decisions name nothing in the piece that realises them, or name what is
    not there (the link realised_by, to parts, assemblies, joints or motions of the piece)."""
    return float(len(_unrealised(tree, piece)))


def _unchecked(tree: Quern, piece: str) -> list[str]:
    purposes, decisions = _ledger(tree, piece)
    texts = [(d.id, a) for d in decisions for a in (d.payload or {}).get("answers") or []]
    texts += [(d.id, d.name) for d in decisions]
    figures = {d.id: (d.payload or {}).get("figures") or [] for d in decisions}
    out = []
    for did, text in texts:
        for number in re.findall(r"\d+(?:[.,]\d+)?\s*(?:mm|cm|m|kg|°|%)", str(text)):
            if not any(_flat(number) in _flat(f.get("says", "")) for f in figures[did] if isinstance(f, dict)):
                out.append(f"{did}: “{number}” is stated, and no figure of the decision holds the model to it")
    stated = " ".join(_flat(t) for _, t in texts)
    for p in purposes:
        for number in re.findall(r"\d+(?:[.,]\d+)?\s*(?:mm|cm|m|kg|°|%)", p.name):
            if _flat(number) not in stated:
                out.append(f"the purpose states “{number}”, and no decision takes it up")
    return sorted(set(out))


def unchecked_numbers(tree: Quern, piece: str) -> float:
    """How many quantities the piece's purpose and decisions state in words (a number with mm, cm, m,
    kg, ° or %) that no figure holds the model to: a decision's payload figures, each {"says": the
    words, "value", "is": an expression over the piece's params}."""
    return float(len(_unchecked(tree, piece)))


def _off(tree: Quern, piece: str) -> list[str]:
    _, decisions = _ledger(tree, piece)
    out = []
    for d in decisions:
        for f in (d.payload or {}).get("figures") or []:
            try:
                got = natives.number(tree, piece, f["is"], "figure")
                want = Quantity(value=float(f["value"]), unit=str(f.get("unit", "mm")), provenance="design-target",
                                grounded=False, tolerance=f.get("tolerance"))
            except (KeyError, TypeError, ValueError) as e:
                out.append(f"{d.id}: the figure “{f.get('says', '?') if isinstance(f, dict) else f}” cannot be read ({e})")
                continue
            if not agree(want, Quantity(value=got, unit=want.unit, provenance="derived", grounded=False)):
                out.append(f"{d.id}: “{f.get('says', '')}” is {want.value:g} in the ledger and {got:g} in the model "
                           f"({f['is']})")
    return out


def figures_off(tree: Quern, piece: str) -> float:
    """How many figures of the piece's decisions the model does not give: `is`, evaluated over the
    piece's params, differs from `value` (beyond `tolerance` when the figure states one, else at the
    precision written), or cannot be evaluated."""
    return float(len(_off(tree, piece)))


# --- the assembly steps -------------------------------------------------------------------------

def _steps(tree: Quern, piece: str) -> list[dict]:
    return [s for s in (_piece(tree, piece).payload or {}).get("steps") or [] if isinstance(s, dict)]


def _unplaced(tree: Quern, piece: str) -> list[str]:
    added = {str(a) for s in _steps(tree, piece) if not s.get("prepare") for a in s.get("add") or []}
    return [f"{b.path}: no assembly step brings it in" for b in natives.bodies(tree, piece)
            if b.path.rpartition("/")[2] not in added]


def steps_unplaced(tree: Quern, piece: str) -> float:
    """How many parts of the piece no assembly step brings in (a step's add names parts by their id;
    a preparation step, which makes a part ready, brings none in)."""
    return float(len(_unplaced(tree, piece)))


def _misclosed(tree: Quern, piece: str) -> list[str]:
    joints = {p.rpartition("/")[2]: j for p, j in _nodes(_piece(tree, piece), piece, "joint")}
    closed: dict[str, int] = {}
    placed: set[str] = set()
    out = []
    for n, s in enumerate([s for s in _steps(tree, piece) if not s.get("prepare")], 1):
        placed |= {str(a) for a in s.get("add") or []}
        for jid in s.get("joints") or []:
            if jid not in joints:
                out.append(f"step {n} closes {jid}, which is not a joint of the piece")
                continue
            closed.setdefault(jid, n)
            missing = [t.rpartition("/")[2] for t in joints[jid].links.get("joins", [])
                       if t.rpartition("/")[2] not in placed]
            if missing:
                out.append(f"step {n} closes {jid} before {', '.join(missing)} is brought in")
    return out + [f"{jid}: no assembly step closes it" for jid in joints if jid not in closed]


def joints_misclosed(tree: Quern, piece: str) -> float:
    """How many faults the piece's assembly steps have in the joints they close (a step's joints): a
    joint no step closes, one closed before every part it joins is brought in, a name that is no joint."""
    return float(len(_misclosed(tree, piece)))


NATIVES = {
    "furniture/unheld_turns": unheld_turns,
    "furniture/turn_crossings": turn_crossings,
    "furniture/steps_unplaced": steps_unplaced,
    "furniture/joints_misclosed": joints_misclosed,
    "furniture/motions_unstated": motions_unstated,
    "furniture/unheld_slides": unheld_slides,
    "furniture/slide_crossings": slide_crossings,
    "furniture/loose_parts": loose_parts,
    "furniture/purpose_uncovered": purpose_uncovered,
    "furniture/unrealised_decisions": unrealised_decisions,
    "furniture/unchecked_numbers": unchecked_numbers,
    "furniture/figures_off": figures_off,
}

EXPLAINERS = {
    "furniture/unheld_turns": _uncarried,
    "furniture/turn_crossings": _swept,
    "furniture/steps_unplaced": _unplaced,
    "furniture/joints_misclosed": _misclosed,
    "furniture/motions_unstated": _unstated,
    "furniture/unheld_slides": _unheld,
    "furniture/slide_crossings": _crossings,
    "furniture/loose_parts": _loose,
    "furniture/purpose_uncovered": _uncovered,
    "furniture/unrealised_decisions": _unrealised,
    "furniture/unchecked_numbers": _unchecked,
    "furniture/figures_off": _off,
}


# --- an example: two doors sliding in one rail --------------------------------------------------
#
# One angle (20 x 20 x 1) screwed under a lintel, its flange on top and its leg down at the back; one
# channel (12 x 12 x 1, open downwards) glued under the flange at its front edge. The front door's top
# (8 mm) runs in the channel; the back door's runs between the channel and the angle's leg. Glued in
# the angle instead, the channel leaves the back door nothing to run in: the counter-example.

_PIECE = "pieces/doors"
_ANGLE = [[0, 19], [20, 19], [20, 20], [0, 20]], [[19, 0], [20, 0], [20, 20], [19, 20]]   # flange, leg


def _part(id_: str, size: list, at: list, section: list | None = None) -> Node:
    payload = {"shape": {"op": "box", "size": size}, "transform": {"translate": at}}
    if section:
        payload["section"] = section
    return Node(id=id_, kind="part", payload=payload,
                params={"mass": Quantity(value=1.0, unit="kg", provenance="design-target", grounded=False)})


def example_piece(*, channel_at: float = 0.0, joints: bool = True, back_guides: tuple[str, ...] = ("channel", "angle"),
                  overlap: float = 50.0, travel: list | None = None, motions: bool = True,
                  steps: list | None = None, flap: dict | None = None) -> Node:
    """Two doors, 600 wide, in an opening `2 * 600 - overlap` wide; the channel `channel_at` mm from the
    flange's front edge (0: at the edge, as designed; 7: glued in the angle)."""
    angle = _part("angle", ["width", 20, 20], [0, 0, 1180],
                  [[0, 19], [19, 19], [19, 0], [20, 0], [20, 20], [0, 20]])
    channel = _part("channel", ["width", 12, 12], [0, channel_at, 1187],
                    [[0, 0], [1, 0], [1, 11], [11, 11], [11, 0], [12, 0], [12, 12], [0, 12]])
    front = Node(id="front-door", kind="assembly", children=[_part("front-panel", [600, 8, 1190], [0, channel_at + 2, 5])])
    back = Node(id="back-door", kind="assembly",
                children=[_part("back-panel", [600, 6, 1190], ["width - 600", 12.5, 5])])
    children = [angle, channel, front, back]
    if joints:
        children += [Node(id="angle-to-lintel", kind="joint", links={"joins": [f"{_PIECE}/angle"]},
                          payload={"to": "the lintel"}),
                     Node(id="channel-to-angle", kind="joint", links={"joins": [f"{_PIECE}/channel", f"{_PIECE}/angle"]})]
    if motions:
        children += [
            Node(id="front-slides", kind="motion", payload={"type": "slide", "axis": "x", "travel": travel or [0, "width - 600"]},
                 links={"moves": [f"{_PIECE}/front-door"], "guided_by": [f"{_PIECE}/channel"]}),
            Node(id="back-slides", kind="motion", payload={"type": "slide", "axis": "x", "travel": ["600 - width", 0]},
                 links={"moves": [f"{_PIECE}/back-door"], "guided_by": [f"{_PIECE}/{g}" for g in back_guides]})]
    if flap is not None:
        # a flap in front of the rail, hinged on the angle's top front edge: it lifts outwards (-90 degrees
        # about x); `flap` overrides what its motion states (the counter-examples)
        children += [_part("flap", [300, 8, 100], [0, -8, 1100]),
                     Node(id="flap-turns", kind="motion",
                          payload={"type": "turn", "axis": "x", "pivot": [0, 1200], "travel": [-90, 0]} | flap,
                          links={"moves": [f"{_PIECE}/flap"], "guided_by": [f"{_PIECE}/angle"]})]
        steps = (STEPS if steps is None else steps) + [{"add": ["flap"]}]
    return Node(id="doors", kind="piece", children=children,
                payload={"steps": STEPS if steps is None else steps},
                params={"width": Quantity(value=1200.0 - overlap, unit="mm", provenance="design-target", grounded=False)})


STEPS = [{"add": ["angle", "channel"], "joints": ["angle-to-lintel", "channel-to-angle"]},
         {"add": ["back-panel", "front-panel"]}]


def example_ledger(*, answers: bool = True, realised: bool = True, figure: float | None = 50.0,
                   purpose: bool = True) -> Node:
    said = "Two doors slide in one rail, one behind the other. Closed, they overlap by 50 mm in the middle."
    slide = Node(id="one-rail-two-doors", kind="decision",
                 name="One angle and one channel make the rail: the front door runs in the channel, the back door "
                      "between the channel and the angle's leg",
                 payload={"answers": ["Two doors slide in one rail, one behind the other"] if answers else []},
                 links={"realised_by": [f"{_PIECE}/front-slides", f"{_PIECE}/back-slides"]} if realised else {})
    lap = Node(id="the-doors-overlap", kind="decision", name="Closed, the doors overlap by 50 mm",
               payload={"answers": ["they overlap by 50 mm in the middle"],
                        "figures": [{"says": "overlap by 50 mm", "value": figure, "unit": "mm", "tolerance": 1,
                                     "is": "2 * 600 - width"}] if figure is not None else []},
               links={"realised_by": [f"{_PIECE}/front-door", f"{_PIECE}/back-door"]})
    return Node(id=LEDGERS, kind="", children=[Node(id="doors", kind="", children=(
        [Node(id="what-it-is-for", kind="purpose", name=said)] if purpose else []) + [slide, lap])])


def piece_world(piece: Node | None = None, ledger: Node | None = None) -> list[Node]:
    return [Node(id="pieces", kind="", children=[piece or example_piece()]), ledger or example_ledger()]


def _demo(contract: str, expect: float, because: str, **kw):
    from quern.tree import Demonstration
    return Demonstration(contract=contract, nodes=piece_world(**kw), args=[_PIECE], expect=expect, because=because)


SPEC = {
    "furniture/unheld_turns": [
        _demo("furniture/unheld_turns", 0, "a flap hinged on the angle's top front edge, which it touches",
              piece=example_piece(flap={})),
        _demo("furniture/unheld_turns", 2, "a flap said to turn about a line in mid-air, 100 mm in front of it",
              piece=example_piece(flap={"pivot": [-108, 1200]})),
    ],
    "furniture/turn_crossings": [
        _demo("furniture/turn_crossings", 0, "the flap lifts outwards, clear of the rail",
              piece=example_piece(flap={})),
        _demo("furniture/turn_crossings", 3, "the flap said to turn inwards: through the angle, the channel and "
              "the front door", piece=example_piece(flap={"travel": [0, 90]})),
    ],
    "furniture/steps_unplaced": [
        _demo("furniture/steps_unplaced", 0, "the rail, then the two doors: every part is brought in"),
        _demo("furniture/steps_unplaced", 2, "steps that stop at the rail leave both doors on the floor",
              piece=example_piece(steps=STEPS[:1])),
    ],
    "furniture/joints_misclosed": [
        _demo("furniture/joints_misclosed", 0, "the rail's two joints are closed in the step that brings it in"),
        _demo("furniture/joints_misclosed", 1, "the channel glued to an angle that comes one step later",
              piece=example_piece(steps=[{"add": ["channel"], "joints": ["channel-to-angle"]},
                                         {"add": ["angle", "back-panel", "front-panel"], "joints": ["angle-to-lintel"]}])),
        _demo("furniture/joints_misclosed", 2, "steps that bring parts in and say nothing of what fixes them",
              piece=example_piece(steps=[{"add": ["angle", "channel", "back-panel", "front-panel"]}])),
    ],
    "furniture/motions_unstated": [
        _demo("furniture/motions_unstated", 0, "each slide states its axis, its travel, what moves and what guides"),
        _demo("furniture/motions_unstated", 1, "a turn that does not say where the line it turns about is",
              piece=example_piece(flap={"pivot": []})),
        _demo("furniture/motions_unstated", 1, "a travel that is one number, not from and to",
              piece=example_piece(travel=[600])),
    ],
    "furniture/unheld_slides": [
        _demo("furniture/unheld_slides", 0, "the front door between the channel's walls, the back door between "
              "the channel and the angle's leg"),
        _demo("furniture/unheld_slides", 1, "the back door guided by the channel alone: nothing behind it",
              piece=example_piece(back_guides=("channel",))),
    ],
    "furniture/slide_crossings": [
        _demo("furniture/slide_crossings", 0, "each door runs clear of the rail and of the other door"),
        _demo("furniture/slide_crossings", 3, "the channel glued in the angle: the back door, where it was meant "
              "to run, crosses the channel and the front door, and the front door crosses it",
              piece=example_piece(channel_at=7.0)),
    ],
    "furniture/loose_parts": [
        _demo("furniture/loose_parts", 0, "the angle is screwed, the channel glued to it, the doors slide"),
        _demo("furniture/loose_parts", 2, "no joint: the angle and the channel hold to nothing",
              piece=example_piece(joints=False)),
    ],
    "furniture/purpose_uncovered": [
        _demo("furniture/purpose_uncovered", 0, "each sentence of the purpose is quoted by a decision"),
        _demo("furniture/purpose_uncovered", 1, "nobody decided how two doors slide in one rail",
              ledger=example_ledger(answers=False)),
        _demo("furniture/purpose_uncovered", 1, "a ledger with no purpose answers nothing",
              ledger=example_ledger(purpose=False)),
    ],
    "furniture/unrealised_decisions": [
        _demo("furniture/unrealised_decisions", 0, "each decision names the motions or the doors that realise it"),
        _demo("furniture/unrealised_decisions", 1, "a decision about the rail that names nothing of the piece",
              ledger=example_ledger(realised=False)),
    ],
    "furniture/unchecked_numbers": [
        _demo("furniture/unchecked_numbers", 0, "the 50 mm of overlap is a figure the model is held to"),
        _demo("furniture/unchecked_numbers", 1, "50 mm said in the decision and its answer, and no figure",
              ledger=example_ledger(figure=None)),
    ],
    "furniture/figures_off": [
        _demo("furniture/figures_off", 0, "two doors of 600 in 1150: 50 mm"),
        _demo("furniture/figures_off", 1, "two doors of 600 in 1153: 47 mm where the ledger says 50",
              piece=example_piece(overlap=47.0)),
    ],
}
