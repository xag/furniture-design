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
