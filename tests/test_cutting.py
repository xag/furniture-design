"""The cutting sheet: the rectangles the saw cuts, laid on the sheets a shop sells, grain with grain."""

from quern import Quern

from furniture_design import drawings
from furniture_design.cutting import Cut, cuts, cutting_sheet, pack, panels
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
