"""Load "filled outline" icons and restyle them for patchworks.

Source structure (Envato "filled outline" sets): coloured shapes carry a fill via
`style="fill:#…"`, a `fill` attribute or a CSS class; the outline is the shape(s) with
**no** fill (SVG default black). A few icons also draw with `stroke:#000`.

Reference style (D-patchwork): every fill → white, the dominant saturated hue → the
node's accent tint (its darker sibling → the accent shade), near-black → ink, and the
outline → ink.
"""
from __future__ import annotations

import colorsys
import hashlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from fontTools.pens.areaPen import AreaPen
from fontTools.svgLib.path import parse_path

SVG_NS = "{http://www.w3.org/2000/svg}"
SHAPES = {"path", "rect", "circle", "ellipse", "polygon", "polyline", "line"}
GEOM = ("d", "x", "y", "width", "height", "rx", "ry", "cx", "cy", "r", "points",
        "x1", "y1", "x2", "y2", "transform")


@dataclass
class Shape:
    tag: str
    attrs: dict[str, str]        # geometry only
    fill: str | None             # "#rrggbb" or None → outline
    stroke: str | None
    stroke_width: str | None
    area: float


@dataclass
class Icon:
    id: str                      # "<set>/<name>"
    sha256: str                  # of the canonical source bytes
    view: float                  # viewBox size (square)
    shapes: list[Shape]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _style(el: ET.Element, classes: dict[str, dict[str, str]]) -> dict[str, str]:
    st: dict[str, str] = {}
    for cls in (el.get("class") or "").split():
        st.update(classes.get(cls, {}))
    for k in ("fill", "stroke", "stroke-width"):
        if el.get(k):
            st[k] = el.get(k)  # type: ignore[assignment]
    for decl in (el.get("style") or "").split(";"):
        if ":" in decl:
            k, v = decl.split(":", 1)
            st[k.strip()] = v.strip()
    return st


def _area(tag: str, a: dict[str, str]) -> float:
    g = lambda k: float(a.get(k, 0) or 0)  # noqa: E731
    try:
        if tag == "rect":
            return g("width") * g("height")
        if tag == "circle":
            return 3.14159 * g("r") ** 2
        if tag == "ellipse":
            return 3.14159 * g("rx") * g("ry")
        if tag in ("polygon", "polyline"):
            nums = [float(n) for n in re.findall(r"-?[\d.]+(?:e-?\d+)?", a.get("points", ""))]
            pts = list(zip(nums[::2], nums[1::2]))
            return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2
        if tag == "path":
            pen = AreaPen()
            parse_path(a.get("d", ""), pen)
            return abs(pen.value)
    except Exception:  # malformed geometry: treat as tiny
        return 0.0
    return 0.0


def _norm_hex(v: str) -> str | None:
    v = v.strip().lower()
    if v in ("none", "transparent"):
        return "none"
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", v)
    if not m:
        return None
    h = m.group(1)
    return "#" + ("".join(c * 2 for c in h) if len(h) == 3 else h)


def load(path: Path, icon_id: str) -> Icon:
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    vb = [float(n) for n in (root.get("viewBox") or "0 0 64 64").split()]
    classes: dict[str, dict[str, str]] = {}
    for st in root.iter(f"{SVG_NS}style"):
        for sel, body in re.findall(r"\.([\w-]+)\s*\{([^}]*)\}", st.text or ""):
            classes[sel] = {k.strip(): v.strip() for k, v in
                            (d.split(":", 1) for d in body.split(";") if ":" in d)}
    shapes: list[Shape] = []

    def walk(el: ET.Element, inherited: dict[str, str], gtransform: str) -> None:
        tag = el.tag.replace(SVG_NS, "")
        st = {**inherited, **_style(el, classes)}
        tr = " ".join(t for t in (gtransform, el.get("transform") or "") if t)
        if tag in ("g", "svg"):
            for ch in el:
                walk(ch, {k: v for k, v in st.items() if k in ("fill", "stroke", "stroke-width")},
                     tr if tag == "g" else gtransform)
            return
        if tag not in SHAPES:
            return
        attrs = {k: el.get(k) for k in GEOM if el.get(k) is not None}  # type: ignore[misc]
        if tr:
            attrs["transform"] = tr
        fill = _norm_hex(st["fill"]) if "fill" in st else None
        stroke = _norm_hex(st.get("stroke", "")) if "stroke" in st else None
        if tag in ("line", "polyline") and fill is None and stroke:
            fill = "none"
        shapes.append(Shape(tag, attrs, fill, stroke if stroke not in (None, "none") else None,
                            st.get("stroke-width", "").replace("px", "") or None, _area(tag, attrs)))

    walk(root, {}, "")
    return Icon(icon_id, sha256_bytes(raw), vb[2], shapes)


def _hsl(hexv: str) -> tuple[float, float, float]:
    r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, l, s


def palette_roles(icon: Icon) -> dict[str, str]:
    """Map each source colour to a role: white | accent | accentShade | ink | shade."""
    weight: dict[str, float] = {}
    for sh in icon.shapes:
        if sh.fill and sh.fill != "none":
            weight[sh.fill] = weight.get(sh.fill, 0) + sh.area
    roles: dict[str, str] = {}
    hue_w: dict[int, float] = {}
    for col, w in weight.items():
        h, l, s = _hsl(col)
        if l < 0.2:
            roles[col] = "ink"
        elif s > 0.3 and 0.25 < l < 0.85:
            hue_w[int(h * 12) % 12] = hue_w.get(int(h * 12) % 12, 0) + w
    if hue_w:
        bucket = max(hue_w, key=lambda k: hue_w[k])
        members = [c for c in weight if c not in roles and _hsl(c)[2] > 0.3
                   and 0.25 < _hsl(c)[1] < 0.85 and int(_hsl(c)[0] * 12) % 12 == bucket]
        members.sort(key=lambda c: -_hsl(c)[1])          # lightest first
        for i, c in enumerate(members):
            roles[c] = "accent" if i == 0 else "accentShade"
    for col in weight:
        if col not in roles:
            # Darker shade layers (a darker twin of a lighter colour) read as soft depth.
            roles[col] = "shade" if _hsl(col)[1] < 0.62 else "white"
    return roles


def markup(icon: Icon, colors: dict[str, str], ink: str, mono: bool = False) -> str:
    """Icon shapes as SVG markup in the icon's own coordinates.

    colors: role → hex for white/accent/accentShade/shade. mono=True keeps only the outline
    (and stroked shapes) painted with currentColor.
    """
    roles = palette_roles(icon)
    out: list[str] = []
    for sh in icon.shapes:
        geo = " ".join(f'{k}="{v}"' for k, v in sh.attrs.items())
        stroke = ""
        if sh.stroke:
            sc = "currentColor" if mono else ink
            stroke = f' stroke="{sc}" stroke-width="{sh.stroke_width or 2}" stroke-linejoin="round"'
        if sh.fill is None:                     # outline layer
            fill = "currentColor" if mono else ink
        elif sh.fill == "none":
            fill = "none"
        elif mono:
            if roles.get(sh.fill) == "ink":
                fill = "currentColor"
            elif sh.stroke:
                fill = "none"
            else:
                continue
        else:
            role = roles.get(sh.fill, "white")
            fill = ink if role == "ink" else colors[role]
        out.append(f'<{sh.tag} {geo} fill="{fill}"{stroke}/>')
    return "".join(out)
