"""A joint fastened by screws or a glue is not judged by the rules of a connector.

The rules on a joint's seat (how thick and wide its parts must be, the tool that cuts it) read a
connector's limits through `uses`. Screws, or a glue, named in `uses` have no seat and state none of
them: judged anyway, the joint came out absent or broken and the piece non-compliant.
"""

from __future__ import annotations

from quern import Quern, run_rules
from quern.tree import Node

CONNECTOR_RULES = {"a-joined-part-is-thick-enough-for-the-cut", "a-joined-part-is-wide-enough",
                   "a-joint-is-cut-with-a-tool-its-connector-takes"}


def _judged(uses: list[str], made_with: list[str] | None = None, payload: dict | None = None) -> list[str]:
    from furniture_design.package import PACKAGE, _world

    nodes = _world()
    box = next(p for p in next(n for n in nodes if n.id == "pieces").children if p.id == "box")
    corner = next(c for c in box.children if c.id == "corner")
    corner.payload = corner.payload if payload is None else payload
    corner.links = {"joins": corner.links["joins"], "uses": uses, "made_with": made_with or []}
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = nodes
    return sorted(r.rule for r in run_rules(tree)
                  if not r.ok and r.rule in CONNECTOR_RULES and r.node == "pieces/box/corner")


def test_a_screwed_joint_is_not_judged_by_a_connectors_rules():
    """Screws the knowledge holds as a material, as a person's own package may."""
    assert _judged(["materials/birch-yellow"], payload={}) == []


def test_a_joint_with_a_connector_still_is():
    """The same joint fastened by the connector again, its seat cut with nothing: its sides are
    thick and wide enough for the connector, and no tool cuts its seat."""
    assert _judged(["connectors/example-connector"]) == ["a-joint-is-cut-with-a-tool-its-connector-takes"]


def _verdicts(change) -> dict[tuple[str, str], str]:
    """Every verdict of the package's rules on the example world after `change(nodes)`, by (rule, node)."""
    from furniture_design.package import PACKAGE, _world

    nodes = _world()
    change(nodes)
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = nodes
    return {(r.rule, r.node): r.verdict for r in run_rules(tree)}


def _piece(nodes, id_):
    return next(p for p in next(n for n in nodes if n.id == "pieces").children if p.id == id_)


def _unstated(size: float):
    """The box's sides and the notched bench side state no thickness param: their boxes say it, `size` thick."""
    def change(nodes):
        for side in (c for c in _piece(nodes, "box").children if c.kind == "part"):
            side.params.pop("thickness")
            side.payload["shape"]["size"][0] = size
        notched = _piece(nodes, "bench-side").children[0]
        notched.params.pop("thickness")
        notched.payload["shape"]["size"][0] = size
    return change


def test_a_joined_or_sawn_part_that_states_no_thickness_is_as_thick_as_its_box_says():
    ok = _verdicts(_unstated(18))
    assert ok[("a-joined-part-is-thick-enough-for-the-cut", "pieces/box/corner")] == "holds"
    assert ok[("a-part-is-no-thicker-than-its-saw-cuts", "pieces/bench-side/side")] == "holds"
    thin, thick = _verdicts(_unstated(12)), _verdicts(_unstated(60))
    assert thin[("a-joined-part-is-thick-enough-for-the-cut", "pieces/box/corner")] == "broken"
    assert thick[("a-part-is-no-thicker-than-its-saw-cuts", "pieces/bench-side/side")] == "broken"


def test_a_beam_still_states_its_thickness():
    def change(nodes):
        shelf = _piece(nodes, "bookshelf").children[0]
        shelf.params.pop("thickness")
        shelf.payload["shape"]["size"][2] = 19
    assert _verdicts(change)[("a-beam-is-strong-enough", "pieces/bookshelf/shelf")] == "absent"


# --- a fastener that bonds, and one that is driven in --------------------------------------------
#
# Found on a window's cladding (feedback 4VzTS0vis0bizQVTl3vl): a board glued to a wall with a mastic was asked
# how many mastics it took, the dabs it was given were laid out as screws and driven through the frame in front
# of the wall, and the page of what is needed counted "17 ×" of the mastic, the plugs of the other joints among
# them. How a fastener holds and how it is counted are on its node: holds (driven or bonds) and counted (pieces
# or none). A made-up wall here, a batten on it, and a trim already there in front of the batten.

_MASTIC = Node(id="example-mastic", kind="material", name="Example mastic",
               payload={"form": "adhesive sealant", "measured_along": "unstated", "holds": "bonds", "counted": "none"})
_PLUG = Node(id="example-plug", kind="material", name="Example plug",
             payload={"form": "wall plug", "measured_along": "unstated", "holds": "driven", "counted": "pieces"})
_CLADDING = "pieces/cladding"


def _cladding(uses: list[str], count: int | None = None) -> Quern:
    """A batten glued, or glued and plugged, to a wall already there, with a trim already there in front of it,
    brought in from the left so that nothing but its fasteners can cross the trim."""
    from quern.provenance import Quantity

    from furniture_design.knowledge import knowledge, merge
    from furniture_design import standards
    from furniture_design.package import PACKAGE

    q = lambda v: Quantity(value=v, unit="mm", provenance="design-target", grounded=False)  # noqa: E731
    wall = Node(id="wall", kind="part", name="Wall", payload={
        "existing": "a concrete wall", "shape": {"op": "box", "size": [1000, 200, 1000]},
        "transform": {"translate": [0, 22, 0]}})
    trim = Node(id="trim", kind="part", name="Trim", payload={
        "existing": "a window's frame", "shape": {"op": "box", "size": [40, 20, 1000]},
        "transform": {"translate": [0, -30, 0]}})
    batten = Node(id="batten", kind="part", name="Batten", links={"uses": ["materials/birch-yellow"]},
                  params={"thickness": q(22), "width": q(40)},
                  payload={"shape": {"op": "box", "size": [40, 22, 1000]}, "bought_to_size": "a shop"})
    joint = Node(id="fixed", kind="joint", name="Batten to the wall",
                 links={"joins": [f"{_CLADDING}/batten", f"{_CLADDING}/wall"], "uses": uses},
                 params={} if count is None else {"count": Quantity(value=count, provenance="design-target",
                                                                     grounded=False)})
    piece = Node(id="cladding", kind="piece", name="Cladding", children=[wall, trim, batten, joint],
                 payload={"steps": [{"add": ["batten"], "direction": {"batten": "left"}, "joints": ["fixed"]}]})
    tree = Quern(vocabulary=PACKAGE.vocabulary + standards.VOCABULARY, rules=PACKAGE.rules + standards.RULES,
                 solvers=PACKAGE.solvers + standards.SOLVERS)
    tree.root.children = merge(knowledge(), [Node(id="materials", kind="", children=[_MASTIC, _PLUG])]) + [
        Node(id="pieces", kind="", children=[piece])]
    return tree


def _fastened(tree: Quern) -> str:
    return next(r.verdict for r in run_rules(tree) if r.rule == "a-pieces-joints-say-what-fastens-them"
                and r.node == _CLADDING)


def _driven(tree: Quern) -> list[str]:
    from furniture_design.standards_piece import EXPLAINERS

    return [line for line in EXPLAINERS["furniture/arrivals_blocked"](tree, _CLADDING) if "driven" in line]


GLUED, PLUGGED = ["materials/example-mastic"], ["materials/example-mastic", "materials/example-plug"]


def test_a_batten_glued_to_a_wall_states_no_count_and_goes_through_nothing():
    assert _fastened(_cladding(GLUED)) == "holds"
    assert _driven(_cladding(GLUED)) == []
    # a count written on it anyway places nothing: the mastic is not laid out as screws
    from furniture_design.scene import scene

    joint = scene(_cladding(GLUED, count=6), _CLADDING).joints[0]
    assert joint.positions == [] and joint.bonded and joint.count == 0
    assert _driven(_cladding(GLUED, count=6)) == []


def test_a_batten_glued_and_plugged_counts_its_plugs_and_drives_them_alone():
    assert _fastened(_cladding(PLUGGED)) == "broken"
    assert _fastened(_cladding(PLUGGED, count=3)) == "holds"
    assert _driven(_cladding(PLUGGED, count=3)) == [
        f"step 1: 3 of the 3 connectors of {_CLADDING}/fixed are driven in through {_CLADDING}/trim "
        "(numbers 1, 2, 3 along the joint)"]


def _needed(tree: Quern, tmp_path) -> tuple[list, list[str], dict]:
    """The hardware of the needed screen, the counts printed on the page of what is needed, and the step's frame."""
    import json

    from furniture_design import drawings

    made = drawings.document(tree, _CLADDING, tmp_path, "assembly")
    screens = json.loads(made["steps"].read_text(encoding="utf-8"))["screens"]
    drawn = Node.model_validate(json.loads(made["pages"].read_text(encoding="utf-8")))
    pages = [p for p in drawn.children[0].children if p.kind == "page"]
    counts = [w["text"] for p in pages if not any(f.payload.get("kind") == "step" for f in p.children)
              for w in p.payload["words"] if w["text"].endswith(" ×")]
    step = next(f.payload for p in pages for f in p.children if f.payload.get("kind") == "step")
    return next(s for s in screens if s["kind"] == "needed")["hardware"], counts, step


def test_the_documents_name_a_mastic_and_count_only_the_plugs(tmp_path):
    hardware, counts, step = _needed(_cladding(PLUGGED, count=3), tmp_path / "plugged")
    assert hardware == [{"name": "Example mastic"}, {"name": "Example plug", "count": 3}]
    assert counts == ["1 ×", "3 ×"]           # the batten, then the plugs; the mastic has no count
    hardware, counts, step = _needed(_cladding(GLUED), tmp_path / "glued")
    assert hardware == [{"name": "Example mastic"}] and counts == ["1 ×"]
    assert step["closes"] == ["fixed"] and step["fastened"] == ["fixed"]   # the glued face is drawn
