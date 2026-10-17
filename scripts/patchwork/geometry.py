"""Patch layouts.

Engine v4 (D16 rev 4): **square in a square**, the classic "economy" quilt block. The tile
is cut on fixed, symmetric lines (mirror on both axes and both diagonals) and every level
of the hierarchy nests one shape further in:

    subject   hourglass X (top+bottom, left+right) + corner triangles (two diagonal pairs)
    topic     + a diamond whose points touch the edge midpoints
    subtopic  + a square laid over the diamond (its corners poke out: an 8-point star)
    quest     + a wider square under the subtopic's, showing as a band round it

Patches are painted in order, so a patch's visible region is its polygons minus every
patch painted after it. Uniqueness comes from the styles, never from the cuts. Pure
Python, deterministic.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

Point = tuple[float, float]

CORNER = 0.24        # corner triangle leg, × tile
SQUARE = 0.38       # subtopic square half-side, × tile (corners stay inside the X)
QUEST_SQUARE = 0.42  # quest square half-side, × tile


@dataclass
class Patch:
    role: int                    # style index this patch is painted with
    polys: list[list[Point]]     # one or two mirrored pieces
    bbox: tuple[float, float, float, float]
    area: float

    @property
    def d(self) -> str:
        return "".join(poly_d(p) for p in self.polys)


@dataclass
class Layout:
    w: float
    h: float
    patches: list[Patch]         # paint order


def _fmt(v: float) -> str:
    return str(int(round(v))) if abs(v - round(v)) < 0.25 else f"{v:.1f}"


def poly_d(poly: list[Point]) -> str:
    return "M" + "L".join(f"{_fmt(x)} {_fmt(y)}" for x, y in poly) + "Z"


def area(poly: list[Point]) -> float:
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]))) / 2


def bbox(polys: list[list[Point]]) -> tuple[float, float, float, float]:
    xs, ys = [p[0] for pl in polys for p in pl], [p[1] for pl in polys for p in pl]
    return min(xs), min(ys), max(xs), max(ys)


def inside(p: Point, poly: list[Point]) -> bool:
    """Even-odd point-in-polygon."""
    x, y = p
    hit = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def seg_dist(p: Point, a: Point, b: Point) -> float:
    vx, vy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / (vx * vx + vy * vy or 1)))
    return math.hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy)


def edges(poly: list[Point], w: float, h: float) -> list[tuple[Point, Point]]:
    """Polygon edges that are seams, i.e. not lying on the tile border."""
    def on_border(a: Point, b: Point) -> bool:
        return any(abs(a[i] - v) < 1e-6 and abs(b[i] - v) < 1e-6 for i, v in ((0, 0), (0, w), (1, 0), (1, h)))
    return [(a, b) for a, b in zip(poly, poly[1:] + poly[:1]) if not on_border(a, b)]


def square_in_square(n: int, s: float) -> Layout:
    """n = 4 (subject) … 7 (quest) patches over an s × s tile, in paint order."""
    c, k = s / 2, s * CORNER

    def patch(role: int, *polys: list[Point]) -> Patch:
        return Patch(role, list(polys), bbox(list(polys)), sum(area(p) for p in polys))

    def square(r: float) -> list[Point]:
        return [(c - r, c - r), (c + r, c - r), (c + r, c + r), (c - r, c + r)]

    out = [
        patch(0, [(0, 0), (s, 0), (c, c)], [(s, s), (0, s), (c, c)]),           # X: top + bottom
        patch(1, [(s, 0), (s, s), (c, c)], [(0, s), (0, 0), (c, c)]),           # X: right + left
        patch(2, [(0, 0), (k, 0), (0, k)], [(s, s), (s - k, s), (s, s - k)]),   # corners ↖ ↘
        patch(3, [(s, 0), (s, k), (s - k, 0)], [(0, s), (0, s - k), (k, s)]),   # corners ↗ ↙
    ]
    if n >= 5:
        out.append(patch(4, [(c, 0), (s, c), (c, s), (0, c)]))                  # diamond
    if n >= 7:
        out.append(patch(6, square(s * QUEST_SQUARE)))                          # quest band
    if n >= 6:
        out.append(patch(5, square(s * SQUARE)))                                # subtopic square
    return Layout(s, s, out)


# Which roles share a seam (tints must differ). The subject's four all touch each other.
NEIGHBOURS = {4: {0, 1}, 5: {0, 1, 4}, 6: {0, 1, 2, 3, 4}}


# ── plates: one shape per level ───────────────────────────────────────────────────────
PLATE_BY_LEVEL = {"subject": "hexagon", "topic": "pentagon", "subtopic": "square", "quest": "square"}
PLATE_SIZE = {"hexagon": 0.375, "pentagon": 0.365, "square": 0.32}   # circumradius / half-side, × tile
PLATE_ROUND = {"hexagon": 0.045, "pentagon": 0.045, "square": 0.08}  # corner radius, × tile


def plate_points(kind: str, cx: float, cy: float, s: float) -> list[Point]:
    r = s * PLATE_SIZE[kind]
    if kind == "square":
        return [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)]
    sides, start = (6, 0.0) if kind == "hexagon" else (5, -90.0)    # flat-top hexagon, point-up pentagon
    return [(cx + r * math.cos(math.radians(start + 360 * i / sides)),
             cy + r * math.sin(math.radians(start + 360 * i / sides))) for i in range(sides)]


def plate_inradius(kind: str, s: float) -> float:
    r = s * PLATE_SIZE[kind]
    return r if kind == "square" else r * math.cos(math.pi / (6 if kind == "hexagon" else 5))


def rounded_d(pts: list[Point], r: float) -> str:
    """Closed polygon with each corner rounded by a quadratic curve of radius ≈ r."""
    n = len(pts)
    out = []
    for i in range(n):
        p, a, b = pts[i], pts[i - 1], pts[(i + 1) % n]
        la, lb = math.dist(p, a), math.dist(p, b)
        t = min(r, la / 2, lb / 2)
        p0 = (p[0] + (a[0] - p[0]) * t / la, p[1] + (a[1] - p[1]) * t / la)
        p1 = (p[0] + (b[0] - p[0]) * t / lb, p[1] + (b[1] - p[1]) * t / lb)
        out.append(f"{'M' if i == 0 else 'L'}{_fmt(p0[0])} {_fmt(p0[1])}Q{_fmt(p[0])} {_fmt(p[1])} {_fmt(p1[0])} {_fmt(p1[1])}")
    return "".join(out) + "Z"
