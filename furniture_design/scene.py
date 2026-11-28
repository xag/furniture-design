"""A piece as a scene: what the viewer, the design document and the assembly instructions
all draw. Everything is read from the quern tree; nothing here is typed twice.

- parts, placed in the piece's frame (x across from the left, y from the front to the
  back, z up from the floor, mm), each with the letter it carries in the cut list (parts
  of the same size, material and grain share a letter, as identical boards do);
- joints, with the face where the parts meet and where its connectors sit, placed by
  natives.joint_layout as the checks place them (spread evenly along the longer side of that
  face unless the joint states `positions`, mm along that side), and the connector's size
  (its params length and thickness) when its node states it;
- cuts a part carries in its payload (`cuts`: boxes {at, size} in the part's own frame,
  each entry a number or an expression over params, as for a part's own size,
  such as a notch for a skirting board), drawn but not counted by the checks, and the
  tools the part links `made_with` with what each says of its use (`say`, per language);
  the saws it links `sawn_with`, which cut it out of its board, each with the width it takes out
  (its param kerf, else max_kerf, the widest blade it takes); cut_plan() reads a cut's shape: the edges it touches, its measures from them, and the
  saw lines that make it, in order;
- the steps: the piece's payload `steps`, each {text, add, joints, prepare, tools,
  direction}: `add` the part ids it brings in, `joints` the joint ids it closes,
  `prepare` true for the work done on parts before they are put together, `split` the
  glued-up parts shown as their separate sheets (the gluing step), `cuts` the parts whose
  cuts the step makes (shown hatched), `direction`
  for each added part the side it comes in from (up: lowered from above; front: slid in
  from the front; ...). Added parts with no direction are set down where they go.
- `material_names`: how the documents name each material, by its id.
- `info["instructions"]`: the piece's payload instructions, full (when absent) or short, how much the
  assembly instructions show of the tools in use (INSTRUCTIONS); any other value is refused.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from quern import Quern
from quern.tree import _segs, get_node

from .natives import DIRECTIONS, _param, board, bodies, joint_layout, number, section, stock_thickness

TOUCH = 0.5


# How much of the assembly instructions show the tools in use (a piece's payload instructions): full
# shows them; short leaves them out for someone who knows their tools, keeping what the piece needs.
INSTRUCTIONS = ("full", "short")


@dataclass
class Tool:
    path: str
    name: str
    say: dict                  # per language: {name, method: [sentences]}
    cites: list[tuple[str, str]]   # each clause it rests on: (its source, its locator)
    model: dict | None = None  # its solids, for the drawings (lineart.solids), when it has them
    follows: list[str] = field(default_factory=list)  # the general tools whose method it follows


@dataclass
class Part:
    path: str
    id: str
    name: str
    mark: str
    lo: tuple[float, float, float]
    hi: tuple[float, float, float]
    material: str
    material_name: str
    grain: str = ""
    sheets: int = 1
    cuts: list[tuple[tuple, tuple]] = field(default_factory=list)  # (lo, hi) in the piece frame
    tools: list[Tool] = field(default_factory=list)                # what cuts its cuts
    saws: list[tuple[str, float | None]] = field(default_factory=list)  # what cuts it out: (name, kerf)
    within: list[tuple[str, str]] = field(default_factory=list)   # the groups holding it, outermost first: (id, name)
    section: list[tuple[float, float]] = field(default_factory=list)  # a profile's outline across its length, from lo
    bought: str = ""   # who sells it cut to its size (payload bought_to_size), when no saw cuts it out here
    existing: str = ""  # what it is, when it is already there (payload existing): drawn in the steps, never listed
    stock: float | None = None  # the thickness of the board it is cut from (payload stock_thickness), when stated

    def board(self) -> tuple[float, float, float]:
        """Its face's two sides, longest first, and the thickness of one of its sheets (natives.board)."""
        return board(self.size, self.sheets, self.stock, self.path)

    @property
    def size(self) -> tuple[float, float, float]:
        return tuple(h - lo for lo, h in zip(self.lo, self.hi))

    @property
    def centre(self) -> tuple[float, float, float]:
        return tuple((lo + h) / 2 for lo, h in zip(self.lo, self.hi))

    def profile(self, offset=(0.0, 0.0, 0.0)) -> "Profile":
        """The board as what it is: its outline in the plane of its two longer sides, cuts
        through its thickness taken out (a notch is a missing corner), extruded across
        its thickness."""
        from shapely.geometry import box as rect
        from shapely.geometry.polygon import orient

        lo = [a + o for a, o in zip(self.lo, offset)]
        hi = [a + o for a, o in zip(self.hi, offset)]
        if self.section:   # a profile: its section, run along its length
            t = max(range(3), key=lambda i: self.size[i])
            u, v = [i for i in range(3) if i != t]
            pts = [(lo[u] + a, lo[v] + b) for a, b in self.section]
            if sum(a * d - c * b for (a, b), (c, d) in zip(pts, pts[1:] + pts[:1])) < 0:
                pts.reverse()
            return Profile(u, v, t, pts, lo[t], hi[t])
        t = min(range(3), key=lambda i: self.size[i])
        u, v = [i for i in range(3) if i != t]
        shape = rect(lo[u], lo[v], hi[u], hi[v])
        for clo, chi in self.cuts:
            clo = [a + o for a, o in zip(clo, offset)]
            chi = [a + o for a, o in zip(chi, offset)]
            if clo[t] <= lo[t] + TOUCH and chi[t] >= hi[t] - TOUCH:
                shape = shape.difference(rect(clo[u], clo[v], chi[u], chi[v]))
        shape = orient(shape, 1.0)
        return Profile(u, v, t, [tuple(p) for p in list(shape.exterior.coords)[:-1]],
                       lo[t], hi[t])


EDGES = {(2, 0): "bottom", (2, 1): "top", (1, 0): "front", (1, 1): "back",
         (0, 0): "left", (0, 1): "right"}


@dataclass
class CutPlan:
    """A cut as the person marking it out sees it, on the board's face: `h` the piece axis
    drawn across, `v` the one drawn up, `t` the thickness. `measures`: per face axis, the
    edge it is measured from (an EDGES name) and the distance, with `offset` its start
    when it touches no edge; `lines`: the saw lines, each (start, end) in (h, v), starting
    at an edge of the board when it reaches one, those first; `depth` when the cut does
    not go through the thickness."""
    h: int
    v: int
    t: int
    measures: list[tuple[int, str, float, float]]   # (axis, edge, distance, offset)
    lines: list[tuple[tuple[float, float], tuple[float, float]]]
    depth: float | None
    from_edge: int                 # how many of the lines (the first ones) start at an edge


def cut_plan(part: "Part", lo, hi) -> CutPlan:
    t = min(range(3), key=lambda i: part.size[i])
    face = [i for i in range(3) if i != t]
    v = 2 if 2 in face else face[1]
    h = next(i for i in face if i != v)
    lo = [max(a, b) for a, b in zip(lo, part.lo)]
    hi = [min(a, b) for a, b in zip(hi, part.hi)]
    on_lo = [lo[i] <= part.lo[i] + TOUCH for i in range(3)]
    on_hi = [hi[i] >= part.hi[i] - TOUCH for i in range(3)]
    measures = []
    for a in (h, v):
        if on_lo[a] and on_hi[a]:
            continue                       # the cut spans the board this way
        if on_hi[a]:
            measures.append((a, EDGES[(a, 1)], part.hi[a] - lo[a], 0.0))
        elif on_lo[a]:
            measures.append((a, EDGES[(a, 0)], hi[a] - part.lo[a], 0.0))
        else:
            measures.append((a, EDGES[(a, 0)], hi[a] - lo[a], lo[a] - part.lo[a]))
    lines, opened = [], []
    for a, b in ((h, v), (v, h)):          # the cut's sides across a, at each end of a
        for side, at in ((0, lo[a]), (1, hi[a])):
            if (on_lo[a] if side == 0 else on_hi[a]):
                continue                   # that side is the board's own edge
            p0, p1 = [0.0, 0.0], [0.0, 0.0]
            ia, ib = (0, 1) if a == h else (1, 0)
            p0[ia] = p1[ia] = at
            p0[ib], p1[ib] = lo[b], hi[b]
            if on_hi[b] and not on_lo[b]:
                p0, p1 = p1, p0            # start at the edge it reaches
            (opened if on_lo[b] or on_hi[b] else lines).append((tuple(p0), tuple(p1)))
    opened.sort(key=lambda ln: -abs(ln[1][0] - ln[0][0]) - abs(ln[1][1] - ln[0][1]))
    through = on_lo[t] and on_hi[t]
    return CutPlan(h, v, t, measures, opened + lines, None if through else hi[t] - lo[t],
                   len(opened))


@dataclass
class Profile:
    """A board as an outline in its (u, v) plane, piece-frame coordinates, counter-clockwise,
    extruded along axis t from t0 to t1."""
    u: int
    v: int
    t: int
    outline: list[tuple[float, float]]
    t0: float
    t1: float

    def point(self, a: float, b: float, c: float) -> tuple[float, float, float]:
        p = [0.0, 0.0, 0.0]
        p[self.u], p[self.v], p[self.t] = a, b, c
        return tuple(p)


@dataclass
class Joint:
    path: str
    id: str
    name: str
    parts: list[str]           # part ids
    connector: str
    count: int
    setting: str
    tools: list[str]
    face_lo: tuple[float, float, float]   # the face where the parts meet
    face_hi: tuple[float, float, float]
    normal_axis: int                      # the axis the face is perpendicular to
    along_axis: int                       # the axis the connectors are spread along
    positions: list[tuple[float, float, float]] = field(default_factory=list)
    stated: bool = False                  # the joint gives its connectors' positions itself
    size: tuple[float, float] | None = None   # a connector's length along, thickness across
    methods: list[Tool] = field(default_factory=list)  # how its seats are cut and drilled, in order
    groove_offset: float | None = None    # the machine's reference face to its groove's middle
    spacers: list[float] = field(default_factory=list)  # what brings that groove nearer, mm
    hole: tuple[float, float] | None = None  # the access hole: (diameter, from the joint face)
    machine: str = ""          # the tool its grooves are cut with (the one stating groove_offset)
    jig: str = ""              # the tool its access holes are drilled with
    test_recess: float | None = None   # how far under the surface a test groove's connector sits
    tool_keys: list[str] = field(default_factory=list)   # the paths of its tools, as `tools` names them
    fasteners: list[tuple[str, str, tuple | None]] = field(default_factory=list)  # each thing it uses: path, name, size


SIDES = {(0, False): "left", (0, True): "right", (1, False): "front", (1, True): "back",
         (2, False): "bottom", (2, True): "top"}


@dataclass
class Seat:
    """One part's grooves of one joint, as they are marked, set and cut: the surface they go in (an
    edge when the joint meets the part's edge or end, else a face, named by its side), where along
    it (mm from the part's edge `start`), the face or edge the machine registers on and how far the
    groove's middle is from it with the spacer that gives it, and for a part grooved in its edge the
    access holes, drilled from the face away from that reference. A shelf that meets a face away
    from its ends (`line`) is placed by a line drawn on that face, its top face's, measured from
    the face's edge `line_from`."""
    joint: str
    part: str
    other: str
    in_edge: bool
    side: str                   # the side of the part the grooves open on
    start: str                  # the part's edge the positions are measured from
    at: list[float]
    reference: str              # the side of the part the machine registers on
    offset: float | None        # mm from the reference to the groove's middle
    spacer: float = 0.0
    line: float | None = None
    line_from: str = ""
    hole_side: str = ""
    hole: tuple[float, float] | None = None
    points: list[tuple[float, float, float]] = field(default_factory=list)  # each groove's middle
    holes: list[tuple[float, float, float]] = field(default_factory=list)   # each hole's centre
    length: float | None = None   # the connector's length along the joint


def _thin(p: "Part") -> int:
    return min(range(3), key=lambda i: p.hi[i] - p.lo[i])


def _spacer(offset: float | None, spacers: list[float], thickness: float) -> float:
    """The spacer (none, or one of `spacers`) that brings the groove's middle nearest the middle of
    `thickness`; of two as near, the thinner."""
    if offset is None:
        return 0.0
    return min([0.0, *spacers], key=lambda s: (round(abs(offset - s - thickness / 2), 6), s))


def seats(sc: "Scene", j: Joint) -> list[Seat]:
    """Where each part of `j` is grooved and drilled, and from what reference, so that the two
    grooves of every connector meet: both cut from one plane, the face where the parts are flush,
    else the top face of the part whose edge meets the other's face, placed on a line."""
    if len(j.parts) != 2:
        return []
    a, b = (sc.part(i) for i in j.parts)
    n, al = j.normal_axis, j.along_axis
    across = next(i for i in range(3) if i not in (n, al))
    face = [p for p in (a, b) if _thin(p) == n]
    edge = [p for p in (a, b) if _thin(p) != n]
    if len(face) != 1 or len(edge) != 1:
        return []
    F, E = face[0], edge[0]
    if abs(E.lo[across] - F.lo[across]) <= TOUCH:
        high, line = False, None
    elif abs(E.hi[across] - F.hi[across]) <= TOUCH:
        high, line = True, None
    else:
        high, line = True, E.hi[across] - F.lo[across]
    spacer = _spacer(j.groove_offset, j.spacers, E.hi[across] - E.lo[across])
    offset = None if j.groove_offset is None else j.groove_offset - spacer
    plane = E.hi[across] if high else E.lo[across]
    meet = j.face_lo[n]

    def at_middle(q):
        pt = list(q)
        if offset is not None:
            pt[across] = plane - offset if high else plane + offset
        return tuple(pt)
    middles = [at_middle(q) for q in j.positions]
    inward = 1 if (E.lo[n] + E.hi[n]) / 2 > meet else -1
    out = []
    for p, other in ((E, F), (F, E)):
        toward = (other.lo[n] + other.hi[n]) / 2 > (p.lo[n] + p.hi[n]) / 2
        at = [round(q[al] - p.lo[al], 1) for q in j.positions]
        seat = Seat(j.id, p.id, other.id, p is E, SIDES[(n, toward)], SIDES[(al, False)], at,
                    SIDES[(across, high)], offset, spacer, points=middles,
                    length=j.size[0] if j.size else None)
        if p is F and line is not None:
            seat.reference, seat.line, seat.line_from = "", line, SIDES[(across, False)]
        if p is E and j.hole is not None:
            seat.hole_side, seat.hole = SIDES[(across, not high)], j.hole
            face_at = E.lo[across] if high else E.hi[across]
            for q in middles:
                h = list(q)
                h[n], h[across] = meet + inward * j.hole[1], face_at
                seat.holes.append(tuple(h))
        out.append(seat)
    return out


@dataclass
class Step:
    number: int
    text: str
    add: list[str]
    joints: list[str]
    prepare: bool
    tools: list[str]
    direction: dict[str, tuple[int, int, int]]
    split: list[str] = field(default_factory=list)
    cuts: list[str] = field(default_factory=list)
    builds: str = ""   # the assembly it puts together aside, away from the piece (payload builds), by id
    wholes: dict[str, str] = field(default_factory=dict)   # part id -> the assembly it comes in with, whole
    keys: list[str] = field(default_factory=list)   # by tool, its path when the step names it by path, else ""


def place_of(keys, places: dict | None) -> str | None:
    """The one place that holds every tool a step names by path (`keys`, "" for a tool named in words, a
    material, which is not counted), given where the person has each tool (`places`: {path: place name}):
    None when the step names no tool by path, when a tool it names is at no place of the person's, and when
    its tools are at two places. A place is never said for a step that cannot be done there."""
    held = [k for k in keys or () if k]
    if not held or not places:
        return None
    where = {places.get(k) for k in held}
    return next(iter(where)) if len(where) == 1 and None not in where else None


@dataclass
class Scene:
    title: str
    piece: str
    parts: list[Part]
    joints: list[Joint]
    steps: list[Step]
    info: dict
    existing: list[Part] = field(default_factory=list)   # what is already there: a lintel, a wall
    tool_paths: dict[str, str] = field(default_factory=dict)   # a tool's name as the instructions say it -> its path

    def part(self, id_: str) -> Part:
        return next(p for p in [*self.parts, *self.existing] if p.id == id_)

    @property
    def lo(self):
        return tuple(min(p.lo[i] for p in self.parts) for i in range(3))

    @property
    def hi(self):
        return tuple(max(p.hi[i] for p in self.parts) for i in range(3))

    def connectors(self) -> int:
        return sum(j.count for j in self.joints)

    def part_at(self, path: str) -> Part:
        return next(p for p in self.parts if p.path == path)

    def apart(self) -> list[tuple[str, tuple, tuple, list[str]]]:
        """The things the piece is made of that stand apart from each other (standing_apart), each
        (name, lo, hi, the paths of its parts). One for a piece that is one thing; two for two wardrobes'
        doors modelled side by side with a gap the model chose for the drawing, whose overall size would
        print the gap as a fact."""
        names = {(p.within[0] if p.within else (p.id, p.name))[0]: (p.within[0] if p.within else (p.id, p.name))[1]
                 for p in self.parts}
        by = {p.path: p for p in self.parts}
        groups = standing_apart([(p.path, (p.within[0][0] if p.within else p.id), p.lo, p.hi) for p in self.parts])
        if len(groups) == 1:
            return [(self.title, self.lo, self.hi, [p.path for p in self.parts])]
        out = []
        for g in groups:
            ps = [by[q] for q in g]
            keys = list(dict.fromkeys(p.within[0][0] if p.within else p.id for p in ps))
            lo = tuple(min(p.lo[i] for p in ps) for i in range(3))
            hi = tuple(max(p.hi[i] for p in ps) for i in range(3))
            out.append((" + ".join(names[k] for k in keys), lo, hi, g))
        return out


def standing_apart(items: list[tuple[str, str, tuple, tuple]]) -> list[list[str]]:
    """The things that stand apart from each other, as the paths of their parts, left to right: `items` are
    the parts, each (path, the part or top-level group of the piece holding it, lo, hi); a top-level group
    is one thing, and those whose boxes meet are taken together."""
    top: dict[str, list] = {}
    for path, key, lo, hi in items:
        top.setdefault(key, []).append((path, lo, hi))
    boxes = {k: (tuple(min(lo[i] for _, lo, _ in ps) for i in range(3)), tuple(max(hi[i] for _, _, hi in ps) for i in range(3)))
             for k, ps in top.items()}
    groups: list[list[str]] = []
    for k in boxes:
        meets = [g for g in groups if any(all(boxes[k][0][i] <= boxes[o][1][i] + TOUCH and
                                              boxes[o][0][i] <= boxes[k][1][i] + TOUCH for i in range(3)) for o in g)]
        merged = [k] + [o for g in meets for o in g]
        groups = [g for g in groups if g not in meets] + [merged]
    groups.sort(key=lambda g: min(boxes[k][0][0] for k in g))
    return [[path for k in g for path, _, _ in top[k]] for g in groups]


def material_label(tree: Quern, piece: str, path: str) -> str:
    """How the documents name the material a part is cut from: the piece's payload material_names for it,
    else the material's payload label, else its name up to the first comma; empty when it names none."""
    uses = ((get_node(tree, path).links or {}).get("uses") or [])
    if not uses:
        return ""
    mat = get_node(tree, uses[0])
    names = (get_node(tree, piece).payload or {}).get("material_names", {})
    return (names.get(uses[0].rsplit("/", 1)[-1]) or ((mat.payload or {}).get("label") if mat else "")
            or ((mat.name if mat else "") or "").split(",")[0])


def connector_size(tree: Quern, links: dict) -> tuple[float, float] | None:
    """The size of a joint's connector, (length, thickness), from the first connector it uses that states
    both; None when none does."""
    for c in links.get("uses", []):
        length, thickness = _param(tree, c, "length"), _param(tree, c, "thickness")
        if length is not None and thickness is not None:
            return (length, thickness)
    return None


def _tool(tree: Quern, path: str) -> Tool:
    node = get_node(tree, path)
    cites = []
    for ref in (node.links or {}).get("per", []):
        clause = get_node(tree, ref)
        source = get_node(tree, ref.rsplit("/", 1)[0])
        short = (source.payload or {}).get("identifier") or source.name or source.id
        cites.append((short, (clause.payload or {}).get("locator", clause.id)))
    return Tool(path, node.name or node.id, (node.payload or {}).get("say", {}), cites,
                (node.payload or {}).get("model"), list((node.links or {}).get("follows", [])))


def _seat_methods(tree: Quern, joint: Joint, links: dict) -> None:
    """What a joint's tools and connector say of cutting its seats: each tool after the general tool
    it follows, its groove's distance from its reference and its spacers, then the connector's
    access hole and the tool that drills it."""
    seen: list[str] = []
    for t in links.get("made_with", []):
        for f in [*(get_node(tree, t).links or {}).get("follows", []), t]:
            if f not in seen:
                seen.append(f)
        if joint.groove_offset is None and _param(tree, t, "groove_offset") is not None:
            joint.groove_offset = _param(tree, t, "groove_offset")
            joint.machine = t
            joint.test_recess = _param(tree, t, "test_recess")
            joint.spacers = [float(x) for x in (get_node(tree, t).payload or {}).get("spacers_mm", [])]
    for c in links.get("uses", []):
        d, o = _param(tree, c, "access_hole_diameter"), _param(tree, c, "access_hole_offset")
        if d is not None and o is not None:
            joint.hole = (d, o)
            drills = (get_node(tree, c).links or {}).get("drilled_with", [])
            joint.jig = joint.jig or next(iter(drills), "")
            seen += [t for t in drills if t not in seen]
    joint.methods = [_tool(tree, t) for t in seen]


def _kerf(tree: Quern, path: str) -> float | None:
    """The width a saw takes out: its blade's kerf, else the widest blade it takes (max_kerf), else
    None when its maker states neither."""
    kerf = _param(tree, path, "kerf")
    return kerf if kerf is not None else _param(tree, path, "max_kerf")


def scene(tree: Quern, piece: str) -> Scene:
    from .drawings import cut_list

    rows = cut_list(tree, piece)
    marks = {p: r.mark for r in rows for p in r.paths}
    parts = []
    root_path = "/".join(_segs(piece))
    for b in bodies(tree, piece, existing=True):
        node = get_node(tree, b.path)
        uses = (node.links or {}).get("uses", [])
        payload = node.payload or {}
        cuts = []
        for c in payload.get("cuts", []):
            at = [number(tree, b.path, v, "cut's place") for v in c["at"]]
            size = [number(tree, b.path, v, "cut's size") for v in c["size"]]
            lo = tuple(b.lo[i] + at[i] for i in range(3))
            cuts.append((lo, tuple(lo[i] + size[i] for i in range(3))))
        tools = [_tool(tree, t) for t in (node.links or {}).get("made_with", [])]
        saws = [(get_node(tree, t).name or t.rsplit("/", 1)[-1], _kerf(tree, t))
                for t in (node.links or {}).get("sawn_with", [])]
        material = uses[0].rsplit("/", 1)[-1] if uses else ""
        label = material_label(tree, piece, b.path)
        segs, within = b.path[len(root_path) + 1:].split("/")[:-1], []
        for i in range(len(segs)):
            holder = get_node(tree, "/".join([root_path, *segs[:i + 1]]))
            if holder.kind != "part":
                within.append((holder.id, holder.name or holder.id))
        parts.append(Part(b.path, node.id, node.name or node.id, marks.get(b.path, ""),
                          tuple(b.lo), tuple(b.hi), material, label,
                          payload.get("span_along", ""),
                          int(payload.get("sheets", 1)), cuts, tools, saws, within,
                          section(tree, b.path, node), str(payload.get("bought_to_size") or ""), b.existing,
                          stock_thickness(tree, b.path, node)))
    by_path = {p.path: p for p in parts}
    there, parts = [p for p in parts if p.existing], [p for p in parts if not p.existing]
    joints = []
    prefix = piece.rstrip("/") + "/"
    for path, node in tree.walk(piece, kind="joint"):
        if not path.startswith(prefix):
            continue
        links = node.links or {}
        lay = joint_layout(tree, path, node, by_path)
        if lay is None:
            continue
        ps = [by_path["/".join(_segs(t))] for t in links.get("joins", [])]
        connector = ", ".join((get_node(tree, c).name or c.rsplit("/", 1)[-1])
                              for c in links.get("uses", []))
        tools = [(get_node(tree, t).name or t.rsplit("/", 1)[-1])
                 for t in links.get("made_with", [])]
        size = connector_size(tree, links)
        joint = Joint(path, node.id, node.name or node.id, [p.id for p in ps], connector,
                      int(_param(tree, path, "count") or 0),
                      (node.payload or {}).get("setting", ""), tools, lay.lo, lay.hi,
                      lay.normal, lay.along, lay.positions, lay.stated, size)
        joint.tool_keys = list(links.get("made_with", []))
        joint.fasteners = [(c, get_node(tree, c).name or c.rsplit("/", 1)[-1], connector_size(tree, {"uses": [c]}))
                           for c in links.get("uses", [])]
        _seat_methods(tree, joint, links)
        joints.append(joint)
    root = get_node(tree, piece)
    payload = root.payload or {}
    steps = []
    tool_paths: dict[str, str] = {}
    for j in joints:       # the tools a joint is made with are named by path in its links
        for t, name in zip(j.tool_keys, j.tools):
            tool_paths.setdefault(name, t)
    for i, s in enumerate(payload.get("steps", []), 1):
        if isinstance(s, str):
            s = {"text": s}
        add, wholes = [], {}
        coming = {k: DIRECTIONS[v] for k, v in (s.get("direction") or {}).items()}
        for a in s.get("add", []):      # an assembly named whole comes in as its parts, all the same way
            inside = [p.id for p in parts if a in [g for g, _ in p.within]]
            if inside and a not in [p.id for p in parts]:
                add += inside
                wholes |= {i: a for i in inside}
                if a in coming:
                    coming |= {i: coming[a] for i in inside}
            else:
                add.append(a)
        said, keys = [], []
        for t in s.get("tools", []):     # a tool named by its path says its node's name; any other text is said as it is
            node = get_node(tree, t) if isinstance(t, str) and t.startswith("tools/") else None
            said.append((node.name or node.id) if node is not None else t)
            keys.append(t if node is not None else "")
            if node is not None:
                tool_paths[said[-1]] = t
        steps.append(Step(i, s.get("text", ""), add, list(s.get("joints", [])),
                          bool(s.get("prepare", False)), said, coming,
                          list(s.get("split", [])), list(s.get("cuts", [])), str(s.get("builds") or ""), wholes, keys))
    info = {k: payload[k] for k in ("version", "authors", "date", "project", "use", "description")
            if k in payload}
    info["instructions"] = payload.get("instructions", "full")
    if info["instructions"] not in INSTRUCTIONS:
        raise ValueError(f"the piece {piece} has payload instructions {info['instructions']!r}: it must be "
                         f"one of {', '.join(INSTRUCTIONS)}")
    return Scene(root.name or root.id, piece, parts, joints, steps, info, there, tool_paths=tool_paths)
