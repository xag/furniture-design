"""The grooves a joint's parts are cut with, as the assembly instructions give them: one reference for
both parts of a joint, the spacer that centres the groove, the access holes, and the sentences."""

import pytest
from quern import Quern
from quern.provenance import Quantity
from quern.tree import Node

from furniture_design.knowledge import knowledge, merge
from furniture_design.package import PACKAGE
from furniture_design.scene import _spacer, scene, seats
from furniture_design.sheets import LABELS, assembly_instructions, seat_sentences

THICK = 18


def _mm(v: float) -> Quantity:
    return Quantity(value=v, unit="mm", provenance="published")


def _part(id_: str, size: list, at: list) -> Node:
    return Node(id=id_, kind="part", links={"uses": ["materials/birch-yellow"]},
                payload={"shape": {"op": "box", "size": size}, "transform": {"translate": at}})


def _joint(id_: str, a: str, b: str, count: int) -> Node:
    return Node(id=id_, kind="joint", payload={"cut": "surface", "setting": "S-1"},
                params={"count": Quantity(value=count, unit="", provenance="design-target")},
                links={"joins": [f"pieces/cabinet/{a}", f"pieces/cabinet/{b}"],
                       "uses": ["connectors/holed"], "made_with": ["tools/jointer"]})


def _tree(thickness: float = THICK) -> Quern:
    """A top on two sides, flush with their outsides, and a shelf between them, away from their
    edges; a jointer whose groove is 10 mm from its reference with spacers of 2 and 4 mm, and a
    connector closed through a 6 mm hole 7.5 mm from the joint face."""
    t = thickness
    parts = [_part("left", [t, 300, 500], [0, 0, 0]), _part("right", [t, 300, 500], [600 - t, 0, 0]),
             _part("top", [600, 300, t], [0, 0, 500]), _part("shelf", [600 - 2 * t, 250, t], [t, 25, 200])]
    joints = [_joint("top-left", "top", "left", 2), _joint("top-right", "top", "right", 2),
              _joint("shelf-left", "shelf", "left", 2), _joint("shelf-right", "shelf", "right", 2)]
    steps = [{"text": "Cut the grooves.", "prepare": True, "add": ["left", "right", "top", "shelf"],
              "joints": [j.id for j in joints]}]
    cabinet = Node(id="cabinet", kind="piece", payload={"steps": steps}, children=parts + joints)
    hardware = [
        Node(id="connectors", kind="", children=[Node(
            id="holed", kind="connector", params={"access_hole_diameter": _mm(6), "access_hole_offset": _mm(7.5),
                                                  "length": _mm(64), "thickness": _mm(9.7)},
            links={"needs": ["tools/jointer"], "drilled_with": ["tools/jig"]})]),
        Node(id="tools", kind="", children=[
            Node(id="jointer", kind="tool", name="A jointer",
                 payload={"spacers_mm": [2, 4], "say": {"fr": {"name": "Une lamelleuse", "method": ["Plonger."]}}},
                 params={"groove_offset": _mm(10)}, links={"follows": ["tools/plate-jointer"]}),
            Node(id="jig", kind="tool", name="A jig", payload={"say": {"fr": {"name": "Un gabarit", "method": ["Percer."]}}})])]
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = merge(knowledge(), hardware) + [Node(id="pieces", kind="", children=[cabinet])]
    return tree


def _seats(tree: Quern, joint: str) -> dict:
    sc = scene(tree, "pieces/cabinet")
    j = next(j for j in sc.joints if j.id == joint)
    return sc, {s.part: s for s in seats(sc, j)}


@pytest.mark.parametrize("thickness, spacer", [(20, 0), (16, 2), (12, 4), (18, 0), (19, 0), (17, 2)])
def test_the_spacer_is_the_one_that_centres_the_groove_and_of_two_as_near_the_thinner(thickness, spacer):
    # Lamello: 10 mm from the base plate is the middle of 20 mm; its 16 mm corner is drawn with the 2 mm spacer
    assert _spacer(10, [2, 4], thickness) == spacer


@pytest.mark.parametrize("thickness", [12, 16, 18, 20])
def test_both_grooves_of_every_connector_meet_and_lie_in_both_parts(thickness):
    tree = _tree(thickness)
    sc = scene(tree, "pieces/cabinet")
    for j in sc.joints:
        e, f = seats(sc, j)
        assert e.points == f.points and len(e.points) == j.count
        for q in e.points:
            for p in (sc.part(e.part), sc.part(f.part)):
                assert all(lo - 0.01 <= v <= hi + 0.01 for v, lo, hi in zip(q, p.lo, p.hi)), (j.id, p.id, q)


def test_a_corner_is_cut_from_the_face_where_its_parts_are_flush_and_drilled_from_the_other():
    sc, s = _seats(_tree(), "top-left")
    side, top = s["left"], s["top"]
    assert (side.in_edge, side.side, side.reference, side.offset, side.spacer) == (True, "top", "left", 10, 0)
    assert (top.in_edge, top.side, top.reference) == (False, "bottom", "left")
    assert side.at == top.at == [100, 200] and side.start == "front"
    assert side.hole_side == "right" and side.hole == (6, 7.5) and not top.holes
    assert all(h[2] == 500 - 7.5 and h[0] == THICK for h in side.holes)
    assert all(q[0] == 10 for q in side.points)


def test_a_shelf_is_placed_by_the_line_of_its_top_face_and_cut_10_mm_below_it():
    sc, s = _seats(_tree(), "shelf-left")
    shelf, side = s["shelf"], s["left"]
    assert (shelf.in_edge, shelf.side, shelf.reference, shelf.hole_side) == (True, "left", "top", "bottom")
    assert (side.line, side.line_from, side.side) == (200 + THICK, "bottom", "right")
    assert all(q[2] == 200 + THICK - 10 for q in side.points)
    assert shelf.at == [round(250 / 3, 1), round(500 / 3, 1)] and side.at == [round(25 + 250 / 3, 1), round(25 + 500 / 3, 1)]


def test_the_card_says_each_grooves_place_reference_and_hole_in_whole_sentences():
    tree = _tree()
    L = LABELS["fr"]
    sc, s = _seats(tree, "top-left")
    top, side = sc.part("top").mark, sc.part("left").mark
    assert seat_sentences(s["left"], sc, L, "fr") == [
        f"Le chant du haut (contre {top}) : rainures à 100 et 200 depuis le chant avant ; leur milieu à 10 "
        f"de la face gauche, sans cale : la face qui affleure avec {top}.",
        "Trous d'accès Ø 6 dans la face droite, à 7.5 du chant du haut, au milieu de chaque rainure."]
    assert seat_sentences(s["top"], sc, L, "fr") == [
        f"La face du dessous (contre {side}) : rainures à 100 et 200 depuis le chant avant ; leur milieu à 10 "
        f"du chant gauche, sans cale : le chant qui affleure avec {side}."]
    sc, s = _seats(tree, "shelf-left")
    mark = sc.part("shelf").mark
    assert seat_sentences(s["left"], sc, L, "fr") == [
        f"La face droite (contre {mark}) : tracer le dessus de {mark} à 218 depuis le chant du bas ; rainures "
        f"à 108.3 et 191.7 depuis le chant avant, leur milieu à 10 du trait, du côté de {mark}."]


def test_a_joints_methods_are_the_general_one_its_tool_follows_then_its_own_then_the_drills():
    sc = scene(_tree(), "pieces/cabinet")
    assert [t.path for t in sc.joints[0].methods] == ["tools/plate-jointer", "tools/jointer", "tools/jig"]
    general = sc.joints[0].methods[0]
    assert len(general.say["fr"]["method"]) == len(general.say["en"]["method"]) == 7
    assert ("Popular Woodworking: Plate joiner tips and techniques",
            "the shelf clamped on its line, photos A and B") in general.cites


def test_a_step_that_cuts_grooves_prints_its_method_and_a_card_per_part(tmp_path):
    tree = _tree()
    with_cards = assembly_instructions(scene(tree, "pieces/cabinet"), tmp_path / "with.pdf", "fr")
    tree.get("pieces/cabinet").payload["steps"][0]["joints"] = []
    without = assembly_instructions(scene(tree, "pieces/cabinet"), tmp_path / "without.pdf", "fr")
    pages = [p.read_bytes().count(b"/Type /Page\n") or p.read_bytes().count(b"/Type /Page")
             for p in (with_cards, without)]
    assert pages[0] - pages[1] == 1 + 2   # the method's page, and four cards two to a page
