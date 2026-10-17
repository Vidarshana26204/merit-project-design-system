"""Geometric pattern library, expanded to plain primitives (no SVG <pattern>).

flutter_svg / vector_graphics do not render <pattern> reliably, so each pattern emits
explicit shapes; the caller clips them with <clipPath>.

Engine v3: every pattern is a list of **elements**, each a small shape around its own
anchor point that can be drawn at any scale k ∈ (0, 1]. Continuous patterns (stripes,
hatch, grid, waves, …) are cut into cell-sized pieces, so a pattern can dissolve: the
caller decides k per element (seam morph, corner wash, banner fade) and tiny elements
are dropped. Unscaled, the pieces join up and the pattern reads exactly as before.

    elements(name, box, s) -> (kind, [Element])     kind: "fill" | "stroke"
    draw(kind, elements, ks, ink, width, opacity=…) -> markup
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

Box = tuple[float, float, float, float]   # x0, y0, x1, y1


def f(v: float) -> str:
    """Compact number: integers where the eye can't tell, one decimal otherwise."""
    r = round(v)
    if abs(v - r) < 0.25:
        return str(int(r))
    return f"{v:.1f}"


@dataclass
class Element:
    x: float                                  # anchor (local, pre-rotation frame)
    y: float
    shape: Callable[[float], str]             # k → path data, scaled about the anchor
    weight: float = 1.0                       # intrinsic size factor (halftone ramp)


# ── shape builders (all scale about the anchor) ─────────────────────────────────────────
def _circle(cx: float, cy: float, r: float) -> Callable[[float], str]:
    def d(k: float) -> str:
        rr = r * k
        return f"M{f(cx - rr)} {f(cy)}a{f(rr)} {f(rr)} 0 1 0 {f(2 * rr)} 0a{f(rr)} {f(rr)} 0 1 0 {f(-2 * rr)} 0"
    return d


def _poly(cx: float, cy: float, pts: list[tuple[float, float]], close: bool = True) -> Callable[[float], str]:
    """Points relative to the anchor; drawn as one sub-path."""
    def d(k: float) -> str:
        x, y = cx + pts[0][0] * k, cy + pts[0][1] * k
        out = [f"M{f(x)} {f(y)}"]
        px, py = pts[0]
        for qx, qy in pts[1:]:
            out.append(f"l{f((qx - px) * k)} {f((qy - py) * k)}")
            px, py = qx, qy
        if close:
            out.append("Z")
        return "".join(out)
    return d


def _quad(cx: float, cy: float, a: tuple[float, float], c: tuple[float, float], b: tuple[float, float]) -> Callable[[float], str]:
    """Quadratic curve a → b with control c, relative to the anchor."""
    def d(k: float) -> str:
        return (f"M{f(cx + a[0] * k)} {f(cy + a[1] * k)}"
                f"q{f((c[0] - a[0]) * k)} {f((c[1] - a[1]) * k)} {f((b[0] - a[0]) * k)} {f((b[1] - a[1]) * k)}")
    return d


def _arc(cx: float, cy: float, a: tuple[float, float], b: tuple[float, float], r: float, sweep: int) -> Callable[[float], str]:
    def d(k: float) -> str:
        return (f"M{f(cx + a[0] * k)} {f(cy + a[1] * k)}"
                f"a{f(r * k)} {f(r * k)} 0 0 {sweep} {f((b[0] - a[0]) * k)} {f((b[1] - a[1]) * k)}")
    return d


def _grid(box: Box, s: float, stagger: bool = False, sy: float | None = None):
    x0, y0, x1, y1 = box
    sy = sy or s
    row = 0
    y = y0 - sy
    while y <= y1 + sy:
        off = s / 2 if stagger and row % 2 else 0
        x = x0 - s + off
        while x <= x1 + s:
            yield x, y, row
            x += s
        y += sy
        row += 1


# ── the 16 patterns ─────────────────────────────────────────────────────────────────────
def dots(box: Box, s: float):
    return "fill", [Element(x, y, _circle(x, y, s * 0.24)) for x, y, _ in _grid(box, s, stagger=True)]


def halftone(box: Box, s: float):
    x0, _, x1, _ = box
    span = max(1.0, x1 - x0)
    out = []
    for x, y, _ in _grid(box, s * 0.8, stagger=True):
        t = min(1.0, max(0.0, (x - x0) / span))
        out.append(Element(x, y, _circle(x, y, s * 0.32), weight=0.2 + 0.8 * t))
    return "fill", out


def stripes(box: Box, s: float):
    """Vertical bars, cut into s-long pieces."""
    w = s * 0.42
    return "fill", [Element(x + w / 2, y, _poly(x + w / 2, y, [(-w / 2, -s / 2 - .3), (w / 2, -s / 2 - .3), (w / 2, s / 2 + .3), (-w / 2, s / 2 + .3)]))
                    for x, y, _ in _grid(box, s)]


def checks(box: Box, s: float):
    h = s / 4
    sq = [(-h, -h), (h, -h), (h, h), (-h, h)]
    out = []
    for x, y, _ in _grid(box, s):
        out.append(Element(x + h, y + h, _poly(x + h, y + h, sq)))
        out.append(Element(x + 3 * h, y + 3 * h, _poly(x + 3 * h, y + 3 * h, sq)))
    return "fill", out


def hatch(box: Box, s: float):
    """Cross-hatch: one small X per cell; neighbouring Xs join into diagonals."""
    h = s / 2
    return "stroke", [Element(x, y, lambda k, x=x, y=y: _poly(x, y, [(-h, -h), (h, h)], False)(k) + _poly(x, y, [(-h, h), (h, -h)], False)(k))
                      for x, y, _ in _grid(box, s)]


def waves(box: Box, s: float):
    a = s * 0.28
    out = []
    for x, y, row in _grid(box, s / 2, sy=s * 0.7):
        up = (round((x - box[0]) / (s / 2)) % 2) == 0
        out.append(Element(x, y, _quad(x, y, (-s / 4, 0), (0, -a if up else a), (s / 4, 0))))
    return "stroke", out


def zigzag(box: Box, s: float):
    h = s * 0.3
    out = []
    for x, y, _ in _grid(box, s / 2, sy=s * 0.75):
        up = (round((x - box[0]) / (s / 2)) % 2) == 0
        dy = -h if up else h
        out.append(Element(x, y, _poly(x, y, [(-s / 4, -dy / 2), (s / 4, dy / 2)], False)))
    return "stroke", out


def chevron(box: Box, s: float):
    t = s * 0.22
    v = s / 2.6
    pts = [(-s / 2, -v / 2), (0, v / 2), (s / 2, -v / 2), (s / 2, -v / 2 + t), (0, v / 2 + t), (-s / 2, -v / 2 + t)]
    return "fill", [Element(x + s / 2, y, _poly(x + s / 2, y, pts)) for x, y, _ in _grid(box, s)]


def triangles(box: Box, s: float):
    pts = [(-s * 0.4, s * 0.3), (0, -s * 0.3), (s * 0.4, s * 0.3)]
    return "fill", [Element(x + s * 0.4, y + s * 0.5, _poly(x + s * 0.4, y + s * 0.5, pts)) for x, y, _ in _grid(box, s, stagger=True)]


def grid(box: Box, s: float):
    """A plus at every node with arms of s/2: neighbours join into a grid."""
    h = s / 2
    return "stroke", [Element(x, y, lambda k, x=x, y=y: _poly(x, y, [(-h, 0), (h, 0)], False)(k) + _poly(x, y, [(0, -h), (0, h)], False)(k))
                      for x, y, _ in _grid(box, s)]


def plus(box: Box, s: float):
    a, t = s * 0.22, s * 0.07
    pts = [(-t, -a), (t, -a), (t, -t), (a, -t), (a, t), (t, t), (t, a), (-t, a), (-t, t), (-a, t), (-a, -t), (-t, -t)]
    return "fill", [Element(x, y, _poly(x, y, pts)) for x, y, _ in _grid(box, s, stagger=True)]


def arcs(box: Box, s: float):
    """Concentric rings centred on the box's top-left corner, cut into ~s-long arc pieces."""
    x0, y0, x1, y1 = box
    reach = math.hypot(x1 - x0, y1 - y0) + s
    out = []
    r = s * 0.6
    while r <= reach:
        n = max(1, round((math.pi / 2) * r / s))
        for i in range(n):
            t0, t1 = (math.pi / 2) * i / n, (math.pi / 2) * (i + 1) / n
            tm = (t0 + t1) / 2
            ax, ay = x0 + r * math.cos(tm), y0 + r * math.sin(tm)
            p0 = (r * math.cos(t0) - (ax - x0), r * math.sin(t0) - (ay - y0))
            p1 = (r * math.cos(t1) - (ax - x0), r * math.sin(t1) - (ay - y0))
            out.append(Element(ax, ay, _arc(ax, ay, p0, p1, r, 1)))
        r += s * 0.55
    return "stroke", out


def diamonds(box: Box, s: float):
    a = s * 0.24
    return "fill", [Element(x, y, _poly(x, y, [(0, -a), (a, 0), (0, a), (-a, 0)])) for x, y, _ in _grid(box, s, stagger=True)]


def scales(box: Box, s: float):
    r = s / 2
    return "stroke", [Element(x, y + r / 2, _arc(x, y + r / 2, (-r, -r / 2), (r, -r / 2), r, 0)) for x, y, _ in _grid(box, s, stagger=True)]


def bricks(box: Box, s: float):
    """One brick = its top edge + left edge (an L); the rows tile into a wall."""
    h = s * 0.55
    out = []
    for x, y, row in _grid(box, s, sy=h):
        x += s / 2 if row % 2 else 0
        cx, cy = x + s / 2, y + h / 2
        out.append(Element(cx, cy, _poly(cx, cy, [(-s / 2, h / 2), (-s / 2, -h / 2), (s / 2, -h / 2)], False)))
    return "stroke", out


def dashes(box: Box, s: float):
    return "stroke", [Element(x, y, _poly(x, y, [(-s * 0.2, 0), (s * 0.2, 0)], False)) for x, y, _ in _grid(box, s * 0.7, stagger=True)]


PATTERNS: dict[str, Callable[[Box, float], tuple[str, list[Element]]]] = {
    "dots": dots, "halftone": halftone, "stripes": stripes, "checks": checks,
    "hatch": hatch, "waves": waves, "zigzag": zigzag, "chevron": chevron,
    "triangles": triangles, "grid": grid, "plus": plus, "arcs": arcs,
    "diamonds": diamonds, "scales": scales, "bricks": bricks, "dashes": dashes,
}
# Patterns whose look depends on rotation; the rest only use angle 0/45.
ROTATABLE = {"stripes", "hatch", "waves", "zigzag", "chevron", "halftone", "bricks", "dashes", "scales", "triangles", "arcs"}
ANGLES = (0, 45, 90, 135)
DENSITY = (15.0, 19.0, 24.0)   # spacing in a 256-unit tile
STROKE = 2.4                   # stroke width at k = 1, scale 1
K_MIN = 0.14                   # elements smaller than this are dropped


def smoothstep(e0: float, e1: float, x: float) -> float:
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0))) if e1 != e0 else float(x >= e1)
    return t * t * (3 - 2 * t)


def field(name: str, box: Box, density: int | float, angle: int, scale: float = 1.0):
    """Generate a pattern over `box` (rotated about its centre).

    Returns (kind, elements, to_world) where to_world maps an element anchor to the
    unrotated frame, so callers can compute k from world positions.
    """
    s = (DENSITY[density] if isinstance(density, int) else density) * scale
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if angle:
        half = math.hypot(x1 - x0, y1 - y0) / 2
        gen_box = (cx - half, cy - half, cx + half, cy + half)
    else:
        gen_box = box
    kind, els = PATTERNS[name](gen_box, s)
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))

    def to_world(x: float, y: float) -> tuple[float, float]:
        dx, dy = x - cx, y - cy
        return cx + dx * ca - dy * sa, cy + dx * sa + dy * ca
    return kind, els, to_world, (angle, cx, cy)


BUCKETS = (1.0, 0.72, 0.46, 0.24)   # stroke widths / opacities quantise to these


def _bucket(k: float) -> int:
    return min(range(len(BUCKETS)), key=lambda i: abs(BUCKETS[i] - k))


def draw(kind: str, els: list[Element], ks: list[float], ink: str, rot: tuple[float, float, float],
         scale: float = 1.0, opacity_by_k: bool = False) -> str:
    """Emit elements at their k (dropping k < K_MIN).

    Fill elements scale their geometry; stroke elements scale geometry *and* width, so
    stroke paths are grouped by width bucket. With `opacity_by_k`, every element is also
    grouped into an opacity bucket (used by fades that should thin out, not just shrink).
    """
    groups: dict[int, list[str]] = {}
    for el, k in zip(els, ks):
        k *= el.weight
        if k < K_MIN:
            continue
        b = _bucket(k) if (kind == "stroke" or opacity_by_k) else 0
        groups.setdefault(b, []).append(el.shape(min(1.0, k)))
    out = []
    for b in sorted(groups):
        d = "".join(groups[b])
        op = f' opacity="{BUCKETS[b]:.2f}"' if opacity_by_k and b else ""
        if kind == "fill":
            out.append(f'<path d="{d}" fill="{ink}"{op}/>')
        else:
            w = STROKE * scale * (BUCKETS[b] if not opacity_by_k else 1.0)
            out.append(f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{f(w) if w >= 1 else f"{w:.1f}"}" '
                       f'stroke-linecap="round"{op}/>')
    if not out:
        return ""
    angle, cx, cy = rot
    body = "".join(out)
    return f'<g transform="rotate({angle} {f(cx)} {f(cy)})">{body}</g>' if angle else body


def render(name: str, box: Box, density: int, angle: int, ink: str, scale: float = 1.0) -> str:
    """Whole, undissolved pattern over `box` (swatches)."""
    kind, els, _, rot = field(name, box, density, angle, scale)
    return draw(kind, els, [1.0] * len(els), ink, rot, scale)
