"""What whoever designs with the package is told (furniture_design.guidance), and that what it tells works."""
from quern import Node, Quern
from quern.provenance import Quantity

from furniture_design.guidance import guidance
from furniture_design.package import EXAMPLES, PACKAGE
from furniture_design.scene import scene


def _said(id_: str) -> str:
    return next(n for n in guidance().children if n.id == id_).payload["text"]


def test_the_guidance_says_how_to_build_aside_fit_what_is_there_and_survey_it():
    aside = _said("assemblies-built-aside")
    assert "builds" in aside and "whole" in aside
    fitted = _said("a-section-already-there-and-the-cut-that-fits-it")
    assert "section" in fitted and "cuts" in fitted and "params" in fitted
    survey = _said("surveying-what-is-there")
    assert "sketch" in survey and "starts and ends" in survey and "measured" in survey


def _mm(v: float) -> Quantity:
    return Quantity(value=v, unit="mm", provenance="measured", grounded=True, tolerance=1)


def test_a_section_already_there_and_the_cut_that_fits_it_follow_one_measure():
    """What the guidance on a section already there says works: a frame whose nose (an L across its length) goes
    into the notch of the side that fits it, both read from the same two params, so measuring the rebate again
    moves both."""
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = [n.model_copy(deep=True) for n in EXAMPLES]
    piece = tree.get("pieces/bench-side")
    piece.params = {"rebate_depth": _mm(25), "rebate_height": _mm(115)}
    piece.children.append(Node(id="frame", kind="part", payload={
        "existing": "the window's frame",
        "shape": {"op": "box", "size": [1000, "rebate_depth + 35", 200]},
        "transform": {"translate": [-500, "300 - rebate_depth", 0]},
        "section": [[0, 0], ["rebate_depth + 35", 0], ["rebate_depth + 35", 200], ["rebate_depth", 200],
                    ["rebate_depth", "rebate_height"], [0, "rebate_height"]]}))
    side = tree.get("pieces/bench-side/side")
    side.params.pop("skirting_depth"), side.params.pop("skirting_height")
    side.payload["cuts"] = [{"at": [0, "300 - rebate_depth", 0], "size": [18, "rebate_depth", "rebate_height"]}]

    def read():
        sc = scene(tree, "pieces/bench-side")
        frame = next(p for p in sc.existing if p.id == "frame")
        cut = next(p for p in sc.parts if p.id == "side").cuts[0]
        return frame.section[3:5], (cut[1][1] - cut[0][1], cut[1][2] - cut[0][2])

    assert read() == ([(25, 200), (25, 115)], (25, 115))
    piece.params["rebate_depth"] = _mm(27)
    assert read() == ([(27, 200), (27, 115)], (27, 115))
