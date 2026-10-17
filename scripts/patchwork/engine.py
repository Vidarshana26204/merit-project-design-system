"""Patchwork engine: node + icon (+ parent) → deterministic, unique composition → SVG.

    signature = sha256(node_id | icon_sha256 | ENGINE_VERSION)
    seed      = sha256(signature | salt)            salt starts at 0, bumps on collision

Layout (D16 rev 2): radial wedges that all meet at the centred icon. Patch count follows
the hierarchy: subject 4, topic 5, subtopic 6 (quest 7). A child keeps its parent's patch
styles in order and inserts exactly one new patch, so a topic reads as "its subject + 1".

Engine v3 (D16 rev 3): no ink seams. Neighbouring patches blend across a morph band: a
tint gradient strip runs along every ray and each pattern dissolves (its elements shrink
to nothing) as it nears a seam. Subtopics also get a `wash`: the pattern they added,
fading out from a card's top-right corner (replaces v2's `corner` swatch).

The composition key (rays + per-patch style + plate) is unique across every node of every
subject, and the added patch is unique among siblings; the Registry enforces both and
records the salt so regeneration is reproducible.
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

ENGINE_VERSION = "3"
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
                         {s.pattern for s in base if s.pattern}, allow_wedge=False, need_pattern=True)
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


MORPH = 16.0          # how far from a seam a pattern dissolves (tile units, × pattern_scale)
BLEND = 0.6           # tint gradient half-width, as a fraction of MORPH


def _ray_dist(px: float, py: float, c: tuple[float, float], q: tuple[float, float]) -> float:
    """Distance from p to the segment c→q."""
    vx, vy = q[0] - c[0], q[1] - c[1]
    t = max(0.0, min(1.0, ((px - c[0]) * vx + (py - c[1]) * vy) / (vx * vx + vy * vy)))
    return math.hypot(px - c[0] - t * vx, py - c[1] - t * vy)


def _angle(c: tuple[float, float], p: tuple[float, float]) -> float:
    return math.atan2(p[1] - c[1], p[0] - c[0]) % math.tau


def _seam_strip(c: tuple[float, float], q: tuple[float, float], toward: tuple[float, float],
                a: str, b: str, band: float, gid: str) -> tuple[str, str]:
    """A band along the ray c→q, graded across from tint a (one side) to tint b (`toward`'s side)."""
    ux, uy = q[0] - c[0], q[1] - c[1]
    ln = math.hypot(ux, uy)
    nx, ny = -uy / ln, ux / ln
    if (toward[0] - c[0]) * nx + (toward[1] - c[1]) * ny < 0:
        nx, ny = -nx, -ny
    mx, my = (c[0] + q[0]) / 2, (c[1] + q[1]) / 2
    ext = 1 + band / ln                                   # run past the frame so the clip trims it
    ex, ey = c[0] + ux * ext, c[1] + uy * ext
    pts = [(c[0] - nx * band, c[1] - ny * band), (ex - nx * band, ey - ny * band),
           (ex + nx * band, ey + ny * band), (c[0] + nx * band, c[1] + ny * band)]
    grad = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{patterns.f(mx - nx * band)}" '
            f'y1="{patterns.f(my - ny * band)}" x2="{patterns.f(mx + nx * band)}" y2="{patterns.f(my + ny * band)}">'
            f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')
    return grad, f'<path d="{geometry.poly_d(pts)}" fill="url(#{gid})"/>'


def _body(layout: geometry.Layout, styles: list[PatchStyle], uid: str, clip_rx: float | None,
          pattern_scale: float = 1.0, plate_r: float = 0.0) -> tuple[str, str]:
    """Wedge tints, seam blend strips, then dissolving patterns. Returns (defs, markup)."""
    w, h = layout.w, layout.h
    c = (w / 2, h / 2)
    band = MORPH * pattern_scale
    defs: list[str] = []
    fills, strips, pats = [], [], []
    n = len(layout.patches)
    edges = [p.poly[1] for p in layout.patches]           # ray i ends where wedge i starts
    for p, s in zip(layout.patches, styles):
        fills.append(f'<path d="{p.d}" fill="{C[s.tint]}"/>')
    for i in range(n):                                    # seam i: wedge i-1 | wedge i
        prev, cur = layout.patches[(i - 1) % n], layout.patches[i]
        cen = (sum(x for x, _ in cur.poly) / len(cur.poly), sum(y for _, y in cur.poly) / len(cur.poly))
        g, strip = _seam_strip(c, edges[i], cen, C[styles[(i - 1) % n].tint], C[styles[i].tint], band * BLEND, f"{uid}g{i}")
        defs.append(g)
        strips.append(strip)
    for i, (p, s) in enumerate(zip(layout.patches, styles)):
        if not s.pattern:
            continue
        q0, q1 = edges[i], edges[(i + 1) % n]
        a0 = _angle(c, q0)
        span = (_angle(c, q1) - a0) % math.tau or math.tau
        kind, els, to_world, rot = patterns.field(s.pattern, p.bbox, s.density, s.angle, pattern_scale)
        keep, ks = [], []
        for el in els:
            x, y = to_world(el.x, el.y)
            if (_angle(c, (x, y)) - a0) % math.tau >= span:
                continue                                  # anchor outside this wedge
            if math.hypot(x - c[0], y - c[1]) < plate_r - band:
                continue                                  # hidden under the plate
            if not (-band <= x <= w + band and -band <= y <= h + band):
                continue
            d = min(_ray_dist(x, y, c, q0), _ray_dist(x, y, c, q1))
            keep.append(el)
            ks.append(patterns.smoothstep(band * 0.15, band, d))
        ink = mix(C[s.tint], INK, 0.3 if s.wedge else 0.42)
        pats.append(patterns.draw(kind, keep, ks, ink, rot, pattern_scale))
    out = "".join(fills) + "".join(strips) + "".join(pats)
    if clip_rx is not None:
        fid = f"{uid}f"
        defs.append(f'<clipPath id="{fid}"><rect width="{patterns.f(w)}" height="{patterns.f(h)}" rx="{clip_rx}"/></clipPath>')
        return "".join(defs), f'<g clip-path="url(#{fid})">{out}</g>'
    return "".join(defs), out


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
    defs, body = _body(comp.layout(TILE, TILE), comp.styles, "t", FRAME_RX, plate_r=78)
    c = TILE / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img">'
            f'{_title(comp)}<defs>{defs}</defs>{body}{_plate(comp.plate, c, c, 78)}'
            f'{_icon_g(comp, c, c, 124)}{_frame(TILE, TILE)}</svg>\n')


def render_row(comp: Composition) -> str:
    """Same rays and styles as the tile; the wedges stretch sideways around the centred icon."""
    defs, body = _body(comp.layout(ROW_W, ROW_H), comp.styles, "r", FRAME_RX, pattern_scale=1.4, plate_r=86)
    cx, cy = ROW_W / 2, ROW_H / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 256" width="1024" height="256" role="img">'
            f'{_title(comp)}<defs>{defs}</defs>{body}{_plate(comp.plate, cx, cy, 86)}'
            f'{_icon_g(comp, cx, cy, 136)}{_frame(ROW_W, ROW_H)}</svg>\n')


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


RENDERERS = {"tile": render_tile, "row": render_row, "wash": render_wash, "mono": render_mono}
BUDGET = {"tile": 48_000, "row": 72_000, "wash": 40_000}   # bytes per variant


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
