"""The drawings read the tree: the example bench's cut list, joints and plans."""

from quern import Quern
from quern.tree import get_node

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


def test_the_scene_letters_equal_boards_alike_and_spreads_connectors_along_the_joint():
    from furniture_design.scene import scene
    sc = scene(_tree(), BENCH)
    marks = {p.id: p.mark for p in sc.parts}
    assert marks["left"] == marks["right"] != marks["top"]
    top = next(j for j in sc.joints if j.id == "back-top")
    xs = sorted(p[0] for p in top.positions)   # 4 connectors along the 960 mm back
    assert len(xs) == 4 and abs(xs[0] - (20 + 960 / 5)) < 1e-6


def test_a_connector_is_drawn_at_the_size_its_node_states():
    from furniture_design.scene import scene
    tree = _tree()
    joint = next(j for j in scene(tree, BENCH).joints if j.id == "back-top")
    assert joint.size == (60.0, 8.0)   # the example maker's catalogue: 60 long, 8 thick
    del get_node(tree, "connectors/example-connector").params["length"]
    assert next(j for j in scene(tree, BENCH).joints if j.id == "back-top").size is None


def test_stated_positions_are_drawn_where_they_are_stated():
    from furniture_design.scene import scene
    tree = _tree()
    get_node(tree, f"{BENCH}/back-top").payload["positions"] = [100, 300, 660, 860]
    joint = next(j for j in scene(tree, BENCH).joints if j.id == "back-top")
    assert [p[0] for p in joint.positions] == [120, 320, 680, 880] and joint.stated


def test_the_checks_read_as_sentences_with_their_numbers():
    from furniture_design.report import checks
    rows = checks(_tree(), BENCH)
    sideways = [r for r in rows if r["requirement"].startswith("Poussée")]
    assert sideways and sideways[0]["verdict"] == "ok" and "N" in sideways[0]["result"]


def test_the_three_documents_are_written(tmp_path):
    out = drawings.documents(_tree(), BENCH, tmp_path)
    assert out["design"].read_bytes()[:4] == b"%PDF" and out["assembly"].read_bytes()[:4] == b"%PDF"
    page = out["viewer"].read_text(encoding="utf-8")
    assert "three.min.js" in page and '"mark": "A"' in page
