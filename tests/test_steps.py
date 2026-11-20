"""The assembly instructions as screens: each drawing cut from the PDF where the instructions drew it,
the words beside it read from the piece."""
import json

from PIL import Image

from furniture_design.scene import scene
from furniture_design.sheets import assembly_instructions
from furniture_design.steps import instruction_screens
from test_drawings import _tree as bench_tree
from test_seats import _tree as cabinet_tree


def _screens(tree, piece, tmp_path):
    sc = scene(tree, piece)
    regions = []
    pdf = assembly_instructions(sc, tmp_path / "montage.pdf", "fr", regions)
    path = instruction_screens(sc, pdf, regions, tmp_path / "montage", "fr")
    return sc, json.loads(path.read_text(encoding="utf-8")), tmp_path / "montage"


def _images(s):
    return [v for k, v in s.items() if k == "image" and v] + list(s.get("images", [])) + \
        [b["image"] for b in s.get("boards", []) if b.get("image")]


def test_every_step_has_a_screen_and_every_drawing_a_file(tmp_path):
    tree = cabinet_tree()
    tree.get("tools/jointer").payload["model"] = {
        "parts": [{"op": "box", "lo": [-60, 0, 0], "hi": [60, 150, 30]}],
        "poses": {"flat": [{"op": "box", "lo": [-60, -70, 20], "hi": [60, 0, 23]}], "standing": []},
        "dials": [{"at": [50, 10, 40], "shows": "max"}, {"at": [-30, 30, 90], "shows": "setting"}]}
    sc, data, out = _screens(tree, "pieces/cabinet", tmp_path)
    kinds = [s["kind"] for s in data["screens"]]
    assert kinds[:2] == ["cover", "needed"] and data["steps"] == len(sc.steps)
    assert [s["step"] for s in data["screens"] if s["kind"] == "step"] == [s.number for s in sc.steps]
    assert {b["mark"] for b in data["screens"][1]["boards"]} == {p.mark for p in sc.parts}
    # each board names the parts it is, so a case about a part is shown on its board
    assert sorted(q for b in data["screens"][1]["boards"] for q in b["parts"]) == sorted(p.path for p in sc.parts)
    blocks = [s for s in data["screens"] if s["kind"] == "block"]
    # the grooving settings with the step's head, then a block of four frames per kind of joint, counted
    assert blocks[0].get("head", {}).get("number") == 1 and len(blocks[0]["images"]) == 2
    assert [len(b["images"]) for b in blocks[1:]] == [4, 4] and all(b.get("count") == 2 for b in blocks[1:])
    for s in data["screens"]:
        for im in _images(s):
            w, h = Image.open(out / im["file"]).size
            assert w > 50 and h > 20, (s["kind"], im)
    frame = Image.open(out / blocks[1]["images"][0]["file"]).size
    assert abs(frame[0] / frame[1] - 88 / 62) < 0.05          # a frame is cut whole, border to border


def test_a_cut_is_its_frames_and_no_words(tmp_path):
    tree = bench_tree()
    tree.get("pieces/bench-side").payload["steps"] = [
        {"text": "Cut the notch.", "prepare": True, "add": ["side"], "cuts": ["side"]}]
    sc, data, out = _screens(tree, "pieces/bench-side", tmp_path)
    card = next(s for s in data["screens"] if s["kind"] == "block")
    assert "card" not in card and len(card["images"]) == 1   # the marks' frame: the general saw has no model
