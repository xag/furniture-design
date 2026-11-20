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


def test_a_part_says_the_assemblies_holding_it_and_stays_where_it_was(tmp_path):
    from quern import Node

    from furniture_design.scene import scene
    flat = {p.id: (p.lo, p.hi, p.within) for p in scene(_tree(), BENCH).parts}
    assert all(within == [] for _, _, within in flat.values())
    tree = _tree()
    bench = tree.get(BENCH)
    sides = [c for c in bench.children if c.id in ("left", "right")]
    bench.children = [c for c in bench.children if c not in sides] + [
        Node(id="frame", kind="assembly", name="Frame", children=[
            Node(id="sides", kind="assembly", name="Sides", children=sides)])]
    for _, node in tree.walk(""):   # what names a side by its path names it where it now is
        for name, targets in (node.links or {}).items():
            node.links[name] = [t.replace(f"{BENCH}/left", f"{BENCH}/frame/sides/left")
                                .replace(f"{BENCH}/right", f"{BENCH}/frame/sides/right") for t in targets]
    grouped = {p.id: (p.lo, p.hi, p.within) for p in scene(tree, BENCH).parts}
    assert grouped["left"][2] == [("frame", "Frame"), ("sides", "Sides")] and grouped["top"][2] == []
    assert {k: v[:2] for k, v in grouped.items()} == {k: v[:2] for k, v in flat.items()}
    page = drawings.documents(tree, BENCH, tmp_path)["viewer"].read_text(encoding="utf-8")
    assert '"within": [["frame", "Frame"], ["sides", "Sides"]]' in page


def test_a_profile_is_one_part_drawn_and_weighed_by_its_section(tmp_path):
    from furniture_design.natives import bodies
    from furniture_design.scene import scene
    tree = _tree()
    top = tree.get(f"{BENCH}/top")
    whole = next(b for b in bodies(tree, BENCH) if b.path == f"{BENCH}/top").mass
    assert next(p for p in scene(tree, BENCH).parts if p.id == "top").profile().t == 2   # a board: across its thickness
    # the top as a channel open upwards: 1000 long, 300 across, 20 high, its walls 5 thick
    top.payload["section"] = [[0, 0], [300, 0], [300, 20], [295, 20], [295, 5], [5, 5], [5, 20], [0, 20]]
    part = next(p for p in scene(tree, BENCH).parts if p.id == "top")
    f = part.profile()
    assert (f.t, f.t1 - f.t0, len(f.outline)) == (0, 1000, 8)   # run along its length, all eight corners
    assert {(round(a - part.lo[1]), round(b - part.lo[2])) for a, b in f.outline} >= {(5, 5), (295, 5)}
    share = (300 * 5 + 2 * 5 * 15) / (300 * 20)
    assert abs(next(b for b in bodies(tree, BENCH) if b.path == f"{BENCH}/top").mass - whole * share) < 1e-9
    drawings.documents(tree, BENCH, tmp_path)   # the 3D view and the PDFs draw it
    top.payload["section"] = [[0, 0], [300, 0], [300, 25]]
    with pytest.raises(ValueError, match="outside its box"):
        scene(tree, BENCH)


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


# A maker's hand saw, as a saws package gives one: it follows the general saw, whose method the frames draw,
# and carries its own model.
MAKERS_SAW = {"parts": [{"op": "prism", "profile": [[0, 0], [500, 0], [500, 30], [0, 100]], "x": [-0.5, 0.5]}],
              "teeth": {"from": [0, 0], "to": [500, 0]}}


def _with_a_makers_saw(tree: Quern, follows: tuple = ("tools/crosscut-saw",)) -> Quern:
    from quern.tree import Node
    tree.get("tools").children.append(Node(id="makers-saw", kind="tool", name="A maker's hand saw",
                                           links={"follows": list(follows)},
                                           payload={"model": MAKERS_SAW, "stroke": "push"}))
    side = tree.get("pieces/bench-side/side")
    side.links["made_with"] = ["tools/makers-saw"]
    return tree


def test_the_sides_saw_is_the_crosscut_saw_its_method_resting_on_tm_9_243_and_its_model_its_makers():
    sc = scene(_tree(), "pieces/bench-side")
    side = sc.part("side")
    plan = cut_plan(side, *side.cuts[0])
    assert [(e, d) for _, e, d, _ in plan.measures] == [("back", 25.0), ("bottom", 115.0)]
    saw, = side.tools
    assert saw.say["fr"]["name"] == "Scie égoïne" and len(saw.say["fr"]["method"]) == 4
    assert ("TM 9-243, change 2, 8 April 2022",
            "46.4 Using the crosscut saw, f, p. 46-7") in saw.cites
    assert saw.model is None  # a general method: the model drawn is a maker's saw's, which follows it


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


def test_a_value_the_material_lacks_leaves_its_check_open_and_the_others_said():
    """A board on sale may print its stiffness and not its strength, or a solid wood a true
    modulus with no shear modulus named by the part: the checks say which value is missing, as an
    open point, and still say every other row, in each language."""
    from furniture_design.report import TEXT, checks

    SHELF = "pieces/bookshelf"

    for lang in ("fr", "en"):
        for drop, payload, expect in (("design_bending_stress", {}, "no_strength"),
                                      ("modulus_of_elasticity", {}, "no_stiffness"),
                                      ("", {"modulus": "true"}, "no_shear")):
            tree = _tree()
            beam = next(p for p, n in tree.walk(SHELF) if n.kind == "part" and (n.links or {}).get("bends_as"))
            material = get_node(tree, get_node(tree, beam).links["uses"][0])
            material.params.pop(drop, None)
            material.payload = {**(material.payload or {}), **payload}
            if expect == "no_shear":  # nor does the part name a shear modulus to read
                get_node(tree, beam).payload.pop("shear_modulus", None)
            whole = checks(_tree(), SHELF, lang)
            rows = checks(tree, SHELF, lang)
            assert any(r["result"] == TEXT[lang][expect] for r in rows), (lang, expect)
            assert len(rows) == len(whole), (lang, expect)


def test_a_sag_limit_is_read_beside_the_sag_with_creep_it_is_compared_with():
    """The limit a part is held to is a longtime one, so the row beside it gives the sag with creep
    (the initial sag over the material's initial_share_of_longtime), the number the rule compares
    with it: a row that set the initial sag beside the limit would read as passing when it fails."""
    from furniture_design.natives import deflection
    from furniture_design.report import checks

    for limit in (4.0, 1.0):
        tree = _tree()
        get_node(tree, "requirements/bookshelf-sag").params["limit"].value = limit
        shelf = "pieces/bookshelf/shelf"
        initial = deflection(tree, shelf)
        share = tree.get(get_node(tree, shelf).links["uses"][0]).params["initial_share_of_longtime"].value
        longtime = initial / share
        for lang, sep in (("fr", ","), ("en", ".")):
            [row] = [r for r in checks(tree, "pieces/bookshelf", lang) if r["requirement"].startswith(("Flèche", "Sag"))]
            assert f"{longtime:.2f}".replace(".", sep) in row["result"], (lang, row)
            assert row["verdict"] == ("ok" if longtime <= limit else "fail"), (lang, limit, row)


def test_the_plans_print_the_notes_they_are_given_under_their_headings(monkeypatch, tmp_path):
    """The design notes are the caller's: each section's heading and its paragraphs are printed,
    and the piece's own description is not when notes are given; given none, it is."""
    tree = _tree()
    get_node(tree, BENCH).payload["description"] = ["Un paragraphe écrit à la main."]
    given = [("Décisions", ["Le plateau fait 36 mm."]),
             ("Ouvert", [("La poussée de côté n'est pas tranchée.", ["Visser la traverse au mur"])])]
    from furniture_design import sheets
    said = []
    real = sheets.Pen.text
    monkeypatch.setattr(sheets.Pen, "text", lambda self, x, y, s, *a, **k: (said.append(str(s)), real(self, x, y, s, *a, **k))[1])
    drawings.documents(tree, BENCH, tmp_path / "a", notes=given)
    text = " ".join(said)
    assert all(w in text for w in ("Décisions", "Le plateau fait 36 mm.", "Ouvert", "La poussée de côté",
                                   "Visser la traverse au mur"))
    assert "écrit à la main" not in text
    said.clear()
    drawings.documents(tree, BENCH, tmp_path / "b")
    assert "Un paragraphe écrit à la main." in " ".join(said)


def test_notes_start_under_the_checks_and_go_on_over_sheets_of_their_own(monkeypatch, tmp_path):
    """The notes are set under the checks, and what does not fit above the title block goes on
    over sheets of their own, every sheet saying it is one of all of them; short notes keep the
    design document to three sheets. No line is lost and none is set twice."""
    from furniture_design import sheets
    said = []
    real = sheets.Pen.text
    monkeypatch.setattr(sheets.Pen, "text", lambda self, x, y, s, *a, **k: (said.append(str(s)), real(self, x, y, s, *a, **k))[1])
    drawings.documents(_tree(), BENCH, tmp_path / "short", notes=[("Décisions", ["Une seule."])])
    assert "3/3" in said and "Une seule." in " ".join(said)
    said.clear()
    long = [("Décisions", [f"Décision numéro {i}." for i in range(120)])]
    drawings.documents(_tree(), BENCH, tmp_path / "long", notes=long)
    n = max(int(x.split("/")[1]) for x in said if x.count("/") == 1 and x.replace("/", "").isdigit())
    assert n >= 4 and all(f"{k}/{n}" in said for k in range(1, n + 1))
    lines = [x for x in said if x.startswith("- Décision numéro")]
    assert lines == [f"- Décision numéro {i}." for i in range(120)]


def test_the_checks_name_the_step_that_slides_a_part_onto_its_connectors():
    """The design document's checks say which step brings a part in against its connectors,
    and say so in the reader's language; a design put together square passes. Tested and not
    proved: the row is wording over misfit_closings, whose answers spec.py proves."""
    from furniture_design.package import COUNTER_EXAMPLES
    from furniture_design.report import checks
    slid = next(c.nodes for c in COUNTER_EXAMPLES
                if c.rule == "a-step-closes-each-joint-the-way-its-connector-engages")
    for nodes, verdict in [(EXAMPLES, "ok"), (slid, "fail")]:
        tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
        tree.root.children.extend(nodes)
        for lang, head in [("fr", "Montage"), ("en", "Assembly")]:
            row, = [r for r in checks(tree, "pieces/bench", lang) if r["requirement"].startswith(head)]
            assert row["verdict"] == verdict
            if verdict == "fail":
                assert "2" in row["result"] and "back-left, back-right, back-top" in row["result"]


def _written(monkeypatch, tree, piece, out_dir) -> list[str]:
    from furniture_design.sheets import Pen
    written, real = [], Pen.text
    monkeypatch.setattr(Pen, "text", lambda self, x, y, s, *a, **k: (written.append(s), real(self, x, y, s, *a, **k)))
    drawings.documents(tree, piece, out_dir)
    return written


def _cut_drawn(monkeypatch, tree, out_dir) -> tuple[list[str], list[list[dict]]]:
    """What the instructions print, and the models they draw, for the bench side with a step cutting it."""
    from furniture_design import lineart
    drawn, real = [], lineart.solids
    monkeypatch.setattr(lineart, "solids", lambda spec: (drawn.append(spec), real(spec))[1])
    return _written(monkeypatch, tree, "pieces/bench-side", out_dir), drawn


def test_a_cut_is_drawn_with_its_marks_distances_and_no_sentence(monkeypatch, tmp_path):
    tree = _tree()
    tree.get("pieces/bench-side").payload["steps"] = [
        {"text": "Cut the notch.", "prepare": True, "add": ["side"], "cuts": ["side"]}]
    written, _ = _cut_drawn(monkeypatch, tree, tmp_path)
    saw = scene(tree, "pieces/bench-side").part("side").tools[0]
    said = [x for lang in saw.say.values() for x in [lang["name"], *lang["method"]]]
    assert not [s for s in written if "Tracer" in s or "Mark out" in s or s in said or
                any(m[:30] in s for m in said if len(m) > 30)]
    assert "25 mm" in written and "115 mm" in written


def test_short_instructions_draw_the_marks_and_leave_the_saw_at_work_out(monkeypatch, tmp_path):
    tree = _tree()
    side = tree.get("pieces/bench-side")
    side.payload["steps"] = [{"text": "Cut the notch.", "prepare": True, "add": ["side"], "cuts": ["side"]}]
    _with_a_makers_saw(tree)
    saw_parts = MAKERS_SAW["parts"]
    full, full_drawn = _cut_drawn(monkeypatch, tree, tmp_path / "full")
    side.payload["instructions"] = "short"
    short, short_drawn = _cut_drawn(monkeypatch, tree, tmp_path / "short")
    assert "25 mm" in short and "115 mm" in short
    assert any(d[:len(saw_parts)] == saw_parts for d in full_drawn)
    assert not any(d[:len(saw_parts)] == saw_parts for d in short_drawn)


def test_a_pieces_instructions_are_full_or_short():
    tree = _tree()
    assert scene(tree, "pieces/bench-side").info["instructions"] == "full"
    tree.get("pieces/bench-side").payload["instructions"] = "brief"
    with pytest.raises(ValueError, match="full, short"):
        scene(tree, "pieces/bench-side")


def test_a_saw_is_drawn_at_work_only_when_it_follows_the_general_saw_whose_method_the_frames_draw(monkeypatch, tmp_path):
    tree = _tree()
    tree.get("pieces/bench-side").payload["steps"] = [
        {"text": "Cut the notch.", "prepare": True, "add": ["side"], "cuts": ["side"]}]
    _with_a_makers_saw(tree, follows=())        # a saw of another kind (a pull saw): its model, no method drawn
    written, drawn = _cut_drawn(monkeypatch, tree, tmp_path / "other")
    assert "25 mm" in written and not any(d[:1] == MAKERS_SAW["parts"] for d in drawn)
    tree = _with_a_makers_saw(_tree())
    tree.get("pieces/bench-side").payload["steps"] = [
        {"text": "Cut the notch.", "prepare": True, "add": ["side"], "cuts": ["side"]}]
    written, drawn = _cut_drawn(monkeypatch, tree, tmp_path / "follows")
    assert any(d[:1] == MAKERS_SAW["parts"] for d in drawn)


def test_the_instructions_draw_at_work_the_tools_they_are_given_and_no_other(monkeypatch, tmp_path):
    """at_work overrides the payload's full or short tool by tool: the saw is drawn at work only when its path
    is given, and the marks are drawn either way."""
    tree = _tree()
    tree.get("pieces/bench-side").payload["steps"] = [
        {"text": "Cut the notch.", "prepare": True, "add": ["side"], "cuts": ["side"]}]
    _with_a_makers_saw(tree)
    saw = next(t for t in scene(tree, "pieces/bench-side").part("side").tools if t.model)
    from furniture_design import lineart
    drawn, real = [], lineart.solids
    monkeypatch.setattr(lineart, "solids", lambda spec: (drawn.append(spec), real(spec))[1])
    for given, at_work in [(set(), False), ({saw.path}, True), ({"tools/another"}, False)]:
        drawn.clear()
        out = drawings.document(tree, "pieces/bench-side", tmp_path / str(len(given)) / str(at_work), "assembly",
                                at_work=given)
        assert out["assembly"].is_file() and out["steps"].is_file() and out["pages"].is_file()
        assert any(d[:len(MAKERS_SAW["parts"])] == MAKERS_SAW["parts"] for d in drawn) is at_work


def test_one_document_is_drawn_as_the_four_are_and_says_how_far_it_has_got(tmp_path):
    tree = _tree()
    every = drawings.documents(tree, BENCH, tmp_path / "all")
    seen: list[float] = []
    for what in drawings.DOCUMENTS:
        one = drawings.document(tree, BENCH, tmp_path / "one", what, progress=seen.append)
        # the plans and the cutting sheet as drawn: "pages" alone, "pages-<what>" among the four
        named = {k: f"pages-{what}" if k == "pages" and what != "assembly" else k for k in one}
        assert {k: v.name for k, v in one.items()} == {k: every[named[k]].name for k in one}
    assert seen and seen == sorted(seen) and seen[0] >= 0 and seen[-1] == 1.0
    with pytest.raises(ValueError, match="viewer, design, assembly, cutting"):
        drawings.document(tree, BENCH, tmp_path, "poster")


def test_a_tools_pages_are_the_blocks_that_show_it_at_work_keyed_by_their_place(tmp_path):
    """tool_pages draws the instructions with the tool at work and keeps the blocks that show it, each keyed by
    its step and its place among the step's blocks, the place it has in the instructions drawn without it."""
    import json
    tree = _tree()
    tree.get("pieces/bench-side").payload["steps"] = [
        {"text": "Cut the notch.", "prepare": True, "add": ["side"], "cuts": ["side"]}]
    _with_a_makers_saw(tree)
    saw = next(t for t in scene(tree, "pieces/bench-side").part("side").tools if t.model)
    short = drawings.document(tree, "pieces/bench-side", tmp_path / "short", "assembly", at_work=set())
    base = [s for s in json.loads(short["steps"].read_text(encoding="utf-8"))["screens"] if s["kind"] == "block"]
    made = drawings.tool_pages(tree, "pieces/bench-side", tmp_path / "tool", saw.path)
    kept = json.loads(made["steps"].read_text(encoding="utf-8"))
    assert made["tool"].is_file() and kept["tool"] == saw.path and kept["screens"]
    for screen in kept["screens"]:
        assert screen["tool"] == saw.path and (made["steps"].parent / screen["images"][0]["file"]).is_file()
        same = [b for b in base if b["step"] == screen["step"]][screen["index"]]
        assert same["tool"] == saw.path
    with pytest.raises(ValueError, match="no block"):
        drawings.tool_pages(tree, "pieces/bench-side", tmp_path / "none", "tools/another")


def test_the_documents_drawn_print_only_what_the_model_says_and_keep_to_the_paper(tmp_path):
    """The instructions, the plans and the cutting sheet each note what they print and of what in the model,
    and what they draw beyond the paper (pages.model): drawn from the bench, the standards find nothing in
    them that the model does not say, and nothing off the paper."""
    import json

    from quern.tree import Node

    from furniture_design import standards_pages as pg
    tree = _tree()
    made = drawings.documents(tree, BENCH, tmp_path)
    for key in ("pages", "pages-design", "pages-cutting"):
        tree.root.children = tree.root.children + [Node.model_validate(json.loads(made[key].read_text(encoding="utf-8")))]
    assert tree.get(f"plans/{BENCH.rsplit('/', 1)[-1]}", depth=0) is not None
    assert pg.EXPLAINERS["furniture/printed_unsupported"](tree, BENCH) == []
    assert pg.EXPLAINERS["furniture/drawn_off_the_paper"](tree, BENCH) == []


def test_a_stored_3d_view_is_drawn_by_todays_interface_from_its_scene_alone(tmp_path):
    """The interface is the app's, whatever viewer made the document: app_page reads the scene (DATA) of a document
    made now, of one made before outlines, sizes, titles and assemblies existed, and of one in English."""
    import json
    import re

    from furniture_design.viewer import app_page
    made = drawings.documents(_tree(), BENCH, tmp_path)["viewer"].read_text(encoding="utf-8")
    data = json.loads(re.search(r"const DATA = (\{.*?\});\n", made).group(1))
    page = app_page(made)
    assert "Montrer les fixations" in page and "Connecteurs" not in page and 'id="foldtop"' in page
    assert json.loads(re.search(r"const DATA = (\{.*?\});\n", page).group(1)) == data   # nothing of the scene changes
    old = {k: v for k, v in data.items() if k not in ("title", "existing")}
    old["parts"] = [{k: v for k, v in p.items() if k not in ("profile", "within")} for p in data["parts"]]
    old["joints"] = [{k: v for k, v in j.items() if k != "size"} for j in data["joints"]]
    stored = made.replace(json.dumps(data, ensure_ascii=False), json.dumps(old, ensure_ascii=False))
    drawn = json.loads(re.search(r"const DATA = (\{.*?\});\n", app_page(stored)).group(1))
    assert drawn["existing"] == [] and drawn["title"] == data["title"]
    assert all(p["within"] == [] and len(p["profile"]["outline"]) == 4 for p in drawn["parts"])
    english = drawings.documents(_tree(), BENCH, tmp_path / "en", lang="en")["viewer"].read_text(encoding="utf-8")
    assert "Show the fixings" in app_page(english) and '<html lang="en">' in app_page(english)
    import pytest
    with pytest.raises(ValueError):
        app_page("<html>not a 3D view</html>")
