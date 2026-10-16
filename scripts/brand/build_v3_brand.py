#!/usr/bin/env python3
"""Merit v3 brand + illustration kit generator.

    python3 -m venv .venv && .venv/bin/pip install fonttools
    .venv/bin/python scripts/brand/build_v3_brand.py

Reads  assets/brand/*.svg (v2 masters) and assets/fonts/GeneralSans-*.ttf (local only,
        see assets/fonts/README.md).
Writes assets/v3/brand/*.svg, assets/v3/patterns/*.svg, assets/v3/motifs/*.svg,
        assets/v3/tiles/*.svg and assets/v3/spots/*.svg.

All colours come from build/json/merit-tokens.json (light theme), so a token change
followed by a re-run keeps the art in sync. Output is deterministic.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOK = json.loads((ROOT / "build/json/merit-tokens.json").read_text())["themes"]
L, D = TOK["light"], TOK["dark"]
OUT = ROOT / "assets/v3"


def c(token: str, theme: dict = L) -> str:
    return theme[f"color.{token}"].upper()


INK, WHITE = c("ink.900"), c("white")

# ── 1. Brand masters: recolour v2 → v3, drop hard shadow, thin outlines (D11) ────────
V2_TO_V3 = {
    "#000000": INK,                 # outline
    "#FFF7ED": c("mist.50"),        # dark-mode outline
    "#29261B": INK,
    "#1B161B": c("night.900"),
    "#FFCC00": c("orange.500"),
    "#F2D43B": c("coral.300"),
    "#9ED5B7": c("sage.300"),
    "#9CE7C8": c("sage.500"),
    "#8E55D7": c("violet.500"),
    "#6E36B8": c("violet.700"),
    "#FFEFD7": c("sand.300"),
    "#FFFFFF": WHITE,
}
COIN_TO_V3 = {**V2_TO_V3, "#FFCC00": c("butter.300"), "#F2D43B": c("butter.500")}
OUTLINES = {"#000000", "#FFF7ED"}
SHADOW = re.compile(r'<polygon points="(?!128\.00,34\.00|128\.00,88\.00)[^"]*" fill="(#000000|#FFF7ED)" stroke="\1"[^>]*/>')
STROKE = re.compile(r'stroke-width="([\d.]+)"')


def v3ify(svg: str, palette: dict[str, str]) -> str:
    # The first outline-coloured polygon offset from the apex is the v2 hard shadow.
    svg = SHADOW.sub("", svg, count=1)
    svg = STROKE.sub(lambda m: f'stroke-width="{float(m.group(1)) * 0.75:g}"', svg)
    svg = re.sub(r"#[0-9A-Fa-f]{6}", lambda m: palette.get(m.group(0).upper(), m.group(0).upper()), svg)
    return svg.replace("<title id=\"t\">", "<title id=\"t\">v3 · ")


def build_brand_masters() -> list[str]:
    out = []
    for src in sorted((ROOT / "assets/brand").glob("*.svg")):
        if src.name.startswith("merit-lockup"):
            continue  # rebuilt with the v3 wordmark below
        palette = COIN_TO_V3 if "coin" in src.name else V2_TO_V3
        write(f"brand/{src.name}", v3ify(src.read_text(), palette))
        out.append(src.name)
    return out


# ── 2. Wordmark: General Sans Bold Italic, outlined (a logo is not a Derivative Work) ─
def glyph_run(font_file: str, text: str, size: float, tracking_em: float = 0.0):
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont

    path = ROOT / "assets/fonts" / font_file
    if not path.exists():
        raise SystemExit(f"missing {path} — see assets/fonts/README.md")
    font = TTFont(path)
    gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
    hmtx = font["hmtx"]
    scale = size / upm
    pen, x = SVGPathPen(gs), 0.0
    for ch in text:
        name = cmap[ord(ch)]
        gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
        x += hmtx[name][0] * scale + tracking_em * size
    cap = font["OS/2"].sCapHeight * scale
    return pen.getCommands(), x - tracking_em * size, cap


def lockup(kind: str, dark: bool) -> str:
    th = D if dark else L
    fg = c("text.primary", th)
    dot = c("action.primary", th)
    sub = c("text.secondary", th)
    bg = c("bg.app", th)
    mark = (OUT / f"brand/merit-mark{'-dark' if dark else ''}.svg").read_text()
    mark_g = re.search(r"(<g .*</g>)", mark, re.S).group(1)

    big, big_w, big_cap = glyph_run("GeneralSans-BoldItalic.ttf", "MERIT", 96)
    small, small_w, small_cap = glyph_run("GeneralSans-Semibold.ttf", "PROJECT", 26, 0.32)
    dot_r = 9.5

    if kind == "horizontal":
        w, h = 256 + 24 + big_w + dot_r * 2 + 12 + 16, 256
        tx, base = 256 + 16, 128 + big_cap / 2 - 6
        sub_y = base + 22 + small_cap
        mark_tf = ""
    else:  # stacked
        w = max(big_w + dot_r * 2 + 16, 256) + 48
        h = 256 + big_cap + small_cap + 64
        tx, base = (w - big_w - dot_r * 2 - 8) / 2, 256 + big_cap + 4
        sub_y = base + 20 + small_cap
        mark_tf = f' transform="translate({(w - 256) / 2:.2f} 0)"'
    sub_x = tx + 3 if kind == "horizontal" else (w - small_w) / 2
    title = f"Merit Project — v3 {kind}{' dark' if dark else ''}"
    rect = f'<rect width="{w:.0f}" height="{h:.0f}" fill="{bg}"/>' if dark else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-labelledby="t">'
        f'<title id="t">{title}</title>{rect}<g{mark_tf}>{mark_g}</g>'
        f'<path transform="translate({tx:.2f} {base:.2f})" fill="{fg}" d="{big}"/>'
        f'<circle cx="{tx + big_w + dot_r + 4:.2f}" cy="{base - dot_r:.2f}" r="{dot_r}" fill="{dot}"/>'
        f'<path transform="translate({sub_x:.2f} {sub_y:.2f})" fill="{sub}" d="{small}"/>'
        "</svg>\n"
    )


# ── 3. Patterns (D14) — ink at partial opacity, so they overlay any category tint ──
PATTERNS = {
    "dots": '<circle cx="4" cy="4" r="1.6" fill="{ink}" fill-opacity=".55"/>',
    "stripes": '<rect width="3" height="8" fill="{ink}" fill-opacity=".45"/>',  # rotated 45° by patternTransform
    "checks": '<rect width="4" height="4" fill="{ink}" fill-opacity=".25"/><rect x="4" y="4" width="4" height="4" fill="{ink}" fill-opacity=".25"/>',
    "hatch": '<path d="M0 0L8 8M8 0L0 8" stroke="{ink}" stroke-opacity=".45" stroke-width=".8"/>',
}


def pattern_def(name: str, pid: str | None = None) -> str:
    rotate = ' patternTransform="rotate(45)"' if name == "stripes" else ""
    body = PATTERNS[name].format(ink=INK)
    return f'<pattern id="{pid or name}" width="8" height="8" patternUnits="userSpaceOnUse"{rotate}>{body}</pattern>'


def build_patterns() -> None:
    for name in PATTERNS:
        write(f"patterns/{name}.svg",
              f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
              f'<defs>{pattern_def(name)}</defs><rect width="64" height="64" fill="url(#{name})"/></svg>\n')


# ── 4. Motifs — sparkle, brush underline, dotted connector ───────────────────────────
SPARKLE = "M12 0C13 8 16 11 24 12C16 13 13 16 12 24C11 16 8 13 0 12C8 11 11 8 12 0Z"
BRUSH = "M2 9C34 3 92 1 198 4c-6 2-50 3-92 5C70 11 30 12 6 13 1 13 0 10 2 9z"


def build_motifs() -> None:
    for name, tok in (("sparkle", "decor.sparkle"), ("sparkle-warm", "decor.sparkleWarm")):
        write(f"motifs/{name}.svg",
              f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path d="{SPARKLE}" fill="{c(tok)}"/></svg>\n')
    write("motifs/sparkle-mono.svg",
          f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path d="{SPARKLE}" fill="currentColor"/></svg>\n')
    write("motifs/brush-underline.svg",
          f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 14" width="200" height="14" preserveAspectRatio="none"><path d="{BRUSH}" fill="{c("decor.underline")}"/></svg>\n')
    write("motifs/brush-underline-mono.svg",
          f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 14" width="200" height="14" preserveAspectRatio="none"><path d="{BRUSH}" fill="currentColor"/></svg>\n')
    write("motifs/connector.svg",
          f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 24" width="160" height="24">'
          f'<path d="M8 12H152" stroke="{c("decor.connector")}" stroke-width="2" stroke-linecap="round" stroke-dasharray="2 7" fill="none"/>'
          f'<circle cx="8" cy="12" r="4" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
          f'<circle cx="152" cy="12" r="4" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/></svg>\n')


# ── 5. Subject patchwork tiles (category 1–6) + spot illustrations ───────────────────
# category index → (tint token, second-patch token, pattern). Glyphs are drawn in ink
# line on the white focal patch so the tile reads without an icon font.
CATEGORIES = [
    ("biology", "category.1", "coral.300", "dots"),
    ("physics", "category.2", "orange.500", "checks"),
    ("chemistry", "category.3", "violet.500", "stripes"),
    ("maths", "category.4", "violet.700", "hatch"),
    ("ict", "category.5", "coral.300", "dots"),
    ("languages", "category.6", "sage.300", "stripes"),
]
GLYPHS = {
    # simple 24×24 line drawings (ink, 1.5 stroke), centred on the focal patch
    "biology": '<path d="M8 3c0 6 8 6 8 12s-8 6-8 6M16 3c0 6-8 6-8 12s8 6 8 6M9 7h6M9 17h6"/>',
    "physics": '<ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(-60 12 12)"/><circle cx="12" cy="12" r="1.6" fill="{ink}"/>',
    "chemistry": '<path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2h12.4a1.5 1.5 0 0 0 1.3-2L14 9V3M7 15h10"/>',
    "maths": '<path d="M4 6h7M7.5 2.5v7M4 18h7M13 4l7 7M20 4l-7 7M13 17h7M16.5 14v0M16.5 20v0"/><circle cx="16.5" cy="14" r=".6" fill="{ink}"/><circle cx="16.5" cy="20" r=".6" fill="{ink}"/>',
    "ict": '<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
    "languages": '<path d="M3 5h10M8 3v2M5 5c1 4 4 7 7 8M11 5c-1 4-4 7-7 8M13 21l4-9 4 9M14.5 18h5"/>',
}


def tile(name: str, tint: str, patch: str, pattern: str) -> str:
    glyph = GLYPHS[name].format(ink=INK)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120" role="img" aria-labelledby="t">'
        f'<title id="t">{name.capitalize()} patchwork tile</title>'
        f'<defs>{pattern_def(pattern, "p")}<clipPath id="r"><rect x="4" y="4" width="112" height="112" rx="24"/></clipPath></defs>'
        f'<g clip-path="url(#r)"><rect x="4" y="4" width="112" height="112" fill="{c(tint)}"/>'
        f'<path d="M4 70L60 116H4Z" fill="{c(patch)}"/><path d="M4 70L60 116H4Z" fill="url(#p)"/>'
        f'<path d="M70 4H116V60Z" fill="url(#p)"/></g>'
        f'<g fill="none" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round">'
        f'<rect x="4" y="4" width="112" height="112" rx="24"/><path d="M4 70L60 116M70 4L116 60"/></g>'
        f'<rect x="32" y="32" width="56" height="56" rx="14" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
        f'<g transform="translate(42 42) scale(1.5)" fill="none" stroke="{INK}" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">{glyph}</g>'
        f'<path transform="translate(96 6) scale(.75)" d="{SPARKLE}" fill="{c("decor.sparkleWarm")}"/>'
        "</svg>\n"
    )


SPOTS = {
    "empty": ("Nothing here yet", '<path d="M14 18h20M14 24h14M14 30h18"/><rect x="8" y="8" width="32" height="32" rx="6"/>', "sand.300", "dots"),
    "error": ("Something went wrong", '<path d="M24 10l16 28H8z"/><path d="M24 20v8M24 33v.5"/>', "coral.300", "stripes"),
    "offline": ("You're offline", '<path d="M6 18c10-9 26-9 36 0M12 25c7-6 17-6 24 0M18 32c4-3 8-3 12 0M8 8l32 32"/>', "sky.300", "checks"),
    "not-found": ("Page not found", '<circle cx="21" cy="21" r="11"/><path d="M29 29l10 10M17 19h.5M25 19h.5M17 25c2 2 6 2 8 0"/>', "violet.100", "hatch"),
    "success": ("All done", '<circle cx="24" cy="24" r="16"/><path d="M16 24l6 6 11-12"/>', "sage.300", "dots"),
}


def spot(name: str, title: str, glyph: str, tint: str, pattern: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 160" width="200" height="160" role="img" aria-labelledby="t">'
        f'<title id="t">{title}</title><defs>{pattern_def(pattern, "p")}</defs>'
        f'<rect x="36" y="24" width="128" height="112" rx="28" fill="{c(tint)}" stroke="{INK}" stroke-width="1.5"/>'
        f'<path d="M36 96L84 136H64Q36 136 36 108Z" fill="url(#p)"/>'
        f'<path d="M124 24H136Q164 24 164 52V64Z" fill="{c("orange.500")}" stroke="{INK}" stroke-width="1.5"/>'
        f'<rect x="68" y="44" width="64" height="72" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
        f'<g transform="translate(76 56)" fill="none" stroke="{INK}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{glyph}</g>'
        f'<path transform="translate(16 28) scale(.8)" d="{SPARKLE}" fill="{c("decor.sparkle")}"/>'
        f'<path transform="translate(170 112) scale(.6)" d="{SPARKLE}" fill="{c("decor.sparkleWarm")}"/>'
        f'<path d="M24 76H36M164 76H180" stroke="{c("decor.connector")}" stroke-width="2" stroke-linecap="round" stroke-dasharray="2 6"/>'
        "</svg>\n"
    )


def write(rel: str, content: str) -> None:
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def main() -> None:
    masters = build_brand_masters()
    for kind in ("horizontal", "stacked"):
        write(f"brand/merit-lockup-{kind}.svg", lockup(kind, dark=False))
    write("brand/merit-lockup-horizontal-dark.svg", lockup("horizontal", dark=True))
    build_patterns()
    build_motifs()
    for name, tint, patch, pattern in CATEGORIES:
        write(f"tiles/{name}.svg", tile(name, tint, patch, pattern))
    for name, (title, glyph, tint, pattern) in SPOTS.items():
        write(f"spots/{name}.svg", spot(name, title, glyph, tint, pattern))
    print(f"✓ {len(masters)} brand masters, 3 lockups, {len(PATTERNS)} patterns, 5 motifs, "
          f"{len(CATEGORIES)} tiles, {len(SPOTS)} spots → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
