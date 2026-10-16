"""Patchwork engine: node + icon → deterministic, unique composition → SVG variants.

    signature = sha256(node_id | icon_sha256 | ENGINE_VERSION)
    seed      = sha256(signature | salt)            salt starts at 0, bumps on collision

The composition key (layout slots + per-patch tint/pattern/angle/density + plate) must be
unique across every node of every subject; the Registry enforces that and records the salt
so regeneration is reproducible.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path

from . import geometry, patterns
from .icon import Icon, markup

ENGINE_VERSION = "1"
ROOT = Path(__file__).resolve().parents[2]

TILE = 256.0
ROW_W, ROW_H = 1024.0, 256.0
FRAME_RX = 32.0
SEAM, FRAME = 2.6, 3.6          # ≈1.5 / 2 px at a 128-px tile


def load_tokens() -> dict[str, str]:
    tok = json.loads((ROOT / "build/json/merit-tokens.json").read_text())["themes"]["light"]
    return {k[len("color."):]: v.upper() for k, v in tok.items() if k.startswith("color.")}


C = load_tokens()

# Subject families: patch tints (light, pattern-friendly) + accent wedges (solid, strong).
# Primitive names only, so a token change re-tints everything on the next run.
FAMILIES: dict[str, dict[str, list[str]]] = {
    "warm": {   # Physics
        "tints": ["orange.300", "orange.400", "coral.300", "coral.100", "butter.300", "sand.300", "blush.300"],
        "wedges": ["violet.500", "orange.500", "violet.700"],
        "accent": ["butter.300", "coral.300", "orange.300"],
    },
    "cool": {   # Chemistry
        "tints": ["violet.100", "violet.300", "blush.300", "sky.300", "sand.100", "butter.100", "coral.100"],
        "wedges": ["violet.500", "violet.700", "orange.500"],
        "accent": ["violet.300", "sky.300", "blush.300"],
    },
    "fresh": {  # Biology
        "tints": ["sage.300", "sage.100", "butter.300", "sky.300", "sand.300", "coral.100", "butter.100"],
        "wedges": ["sage.500", "violet.500", "orange.500"],
        "accent": ["sage.300", "butter.300", "coral.300"],
    },
    "mixed": {  # fallback for subjects without a mapped family
        "tints": ["coral.300", "butter.300", "sky.300", "sage.300", "violet.100", "sand.300", "blush.300"],
        "wedges": ["violet.500", "orange.500", "sage.500"],
        "accent": ["butter.300", "sky.300", "coral.300"],
    },
}
SUBJECT_FAMILY = {"PHYSICS": "warm", "CHEMISTRY": "cool", "BIOLOGY": "fresh"}
GLOBAL_TINTS = sorted({t for fam in FAMILIES.values() for t in fam["tints"]})
PLATES = ("circle", "squircle", "hexagon", "none")
PATTERN_NAMES = list(patterns.PATTERNS)


@dataclass
class Node:
    id: str            # stable UUID (or "quest:<subtopic_id>:<n>")
    level: str         # subject | topic | subtopic | quest
    subject: str       # subject code, e.g. PHYSICS
    code: str = ""
    title: str = ""


@dataclass
class PatchStyle:
    tint: str
    pattern: str | None
    angle: int
    density: int
    wedge: bool = False


@dataclass
class Composition:
    node: Node
    icon: Icon | None
    signature: str
    salt: int
    family: str
    layout: geometry.Layout
    styles: list[PatchStyle]
    row_layout: geometry.Layout
    row_styles: list[PatchStyle]
    plate: str
    accent: str

    def key(self) -> str:
        """Canonical, hashable description of what the tile looks like (minus the icon)."""
        body = {
            "cuts": self.layout.cuts, "overlays": self.layout.overlays, "plate": self.plate,
            "patches": [(s.tint, s.pattern, s.angle, s.density, s.wedge) for s in self.styles],
        }
        return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def signature(node: Node, icon_sha: str) -> str:
    return hashlib.sha256(f"{node.id}|{icon_sha}|{ENGINE_VERSION}".encode()).hexdigest()


def _style_patches(rng: random.Random, layout: geometry.Layout, fam: dict[str, list[str]],
                   wedge_ok: bool) -> list[PatchStyle]:
    # Node palette: 2 family tints + 1–2 global tints, so siblings rhyme but differ.
    own = rng.sample(fam["tints"], 2)
    extra = rng.sample([t for t in GLOBAL_TINTS if t not in own], rng.choice((1, 2)))
    palette = own + extra
    styles: list[PatchStyle] = []
    n = len(layout.patches)
    wedge_i = -1
    if wedge_ok and rng.random() < 0.55:
        # the smallest cut patch becomes the accent wedge
        cut = [i for i, p in enumerate(layout.patches) if not p.overlay]
        wedge_i = min(cut, key=lambda i: layout.patches[i].area)
    used_patterns: list[str] = []
    for i in range(n):
        if i == wedge_i:
            styles.append(PatchStyle(rng.choice(fam["wedges"]), rng.choice((None, "dots", "halftone")),
                                     0, 1, wedge=True))
            continue
        neighbours = {styles[j].tint for j in range(i) if geometry.adjacent(layout.patches[i], layout.patches[j])}
        choices = [t for t in palette if t not in neighbours] or [t for t in GLOBAL_TINTS if t not in neighbours]
        least = min(sum(1 for s in styles if s.tint == t) for t in choices)
        tint = rng.choice([t for t in choices if sum(1 for s in styles if s.tint == t) == least])
        if rng.random() < 0.55:
            pool = [p for p in PATTERN_NAMES if p not in used_patterns] or PATTERN_NAMES
            pat: str | None = rng.choice(pool)
            used_patterns.append(pat)
            angle = rng.choice(patterns.ANGLES if pat in patterns.ROTATABLE else (0, 45))
            density = rng.randrange(3)
        else:
            pat, angle, density = None, 0, 0
        styles.append(PatchStyle(tint, pat, angle, density))
    return styles


def compose(node: Node, icon: Icon | None, salt: int = 0) -> Composition:
    sig = signature(node, icon.sha256 if icon else "noicon")
    rng = random.Random(int(hashlib.sha256(f"{sig}|{salt}".encode()).hexdigest(), 16))
    fam_name = SUBJECT_FAMILY.get(node.subject) or list(FAMILIES)[
        int(hashlib.sha256(node.subject.encode()).hexdigest(), 16) % len(FAMILIES)]
    fam = FAMILIES[fam_name]
    layout = geometry.make_layout(rng, TILE, TILE, n_cuts=rng.choice((2, 2, 3)),
                                  n_overlays=rng.choice((0, 1, 1)), min_frac=0.06)
    styles = _style_patches(rng, layout, fam, wedge_ok=True)
    plate = rng.choice(PLATES)
    accent = rng.choice(fam["accent"])
    row_layout = geometry.make_layout(rng, ROW_W, ROW_H, n_cuts=rng.choice((3, 4, 5)),
                                      n_overlays=rng.choice((1, 2)), min_frac=0.03, row=True)
    row_styles = _style_patches(rng, row_layout, fam, wedge_ok=True)
    return Composition(node, icon, sig, salt, fam_name, layout, styles, row_layout, row_styles, plate, accent)


# ── rendering ───────────────────────────────────────────────────────────────────────────
INK, WHITE = C["patchwork.seam"], C["patchwork.plate"]
ICON_COLORS_BASE = {"white": WHITE, "shade": C["patchwork.iconShade"]}
ACCENT_SHADE = {  # a deeper sibling for the accent's darker twin
    "butter.300": "butter.500", "coral.300": "orange.400", "orange.300": "orange.400",
    "violet.300": "violet.400", "sky.300": "sky.500", "blush.300": "coral.300", "sage.300": "sage.500",
}


def _body(layout: geometry.Layout, styles: list[PatchStyle], uid: str, clip_rx: float | None,
          pattern_scale: float = 1.0) -> tuple[str, str]:
    """Patches + patterns + seams. Returns (defs, markup)."""
    w, h = layout.w, layout.h
    defs = []
    out = []
    for i, (p, s) in enumerate(zip(layout.patches, styles)):
        out.append(f'<path d="{p.d}" fill="{C[s.tint]}"/>')
        if s.pattern:
            cid = f"{uid}p{i}"
            defs.append(f'<clipPath id="{cid}"><path d="{p.d}"/></clipPath>')
            ink = mix(C[s.tint], INK, 0.3 if s.wedge else 0.42)
            out.append(f'<g clip-path="url(#{cid})">'
                       f'{patterns.render(s.pattern, p.bbox, s.density, s.angle, ink, pattern_scale)}</g>')
        # seam per patch, so a later overlay paints over the cuts it covers
        out.append(f'<path d="{p.d}" fill="none" stroke="{INK}" stroke-width="{SEAM}" stroke-linejoin="round"/>')
    if clip_rx is not None:
        fid = f"{uid}f"
        defs.append(f'<clipPath id="{fid}"><rect width="{patterns.f(w)}" height="{patterns.f(h)}" rx="{clip_rx}"/></clipPath>')
        return "".join(defs), f'<g clip-path="url(#{fid})">{"".join(out)}</g>'
    return "".join(defs), "".join(out)


def mix(a: str, b: str, t: float) -> str:
    """Blend two hex colours (pattern ink = the patch tint pulled toward ink)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


def _plate(kind: str, cx: float, cy: float, r: float) -> str:
    attrs = f'fill="{WHITE}" stroke="{INK}" stroke-width="{SEAM}" stroke-linejoin="round"'
    if kind == "circle":
        return f'<circle cx="{patterns.f(cx)}" cy="{patterns.f(cy)}" r="{patterns.f(r)}" {attrs}/>'
    if kind == "squircle":
        return (f'<rect x="{patterns.f(cx - r)}" y="{patterns.f(cy - r)}" width="{patterns.f(2 * r)}" '
                f'height="{patterns.f(2 * r)}" rx="{patterns.f(r * 0.42)}" {attrs}/>')
    if kind == "hexagon":
        import math
        pts = " ".join(f"{patterns.f(cx + r * 1.08 * math.cos(math.radians(60 * k + 30)))},"
                       f"{patterns.f(cy + r * 1.08 * math.sin(math.radians(60 * k + 30)))}" for k in range(6))
        return f'<polygon points="{pts}" {attrs}/>'
    return ""


def _icon_g(comp: Composition, cx: float, cy: float, size: float) -> str:
    if not comp.icon:
        return ""
    colors = {**ICON_COLORS_BASE, "accent": C[comp.accent],
              "accentShade": C[ACCENT_SHADE.get(comp.accent, comp.accent)]}
    k = size / comp.icon.view
    return (f'<g transform="translate({patterns.f(cx - size / 2)} {patterns.f(cy - size / 2)}) scale({k:.4f})">'
            f'{markup(comp.icon, colors, C['patchwork.iconLine'])}</g>')


def _title(comp: Composition) -> str:
    t = (comp.node.title or comp.node.code or comp.node.id).replace("&", "&amp;").replace("<", "&lt;")
    return f"<title>{t}</title>"


def render_tile(comp: Composition) -> str:
    uid = "t"
    defs, body = _body(comp.layout, comp.styles, uid, FRAME_RX)
    c = TILE / 2
    plate = _plate(comp.plate, c, c, 78)
    icon = _icon_g(comp, c, c, 124 if comp.plate != "none" else 168)
    frame = (f'<rect x="{FRAME / 2}" y="{FRAME / 2}" width="{TILE - FRAME}" height="{TILE - FRAME}" '
             f'rx="{FRAME_RX - FRAME / 2}" fill="none" stroke="{INK}" stroke-width="{FRAME}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img">'
            f'{_title(comp)}<defs>{defs}</defs>{body}{plate}{icon}{frame}</svg>\n')


def render_row(comp: Composition) -> str:
    uid = "r"
    defs, body = _body(comp.row_layout, comp.row_styles, uid, FRAME_RX, pattern_scale=1.4)
    cx, cy = ROW_W / 3, ROW_H / 2
    plate = _plate(comp.plate if comp.plate != "none" else "circle", cx, cy, 86)
    icon = _icon_g(comp, cx, cy, 136)
    frame = (f'<rect x="{FRAME / 2}" y="{FRAME / 2}" width="{ROW_W - FRAME}" height="{ROW_H - FRAME}" '
             f'rx="{FRAME_RX - FRAME / 2}" fill="none" stroke="{INK}" stroke-width="{FRAME}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 256" width="1024" height="256" role="img">'
            f'{_title(comp)}<defs>{defs}</defs>{body}{plate}{icon}{frame}</svg>\n')


def render_corner(comp: Composition) -> str:
    """The tile's full patch body (tints + patterns, no icon, no frame) for card corners.

    Widgets clip it (e.g. a quarter-circle or the card's top-right radius), so the whole
    composition is kept: any crop still shows the node's own tints and patterns.
    """
    defs, body = _body(comp.layout, comp.styles, "c", None)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="96" height="96" aria-hidden="true">'
            f'<defs>{defs}<clipPath id="cq"><rect width="256" height="256"/></clipPath></defs>'
            f'<g clip-path="url(#cq)">{body}</g></svg>\n')


def render_mono(comp: Composition) -> str:
    if not comp.icon:
        return ""
    v = comp.icon.view
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {patterns.f(v)} {patterns.f(v)}" width="32" height="32" '
            f'fill="currentColor" role="img">{_title(comp)}{markup(comp.icon, {}, INK, mono=True)}</svg>\n')


RENDERERS = {"tile": render_tile, "row": render_row, "corner": render_corner, "mono": render_mono}
BUDGET = {"tile": 40_000, "row": 64_000, "corner": 40_000}   # bytes per variant


def within_budget(comp: Composition) -> bool:
    return all(len(RENDERERS[v](comp).encode()) <= cap for v, cap in BUDGET.items())


# ── registry ───────────────────────────────────────────────────────────────────────────
class Registry:
    """Append-only record of signatures, salts and composition keys (global uniqueness)."""

    def __init__(self, path: Path | None = None):
        self.path = path
        self.data: dict = {"engine_version": ENGINE_VERSION, "nodes": {}}
        if path and path.exists():
            loaded = json.loads(path.read_text())
            if loaded.get("engine_version") == ENGINE_VERSION:
                self.data = loaded
        self.keys = {v["key"]: k for k, v in self.data["nodes"].items()}

    def place(self, node: Node, icon: Icon | None) -> Composition:
        rec = self.data["nodes"].get(node.id)
        icon_sha = icon.sha256 if icon else "noicon"
        if rec and rec["icon_sha256"] == icon_sha:
            comp = compose(node, icon, rec["salt"])
            if comp.key() == rec["key"]:
                return comp
        if rec:  # icon changed → free the old key, re-place
            self.keys.pop(rec["key"], None)
        salt = 0
        while True:
            comp = compose(node, icon, salt)
            k = comp.key()
            if k not in self.keys and within_budget(comp):
                break
            salt += 1
        self.keys[k] = node.id
        self.data["nodes"][node.id] = {
            "level": node.level, "subject": node.subject, "code": node.code,
            "icon": icon.id if icon else None, "icon_sha256": icon_sha,
            "signature": comp.signature, "salt": salt, "key": k,
        }
        return comp

    def save(self) -> None:
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, indent=1, sort_keys=True) + "\n")
