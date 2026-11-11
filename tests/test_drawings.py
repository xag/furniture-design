"""The drawings read the tree: the example bench's cut list, joints and plans."""

from quern import Quern

from furniture_design import drawings
from furniture_design.package import EXAMPLES, PACKAGE

BENCH = "pieces/bench"


def _tree() -> Quern:
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = [n.model_copy(deep=True) for n in EXAMPLES]
    return tree


def test_the_cut_list_groups_equal_boards_and_sorts_their_sizes():
    rows = {(r.length, r.width, r.thickness): r.qty for r in drawings.cut_list(_tree(), BENCH)}
    assert rows == {(1000, 300, 20): 1, (450, 300, 20): 2, (960, 350, 20): 1}


def test_a_glued_up_part_is_cut_as_its_sheets():
    tree = _tree()
    tree.get(f"{BENCH}/top").payload["sheets"] = 2
    top = [r for r in drawings.cut_list(tree, BENCH) if r.length == 1000][0]
    assert (top.qty, top.thickness) == (2, 10)


def test_the_joints_name_their_parts_connector_and_count():
    js = {j["name"]: j for j in drawings.joints(_tree(), BENCH)}
    assert js["back-top"]["count"] == 4 and js["back-top"]["joins"] == ["back", "top"]


def test_a_plan_dimensions_every_edge_and_the_whole():
    svg = drawings.plan_svg(_tree(), BENCH, "front")
    for label in (">1000<", ">20<", ">960<", ">470<", ">350<", ">100<"):
        assert label in svg, label
