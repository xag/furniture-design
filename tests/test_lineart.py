"""The line drawing of solids: an edge is drawn only where it is seen, and a curved surface by its outline,
not its facets."""

import numpy as np
import pytest

from furniture_design import lineart as la

VIEW = la.View.axo(-35, 28)


def _length(dr):
    return sum(np.hypot(*np.diff(np.asarray(pts), axis=0).T).sum() for pts, _w in dr.lines)


def test_a_solid_hidden_behind_another_adds_no_line():
    front = la.box((0, 0, 0), (400, 40, 700))   # tall enough to hide it from above as well
    behind = la.box((260, 120, 100), (330, 160, 200))      # behind the front box, from the front left
    alone, both = la.draw([front], VIEW), la.draw([front, behind], VIEW)
    assert _length(both) == pytest.approx(_length(alone), rel=0.01)
    beside = la.box((600, 0, 0), (700, 60, 100))           # the same box in the open is drawn
    assert _length(la.draw([front, beside], VIEW)) > _length(alone) * 1.2


def test_a_cylinder_is_drawn_by_its_outline_and_not_its_facets():
    side = la.View(np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), np.array([0, 1.0, 0]))   # seen from the front
    dr = la.draw([la.cylinder(30, 100, n=48)], side)
    upright = [pts for pts, _w in dr.lines
               if abs(pts[-1][0] - pts[0][0]) < 0.5 and abs(pts[-1][1] - pts[0][1]) > 50]
    assert len(upright) == 2       # its two silhouettes: no line between them where two facets meet


def test_a_model_is_data_and_an_unknown_solid_is_refused():
    meshes = la.solids([{"op": "box", "lo": [0, 0, 0], "hi": [1, 1, 1]},
                        {"op": "cyl", "r": 1, "h": 2, "axis": "y", "at": [0, 0, 0]},
                        {"op": "prism", "profile": [[0, 0], [2, 0], [2, 2]], "x": [0, 1]},
                        {"op": "rbox", "lo": [0, 0, 0], "hi": [3, 3, 3], "r": 1, "axis": "x"},
                        {"op": "tube", "path": [[0, 0, 0], [0, 10, 0], [0, 20, 5]], "w": 2, "h": 3, "r": 0.5}])
    assert len(meshes) == 5
    for m in meshes:   # every solid closed and turned outward: its volume positive
        v, f = m.v, m.f
        assert np.einsum("ij,ij->i", v[f[:, 0]], np.cross(v[f[:, 1]], v[f[:, 2]])).sum() > 0
    with pytest.raises(ValueError):
        la.solids([{"op": "sphere"}])
