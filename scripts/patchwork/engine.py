"""Patchwork engine: node + icon (+ parent) → deterministic, unique composition → SVG.

    signature = sha256(node_id | icon_sha256 | ENGINE_VERSION)
    seed      = sha256(signature | salt)            salt starts at 0, bumps on collision

Layout (D16 rev 4, engine v4): **square in a square**. Fixed, symmetric cuts (geometry.py);
patch count follows the hierarchy: subject 4, topic 5, subtopic 6 (quest 7), and each level
nests one shape further in (subject: hourglass X + corner triangles; topic: + diamond;
subtopic: + square). A child keeps its parent's patch styles and adds exactly one, so a
topic reads as "its subject + 1". The icon plate's shape says the level: subject hexagon,
topic pentagon, subtopic square.

Seams are crisp tint edges (no ink): each pattern dissolves, its elements shrinking to
nothing, as it nears the edge of the region it shows in. Subtopics also get a `wash`: the
pattern they added, fading out from a card's top-right corner. One variant per use:
tile (1:1), wash, mono. The 4:1 row variant was retired in v4.

The composition key (per-patch styles) is unique across every node of every subject, and
the added patch is unique among siblings; the Registry enforces both and records the salt
so regeneration is reproducible.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

from . import geometry, patterns
from .icon import Icon, markup

ENGINE_VERSION = "4"
ROOT = Path(__file__).resolve().parents[2]

TILE = 256.0
FRAME_RX = 32.0
SEAM, FRAME = 2.6, 3.6          # plate / frame stroke: ≈1.5 / 2 px at a 128-px tile
ICON = 136.0                    # icon box on the tile (v3: 124)


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
    styles: list[PatchStyle]        # one per layout role (geometry.square_in_square), outermost first
    added: int | None               # index of the patch this node added to its parent's (always the last)
    accent: str

    @property
    def plate(self) -> str:
        return geometry.PLATE_BY_LEVEL.get(self.node.level, "square")

    def layout(self, size: float = TILE) -> geometry.Layout:
        return geometry.square_in_square(len(self.styles), size)

    def key(self) -> str:
        """Canonical, hashable description of what the tile looks like (minus the icon)."""
        body = {"layout": "square-in-square", "plate": self.plate,
                "patches": [(s.tint, s.pattern, s.angle, s.density, s.wedge) for s in self.styles]}
        return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()

    def added_key(self) -> str | None:
        if self.added is None:
            return None
        s = self.styles[self.added]
        return f"{s.tint}|{s.pattern}|{s.angle}|{s.density}"


def signature(node: Node, icon_sha: str) -> str:
    return hashlib.sha256(f"{node.id}|{icon_sha}|{ENGINE_VERSION}".encode()).hexdigest()


def _new_style(rng: random.Random, fam: dict[str, list[str]], avoid_tints: set[str],
               avoid_patterns: set[str], allow_wedge: bool, need_pattern: bool = False) -> PatchStyle:
    if allow_wedge and rng.random() < 0.5:
        return PatchStyle(rng.choice(fam["wedges"]), rng.choice((None, "dots", "halftone")), 0, 1, wedge=True)
    pool = fam["tints"] + rng.sample(GLOBAL_TINTS, 3)
    tints = [t for t in pool if t not in avoid_tints] or [t for t in GLOBAL_TINTS if t not in avoid_tints]
    tint = rng.choice(tints)
    if need_pattern or rng.random() < 0.8:
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
        # A root (subject): n fresh styles. Its four roles all touch, so every tint differs;
        # at most one is a solid wedge.
        styles: list[PatchStyle] = []
        wedge_at = rng.randrange(n) if rng.random() < 0.6 else -1
        for i in range(n):
            avoid = {s.tint for s in styles}
            st = _new_style(rng, fam, avoid, {s.pattern for s in styles if s.pattern}, allow_wedge=False)
            if i == wedge_at:
                st = PatchStyle(rng.choice(fam["wedges"]), rng.choice((None, "dots")), 0, 1, wedge=True)
            styles.append(st)
        added = None
    else:
        # A child: the parent's styles + one new patch, nested inside them.
        base = list(parent.styles)
        added = len(base)
        touching = {base[r].tint for r in geometry.NEIGHBOURS.get(added, set()) if r < added}
        new = _new_style(rng, fam, touching | {s.tint for s in base if s.wedge},
                         {s.pattern for s in base if s.pattern}, allow_wedge=False, need_pattern=True)
        styles = base + [new]
    accent = rng.choice(fam["accent"])
    return Composition(node, icon, sig, salt, fam_name, styles, added, accent)


# ── rendering ───────────────────────────────────────────────────────────────────────────
INK, WHITE = C["patchwork.seam"], C["patchwork.plate"]
ICON_COLORS_BASE = {"white": WHITE, "shade": C["patchwork.iconShade"]}
ACCENT_SHADE = {  # a deeper sibling for the accent's darker twin
    "butter.300": "butter.500", "coral.300": "orange.400", "orange.300": "orange.400",
    "violet.300": "violet.400", "sky.300": "sky.500", "blush.300": "coral.300", "sage.300": "sage.500",
}


MORPH = 16.0          # how far from a seam a pattern dissolves (tile units)


def _body(layout: geometry.Layout, styles: list[PatchStyle], uid: str, clip_rx: float, hole_r: float) -> tuple[str, str]:
    """Patch tints in paint order, then each pattern dissolving toward the edges of the region
    its patch shows in (its own seams and those of every patch painted over it). Elements
    under the plate (radius `hole_r`) are skipped. Returns (defs, markup)."""
    w, h = layout.w, layout.h
    c = (w / 2, h / 2)
    band = MORPH
    fills, pats = [], []
    for p in layout.patches:
        fills.append(f'<path d="{p.d}" fill="{C[styles[p.role].tint]}"/>')
    for i, p in enumerate(layout.patches):
        s = styles[p.role]
        if not s.pattern:
            continue
        above = [q for pl in layout.patches[i + 1:] for q in pl.polys]
        seams = [e for poly in p.polys + above for e in geometry.edges(poly, w, h)]
        kind, els, to_world, rot = patterns.field(s.pattern, p.bbox, s.density, s.angle)
        keep, ks = [], []
        for el in els:
            x, y = to_world(el.x, el.y)
            if not any(geometry.inside((x, y), poly) for poly in p.polys):
                continue                                  # anchor outside this patch
            if any(geometry.inside((x, y), poly) for poly in above):
                continue                                  # covered by a later patch
            if math.hypot(x - c[0], y - c[1]) < hole_r - band:
                continue                                  # hidden under the plate
            d = min((geometry.seg_dist((x, y), a, b) for a, b in seams), default=band)
            keep.append(el)
            ks.append(patterns.smoothstep(band * 0.15, band, d))
        ink = mix(C[s.tint], INK, 0.3 if s.wedge else 0.42)
        pats.append(patterns.draw(kind, keep, ks, ink, rot))
    fid = f"{uid}f"
    defs = f'<clipPath id="{fid}"><rect width="{patterns.f(w)}" height="{patterns.f(h)}" rx="{clip_rx}"/></clipPath>'
    return defs, f'<g clip-path="url(#{fid})">{"".join(fills)}{"".join(pats)}</g>'


def mix(a: str, b: str, t: float) -> str:
    """Blend two hex colours (pattern ink = the patch tint pulled toward ink)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


def _plate(kind: str, cx: float, cy: float) -> str:
    pts = geometry.plate_points(kind, cx, cy, TILE)
    d = geometry.rounded_d(pts, TILE * geometry.PLATE_ROUND[kind])
    return f'<path d="{d}" fill="{WHITE}" stroke="{INK}" stroke-width="{SEAM}" stroke-linejoin="round"/>'


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
    c = TILE / 2
    defs, body = _body(comp.layout(), comp.styles, "t", FRAME_RX, geometry.plate_inradius(comp.plate, TILE))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img">'
            f'{_title(comp)}<defs>{defs}</defs>{body}{_plate(comp.plate, c, c)}'
            f'{_icon_g(comp, c, c, ICON)}{_frame(TILE, TILE)}</svg>\n')


WASH = 400.0


def wash_inks(comp: Composition) -> dict[str, str] | None:
    """Colours the app tints the wash with: the added patch's pattern ink (light theme)
    and its tint (dark theme). Shipped in the manifest next to the wash variant."""
    if comp.added is None:
        return None
    t = C[comp.styles[comp.added].tint]
    return {"light": mix(t, INK, 0.42), "dark": t}


def render_wash(comp: Composition) -> str:
    """The pattern this node added, radiating from the top-right corner and fading out.

    Transparent, ink = currentColor: the app tints it and sets the layer opacity per theme
    (MIGRATION §1.4a). Drawn behind flashcard and note content, aligned top-right.
    Only nodes that added a patch (topics, subtopics, quests) have one.
    """
    if comp.added is None or not comp.styles[comp.added].pattern:
        return ""
    st = comp.styles[comp.added]
    kind, els, to_world, rot = patterns.field(st.pattern, (0, 0, WASH, WASH), st.density, st.angle, 1.5)
    diag = math.hypot(WASH, WASH)
    ks = []
    for el in els:
        x, y = to_world(el.x, el.y)
        ks.append(1 - patterns.smoothstep(0.04, 0.46, math.hypot(WASH - x, y) / diag))
    body = patterns.draw(kind, els, ks, "currentColor", rot, 1.5, opacity_by_k=True)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400" aria-hidden="true">'
            f'<defs><clipPath id="wq"><rect width="400" height="400"/></clipPath></defs>'
            f'<g clip-path="url(#wq)">{body}</g></svg>\n')


def render_mono(comp: Composition) -> str:
    if not comp.icon:
        return ""
    v = comp.icon.view
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {patterns.f(v)} {patterns.f(v)}" width="32" height="32" '
            f'fill="currentColor" role="img">{_title(comp)}{markup(comp.icon, {}, INK, mono=True)}</svg>\n')


RENDERERS = {"tile": render_tile, "wash": render_wash, "mono": render_mono}
BUDGET = {"tile": 48_000, "wash": 40_000}   # bytes per variant


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
