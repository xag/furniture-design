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


def test_a_part_is_sized_and_placed_by_expressions_over_its_pieces_params():
    from furniture_design.natives import bodies
    from quern.provenance import Quantity
    tree = _tree()
    bench = get_node(tree, BENCH)
    bench.params.update({k: Quantity(value=v, unit="mm", provenance="design-target")
                         for k, v in {"height": 600.0, "board": 20.0, "lift": 100.0}.items()})
    top = get_node(tree, f"{BENCH}/top")
    top.payload["shape"]["size"][2] = "board"
    top.payload["transform"]["translate"][2] = "height - board"
    back = get_node(tree, f"{BENCH}/back")
    back.payload["shape"]["size"][2] = "height - board - lift"
    back.payload["transform"]["translate"][2] = "lift"
    boxes = {b.path.rsplit("/", 1)[-1]: b for b in bodies(tree, BENCH)}
    assert boxes["top"].lo[2] == 580 and boxes["top"].hi[2] == 600
    assert boxes["back"].lo[2] == 100 and boxes["back"].hi[2] == 580


def test_an_expression_naming_no_param_is_refused():
    import pytest
    from furniture_design.natives import bodies
    tree = _tree()
    get_node(tree, f"{BENCH}/top").payload["transform"]["translate"][2] = "height - 20"
    with pytest.raises(ValueError, match="height"):
        bodies(tree, BENCH)


def test_the_checks_read_as_sentences_with_their_numbers():
    from furniture_design.report import checks
    rows = checks(_tree(), BENCH)
    sideways = [r for r in rows if r["requirement"].startswith("Poussée")]
    assert sideways and sideways[0]["verdict"] == "ok" and "N" in sideways[0]["result"]


def test_every_language_says_the_same_checks_with_the_same_numbers():
    """Each language the documents are written in has every sentence the checks use, and says
    the same rows with the same verdicts: a language that lacks one is a KeyError here, not a
    blank in somebody's plans."""
    from furniture_design.report import DECIMAL, MATERIAL_WORDS, TEXT, checks
    assert set(TEXT) == set(MATERIAL_WORDS) == set(DECIMAL) == {"fr", "en"}
    for lang in TEXT:
        assert set(TEXT[lang]) == set(TEXT["fr"]), lang
        assert set(MATERIAL_WORDS[lang]) == set(MATERIAL_WORDS["fr"]), lang
    fr, en = checks(_tree(), BENCH, "fr"), checks(_tree(), BENCH, "en")
    assert [r["verdict"] for r in fr] == [r["verdict"] for r in en]
    sideways = [r for r in en if r["requirement"].startswith("Sideways push")]
    assert sideways and "N" in sideways[0]["result"]
    assert not any(w in r["requirement"] + r["result"] for r in en for w in ("Poussée", "Flèche", " sous "))


def test_the_documents_are_written_in_english(tmp_path):
    out = drawings.documents(_tree(), BENCH, tmp_path, lang="en")
    assert out["design"].name.endswith("-design.pdf") and out["assembly"].name.endswith("-assembly.pdf")
    assert out["design"].read_bytes()[:4] == b"%PDF" and out["assembly"].read_bytes()[:4] == b"%PDF"


def test_the_three_documents_are_written(tmp_path):
    out = drawings.documents(_tree(), BENCH, tmp_path)
    assert out["design"].read_bytes()[:4] == b"%PDF" and out["assembly"].read_bytes()[:4] == b"%PDF"
    page = out["viewer"].read_text(encoding="utf-8")
    assert "three.min.js" in page and '"mark": "A"' in page


# --- a part's cuts: read from their shape, said with their tools' words ---------------------

import itertools

import pytest

from furniture_design.scene import TOUCH, Part, cut_plan, scene
from furniture_design.sheets import LABELS, cut_sentences

BOARD = Part("p", "p", "Side", "B", (0.0, 0.0, 0.0), (18.0, 300.0, 450.0), "", "")


@pytest.mark.parametrize("y_high,z_high", list(itertools.product((False, True), repeat=2)))
def test_a_corner_notch_is_two_saw_lines_from_its_two_edges_to_its_inner_corner(y_high, z_high):
    """Law over the four corners of a board's face: a notch through the thickness at a
    corner is marked by its two sizes, each from the edge it touches, and sawn as two lines,
    each starting on an edge of the board and both ending at the notch's inner corner."""
    dy, dz = 25.0, 115.0
    y0 = 300 - dy if y_high else 0.0
    z0 = 450 - dz if z_high else 0.0
    plan = cut_plan(BOARD, (0.0, y0, z0), (18.0, y0 + dy, z0 + dz))
    assert (plan.h, plan.v, plan.t, plan.depth) == (1, 2, 0, None)
    assert sorted((e, d) for _, e, d, off in plan.measures) == sorted(
        [("back" if y_high else "front", dy), ("top" if z_high else "bottom", dz)])
    assert all(off == 0 for *_, off in plan.measures)
    inner = (300 - dy if y_high else dy, 450 - dz if z_high else dz)
    assert plan.from_edge == len(plan.lines) == 2
    for (a0, b0), (a1, b1) in plan.lines:
        assert a0 in (0, 300) or b0 in (0, 450)                 # starts on the board's edge
        assert abs(a1 - inner[0]) < TOUCH and abs(b1 - inner[1]) < TOUCH


def test_a_cutout_is_measured_from_the_low_edges_and_sawn_from_a_hole():
    plan = cut_plan(BOARD, (0.0, 100.0, 200.0), (18.0, 150.0, 260.0))
    assert sorted((e, d, off) for _, e, d, off in plan.measures) == [
        ("bottom", 60.0, 200.0), ("front", 50.0, 100.0)]
    assert plan.from_edge == 0 and len(plan.lines) == 4
    words = cut_sentences(Part(**{**BOARD.__dict__, "cuts": [((0.0, 100.0, 200.0),
                                                                (18.0, 150.0, 260.0))]}),
                          LABELS["fr"], "fr")
    assert "200 à 260 depuis le chant du bas" in words[0]
    assert words[1] == LABELS["fr"]["saw_from_hole"]


def test_a_rebate_says_its_depth():
    plan = cut_plan(BOARD, (8.0, 0.0, 0.0), (18.0, 300.0, 20.0))
    assert plan.depth == 10.0 and [e for _, e, _, _ in plan.measures] == ["bottom"]


def test_the_card_says_where_to_mark_the_notch_and_how_its_saw_is_used():
    sc = scene(_tree(), "pieces/bench-side")
    side = sc.part("side")
    said = cut_sentences(side, LABELS["fr"], "fr")
    assert said[0] == "Tracer : 25 depuis le chant arrière, 115 depuis le chant du bas."
    assert said[1] == LABELS["fr"]["saw_from_edge"]
    saw, = side.tools
    assert saw.say["fr"]["name"] == "Scie égoïne" and len(saw.say["fr"]["method"]) == 4
    assert ("TM 9-243, change 2, 8 April 2022",
            "46.4 Using the crosscut saw, f, p. 46-7") in saw.cites


def test_a_step_with_cuts_is_drawn_with_its_card(tmp_path):
    tree = _tree()
    tree.get("pieces/bench-side").payload["steps"] = [
        {"text": "Cut the notch.", "prepare": True, "add": ["side"], "cuts": ["side"]}]
    out = drawings.documents(tree, "pieces/bench-side", tmp_path)
    assert out["assembly"].read_bytes()[:4] == b"%PDF"


def test_a_pieces_checks_are_the_whole_trees_verdicts_under_it():
    """The checks run the rules under the piece only, and answer what running them over the
    whole tree and keeping the piece's verdicts does, in every world the package states (its
    examples and each counter-example's), on every piece in it: a verdict on a piece that
    depended on a run elsewhere, or a sibling whose name starts like the piece's (bench,
    bench-side), would show here as a difference."""
    from quern import run_rules

    from furniture_design.package import COUNTER_EXAMPLES

    worlds = [EXAMPLES] + [c.nodes for c in COUNTER_EXAMPLES]
    seen = 0
    for nodes in worlds:
        tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
        tree.root.children = [n.model_copy(deep=True) for n in nodes]
        whole = run_rules(tree)
        for path, node in tree.walk(""):
            if node.kind != "piece":
                continue
            under = [(r.rule, r.node, r.verdict, r.detail or "") for r in whole
                     if not r.ok and (r.node == path or r.node.startswith(path + "/"))]
            assert sorted(drawings.checks(tree, path)) == sorted(under), path
            seen += 1
    assert seen > len(worlds)
