"""Patch layouts.

Hierarchy patchworks use a **radial** layout (D16 rev 2): N rays from the centre to the
frame, so every patch is a wedge that touches the centre where the icon sits. Rays are
positions on the frame perimeter (fractions in [0, 1), clockwise from the top-left
corner), so the same composition renders in any aspect ratio: the square tile and the
4:1 row share their rays, and in the row the wedges stretch sideways around the centred
icon. Pure Python, deterministic.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

Point = tuple[float, float]


@dataclass
class Patch:
    d: str                      # SVG path data, absolute coords
    area: float
    bbox: tuple[float, float, float, float]
    poly: list[Point] = field(default_factory=list)  # empty for overlays (arcs)
    overlay: bool = False


@dataclass
class Layout:
    w: float
    h: float
    cuts: list[tuple[int, int]]          # perimeter slot pairs
    overlays: list[tuple[str, int, int]]  # (kind, anchor, radius level)
    patches: list[Patch]


def _fmt(v: float) -> str:
    return str(int(round(v))) if abs(v - round(v)) < 0.25 else f"{v:.1f}"


def poly_d(poly: list[Point]) -> str:
    return "M" + "L".join(f"{_fmt(x)} {_fmt(y)}" for x, y in poly) + "Z"


def area(poly: list[Point]) -> float:
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]))) / 2


def bbox(poly: list[Point]) -> tuple[float, float, float, float]:
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def split(poly: list[Point], a: Point, b: Point) -> list[list[Point]]:
    """Split a convex polygon by the infinite line a→b. Returns 1 or 2 polygons."""
    def side(p: Point) -> float:
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])

    left: list[Point] = []
    right: list[Point] = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        sp, sq = side(p), side(q)
        (left if sp >= 0 else right).append(p)
        if (sp > 0 > sq) or (sp < 0 < sq):
            t = sp / (sp - sq)
            x = (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))
            left.append(x)
            right.append(x)
    out = [pl for pl in (left, right) if len(pl) >= 3 and area(pl) > 1e-6]
    return out


def perimeter_slots(w: float, h: float, per_unit: float) -> list[tuple[Point, int]]:
    """Discrete points along the frame edges (excluding corners). Returns (point, edge)."""
    slots: list[tuple[Point, int]] = []
    nx, ny = max(2, round(w / per_unit)), max(2, round(h / per_unit))
    for i in range(1, nx):
        slots.append(((w * i / nx, 0.0), 0))
    for i in range(1, ny):
        slots.append(((w, h * i / ny), 1))
    for i in range(1, nx):
        slots.append(((w * (nx - i) / nx, h), 2))
    for i in range(1, ny):
        slots.append(((0.0, h * (ny - i) / ny), 3))
    return slots


def _overlay_patch(kind: str, anchor: int, rlevel: int, w: float, h: float) -> Patch:
    s = min(w, h)
    r = s * (0.30, 0.38, 0.46)[rlevel]
    if kind == "quarter":  # quarter disc centred on a frame corner
        cx, cy = [(0, 0), (w, 0), (w, h), (0, h)][anchor]
        sx = 1 if cx == 0 else -1
        sy = 1 if cy == 0 else -1
        p1 = (cx + sx * r, cy)
        p2 = (cx, cy + sy * r)
        sweep = 1 if sx * sy > 0 else 0
        d = (f"M{_fmt(cx)} {_fmt(cy)}L{_fmt(p1[0])} {_fmt(p1[1])}"
             f"A{_fmt(r)} {_fmt(r)} 0 0 {sweep} {_fmt(p2[0])} {_fmt(p2[1])}Z")
        bb = (min(cx, p1[0]), min(cy, p2[1]), max(cx, p1[0]), max(cy, p2[1]))
        return Patch(d, math.pi * r * r / 4, bb, overlay=True)
    # "half": half disc centred on an edge midpoint-ish position (anchor = edge*2 + which third)
    edge, third = divmod(anchor, 2)
    t = (0.3, 0.7)[third]
    r *= 0.8
    if edge == 0:
        cx, cy, a1, a2, sweep = w * t, 0, (w * t - r, 0), (w * t + r, 0), 0
    elif edge == 1:
        cx, cy, a1, a2, sweep = w, h * t, (w, h * t - r), (w, h * t + r), 0
    elif edge == 2:
        cx, cy, a1, a2, sweep = w * t, h, (w * t + r, h), (w * t - r, h), 0
    else:
        cx, cy, a1, a2, sweep = 0, h * t, (0, h * t + r), (0, h * t - r), 0
    d = (f"M{_fmt(a1[0])} {_fmt(a1[1])}A{_fmt(r)} {_fmt(r)} 0 0 {sweep} {_fmt(a2[0])} {_fmt(a2[1])}Z")
    bb = (max(0, cx - r), max(0, cy - r), min(w, cx + r), min(h, cy + r))
    return Patch(d, math.pi * r * r / 2, bb, overlay=True)


def make_layout(rng: random.Random, w: float, h: float, n_cuts: int, n_overlays: int,
                min_frac: float, row: bool = False) -> Layout:
    """Pick cuts slot-by-slot, rejecting choices that leave slivers."""
    slots = perimeter_slots(w, h, per_unit=min(w, h) / 8)
    total = w * h
    for _attempt in range(200):
        polys: list[list[Point]] = [[(0, 0), (w, 0), (w, h), (0, h)]]
        cuts: list[tuple[int, int]] = []
        ok = True
        for _ in range(n_cuts):
            for _try in range(40):
                i, j = rng.randrange(len(slots)), rng.randrange(len(slots))
                (a, ea), (b, eb) = slots[i], slots[j]
                if ea == eb:
                    continue
                if row and {ea, eb} != {0, 2} and rng.random() < 0.7:
                    continue  # rows read as a band: prefer top↔bottom cuts
                new: list[list[Point]] = []
                for pl in polys:
                    new.extend(split(pl, a, b))
                if min(area(p) for p in new) >= total * min_frac and len(new) > len(polys):
                    polys, cuts = new, cuts + [(i, j)]
                    break
            else:
                ok = False
                break
        if ok:
            break
    patches = [Patch(poly_d(p), area(p), bbox(p), p) for p in polys]
    overlays: list[tuple[str, int, int]] = []
    for _ in range(n_overlays):
        kind = rng.choice(("quarter", "half"))
        anchor = rng.randrange(4 if kind == "quarter" else 8)
        rlevel = rng.randrange(3)
        if any(o[0] == kind and o[1] == anchor for o in overlays):
            continue
        overlays.append((kind, anchor, rlevel))
        patches.append(_overlay_patch(kind, anchor, rlevel, w, h))
    return Layout(w, h, cuts, overlays, patches)


def adjacent(p: Patch, q: Patch, eps: float = 0.5) -> bool:
    """Two cut polygons touch if they share ≥2 vertices; overlays touch whatever their bbox hits."""
    if p.overlay or q.overlay:
        a, b = p.bbox, q.bbox
        return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])
    shared = sum(1 for u in p.poly if any(abs(u[0] - v[0]) < eps and abs(u[1] - v[1]) < eps for v in q.poly))
    return shared >= 2


RAY_SLOTS = 96   # perimeter positions a ray may take


def perimeter_point(t: float, w: float, h: float) -> tuple[Point, float]:
    """Point at perimeter fraction t (clockwise from top-left) and its arc position."""
    total = 2 * (w + h)
    d = (t % 1.0) * total
    if d <= w:
        return (d, 0.0), d
    if d <= w + h:
        return (w, d - w), d
    if d <= 2 * w + h:
        return (w - (d - w - h), h), d
    return (0.0, h - (d - 2 * w - h)), d


def radial_layout(rays: list[int], w: float, h: float) -> Layout:
    """Wedges between consecutive rays (slot indices, sorted), all meeting at the centre."""
    c = (w / 2, h / 2)
    total = 2 * (w + h)
    corners = [(w, 0.0, w), (w, h, w + h), (0.0, h, 2 * w + h), (0.0, 0.0, total)]  # (x, y, arc)
    patches: list[Patch] = []
    n = len(rays)
    for i in range(n):
        t0, t1 = rays[i] / RAY_SLOTS, rays[(i + 1) % n] / RAY_SLOTS
        if t1 <= t0:
            t1 += 1.0
        (p0, a0) = perimeter_point(t0, w, h)
        (p1, a1) = perimeter_point(t1, w, h)
        a1 = a0 + (t1 - t0) * total
        poly: list[Point] = [c, p0]
        for lap in (0.0, total):
            for x, y, arc in corners:
                if a0 < arc + lap < a1:
                    poly.append((x, y))
        poly.append(p1)
        patches.append(Patch(poly_d(poly), area(poly), bbox(poly), poly))
    return Layout(w, h, [(r, 0) for r in rays], [], patches)
