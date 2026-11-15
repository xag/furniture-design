"""The grooves a joint's parts are cut with, as the assembly instructions give them: one reference for
both parts of a joint, the spacer that centres the groove, the access holes, and the pages that draw them
without a sentence."""

import pytest
from quern import Quern
from quern.provenance import Quantity
from quern.tree import Node

from furniture_design.knowledge import knowledge, merge
from furniture_design.package import PACKAGE
from furniture_design.scene import _spacer, scene, seats
import re

from reportlab.pdfgen.canvas import Canvas

from furniture_design.grooving import grooving_pages
from furniture_design.sheets import LABELS, Pen, assembly_instructions

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


def test_a_joint_knows_the_machine_its_grooves_are_cut_with_and_the_jig_its_holes_are_drilled_with():
    sc = scene(_tree(), "pieces/cabinet")
    assert {(j.machine, j.jig) for j in sc.joints} == {("tools/jointer", "tools/jig")}
    sc.joints[0].methods[1].model = None
    tree = _tree()
    tree.get("tools/jointer").payload["model"] = {"parts": [{"op": "box", "lo": [-60, 0, 0], "hi": [60, 150, 30]}]}
    sc = scene(tree, "pieces/cabinet")
    assert next(t for t in sc.joints[0].methods if t.path == "tools/jointer").model["parts"][0]["op"] == "box"


def test_a_joints_methods_are_the_general_one_its_tool_follows_then_its_own_then_the_drills():
    sc = scene(_tree(), "pieces/cabinet")
    assert [t.path for t in sc.joints[0].methods] == ["tools/plate-jointer", "tools/jointer", "tools/jig"]
    general = sc.joints[0].methods[0]
    assert len(general.say["fr"]["method"]) == len(general.say["en"]["method"]) == 7
    assert ("Popular Woodworking: Plate joiner tips and techniques",
            "the shelf clamped on its line, photos A and B") in general.cites


def test_a_step_that_cuts_grooves_is_drawn_on_pages_of_its_own_a_block_of_frames_per_kind_of_joint(tmp_path):
    tree = _tree()
    drawn = assembly_instructions(scene(tree, "pieces/cabinet"), tmp_path / "with.pdf", "fr")
    tree.get("pieces/cabinet").payload["steps"][0]["joints"] = []
    without = assembly_instructions(scene(tree, "pieces/cabinet"), tmp_path / "without.pdf", "fr")
    pages = [p.read_bytes().count(b"/Type /Page\n") or p.read_bytes().count(b"/Type /Page")
             for p in (drawn, without)]
    assert pages[0] - pages[1] == 2   # the settings and the corners on one page, the shelves on the next


def test_the_grooving_pages_say_nothing_in_words(tmp_path, monkeypatch):
    """IKEA's instructions carry no sentence: what the grooving pages write is the step's label and its
    tools' names, and otherwise numbers, letters, counts and diameters."""
    written = []
    real = Pen.text
    monkeypatch.setattr(Pen, "text", lambda self, x, y, s, *a, **k: (written.append(s), real(self, x, y, s, *a, **k)))
    tree = _tree()
    tree.get("tools/jointer").payload["model"] = {
        "parts": [{"op": "box", "lo": [-60, 0, 0], "hi": [60, 150, 30]}],
        "poses": {"flat": [{"op": "box", "lo": [-60, -70, 20], "hi": [60, 0, 23]}], "standing": []},
        "dials": [{"at": [50, 10, 40], "shows": "max"}, {"at": [-30, 30, 90], "shows": "setting"}]}
    sc = scene(tree, "pieces/cabinet")
    c = Canvas(str(tmp_path / "grooving.pdf"))
    grooving_pages(c, Pen(c), sc, sc.steps[0], LABELS["fr"])
    c.save()
    allowed = {LABELS["fr"]["prepare"], *sc.steps[0].tools}
    words = [w for w in written if w not in allowed and not re.fullmatch(r"[0-9A-Z×Ø ,.-]{1,7}|max|S-1", w)]
    assert written and not words, words


def test_short_instructions_draw_only_the_marks_and_the_holes_of_each_kind_of_joint(tmp_path):
    tree = _tree()
    full = assembly_instructions(scene(tree, "pieces/cabinet"), tmp_path / "full.pdf", "fr")
    tree.get("pieces/cabinet").payload["instructions"] = "short"
    short = assembly_instructions(scene(tree, "pieces/cabinet"), tmp_path / "short.pdf", "fr")
    pages = [p.read_bytes().count(b"/Type /Page\n") or p.read_bytes().count(b"/Type /Page") for p in (full, short)]
    assert pages[0] - pages[1] == 1   # two frames a kind of joint: the corners and the shelves on one page
