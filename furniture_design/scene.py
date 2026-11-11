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
  such as a notch for a skirting board), drawn but not counted by the checks;
- the steps: the piece's payload `steps`, each {text, add, joints, prepare, tools,
  direction}: `add` the part ids it brings in, `joints` the joint ids it closes,
  `prepare` true for the work done on parts before they are put together, `split` the
  glued-up parts shown as their separate sheets (the gluing step), `cuts` the parts whose
  cuts the step makes (shown hatched), `direction`
  for each added part the side it comes in from (up: lowered from above; front: slid in
  from the front; ...). Added parts with no direction are set down where they go.
- `material_names`: how the documents name each material, by its id.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from quern import Quern
from quern.tree import _segs, get_node

from .natives import _param, bodies, joint_layout, number

DIRECTIONS = {"up": (0, 0, 1), "down": (0, 0, -1), "left": (-1, 0, 0), "right": (1, 0, 0),
              "front": (0, -1, 0), "back": (0, 1, 0)}
TOUCH = 0.5


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

        t = min(range(3), key=lambda i: self.size[i])
        u, v = [i for i in range(3) if i != t]
        lo = [a + o for a, o in zip(self.lo, offset)]
        hi = [a + o for a, o in zip(self.hi, offset)]
        shape = rect(lo[u], lo[v], hi[u], hi[v])
        for clo, chi in self.cuts:
            clo = [a + o for a, o in zip(clo, offset)]
            chi = [a + o for a, o in zip(chi, offset)]
            if clo[t] <= lo[t] + TOUCH and chi[t] >= hi[t] - TOUCH:
                shape = shape.difference(rect(clo[u], clo[v], chi[u], chi[v]))
        shape = orient(shape, 1.0)
        return Profile(u, v, t, [tuple(p) for p in list(shape.exterior.coords)[:-1]],
                       lo[t], hi[t])


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


@dataclass
class Scene:
    title: str
    piece: str
    parts: list[Part]
    joints: list[Joint]
    steps: list[Step]
    info: dict

    def part(self, id_: str) -> Part:
        return next(p for p in self.parts if p.id == id_)

    @property
    def lo(self):
        return tuple(min(p.lo[i] for p in self.parts) for i in range(3))

    @property
    def hi(self):
        return tuple(max(p.hi[i] for p in self.parts) for i in range(3))

    def connectors(self) -> int:
        return sum(j.count for j in self.joints)


def scene(tree: Quern, piece: str) -> Scene:
    from .drawings import cut_list

    rows = cut_list(tree, piece)
    marks = {p: r.mark for r in rows for p in r.paths}
    names = (get_node(tree, piece).payload or {}).get("material_names", {})
    parts = []
    for b in bodies(tree, piece):
        node = get_node(tree, b.path)
        uses = (node.links or {}).get("uses", [])
        mat = get_node(tree, uses[0]) if uses else None
        payload = node.payload or {}
        cuts = []
        for c in payload.get("cuts", []):
            at = [number(tree, b.path, v, "cut's place") for v in c["at"]]
            size = [number(tree, b.path, v, "cut's size") for v in c["size"]]
            lo = tuple(b.lo[i] + at[i] for i in range(3))
            cuts.append((lo, tuple(lo[i] + size[i] for i in range(3))))
        material = uses[0].rsplit("/", 1)[-1] if uses else ""
        label = names.get(material) or ((mat.name if mat else "") or "").split(",")[0]
        parts.append(Part(b.path, node.id, node.name or node.id, marks.get(b.path, ""),
                          tuple(b.lo), tuple(b.hi), material, label,
                          payload.get("span_along", ""),
                          int(payload.get("sheets", 1)), cuts))
    by_path = {p.path: p for p in parts}
    joints = []
    prefix = piece.rstrip("/") + "/"
    for path, node in tree.walk(""):
        if node.kind != "joint" or not path.startswith(prefix):
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
        size = None
        for c in links.get("uses", []):
            length, thickness = _param(tree, c, "length"), _param(tree, c, "thickness")
            if length is not None and thickness is not None:
                size = (length, thickness)
                break
        joints.append(Joint(path, node.id, node.name or node.id, [p.id for p in ps], connector,
                            int(_param(tree, path, "count") or 0),
                            (node.payload or {}).get("setting", ""), tools, lay.lo, lay.hi,
                            lay.normal, lay.along, lay.positions, lay.stated, size))
    root = get_node(tree, piece)
    payload = root.payload or {}
    steps = []
    for i, s in enumerate(payload.get("steps", []), 1):
        if isinstance(s, str):
            s = {"text": s}
        steps.append(Step(i, s["text"], list(s.get("add", [])), list(s.get("joints", [])),
                          bool(s.get("prepare", False)), list(s.get("tools", [])),
                          {k: DIRECTIONS[v] for k, v in (s.get("direction") or {}).items()},
                          list(s.get("split", [])), list(s.get("cuts", []))))
    info = {k: payload[k] for k in ("version", "authors", "date", "project", "use", "description")
            if k in payload}
    return Scene(root.name or root.id, piece, parts, joints, steps, info)
