"""A step that cuts boards, drawn as the instructions draw it: what it prints, where, and what it leaves out.

The piece is made up to show what a reader found on a wall lining: two boards rebated in two passes each
along an edge (one with a notch at its top), each cut in a step of its own before any is put up, with a
panel saw that follows no hand-saw method (so the marks are drawn alone), and a last step bringing two long
parts whose middles nearly meet."""
import math

from quern import Quern
from quern.tree import Node
from reportlab.pdfbase.pdfmetrics import stringWidth

from furniture_design import sheets
from furniture_design.package import EXAMPLES, PACKAGE
from furniture_design.scene import scene
from furniture_design.sheets import assembly_instructions

PIECE = "pieces/lining"
PANEL = {"parts": [{"op": "box", "lo": [-450, -400, 0], "hi": [450, 400, 860]},
                   {"op": "cyl", "at": [0, -2, 796], "axis": "y", "h": 4, "r": 157.5}]}
STEPS = [{"cuts": ["left"]}, {"cuts": ["top"]},
         {"add": ["left"], "direction": {"left": "front"}},
         {"add": ["top"], "direction": {"top": "front"}},
         {"add": ["plate", "batten"], "direction": {"plate": "front", "batten": "front"}}]


def _tree() -> Quern:
    t = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    t.root.children = [n.model_copy(deep=True) for n in EXAMPLES]
    t.get("tools").children.append(Node(id="panel-saw", kind="tool", name="A panel saw",
                                        payload={"model": PANEL, "saw_kind": "panel saw"}))

    def part(id_, size, at, cuts=()):
        return Node(id=id_, kind="part", links={"uses": ["materials/birch-yellow"], "made_with": ["tools/panel-saw"]},
                    payload={"shape": {"op": "box", "size": size}, "transform": {"translate": at},
                             **({"cuts": [{"at": a, "size": s} for a, s in cuts]} if cuts else {})})
    wall = Node(id="wall", kind="part", payload={"shape": {"op": "box", "size": [1200, 100, 1700]},
                                                 "transform": {"translate": [0, 22, 0]}, "existing": "the wall"})
    # rebated from the back in two passes, 25 wide and 7.5 deep at the edge, then 19.5 wide and 19 deep beside
    # it; the first pass's inner side and the second's outer side are one line; a notch at the top
    left = part("left", [400, 22, 1500], [0, 0, 0],
                [([375, 14.5, 0], [25, 7.5, 1500]), ([355.5, 3, 0], [19.5, 19, 1500]),
                 ([375, 3, 1365.5], [25, 11.5, 134.5])])
    top = part("top", [1200, 22, 160], [0, 0, 1500],
               [([0, 14.5, 0], [1200, 7.5, 25]), ([0, 3, 25], [1200, 19, 31.5])])
    plate = part("plate", [1200, 2, 38], [0, -2, 0])
    batten = part("batten", [1080, 13, 25], [0, 0, 7])
    t.get("pieces").children.append(Node(id="lining", kind="piece", payload={"steps": STEPS},
                                         children=[wall, left, top, plate, batten]))
    return t


class Drawn:
    """What the instructions set on each page: texts with their boxes and circles, each with how many regions
    were noted before it (so a block's are those drawn between its note and the next block's or step's), the
    regions noted, and the parts each step's picture brings in."""

    def __init__(self, monkeypatch, tmp_path, tree=None):
        self.texts, self.circles, self.regions, self.pictures = [], [], [], []
        real_text, real_circle, real_picture = sheets.Pen.text, sheets.Pen.circle, sheets._assembly_picture

        def text(pen, x, y, s, size=3.0, color=sheets.INK, anchor="start", bold=False, angle=0, **k):
            if not angle and str(s).strip():
                long = stringWidth(str(s), "Helvetica-Bold" if bold else "Helvetica", size * 2.8346) / 2.8346
                x0 = x + {"start": 0, "middle": -long / 2, "end": -long}[anchor]
                self.texts.append({"page": pen.c.getPageNumber() - 1, "s": str(s), "n": len(self.regions),
                                   "box": (x0, y - 0.2 * size, x0 + long, y + 0.72 * size)})
            return real_text(pen, x, y, s, size, color, anchor, bold, angle, **k)

        def circle(pen, x, y, r, *a, **k):
            self.circles.append({"page": pen.c.getPageNumber() - 1, "at": (x, y), "r": r, "n": len(self.regions)})
            return real_circle(pen, x, y, r, *a, **k)

        def picture(pen, sc, placed_ids, new_ids, *a, **k):
            self.pictures.append(list(new_ids))
            return real_picture(pen, sc, placed_ids, new_ids, *a, **k)
        monkeypatch.setattr(sheets.Pen, "text", text)
        monkeypatch.setattr(sheets.Pen, "circle", circle)
        monkeypatch.setattr(sheets, "_assembly_picture", picture)
        self.sc = scene(tree or _tree(), PIECE)
        assembly_instructions(self.sc, tmp_path / "montage.pdf", "fr", self.regions)

    def block(self, part):
        """The cut block of a part: its page, its frames ([x0, y0, x1, y1] from the page's bottom left), and the
        texts and circles drawn in it before its last frame is noted (a frame is noted once drawn)."""
        i = next(k for k, r in enumerate(self.regions) if r["kind"] == "block" and r.get("part") == part)
        j = next((k for k in range(i + 1, len(self.regions)) if self.regions[k]["kind"] in ("block", "step")),
                 len(self.regions))
        frames = []
        for k in range(i + 1, j):
            if self.regions[k]["kind"] == "frame":
                x0, t0, x1, t1 = self.regions[k]["box"]
                frames.append((x0, 297 - t1, x1, 297 - t0))
                j = k + 1
        return (self.regions[i]["page"], frames, [t for t in self.texts if i < t["n"] < j],
                [c for c in self.circles if i < c["n"] < j])


def _overlap(a, b, gap=0.0):
    return a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap


def test_a_step_that_only_cuts_draws_no_picture_of_the_piece(monkeypatch, tmp_path):
    """A step that cuts a board and brings in nothing draws no picture of what is there: it would show the
    piece as the step before left it, half a page that says nothing of the cut. Its number heads the half
    page its cut is drawn in, and its screen has no picture of its own."""
    d = Drawn(monkeypatch, tmp_path)
    assert d.pictures == [["left"], ["top"], ["plate", "batten"]]
    for n, part in ((1, "left"), (2, "top")):
        step = next(r for r in d.regions if r["kind"] == "step" and r["step"] == n)
        assert step.get("picture") is False
        assert d.block(part)[0] == step["page"]


def test_a_cuts_measures_are_all_printed_inside_its_frame_and_none_over_another(monkeypatch, tmp_path):
    """Every distance of a cut is printed, inside the frame it belongs to, and none is set over another text
    of the frame or over a line's number."""
    d = Drawn(monkeypatch, tmp_path)
    for part, said in (("left", {"25 mm", "19.5 mm", "134.5 mm"}), ("top", {"25 mm", "31.5 mm"})):
        _, frames, texts, circles = d.block(part)
        x0, y0, x1, y1 = frames[0]
        assert said <= {t["s"] for t in texts}, part
        for t in texts:
            assert x0 <= t["box"][0] and t["box"][2] <= x1 and y0 <= t["box"][1] and t["box"][3] <= y1, (part, t)
        for a in (t for t in texts if t["s"].endswith(" mm")):
            for b in texts:
                assert b is a or not _overlap(a["box"], b["box"]), (part, a["s"], b["s"])
            for c in circles:
                (cx, cy), r = c["at"], c["r"]
                assert not _overlap(a["box"], (cx - r, cy - r, cx + r, cy + r)), (part, a["s"])


def test_each_pass_says_how_deep_it_goes(monkeypatch, tmp_path):
    """A cut that does not go through the board is a pass of a given depth, the setting that makes a rebate:
    each one's depth is printed in its frame, 7.5 then 19 mm for the rebate."""
    d = Drawn(monkeypatch, tmp_path)
    for part, depths in (("left", ["7.5 mm", "19 mm"]), ("top", ["7.5 mm", "19 mm"])):
        said = [t["s"] for t in d.block(part)[2]]
        assert all(x in said for x in depths), (part, said)


def test_the_lines_are_numbered_from_one_each_number_seen(monkeypatch, tmp_path):
    """The saw lines are numbered I, II, III... with no number missing: a line two cuts share is one line, as is
    a notch's side that runs on a longer cut's, and no number is set over another."""
    d = Drawn(monkeypatch, tmp_path)
    from furniture_design.sawing import ROMAN
    for part, lines in (("left", 3), ("top", 2)):
        _, _, texts, circles = d.block(part)
        said = [t for t in texts if t["s"] in ROMAN]
        assert sorted(t["s"] for t in said) == sorted(ROMAN[:lines]), part
        circles = [c for c in circles if c["r"] == 2.6]
        for i, a in enumerate(circles):
            for b in circles[i + 1:]:
                assert math.dist(a["at"], b["at"]) >= a["r"] + b["r"], part


def test_no_two_letters_of_a_step_are_set_over_each_other(monkeypatch, tmp_path):
    """Two parts brought in together, their middles close on paper, carry their letters side by side."""
    d = Drawn(monkeypatch, tmp_path)
    step = next(r for r in d.regions if r["kind"] == "step" and r["step"] == 5)
    letters = [c for c in d.circles if c["page"] == step["page"] and c["r"] == 3.2]
    assert len(letters) >= 2
    for i, a in enumerate(letters):
        for b in letters[i + 1:]:
            assert math.dist(a["at"], b["at"]) >= a["r"] + b["r"] + 0.5
