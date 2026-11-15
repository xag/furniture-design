"""Line art of solid models: the edges a viewer sees, as vector polylines, and the faces to fill
under them in an order that is right where it shows.

A model is a list of meshes (triangles, each mesh one solid). The edges drawn are those that
outline a solid or bend it: its boundary edges, its silhouette (one face toward the viewer, the
other away) and its creases (faces meeting at more than `crease` degrees). Whether a point of an
edge is seen is read from a depth buffer of every triangle: an edge is cut where it goes behind
something. Lines are drawn at two weights, outlines thicker than creases, which is how assembly
drawings separate an object from its details.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


# --- meshes ------------------------------------------------------------------------------------

@dataclass
class Mesh:
    v: np.ndarray                 # (n, 3) vertices
    f: np.ndarray                 # (m, 3) triangles, counter-clockwise seen from outside
    fill: tuple = (1, 1, 1)       # rgb of its faces
    name: str = ""
    weight: float = 1.0           # its lines' weight, as a share of the drawing's

    def moved(self, rot: np.ndarray | None = None, by=(0, 0, 0)) -> "Mesh":
        v = self.v if rot is None else self.v @ np.asarray(rot).T
        return Mesh(v + np.asarray(by, float), self.f, self.fill, self.name, self.weight)


def merge(meshes: list[Mesh], fill=None, name="", weight=None) -> Mesh:
    """Several meshes as one solid's surface: their creases between them are drawn as edges."""
    vs, fs, n = [], [], 0
    for m in meshes:
        vs.append(m.v)
        fs.append(m.f + n)
        n += len(m.v)
    first = meshes[0]
    return Mesh(np.vstack(vs), np.vstack(fs), fill or first.fill, name or first.name,
                first.weight if weight is None else weight)


def box(lo, hi, **kw) -> Mesh:
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], float)
    f = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4],
                  [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    return Mesh(v, f, **kw)


def extrude(profile, depth: float, **kw) -> Mesh:
    """A prism: the closed 2D profile [(u, w)] counter-clockwise, in the x-z plane, extruded along
    +y from 0 to `depth`. Concave profiles are fanned from their centre, which holds for the
    star-shaped profiles drawn here."""
    p = np.asarray(profile, float)
    n = len(p)
    front = np.c_[p[:, 0], np.zeros(n), p[:, 1]]
    back = np.c_[p[:, 0], np.full(n, depth), p[:, 1]]
    c = p.mean(axis=0)
    v = np.vstack([front, back, [[c[0], 0, c[1]], [c[0], depth, c[1]]]])
    cf, cb = 2 * n, 2 * n + 1
    f = []
    for i in range(n):
        j = (i + 1) % n
        f += [[cf, j, i], [cb, n + i, n + j], [i, j, n + j], [i, n + j, n + i]]
    return Mesh(v, np.array(f)[:, ::-1].copy(), **kw)   # outward, for a profile counter-clockwise seen from -y


def rounded(w: float, h: float, r: float, seg: int = 6):
    """The profile of a w x h rectangle centred on 0 with corners of radius r, counter-clockwise."""
    r = min(r, w / 2, h / 2)
    pts = []
    for cx, cy, a0 in ((w / 2 - r, -h / 2 + r, -90), (w / 2 - r, h / 2 - r, 0),
                       (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def cylinder(r: float, h: float, n: int = 40, **kw) -> Mesh:
    """A cylinder on the z axis from 0 to h."""
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    ring = np.c_[r * np.cos(a), r * np.sin(a)]
    v = np.vstack([np.c_[ring, np.zeros(n)], np.c_[ring, np.full(n, h)], [[0, 0, 0], [0, 0, h]]])
    f = []
    for i in range(n):
        j = (i + 1) % n
        f += [[2 * n, j, i], [2 * n + 1, n + i, n + j], [i, j, n + j], [i, n + j, n + i]]
    return Mesh(v, np.array(f), **kw)


def rot(axis: str, deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return {"x": np.array([[1, 0, 0], [0, c, -s], [0, s, c]]),
            "y": np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
            "z": np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[axis]


# --- the view ----------------------------------------------------------------------------------

@dataclass
class View:
    right: np.ndarray
    up: np.ndarray
    d: np.ndarray       # the way the viewer looks

    @staticmethod
    def axo(azimuth: float = -35.0, elevation: float = 28.0) -> "View":
        az, el = math.radians(azimuth), math.radians(elevation)
        eye = np.array([math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)])
        d = -eye / np.linalg.norm(eye)
        right = np.cross(d, [0, 0, 1])
        right /= np.linalg.norm(right)
        up = np.cross(right, d)
        return View(right, up, d)

    def project(self, p: np.ndarray) -> np.ndarray:
        return np.c_[p @ self.right, p @ self.up, p @ self.d]


# --- hidden lines ------------------------------------------------------------------------------

@dataclass
class Drawing:
    fills: list = field(default_factory=list)    # (polygon [(x, y)], rgb), back to front
    lines: list = field(default_factory=list)    # (polyline [(x, y)], weight)
    bounds: tuple = (0, 0, 1, 1)
    image: object = None           # (H, W, 3) uint8, top row first
    pixel: tuple = (0, 0, 1)       # x0, y0 of the image's corner and pixels per unit


def _edges(m: Mesh, view: View, crease: float):
    """Edges to consider: (i, j, kind) with kind 'out' (boundary or silhouette) or 'crease'."""
    v, f = m.v, m.f
    n = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    ln = np.linalg.norm(n, axis=1)
    ok = ln > 1e-12
    n[ok] /= ln[ok, None]
    facing = n @ view.d < 0
    adj: dict[tuple, list[int]] = {}
    for t, tri in enumerate(f):
        if not ok[t]:
            continue
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            adj.setdefault((min(a, b), max(a, b)), []).append(t)
    cos_c = math.cos(math.radians(crease))
    out = []
    for (a, b), ts in adj.items():
        if len(ts) == 1:
            if facing[ts[0]]:
                out.append((a, b, "out"))
            continue
        t1, t2 = ts[0], ts[1]
        if facing[t1] != facing[t2]:
            out.append((a, b, "out"))
        elif facing[t1] and n[t1] @ n[t2] < cos_c:
            out.append((a, b, "crease"))
    return out, n, facing


def draw(meshes: list[Mesh], view: View, *, px: int = 1600, crease: float = 28.0) -> Drawing:
    """The visible edges of the meshes seen from `view`, in drawing units (the model's mm projected),
    and their faces back to front."""
    P = [view.project(m.v) for m in meshes]
    allp = np.vstack(P)
    x0, y0 = allp[:, 0].min(), allp[:, 1].min()
    x1, y1 = allp[:, 0].max(), allp[:, 1].max()
    span = max(x1 - x0, y1 - y0) or 1
    s = (px - 4) / span
    W, H = int((x1 - x0) * s) + 4, int((y1 - y0) * s) + 4
    # the depth in single precision and the solid seen as a small integer: at 1800 px a drawing's
    # buffers then take some 20 MB where double precision and a float image took near 200 MB, more
    # than a 512 MB server had to spare beside the app
    zb = np.full((H, W), np.inf, dtype=np.float32)
    ib = np.full((H, W), -1, dtype=np.int16 if len(meshes) < 32767 else np.int32)
    for mi, (m, p) in enumerate(zip(meshes, P)):
        sx = (p[:, 0] - x0) * s + 2
        sy = (p[:, 1] - y0) * s + 2
        nrm = np.cross(m.v[m.f[:, 1]] - m.v[m.f[:, 0]], m.v[m.f[:, 2]] - m.v[m.f[:, 0]])
        for tri in m.f[nrm @ view.d < 1e-9]:
            xa, ya, za = sx[tri], sy[tri], p[tri, 2]
            u0, u1 = max(int(xa.min()), 0), min(int(xa.max()) + 1, W - 1)
            v0, v1 = max(int(ya.min()), 0), min(int(ya.max()) + 1, H - 1)
            if u1 < u0 or v1 < v0:
                continue
            den = (ya[1] - ya[2]) * (xa[0] - xa[2]) + (xa[2] - xa[1]) * (ya[0] - ya[2])
            if abs(den) < 1e-12:
                continue
            # in bands of rows: a face that fills the drawing would otherwise make a handful of
            # full-size arrays at once
            for w0 in range(v0, v1 + 1, 128):
                w1 = min(w0 + 127, v1)
                gx, gy = np.meshgrid(np.arange(u0, u1 + 1) + 0.5, np.arange(w0, w1 + 1) + 0.5)
                l0 = ((ya[1] - ya[2]) * (gx - xa[2]) + (xa[2] - xa[1]) * (gy - ya[2])) / den
                l1 = ((ya[2] - ya[0]) * (gx - xa[2]) + (xa[0] - xa[2]) * (gy - ya[2])) / den
                l2 = 1 - l0 - l1
                inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
                if not inside.any():
                    continue
                z = np.where(inside, l0 * za[0] + l1 * za[1] + l2 * za[2], np.inf).astype(np.float32)
                sub = zb[w0:w1 + 1, u0:u1 + 1]
                nearer = z < sub
                sub[nearer] = z[nearer]
                ib[w0:w1 + 1, u0:u1 + 1][nearer] = mi
    depth_span = allp[:, 2].max() - allp[:, 2].min() or 1
    eps = depth_span * 0.004 + 1.5 / s
    dr = Drawing(bounds=(x0, y0, x1, y1))
    # the fills: each pixel the colour of the solid seen there, as an image under the lines
    img = np.full((H, W, 3), 255, dtype=np.uint8)
    for mi, m in enumerate(meshes):
        img[ib == mi] = (np.asarray(m.fill, float) * 255).astype(np.uint8)   # truncated, as before
    dr.image = np.ascontiguousarray(img[::-1])
    del img
    dr.pixel = (x0 - 2 / s, y0 - 2 / s, s)
    # lines
    for m, p in zip(meshes, P):
        edges, _n, _f = _edges(m, view, crease)
        for a, b, kind in edges:
            pa, pb = p[a], p[b]
            length = math.hypot(*(pb[:2] - pa[:2])) * s
            k = max(int(length / 1.5), 2)
            t = np.linspace(0, 1, k + 1)
            q = pa[None, :] * (1 - t[:, None]) + pb[None, :] * t[:, None]
            ix = np.clip(((q[:, 0] - x0) * s + 2).astype(int), 0, W - 1)
            iy = np.clip(((q[:, 1] - y0) * s + 2).astype(int), 0, H - 1)
            near = np.maximum.reduce([zb[np.clip(iy + dy, 0, H - 1), np.clip(ix + dx, 0, W - 1)]
                                      for dx in (-1, 0, 1) for dy in (-1, 0, 1)])
            seen = q[:, 2] <= near + eps
            w = (1.0 if kind == "out" else 0.55) * m.weight
            run = []
            for i, vis in enumerate(seen):
                if vis:
                    run.append((q[i, 0], q[i, 1]))
                elif run:
                    if len(run) > 1:
                        dr.lines.append((run, w))
                    run = []
            if len(run) > 1:
                dr.lines.append((run, w))
    return dr


def render(pen, dr: Drawing, box, *, line=0.35, pad=2.0, scale=None, fit=None):
    """Draws a drawing into box (x, y, w, h) of a sheets.Pen, fitted to its bounds or to `fit`
    (x0, y0, x1, y1 in drawing units; what lies outside runs off the box), returning the map from
    drawing units to paper and the scale."""
    from reportlab.lib.colors import Color
    x, y, w, h = box
    x0, y0, x1, y1 = fit or dr.bounds
    k = scale or min((w - 2 * pad) / ((x1 - x0) or 1), (h - 2 * pad) / ((y1 - y0) or 1))
    ox = x + (w - (x1 - x0) * k) / 2
    oy = y + (h - (y1 - y0) * k) / 2

    def P(px_, py_):
        return ox + (px_ - x0) * k, oy + (py_ - y0) * k

    if dr.image is not None:
        from PIL import Image
        from reportlab.lib.utils import ImageReader
        from reportlab.lib.units import mm as MM
        ix0, iy0, ps = dr.pixel
        Hh, Ww = dr.image.shape[:2]
        a = P(ix0, iy0)
        pen.c.drawImage(ImageReader(Image.fromarray(dr.image)), a[0] * MM, a[1] * MM,
                        Ww / ps * k * MM, Hh / ps * k * MM)
    c = pen.c
    from reportlab.lib.units import mm
    c.setLineCap(1)
    c.setLineJoin(1)
    for pts, wgt in dr.lines:
        path = c.beginPath()
        a = P(*pts[0])
        path.moveTo(a[0] * mm, a[1] * mm)
        for q in pts[1:]:
            b = P(*q)
            path.lineTo(b[0] * mm, b[1] * mm)
        c.setStrokeColorRGB(0.1, 0.1, 0.1)
        c.setLineWidth(line * wgt * mm)
        c.drawPath(path, stroke=1, fill=0)
    return P, k


def sweep(path, section, closed=False, **kw) -> Mesh:
    """A tube: the 2D `section` [(a, b)] carried along the 3D `path`, its a axis kept along the
    path's plane normal `kw.pop('normal')` and b across. Ends capped unless closed."""
    normal = np.asarray(kw.pop("normal", (1, 0, 0)), float)
    P = np.asarray(path, float)
    m = len(P)
    sec = np.asarray(section, float)
    k = len(sec)
    rings = []
    for i in range(m):
        t = (P[(i + 1) % m] - P[i - 1]) if closed else (P[min(i + 1, m - 1)] - P[max(i - 1, 0)])
        t /= np.linalg.norm(t)
        b = np.cross(t, normal)
        b /= np.linalg.norm(b)
        rings.append(P[i] + sec[:, :1] * normal + sec[:, 1:] * b)
    v = np.vstack(rings + [[P[0]], [P[-1]]])
    f = []
    for i in range(m if closed else m - 1):
        for j in range(k):
            a0, a1 = i * k + j, i * k + (j + 1) % k
            b0, b1 = (i + 1) % m * k + j, (i + 1) % m * k + (j + 1) % k
            f += [[a0, a1, b1], [a0, b1, b0]]
    c0, c1 = m * k, m * k + 1
    for j in range(0 if closed else k):
        f += [[c0, (j + 1) % k, j], [c1, (m - 1) * k + j, (m - 1) * k + (j + 1) % k]]
    mesh = Mesh(v, np.array(f), **kw)
    vol = np.einsum("ij,ij->i", v[mesh.f[:, 0]], np.cross(v[mesh.f[:, 1]], v[mesh.f[:, 2]])).sum()
    if vol < 0:
        mesh.f = mesh.f[:, ::-1].copy()
    return mesh


# --- shapes ----------------------------------------------------------------------------------

def prism_yz(profile_yz, x0, x1, **kw):
    """Prism of a Y-Z profile, built directly: caps at X = x0 and x1."""
    p = np.asarray(profile_yz, float)
    n = len(p)
    a = np.c_[np.full(n, x0), p[:, 0], p[:, 1]]
    b = np.c_[np.full(n, x1), p[:, 0], p[:, 1]]
    c = p.mean(axis=0)
    v = np.vstack([a, b, [[x0, c[0], c[1]], [x1, c[0], c[1]]]])
    ca, cb = 2 * n, 2 * n + 1
    f = []
    for i in range(n):
        j = (i + 1) % n
        f += [[ca, j, i], [cb, n + i, n + j], [i, j, n + j], [i, n + j, n + i]]
    m = Mesh(v, np.array(f), **kw)
    return _outward(m)


def _outward(m: Mesh) -> Mesh:
    """Turns a closed mesh's triangles outward: its signed volume positive."""
    v, f = m.v, m.f
    vol = np.einsum("ij,ij->i", v[f[:, 0]], np.cross(v[f[:, 1]], v[f[:, 2]])).sum()
    if vol < 0:
        m.f = f[:, ::-1].copy()
    return m


def rbox(lo, hi, r, axis="y", seg=5, **kw):
    """A box with its edges along `axis` rounded by r."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    if axis == "y":
        prof = rounded(x1 - x0, z1 - z0, r, seg)
        m = extrude(prof, y1 - y0, **kw).moved(by=((x0 + x1) / 2, y0, (z0 + z1) / 2))
    elif axis == "x":
        prof = rounded(y1 - y0, z1 - z0, r, seg)
        pts = [(x0, (y0 + y1) / 2 + u, (z0 + z1) / 2 + w) for u, w in prof]
        m = prism_yz([(q[1], q[2]) for q in pts], x0, x1, **kw)
    else:
        prof = rounded(x1 - x0, y1 - y0, r, seg)
        m = extrude(prof, z1 - z0, **kw).moved(rot("x", 90), by=((x0 + x1) / 2, (y0 + y1) / 2, z0))
        m = _outward(m)
    return _outward(m)


def cyl(r, h, axis, at, n=40, **kw):
    """A cylinder of radius r, length h along `axis` ('x', 'y' or 'z') from the point `at`."""
    m = cylinder(r, h, n, **kw)
    if axis == "x":
        m = m.moved(rot("y", 90))
    elif axis == "y":
        m = m.moved(rot("x", -90))
    return _outward(m.moved(by=at))


# --- solids from data ------------------------------------------------------------------------------

DARK = (0.55, 0.55, 0.57)


def solids(spec: list[dict]) -> list[Mesh]:
    """Meshes from a model stated as data, each item one solid: {"op": "box", "lo", "hi"}, {"op": "rbox",
    "lo", "hi", "r", "axis"}, {"op": "cyl", "r", "h", "axis", "at", "n"}, {"op": "prism", "profile":
    [[y, z], ...] (counter-clockwise seen from -X), "x": [x0, x1]} or {"op": "tube", "path": [[x, y, z],
    ...], "w", "h", "r", "normal", "closed"} (a closed tube joins its last point to its first: a loop); "dark": true fills it dark (a grip, a switch, a slot), else white."""
    out = []
    for s in spec:
        kw = {"fill": DARK if s.get("dark") else (1, 1, 1)}
        op = s["op"]
        if op == "box":
            out.append(box(s["lo"], s["hi"], **kw))
        elif op == "rbox":
            out.append(rbox(s["lo"], s["hi"], s["r"], axis=s.get("axis", "y"), **kw))
        elif op == "cyl":
            out.append(cyl(s["r"], s["h"], s["axis"], s["at"], n=s.get("n", 32), **kw))
        elif op == "prism":
            out.append(prism_yz(s["profile"], s["x"][0], s["x"][1], **kw))
        elif op == "tube":
            out.append(sweep(s["path"], rounded(s["w"], s["h"], s.get("r", 0), 8), closed=s.get("closed", False),
                             normal=s.get("normal", (1, 0, 0)), **kw))
        else:
            raise ValueError(f"a model's solid has no op {op!r}")
    return out


def placed(meshes: list[Mesh], R, at) -> list[Mesh]:
    """Meshes of a model in its own frame, turned by the matrix R (its axes as columns) and moved to at."""
    return [m.moved(np.asarray(R, float), np.asarray(at, float)) for m in meshes]
