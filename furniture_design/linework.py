"""Line drawings of boxes: flat projections (front, side, top) and a three-quarter view,
as polygons in drawing units, with hidden faces settled so a renderer only has to fill and
stroke them in order. Used by the design document and the assembly instructions.

Boxes are axis-aligned and do not overlap, so they can be ordered back to front pairwise:
two boxes apart along an axis are drawn far one first, the viewing direction saying which
is far. That order is exact for the boxes furniture is made of, where sorting faces by
their centres is not.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

Vec = tuple[float, float, float]


@dataclass
class Face:
    key: str                     # the box it belongs to
    points: list[tuple[float, float]]
    shade: float                 # 0 (lit) .. 1 (dark): which way the face looks


@dataclass
class View:
    """A projection: `to2d` maps a point of the piece frame to the drawing plane (x right,
    y up); `direction` is the way the viewer looks, for ordering."""
    name: str
    right: Vec
    up: Vec
    direction: Vec

    def to2d(self, p: Vec) -> tuple[float, float]:
        return (sum(a * b for a, b in zip(p, self.right)), sum(a * b for a, b in zip(p, self.up)))


def _norm(v: Vec) -> Vec:
    n = math.sqrt(sum(a * a for a in v))
    return tuple(a / n for a in v)


def _cross(a: Vec, b: Vec) -> Vec:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def axonometric(azimuth_deg: float = -35.0, elevation_deg: float = 28.0) -> View:
    """A three-quarter view: looking from the front left and above when the azimuth is
    negative (the viewer stands at x < 0, y < 0)."""
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    # the viewer's position direction, from the piece
    eye = (math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))
    d = _norm(tuple(-a for a in eye))
    right = _norm(_cross(d, (0, 0, 1)))
    up = _cross(right, d)
    return View("axo", right, up, d)


FRONT = View("front", (1, 0, 0), (0, 0, 1), (0, 1, 0))       # seen from the front
LEFT = View("left", (0, -1, 0), (0, 0, 1), (1, 0, 0))        # seen from the left
TOP = View("top", (1, 0, 0), (0, 1, 0), (0, 0, -1))          # seen from above, front at the bottom


_FACES = [  # (axis, side, corner pattern)
    (0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]


def _corners(lo: Vec, hi: Vec, axis: int, side: int) -> list[Vec]:
    a, b = [i for i in range(3) if i != axis]
    fixed = (lo, hi)[side][axis]
    out = []
    for u, v in ((0, 0), (1, 0), (1, 1), (0, 1)):
        p = [0.0, 0.0, 0.0]
        p[axis] = fixed
        p[a] = (lo, hi)[u][a]
        p[b] = (lo, hi)[v][b]
        out.append(tuple(p))
    return out


def order(boxes: dict[str, tuple[Vec, Vec]], view: View) -> list[str]:
    """Box keys back to front for `view`."""
    keys = list(boxes)
    before: dict[str, set[str]] = {k: set() for k in keys}   # drawn before k
    d = view.direction
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            (alo, ahi), (blo, bhi) = boxes[a], boxes[b]
            best, axis, a_low = 0.0, None, None
            for k in range(3):
                if abs(d[k]) < 1e-9:
                    continue
                if ahi[k] <= blo[k] + 0.5:
                    gap = blo[k] - ahi[k] + abs(d[k]) * 1e-3
                    if axis is None or gap > best:
                        best, axis, a_low = gap, k, True
                elif bhi[k] <= alo[k] + 0.5:
                    gap = alo[k] - bhi[k] + abs(d[k]) * 1e-3
                    if axis is None or gap > best:
                        best, axis, a_low = gap, k, False
            if axis is None:
                continue
            # looking towards +k, the box at lower k is nearer: draw the other first
            low, high = (a, b) if a_low else (b, a)
            if d[axis] > 0:
                before[low].add(high)
            else:
                before[high].add(low)
    depth = {k: sum(((lo + hi) / 2) * dk for lo, hi, dk in zip(*boxes[k], d)) for k in keys}
    done, out = set(), []
    while len(out) < len(keys):
        ready = [k for k in keys if k not in done and before[k] <= done]
        if not ready:  # a cycle: fall back on the farthest remaining
            ready = [max((k for k in keys if k not in done), key=lambda k: depth[k])]
        k = max(ready, key=lambda k: depth[k])
        done.add(k)
        out.append(k)
    return out


def faces(boxes: dict[str, tuple[Vec, Vec]], view: View) -> list[Face]:
    """The faces each box shows to the viewer, back to front, with a shade by the way they
    face: tops lightest, then the face turned most towards the viewer."""
    out = []
    for key in order(boxes, view):
        lo, hi = boxes[key]
        for axis, side in _FACES:
            normal = [0.0, 0.0, 0.0]
            normal[axis] = 1.0 if side else -1.0
            facing = -sum(n * dk for n, dk in zip(normal, view.direction))
            if facing <= 1e-6:
                continue
            if axis == 2 and side == 1:
                shade = 0.0
            elif axis == 2:
                shade = 0.7
            else:
                shade = 0.25 + 0.45 * (1 - facing)
            out.append(Face(key, [view.to2d(p) for p in _corners(lo, hi, axis, side)], shade))
    return out


def bounds(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)
