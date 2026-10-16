#!/usr/bin/env python3
"""Merit v3 brand + illustration kit generator.

    python3 -m venv .venv && .venv/bin/pip install fonttools
    .venv/bin/python scripts/brand/build_v3_brand.py

Reads  assets/brand/*.svg (v2 masters) and assets/fonts/GeneralSans-*.ttf (local only,
        see assets/fonts/README.md).
Writes assets/v3/brand/*.svg, assets/v3/patterns/*.svg, assets/v3/motifs/*.svg,
        and assets/v3/spots/*.svg. Hierarchy patchworks: scripts/patchwork/.

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


# ── 5. State spots: line-art mono (never patchwork) ─────────────────────────────────────
# Patterns + icons are reserved for hierarchy identity (SKILL.md §12), so empty / error /
# offline / not-found / success use a different grammar: one flat organic blob in a soft
# tint and a single-weight ink line drawing. No frame, no patches, no patterns, no sparkles.
BLOB = ("M100 22c30 0 58 12 70 36s6 52-14 70-52 22-78 14S30 116 26 90s2-46 22-58 28-10 52-10z")
SPOTS = {
    "empty": ("Nothing here yet", "sage.100",
              '<path d="M58 84l14-30h56l14 30"/><path d="M58 84v34a6 6 0 0 0 6 6h72a6 6 0 0 0 6-6V84h-30'
              'a12 12 0 0 1-24 0z"/><path d="M84 40l-6-10M100 36V24M116 40l6-10"/>'),
    "error": ("Something went wrong", "blush.300",
              '<path d="M28 96c10 0 16-4 22-12"/><rect x="50" y="64" width="34" height="34" rx="6"/>'
              '<path d="M84 74h12M84 88h12"/><rect x="112" y="64" width="34" height="34" rx="6"/>'
              '<path d="M146 81c10 0 18 6 26 14"/><path d="M122 76v0M122 86v0" stroke-width="5"/>'
              '<path d="M100 52l4 8M104 106l-4 8M92 48v8"/>'),
    "offline": ("You're offline", "sky.300",
                '<path d="M66 108h64a22 22 0 0 0 2-44 30 30 0 0 0-58-4 24 24 0 0 0-8 48z"/><path d="M60 40l80 84"/>'),
    "not-found": ("Page not found", "butter.100",
                  '<circle cx="92" cy="74" r="28"/><path d="M112 94l26 26"/>'
                  '<path d="M84 66a8 8 0 1 1 10 8c-2 1-2 3-2 6M92 88h0"/>'),
    "success": ("All done", "sage.300",
                '<circle cx="100" cy="76" r="36"/><path d="M84 76l11 11 22-24"/><path d="M78 108l-8 22 14-6 8 12 6-20M122 108l8 22-14-6-8 12-6-20"/>'),
}


def spot(name: str, title: str, tint: str, drawing: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 160" width="200" height="160" role="img" aria-labelledby="t">'
        f'<title id="t">{title}</title>'
        f'<path d="{BLOB}" fill="{c(tint)}"/>'
        f'<g fill="none" stroke="{INK}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">{drawing}</g>'
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
    for name, (title, tint, drawing) in SPOTS.items():
        write(f"spots/{name}.svg", spot(name, title, tint, drawing))
    print(f"✓ {len(masters)} brand masters, 3 lockups, {len(PATTERNS)} patterns, 5 motifs, "
          f"{len(SPOTS)} spots → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
