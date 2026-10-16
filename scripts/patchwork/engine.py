"""Patchwork engine: node + icon (+ parent) → deterministic, unique composition → SVG.

    signature = sha256(node_id | icon_sha256 | ENGINE_VERSION)
    seed      = sha256(signature | salt)            salt starts at 0, bumps on collision

Layout (D16 rev 2): radial wedges that all meet at the centred icon. Patch count follows
the hierarchy: subject 4, topic 5, subtopic 6 (quest 7). A child keeps its parent's patch
styles in order and inserts exactly one new patch, so a topic reads as "its subject + 1".

The composition key (rays + per-patch style + plate) is unique across every node of every
subject, and the added patch is unique among siblings; the Registry enforces both and
records the salt so regeneration is reproducible.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path

from . import geometry, patterns
from .icon import Icon, markup

ENGINE_VERSION = "2"
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
PLATES = ("circle", "squircle", "hexagon")   # the plate hides where the seams meet
LEVEL_PATCHES = {"subject": 4, "topic": 5, "subtopic": 6, "quest": 7}
PATTERN_NAMES = list(patterns.PATTERNS)


@dataclass
class Node:
    id: str            # stable UUID (or "quest:<subtopic_id>:<n>")
    level: str         # subject | topic | subtopic | quest
    subject: str       # subject code, e.g. PHYSICS
    code: str = ""
    title: str = ""
    parent: str | None = None   # parent node id (topic → subject, subtopic → topic)


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
    rays: list[int]                 # perimeter slots, sorted; len == patch count
    styles: list[PatchStyle]        # one per wedge, clockwise from rays[0]
    added: int | None               # index of the patch this node added to its parent's
    plate: str
    accent: str

    def layout(self, w: float, h: float) -> geometry.Layout:
        return geometry.radial_layout(self.rays, w, h)

    def key(self) -> str:
        """Canonical, hashable description of what the tile looks like (minus the icon)."""
        body = {"rays": self.rays, "plate": self.plate,
                "patches": [(s.tint, s.pattern, s.angle, s.density, s.wedge) for s in self.styles]}
        return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()

    def added_key(self) -> str | None:
        if self.added is None:
            return None
        s = self.styles[self.added]
        return f"{s.tint}|{s.pattern}|{s.angle}|{s.density}"


def signature(node: Node, icon_sha: str) -> str:
    return hashlib.sha256(f"{node.id}|{icon_sha}|{ENGINE_VERSION}".encode()).hexdigest()


def _rays(rng: random.Random, n: int) -> list[int]:
    """n rays spread round the perimeter with jitter, so wedges stay similar in size."""
    slots = geometry.RAY_SLOTS
    step = slots / n
    jitter = max(1, int(step * 0.22))
    offset = rng.randrange(slots)
    rays = {(offset + round(k * step) + rng.randint(-jitter, jitter)) % slots for k in range(n)}
    while len(rays) < n:                       # jitter collision: nudge until distinct
        rays.add(rng.randrange(slots))
    return sorted(rays)


def _new_style(rng: random.Random, fam: dict[str, list[str]], avoid_tints: set[str],
               avoid_patterns: set[str], allow_wedge: bool) -> PatchStyle:
    if allow_wedge and rng.random() < 0.5:
        return PatchStyle(rng.choice(fam["wedges"]), rng.choice((None, "dots", "halftone")), 0, 1, wedge=True)
    pool = fam["tints"] + rng.sample(GLOBAL_TINTS, 3)
    tints = [t for t in pool if t not in avoid_tints] or [t for t in GLOBAL_TINTS if t not in avoid_tints]
    tint = rng.choice(tints)
    if rng.random() < 0.8:
        pats = [p for p in PATTERN_NAMES if p not in avoid_patterns] or PATTERN_NAMES
        pat: str | None = rng.choice(pats)
        angle = rng.choice(patterns.ANGLES if pat in patterns.ROTATABLE else (0, 45))
        return PatchStyle(tint, pat, angle, rng.choice((1, 1, 2)))
    return PatchStyle(tint, None, 0, 0)


def compose(node: Node, icon: Icon | None, salt: int = 0, parent: "Composition | None" = None) -> Composition:
    sig = signature(node, icon.sha256 if icon else "noicon")
    rng = random.Random(int(hashlib.sha256(f"{sig}|{salt}".encode()).hexdigest(), 16))
    fam_name = SUBJECT_FAMILY.get(node.subject) or list(FAMILIES)[
        int(hashlib.sha256(node.subject.encode()).hexdigest(), 16) % len(FAMILIES)]
    fam = FAMILIES[fam_name]
    n = LEVEL_PATCHES.get(node.level, 4) if parent is None else len(parent.styles) + 1

    added: int | None
    if parent is None:
        # A root (subject): n fresh styles, cyclic neighbours never share a tint, at most one wedge.
        styles: list[PatchStyle] = []
        wedge_at = rng.randrange(n) if rng.random() < 0.6 else -1
        for i in range(n):
            avoid = {styles[-1].tint} if styles else set()
            if i == n - 1 and styles:
                avoid.add(styles[0].tint)
            st = _new_style(rng, fam, avoid, {s.pattern for s in styles if s.pattern}, allow_wedge=False)
            if i == wedge_at:
                st = PatchStyle(rng.choice(fam["wedges"]), rng.choice((None, "dots")), 0, 1, wedge=True)
            styles.append(st)
        added = None
    else:
        # A child: the parent's styles in order + one new patch inserted between two of them.
        base = list(parent.styles)
        added = rng.randrange(len(base) + 1)
        left, right = base[(added - 1) % len(base)], base[added % len(base)]
        new = _new_style(rng, fam, {left.tint, right.tint} | {s.tint for s in base if s.wedge},
                         {s.pattern for s in base if s.pattern}, allow_wedge=False)
        styles = base[:added] + [new] + base[added:]
    rays = _rays(rng, n)
    plate = rng.choice(PLATES)
    accent = rng.choice(fam["accent"])
    return Composition(node, icon, sig, salt, fam_name, rays, styles, added, plate, accent)


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


def _frame(w: float, h: float) -> str:
    return (f'<rect x="{FRAME / 2}" y="{FRAME / 2}" width="{w - FRAME}" height="{h - FRAME}" '
            f'rx="{FRAME_RX - FRAME / 2}" fill="none" stroke="{INK}" stroke-width="{FRAME}"/>')


def render_tile(comp: Composition) -> str:
    defs, body = _body(comp.layout(TILE, TILE), comp.styles, "t", FRAME_RX)
    c = TILE / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img">'
            f'{_title(comp)}<defs>{defs}</defs>{body}{_plate(comp.plate, c, c, 78)}'
            f'{_icon_g(comp, c, c, 124)}{_frame(TILE, TILE)}</svg>\n')


def render_row(comp: Composition) -> str:
    """Same rays and styles as the tile; the wedges stretch sideways around the centred icon."""
    defs, body = _body(comp.layout(ROW_W, ROW_H), comp.styles, "r", FRAME_RX, pattern_scale=1.4)
    cx, cy = ROW_W / 2, ROW_H / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 256" width="1024" height="256" role="img">'
            f'{_title(comp)}<defs>{defs}</defs>{body}{_plate(comp.plate, cx, cy, 86)}'
            f'{_icon_g(comp, cx, cy, 136)}{_frame(ROW_W, ROW_H)}</svg>\n')


def render_corner(comp: Composition) -> str:
    """The tile's full patch body (tints + patterns, no icon, no frame) for card corners.

    Widgets clip it (e.g. a quarter-circle or the card's top-right radius), so the whole
    composition is kept: any crop still shows the node's own tints and patterns.
    """
    defs, body = _body(comp.layout(TILE, TILE), comp.styles, "c", None)
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
MAX_SALT = 400


def _size(comp: Composition) -> int:
    return sum(len(RENDERERS[v](comp).encode()) for v in BUDGET)


class Registry:
    """Append-only record of signatures, salts and composition keys.

    Guarantees: composition keys unique across all nodes; the patch a child adds is unique
    among its siblings; files within BUDGET (or, if no salt fits, the smallest candidate).
    """

    def __init__(self, path: Path | None = None):
        self.path = path
        self.data: dict = {"engine_version": ENGINE_VERSION, "nodes": {}}
        if path and path.exists():
            loaded = json.loads(path.read_text())
            if loaded.get("engine_version") == ENGINE_VERSION:
                self.data = loaded
        self.keys = {v["key"]: k for k, v in self.data["nodes"].items()}
        self.added: dict[str, dict[str, str]] = {}          # parent id → added key → node id
        for k, v in self.data["nodes"].items():
            if v.get("parent") and v.get("added"):
                self.added.setdefault(v["parent"], {})[v["added"]] = k
        self.over_budget: list[str] = []

    def _free(self, node: Node, comp: Composition) -> bool:
        if self.keys.get(comp.key(), node.id) != node.id:
            return False
        ak = comp.added_key()
        if ak and self.added.get(node.parent or "", {}).get(ak, node.id) != node.id:
            return False
        return True

    def place(self, node: Node, icon: Icon | None, parent: Composition | None = None) -> Composition:
        rec = self.data["nodes"].get(node.id)
        icon_sha = icon.sha256 if icon else "noicon"
        if rec and rec["icon_sha256"] == icon_sha:
            comp = compose(node, icon, rec["salt"], parent)
            if comp.key() == rec["key"]:
                return comp
        if rec:  # icon or parent changed → free the old entries, re-place
            self.keys.pop(rec["key"], None)
            if rec.get("added"):
                self.added.get(rec.get("parent") or "", {}).pop(rec["added"], None)
        best: tuple[int, Composition] | None = None
        for salt in range(MAX_SALT):
            comp = compose(node, icon, salt, parent)
            if not self._free(node, comp):
                continue
            if within_budget(comp):
                best = (0, comp)
                break
            size = _size(comp)
            if best is None or size < best[0]:
                best = (size, comp)
        if best is None:
            raise RuntimeError(f"no unique composition for {node.id} within {MAX_SALT} salts")
        comp = best[1]
        if best[0]:
            self.over_budget.append(node.id)
        k = comp.key()
        self.keys[k] = node.id
        ak = comp.added_key()
        if ak:
            self.added.setdefault(node.parent or "", {})[ak] = node.id
        self.data["nodes"][node.id] = {
            "level": node.level, "subject": node.subject, "code": node.code, "parent": node.parent,
            "icon": icon.id if icon else None, "icon_sha256": icon_sha,
            "signature": comp.signature, "salt": comp.salt, "key": k, "added": ak,
        }
        return comp

    def save(self) -> None:
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, indent=1, sort_keys=True) + "\n")
