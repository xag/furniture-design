"""Pictures for whoever draws a piece's documents (furniture_design.views): each does one thing, to scale, on a
page of its own, and refuses what the piece does not have."""
from pathlib import Path

import pymupdf
import pytest

from furniture_design import views
from furniture_design.scene import scene
from tests.test_drawings import BENCH, _tree


def test_a_view_draws_the_parts_asked_for_from_the_side_asked_for_to_a_scale_it_says(tmp_path: Path):
    sc = scene(_tree(), BENCH)
    some = [p.id for p in sc.parts][:2]
    told = views.view(sc, tmp_path / "v.pdf", some, "front-right", 60, True)
    assert [p["id"] for p in told["parts"]] == some and told["scale"].startswith("1:") and told["apart"] == 60
    page = pymupdf.open(tmp_path / "v.pdf")[0]
    assert f"front-right  {told['scale']}" in page.get_text()
    assert views.view(sc, tmp_path / "w.pdf", side="top", lettered=False)["parts"] == [
        {"id": p.id, "name": p.name, **({"letter": p.mark} if p.mark else {})} for p in sc.parts]
    with pytest.raises(ValueError, match="no part"):
        views.view(sc, tmp_path / "x.pdf", ["no-such-part"])
    with pytest.raises(ValueError, match="no side"):
        views.view(sc, tmp_path / "x.pdf", side="underneath")


def test_a_connector_is_drawn_at_its_size_or_refused_when_it_states_none(tmp_path: Path):
    tree = _tree()
    sc = scene(tree, BENCH)
    used = next(f[0] for j in sc.joints for f in j.fasteners if f[2])
    told = views.connector(tree, tmp_path / "c.pdf", used, "C")
    assert told["length"] > told["thickness"] > 0 and told["scale"] == "2:1"
    with pytest.raises(ValueError, match="states no length"):
        views.connector(tree, tmp_path / "d.pdf", "materials/no-such-thing")
