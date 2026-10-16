"""Geometric pattern library, expanded to plain primitives (no SVG <pattern>).

flutter_svg / vector_graphics do not render <pattern> reliably, so each pattern emits
explicit shapes over a box; the caller clips them to the patch with <clipPath>.

Every generator returns (kind, data):
  kind "fill"   → data is path d, painted with the pattern ink fill
  kind "stroke" → data is path d, painted with the pattern ink stroke
"""
from __future__ import annotations

import math
from typing import Callable

Box = tuple[float, float, float, float]   # x0, y0, x1, y1


def f(v: float) -> str:
    """Compact number: integers where the eye can't tell, one decimal otherwise."""
    r = round(v)
    if abs(v - r) < 0.25:
        return str(int(r))
    return f"{v:.1f}"


def _grid(box: Box, s: float, stagger: bool = False):
    x0, y0, x1, y1 = box
    row = 0
    y = y0 - s
    while y <= y1 + s:
        off = s / 2 if stagger and row % 2 else 0
        x = x0 - s + off
        while x <= x1 + s:
            yield x, y, row
            x += s
        y += s
        row += 1


def _circle(cx: float, cy: float, r: float) -> str:
    return f"M{f(cx - r)} {f(cy)}a{f(r)} {f(r)} 0 1 0 {f(2 * r)} 0a{f(r)} {f(r)} 0 1 0 {f(-2 * r)} 0"


def dots(box: Box, s: float):
    return "fill", "".join(_circle(x, y, s * 0.24) for x, y, _ in _grid(box, s, stagger=True))


def halftone(box: Box, s: float):
    x0, _, x1, _ = box
    span = max(1.0, x1 - x0)
    parts = []
    for x, y, _ in _grid(box, s * 0.8, stagger=True):
        t = min(1.0, max(0.0, (x - x0) / span))
        r = s * (0.06 + 0.26 * t)
        parts.append(_circle(x, y, r))
    return "fill", "".join(parts)


def stripes(box: Box, s: float):
    x0, y0, x1, y1 = box
    parts = []
    x = x0 - s
    while x <= x1 + s:
        parts.append(f"M{f(x)} {f(y0 - s)}h{f(s * 0.42)}V{f(y1 + s)}h{f(-s * 0.42)}Z")
        x += s
    return "fill", "".join(parts)


def checks(box: Box, s: float):
    return "fill", "".join(f"M{f(x)} {f(y)}h{f(s / 2)}v{f(s / 2)}h{f(-s / 2)}Z"
                           f"M{f(x + s / 2)} {f(y + s / 2)}h{f(s / 2)}v{f(s / 2)}h{f(-s / 2)}Z"
                           for x, y, _ in _grid(box, s))


def hatch(box: Box, s: float):
    x0, y0, x1, y1 = box
    n = (x1 - x0) + (y1 - y0)
    parts = []
    k = -n
    while k <= n:
        parts.append(f"M{f(x0 + k)} {f(y0)}l{f(n)} {f(n)}M{f(x0 + k)} {f(y1)}l{f(n)} {f(-n)}")
        k += s
    return "stroke", "".join(parts)


def waves(box: Box, s: float):
    x0, y0, x1, y1 = box
    parts = []
    y = y0 - s
    a = s * 0.28
    while y <= y1 + s:
        seg = [f"M{f(x0 - s)} {f(y)}q{f(s / 4)} {f(-a)} {f(s / 2)} 0"]
        x = x0 - s / 2
        while x <= x1 + s:
            seg.append(f"t{f(s / 2)} 0")
            x += s / 2
        parts.append("".join(seg))
        y += s * 0.7
    return "stroke", "".join(parts)


def zigzag(box: Box, s: float):
    x0, y0, x1, y1 = box
    parts = []
    y = y0 - s
    h = s * 0.3
    while y <= y1 + s:
        seg = [f"M{f(x0 - s)} {f(y)}"]
        x, up = x0 - s, True
        while x <= x1 + s:
            seg.append(f"l{f(s / 2)} {f(-h if up else h)}")
            x += s / 2
            up = not up
        parts.append("".join(seg))
        y += s * 0.75
    return "stroke", "".join(parts)


def chevron(box: Box, s: float):
    x0, y0, x1, y1 = box
    parts = []
    t = s * 0.22
    for x, y, _ in _grid(box, s):
        parts.append(f"M{f(x)} {f(y)}l{f(s / 2)} {f(s / 2.6)}l{f(s / 2)} {f(-s / 2.6)}v{f(t)}"
                     f"l{f(-s / 2)} {f(s / 2.6)}l{f(-s / 2)} {f(-s / 2.6)}Z")
    return "fill", "".join(parts)


def triangles(box: Box, s: float):
    return "fill", "".join(f"M{f(x)} {f(y + s * 0.8)}l{f(s * 0.4)} {f(-s * 0.6)}l{f(s * 0.4)} {f(s * 0.6)}Z"
                           for x, y, _ in _grid(box, s, stagger=True))


def grid(box: Box, s: float):
    x0, y0, x1, y1 = box
    parts = []
    x = x0 - s
    while x <= x1 + s:
        parts.append(f"M{f(x)} {f(y0 - s)}V{f(y1 + s)}")
        x += s
    y = y0 - s
    while y <= y1 + s:
        parts.append(f"M{f(x0 - s)} {f(y)}H{f(x1 + s)}")
        y += s
    return "stroke", "".join(parts)


def plus(box: Box, s: float):
    a, t = s * 0.22, s * 0.07
    return "fill", "".join(
        f"M{f(x - t)} {f(y - a)}h{f(2 * t)}v{f(a - t)}h{f(a - t)}v{f(2 * t)}h{f(t - a)}v{f(a - t)}"
        f"h{f(-2 * t)}v{f(t - a)}h{f(t - a)}v{f(-2 * t)}h{f(a - t)}Z"
        for x, y, _ in _grid(box, s, stagger=True))


def arcs(box: Box, s: float):
    """Concentric rings centred on the box's top-left corner (quarter-ring look once clipped)."""
    x0, y0, x1, y1 = box
    reach = math.hypot(x1 - x0, y1 - y0) + s
    parts = []
    r = s * 0.6
    while r <= reach:
        parts.append(f"M{f(x0 + r)} {f(y0)}A{f(r)} {f(r)} 0 0 1 {f(x0)} {f(y0 + r)}")
        r += s * 0.55
    return "stroke", "".join(parts)


def diamonds(box: Box, s: float):
    a = s * 0.24
    return "fill", "".join(f"M{f(x)} {f(y - a)}l{f(a)} {f(a)}l{f(-a)} {f(a)}l{f(-a)} {f(-a)}Z"
                           for x, y, _ in _grid(box, s, stagger=True))


def scales(box: Box, s: float):
    r = s / 2
    return "stroke", "".join(f"M{f(x - r)} {f(y)}a{f(r)} {f(r)} 0 0 0 {f(2 * r)} 0"
                             for x, y, _ in _grid(box, s, stagger=True))


def bricks(box: Box, s: float):
    x0, y0, x1, y1 = box
    parts = []
    h = s * 0.55
    y, row = y0 - s, 0
    while y <= y1 + s:
        parts.append(f"M{f(x0 - s)} {f(y)}H{f(x1 + s)}")
        x = x0 - s + (s / 2 if row % 2 else 0)
        while x <= x1 + s:
            parts.append(f"M{f(x)} {f(y)}v{f(h)}")
            x += s
        y += h
        row += 1
    return "stroke", "".join(parts)


def dashes(box: Box, s: float):
    return "stroke", "".join(f"M{f(x - s * 0.2)} {f(y)}h{f(s * 0.4)}" for x, y, _ in _grid(box, s * 0.7, stagger=True))


PATTERNS: dict[str, Callable[[Box, float], tuple[str, str]]] = {
    "dots": dots, "halftone": halftone, "stripes": stripes, "checks": checks,
    "hatch": hatch, "waves": waves, "zigzag": zigzag, "chevron": chevron,
    "triangles": triangles, "grid": grid, "plus": plus, "arcs": arcs,
    "diamonds": diamonds, "scales": scales, "bricks": bricks, "dashes": dashes,
}
# Patterns whose look depends on rotation; the rest only use angle 0/45.
ROTATABLE = {"stripes", "hatch", "waves", "zigzag", "chevron", "halftone", "bricks", "dashes", "scales", "triangles", "arcs"}
ANGLES = (0, 45, 90, 135)
DENSITY = (15.0, 19.0, 24.0)   # spacing in a 256-unit tile


def render(name: str, box: Box, density: int, angle: int, ink: str, scale: float = 1.0) -> str:
    """Pattern markup over `box`, rotated about its centre. Caller wraps it in a clip group."""
    s = DENSITY[density] * scale
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if angle:
        # cover the rotated box: expand to its circumscribed square
        half = math.hypot(x1 - x0, y1 - y0) / 2
        gen_box = (cx - half, cy - half, cx + half, cy + half)
    else:
        gen_box = box
    kind, d = PATTERNS[name](gen_box, s)
    if kind == "fill":
        el = f'<path d="{d}" fill="{ink}"/>'
    else:
        el = (f'<path d="{d}" fill="none" stroke="{ink}" '
              f'stroke-width="{f(2.4 * scale)}" stroke-linecap="round"/>')
    if angle:
        return f'<g transform="rotate({angle} {f(cx)} {f(cy)})">{el}</g>'
    return el
