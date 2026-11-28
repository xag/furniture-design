"""The cutting sheet: the rectangles the saw cuts, laid on the sheets a shop sells, grain with grain."""

from quern import Quern

from furniture_design import drawings
from furniture_design.cutting import Cut, cuts, cutting_sheet, layout, pack, panels
from furniture_design.package import EXAMPLES, PACKAGE
from furniture_design.scene import scene

BENCH = "pieces/bench"


def _tree() -> Quern:
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = [n.model_copy(deep=True) for n in EXAMPLES]
    return tree


def _cut(length, width, mark="A"):
    return Cut(mark, mark, length, width, 18, "materials/m", "Board", False)


def _overlap(a, b):
    (qa, xa, ya), (qb, xb, yb) = a, b
    return xa < xb + qb.length and xb < xa + qa.length and ya < yb + qb.width and yb < ya + qa.width


def test_a_part_is_cut_as_its_rectangle_its_length_along_the_grain():
    got = sorted((c.length, c.width, c.thickness) for c in cuts(scene(_tree(), BENCH)))
    assert got == [(450, 300, 20), (450, 300, 20), (960, 350, 20), (1000, 300, 20)]


def test_a_glued_up_part_is_that_many_rectangles_and_a_part_bent_across_the_grain_turns():
    tree = _tree()
    tree.get(f"{BENCH}/top").payload["sheets"] = 2
    tree.get(f"{BENCH}/back").payload["span_along"] = "across face grain, flat"
    got = sorted((c.length, c.width, c.thickness) for c in cuts(scene(tree, BENCH)))
    assert got == [(350, 960, 20), (450, 300, 20), (450, 300, 20), (1000, 300, 10), (1000, 300, 10)]


def test_the_parts_sit_inside_the_sheet_apart_by_the_blade_and_never_overlap():
    parts = [_cut(780, 295), _cut(780, 295), _cut(732, 250, "C"), _cut(732, 75, "D")]
    placed = pack(parts, 2500, 1220, 4)
    assert placed and len(placed) == 4
    for q, x, y in placed:
        assert x + q.length <= 2500 and y + q.width <= 1220
    for a in placed:
        for b in placed:
            assert a is b or not _overlap(a, b)
    assert pack(parts, 1000, 500, 4) is None


def test_each_panel_is_the_smallest_sheet_its_parts_fit_and_what_no_sheet_takes_is_said():
    sheets = [{"length": 1200, "width": 500, "ref": "s"}, {"length": 1480, "width": 500, "ref": "m"},
              {"length": 1480, "width": 600, "ref": "l"}]
    parts = [_cut(780, 295), _cut(780, 295), _cut(732, 250, "C"), _cut(732, 75, "D")]
    done, left = panels(parts, sheets, 4)
    assert [s["ref"] for s, _ in done] == ["l", "s"] and not left
    assert sorted(q.mark for _, placed in done for q, _, _ in placed) == ["A", "A", "C", "D"]
    done, left = panels([_cut(2000, 300)], sheets, 4)
    assert not done and [q.length for q in left] == [2000]


def test_the_cutting_sheet_is_one_of_the_documents(tmp_path):
    out = drawings.documents(_tree(), BENCH, tmp_path)
    assert out["cutting"].name.endswith("-decoupe.pdf") and out["cutting"].read_bytes()[:4] == b"%PDF"
    sc = scene(_tree(), BENCH)
    stock = {sc.parts[0].material: [{"length": 2500, "width": 1220, "ref": "123"}]}
    en = cutting_sheet(sc, tmp_path / "en.pdf", "en", stock)
    assert en.read_bytes()[:4] == b"%PDF"


def test_the_parts_are_laid_on_the_sheets_sold_of_the_material_their_uses_names():
    sc = scene(_tree(), BENCH)
    path = next(n for n in _tree().get(f"{BENCH}/top").links["uses"])
    stock = {path: [{"length": 2500, "width": 1220, "ref": "123"}]}
    (group, done, left), = layout(sc, stock)
    assert [s["ref"] for s, _ in done] == ["123"] and not left
    assert sorted(q.mark for _, placed in done for q, _, _ in placed) == sorted(q.mark for q in group)


def test_a_material_says_its_own_label_when_its_name_leads_with_something_else():
    tree = _tree()
    m = tree.get(next(n for n in tree.get(f"{BENCH}/top").links["uses"]))
    m.payload = {**(m.payload or {}), "label": "contreplaqué bouleau Boutique"}
    assert {p.material_name for p in scene(tree, BENCH).parts} == {"contreplaqué bouleau Boutique"}


def test_a_glued_up_parts_row_says_its_sheets_make_the_one_part(tmp_path):
    tree = _tree()
    tree.get(f"{BENCH}/top").payload["sheets"] = 2
    sc = scene(tree, BENCH)
    tops = [c for c in cuts(sc) if c.length == 1000]
    assert [(c.thickness, c.glued) for c in tops] == [(10, 2), (10, 2)]
    from furniture_design.cutting import LABELS, part_name
    assert part_name(tops[0], LABELS["fr"]) == "top (2 × 10 collées en 20)"
    assert part_name(tops[0], LABELS["en"]) == "top (2 × 10 glued into 20)"
    assert all(part_name(c, LABELS["fr"]) == c.name for c in cuts(sc) if c.length != 1000)


def test_the_parts_are_laid_apart_by_what_their_saw_takes_out_and_the_sheet_says_whose():
    from furniture_design.cutting import group_kerf
    tree = _tree()
    for part in ("left", "right", "top", "back"):
        tree.get(f"{BENCH}/{part}").links["sawn_with"] = ["tools/example-saw"]
    got = cuts(scene(tree, BENCH))
    assert {(c.kerf, c.saw) for c in got} == {(2.2, "Example plunge saw")}
    assert group_kerf(got, 4.0) == (2.2, "Example plunge saw", [])
    plain = cuts(scene(_tree(), BENCH))
    k, saw, unknown = group_kerf(plain, 4.0)
    assert (k, saw) == (4.0, "") and unknown == plain
    # two strips of 298.5 fit across 600 with a 2.2 mm cut between them, not with 4
    strips = [_cut(1000, 298.5), _cut(1000, 298.5)]
    assert pack(strips, 1000, 600, 2.2) and pack(strips, 1000, 600, 4.0) is None


def test_a_part_with_a_saw_that_states_no_cut_counts_the_default():
    tree = _tree()
    tree.get(f"{BENCH}/top").links["sawn_with"] = ["tools/example-saw", "tools/drill"]
    top = [c for c in cuts(scene(tree, BENCH)) if c.length == 1000]
    assert top and all(c.kerf is None for c in top)


def test_a_part_bought_cut_to_its_size_is_not_on_the_sheet():
    """Twin-wall panels the maker cuts to order: no board is bought for them and no saw cuts them out."""
    tree = _tree()
    tree.get(f"{BENCH}/top").payload["bought_to_size"] = "the panel's maker, cut to order"
    got = sorted((c.length, c.width, c.thickness) for c in cuts(scene(tree, BENCH)))
    assert got == [(450, 300, 20), (450, 300, 20), (960, 350, 20)]


def _spans(pdf):
    import pymupdf
    with pymupdf.open(pdf) as doc:
        return [(s["text"], pymupdf.Rect(s["bbox"])) for page in doc for b in page.get_text("dict")["blocks"]
                for ln in b.get("lines", []) for s in ln["spans"]]


def test_a_panels_title_and_its_reference_never_overlap(tmp_path):
    """A reference as a shop prints it, a whole product name, is long: it goes under the title when the two
    do not fit side by side, and every span of the sheet stands clear of every other."""
    tree = _tree()
    m = tree.get(next(n for n in tree.get(f"{BENCH}/top").links["uses"]))
    m.payload = {**(m.payload or {}), "label": "contreplaqué bouleau qualité ébénisterie"}
    sc = scene(tree, BENCH)
    ref = "Panneau contreplaqué bouleau ép. 20 mm L. 250 x l. 122 cm 81234567"
    stock = {sc.parts[0].material: [{"length": 2500, "width": 1220, "ref": ref}]}
    for lang in ("fr", "en"):
        spans = _spans(cutting_sheet(sc, tmp_path / f"{lang}.pdf", lang, stock))
        title = next(r for t, r in spans if t.startswith(("Panneau 1", "Board 1")))
        refs = [r for t, r in spans if ref in t]
        assert refs and not any(r.intersects(title) for r in refs)
        assert all(r.x1 <= 210 / 25.4 * 72 for r in refs)


def _shim(stock):
    """The bench with a shim 18 x 20 x 35 under its top, cut from the bench's 20 mm board when `stock` is
    20: its thickness is then 20, not its smallest side."""
    from quern.tree import Node
    tree = _tree()
    top = tree.get(f"{BENCH}/top")
    bench = tree.get(BENCH)
    bench.children.append(Node(id="shim", kind="part", links={"uses": list(top.links["uses"])},
                               payload={"shape": {"op": "box", "size": [18, 20, 35]},
                                        "transform": {"translate": [400, 0, 415]},
                                        **({"stock_thickness": stock} if stock is not None else {})}))
    return tree


def test_a_part_cut_from_thicker_stock_is_laid_on_that_stock():
    """A shim 18 x 20 x 35 cut from the 20 mm board the rest is cut from goes on that board, its face 35 by
    18; read by its smallest side it would be 18 thick and want an 18 mm panel of its own."""
    sc = scene(_shim(20), BENCH)
    shim = next(c for c in cuts(sc) if c.name == "shim")
    assert (shim.length, shim.width, shim.thickness) == (35, 18, 20)
    stock = {sc.parts[0].material: [{"length": 2500, "width": 1220, "ref": "123"}]}
    assert [round(group[0].thickness, 1) for group, _, _ in layout(sc, stock)] == [20]
    plain = next(c for c in cuts(scene(_shim(None), BENCH)) if c.name == "shim")
    assert (plain.length, plain.width, plain.thickness) == (35, 20, 18)


def test_a_part_whose_stock_is_none_of_its_sides_is_refused_by_the_rule():
    """The rule refuses a stock no side is within 0.05 mm of, the number written in its expression; the
    documents lay the part on its stock all the same, through its nearest side, and print the rule's red."""
    from quern import run_rules

    def red(stock):
        return [r.rule for r in run_rules(_shim(stock)) if not r.ok and r.node == f"{BENCH}/shim"]
    assert red(22) == red(20.1) == ["a-parts-stock-is-as-thick-as-one-of-its-sides"]
    assert red(20) == red(20.04) == []
    shim = next(c for c in cuts(scene(_shim(22), BENCH)) if c.name == "shim")
    assert (shim.length, shim.width, shim.thickness) == (35, 18, 22)


def _notched_side(steps):
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = [n.model_copy(deep=True) for n in EXAMPLES]
    if steps is not None:
        tree.get("pieces/bench-side").payload = {"steps": steps}
    return scene(tree, "pieces/bench-side")


def test_a_part_with_cuts_is_cut_only_in_the_step_that_lists_it():
    """A notched side is cut in the step that lists it in its cuts, and the sheet sends the reader to the
    instructions; brought in by a step that lists no cuts, no step cuts it and the sheet says nothing of a cut
    to make later (the standards' rule a-pieces-steps-make-every-cut asks for the step); with no step, the same."""
    sc = _notched_side([{"prepare": True, "cuts": ["side"], "add": ["side"]}, {"add": ["side"]}])
    assert [s.cuts for s in sc.steps] == [["side"], []]
    assert [c.cut_later for c in cuts(sc)] == [True]
    sc = _notched_side([{"add": ["side"], "text": "Stand the side against the wall."}])
    assert sc.steps[0].cuts == []
    assert [c.cut_later for c in cuts(sc)] == [False]
    sc = _notched_side(None)
    assert sc.steps == [] and [c.cut_later for c in cuts(sc)] == [False]
