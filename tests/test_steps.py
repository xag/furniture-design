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


def _placed_tree():
    """The cabinet with three steps that name their tools by path: both at one place, one at another and one
    at none, and a glue said in words (a material, which is not counted)."""
    tree = cabinet_tree()
    first = tree.get("pieces/cabinet").payload["steps"][0]
    tree.get("pieces/cabinet").payload["steps"] = [
        first | {"tools": ["tools/jointer", "tools/jig", "Colle à bois"]},
        {"text": "Saw.", "prepare": True, "add": ["left"], "tools": ["tools/jointer", "tools/crosscut-saw"]},
        {"text": "Glue.", "prepare": True, "add": ["right"], "tools": ["tools/jig", "tools/hacksaw-on-profile"]},
        {"text": "Said in words.", "prepare": True, "add": ["top"], "tools": ["Une scie"]}]
    return tree


def _places(tree, places, tree_out):
    sc = scene(tree, "pieces/cabinet")
    regions = []
    pdf = assembly_instructions(sc, tree_out / "montage.pdf", "fr", regions, places=places)
    path = instruction_screens(sc, pdf, regions, tree_out / "montage", "fr", places=places)
    return sc, json.loads(path.read_text(encoding="utf-8"))


def _heads(data):
    return {s["step"]: s["head"] for s in data["screens"] if s["kind"] == "step"}


def test_a_step_names_its_tools_by_path_and_is_at_the_place_that_holds_every_one(tmp_path):
    sc, data = _places(_placed_tree(), {"tools/jointer": "Home", "tools/jig": "Home",
                                        "tools/crosscut-saw": "Les Copeaux"}, tmp_path)
    heads = _heads(data)
    assert sc.steps[0].tools == ["A jointer", "A jig", "Colle à bois"]     # a path says its node's name
    assert heads[1]["place"] == "Home"                                    # the glue, said in words, is a material
    assert "place" not in heads[2]                                        # its tools are at two places
    assert "place" not in heads[3]                                        # a tool is at no place of the person's
    assert "place" not in heads[4] and heads[4]["keys"] == []             # nothing named by path


def test_what_is_needed_lists_each_places_tools_then_the_others_after_a_place(tmp_path):
    _, data = _places(_placed_tree(), {"tools/jointer": "Home", "tools/jig": "Home"}, tmp_path)
    needed = data["screens"][1]
    assert needed["places"] == [{"place": "Home", "tools": ["A jointer", "A jig"]}]
    assert needed["other"] == ["Colle à bois", "Crosscut saw", "Hacksaw on a profile", "Une scie"]
    assert needed["other_title"] == "Autres outils" and "Colle à bois" in needed["tools"]
    _, data = _places(_placed_tree(), {"tools/jointer": "Home", "tools/jig": "Home", "tools/crosscut-saw": "Home",
                                       "tools/hacksaw-on-profile": "Les Copeaux"}, tmp_path)
    assert [p["place"] for p in data["screens"][1]["places"]] == ["Home", "Les Copeaux"]    # the places in their order


def test_with_no_place_the_screens_are_the_former_ones_and_the_tools_stand_under_tools(tmp_path):
    for places in (None, {}, {"tools/not-a-tool-here": "Home"}):
        _, data = _places(_placed_tree(), places, tmp_path)
        needed = data["screens"][1]
        assert "places" not in needed and "other" not in needed and needed["tools_title"] == "Outils"
        assert all("place" not in h for h in _heads(data).values())
