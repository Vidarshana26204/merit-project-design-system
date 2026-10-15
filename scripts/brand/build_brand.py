"""Generate the Merit brand marks (logo, lockups, app icons, merit-coin) as SVG.

    pip install fonttools          # only needed for the wordmark lockups
    python3 scripts/brand/build_brand.py

Writes assets/brand/*.svg. PNG rasters in assets/brand/png/ are rendered from these
SVGs (any SVG renderer; 1024px, transparent except the app icon).

Construction (256 grid) — redrawn from the original cube-in-pyramid mark:
  Pyramid: 60° triangle, apex (128,34), base y=196, half-base 162/√3.
  Cube: isometric hexagon, centre (128,142), R=54 — solved so its upper corners sit exactly
  on the pyramid sides AND the lower facet seams run at exactly 30°; bottom vertex touches
  the base. The cube splits the pyramid into three corners, each with a light/shade facet.
  Every edge is 30°, 60° or 90°.
Colours are DS tokens only; outlines are #000 (cream #FFF7ED in the -dark files, DS §6).
"""
import math
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "brand")
FONTS = os.path.join(ROOT, "assets", "fonts")
R3 = math.sqrt(3)

# ---- geometry
AX, AY, BY = 128, 34, 196
HB = (BY - AY) / R3
BL, BR = (AX - HB, BY), (AX + HB, BY)
CX, CY, R = 128, 142, 54
c30 = R * math.cos(math.radians(30))
T = (CX, CY - R); UR = (CX + c30, CY - R / 2); LR = (CX + c30, CY + R / 2)
B = (CX, CY + R); LL = (CX - c30, CY + R / 2); UL = (CX - c30, CY - R / 2); C = (CX, CY)
A = (AX, AY); BM = (AX, BY)

FACETS = {
    "top_l": [A, UL, T], "top_r": [A, T, UR],
    "left_u": [UL, BL, LL], "left_d": [BL, BM, B, LL],
    "right_u": [UR, LR, BR], "right_d": [LR, B, BM, BR],
}
CUBE = {"c_top": [T, UR, C, UL], "c_left": [UL, C, B, LL], "c_right": [C, UR, LR, B]}
CUBE_HEX = [T, UR, LR, B, LL, UL]
TRI = [A, BR, BL]

# ---- palettes (DS tokens; light/shade pairs are existing DS tones of the same hue)
YELLOW, YELLOW_SOFT = "#FFCC00", "#F2D43B"
INK, CREAM, CREAM_W, DARK_BG, WHITE, BLACK = "#29261B", "#FFEFD7", "#FFF7ED", "#1B161B", "#FFFFFF", "#000000"
DS = dict(top_l=YELLOW, top_r=YELLOW_SOFT, left_u="#9ED5B7", left_d="#9CE7C8",
          right_u="#8E55D7", right_d="#6E36B8", c_top=CREAM, c_left="#8E55D7",
          c_right=YELLOW, line=BLACK)
DS_DARK = dict(DS, c_top=CREAM_W, line=CREAM_W)
# Achiever (Pro) tier: purple summit + gold cube top ("crowned")
ACHIEVER = dict(DS, c_top=YELLOW, c_right=YELLOW_SOFT, top_l="#8E55D7", top_r="#6E36B8")


def P(pts, dx=0, dy=0):
    return " ".join(f"{x + dx:.2f},{y + dy:.2f}" for x, y in pts)


def poly(p, fill, stroke=None, sw=0, dx=0, dy=0):
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ""
    return f'<polygon points="{P(p, dx, dy)}" fill="{fill}"{s}/>'


def mark_brutal(pal, sw=4, sh=7, flat=False):
    """Brand mark: every facet outlined, hard offset shadow under the pyramid.
    flat=True is the small-size cut: one tone per corner."""
    if flat:
        pal = dict(pal, top_r=pal["top_l"], left_d=pal["left_u"], right_d=pal["right_u"])
    line = pal["line"]
    out = [poly(TRI, line, line, sw, sh, sh), poly(TRI, line, line, sw)]
    if flat:
        corners = {"top": ([A, UR, T, UL], pal["top_l"]), "left": ([UL, LL, B, BM, BL], pal["left_u"]),
                   "right": ([UR, BR, BM, B, LR], pal["right_u"])}
        out += [poly(p, f, line, sw) for p, f in corners.values()]
    else:
        out += [poly(p, pal[k], line, sw) for k, p in FACETS.items()]
    out += [poly(p, pal[k], line, sw) for k, p in CUBE.items()]
    return "".join(out)


def mark_one_colour(ink, paper=None, sw=4):
    """Single ink: pyramid solid, cube a real (transparent) hole drawn with ink edges."""
    d = f"M{P(TRI).replace(' ', ' L')} Z M{P(CUBE_HEX).replace(' ', ' L')} Z"
    return (f'<path d="{d}" fill="{ink}" fill-rule="evenodd" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round"/>'
            f'<polygon points="{P(CUBE_HEX)}" fill="{paper or "none"}" stroke="{ink}" stroke-width="{sw*1.25}" stroke-linejoin="round"/>'
            f'<polyline points="{P([UL, C, UR])}" fill="none" stroke="{ink}" stroke-width="{sw*1.25}" stroke-linejoin="round"/>'
            f'<line x1="{C[0]}" y1="{C[1]}" x2="{B[0]}" y2="{B[1]}" stroke="{ink}" stroke-width="{sw*1.25}"/>')


def mark_cube(pal, sw=6, sh=8):
    """Cube only — favicon / 16px / tight spaces. Scaled to fill the canvas."""
    s = 2.05
    tx, ty = 128 - CX * s - sh / 2, 128 - CY * s - sh / 2
    line = pal["line"]
    inner = poly(CUBE_HEX, line, line, sw / s, sh / s, sh / s)
    inner += "".join(poly(p, pal[k], line, sw / s) for k, p in CUBE.items())
    return f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s})">{inner}</g>'


def centred(body, scale=1.0, dy=-3):
    """Optically centre a 256-grid element (pyramid bbox is y 34..196)."""
    oy = 128 - 115 + dy
    return f'<g transform="translate({128 - 128 * scale:.2f} {(128 - 128 * scale) + oy * scale:.2f}) scale({scale})">{body}</g>'


# ---- Merit Points coin (`merit-coin`): the pyramid alone, in gold facets
G = (128, (A[1] + 2 * BL[1]) / 3)                                         # centroid
ML, MR = ((A[0] + BL[0]) / 2, (A[1] + BL[1]) / 2), ((A[0] + BR[0]) / 2, (A[1] + BR[1]) / 2)
SIX = [[A, ML, G], [A, G, MR], [ML, BL, G], [BL, BM, G], [MR, G, BR], [G, BM, BR]]
SIX_C = [YELLOW, YELLOW_SOFT, YELLOW_SOFT, YELLOW, YELLOW, YELLOW_SOFT]
TWO = [[A, BM, BL], [A, BR, BM]]                                         # small cut: one ridge


def coin(line=BLACK, small=False):
    sw, sh = (10, 10) if small else (6, 8)
    facets = zip(TWO, [YELLOW, YELLOW_SOFT]) if small else zip(SIX, SIX_C)
    body = poly(TRI, line, line, sw, sh, sh) + "".join(poly(p, c, line, sw) for p, c in facets)
    return centred(body, 0.96)


def coin_glyph_bold():
    c = "currentColor"
    return centred(f'<polygon points="{P(TRI)}" fill="none" stroke="{c}" stroke-width="22" stroke-linejoin="round"/>'
                   f'<line x1="{A[0]}" y1="{A[1]+20}" x2="{BM[0]}" y2="{BM[1]}" stroke="{c}" stroke-width="18"/>', 0.98)


def coin_glyph_fill():
    c = "currentColor"
    gap = 7   # half-width of the ridge knock-out
    left = [(A[0] - gap, A[1] + gap * 1.73), (BM[0] - gap, BM[1]), BL]
    right = [(A[0] + gap, A[1] + gap * 1.73), BR, (BM[0] + gap, BM[1])]
    return centred(poly(left, c, c, 10) + poly(right, c, c, 10), 0.98)


# ---- wordmark (Clash Display / Plus Jakarta Sans outlined to paths)
def text_path(txt, fontfile, size, x, y, tracking=-0.02):
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    f = TTFont(os.path.join(FONTS, fontfile))
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    s, pen, cx = size / upm, SVGPathPen(f.getGlyphSet()), x
    for ch in txt:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
        cx += gs[g].width * s + tracking * size
    return pen.getCommands(), cx - x - tracking * size


def wordmark(x, y, size, col):
    """MERIT in Clash Display Bold caps; PROJECT tracked out to the same width (justified)."""
    d1, w1 = text_path("MERIT", "ClashDisplay-Bold.ttf", size, x, y, 0.0)
    ps = size * 0.34
    _, w2 = text_path("PROJECT", "PlusJakartaSans-Bold.ttf", ps, 0, 0, 0)
    track = (w1 - 4 - w2) / (6 * ps)
    d2, _ = text_path("PROJECT", "PlusJakartaSans-Bold.ttf", ps, x + 2, y + size * 0.46, track)
    return f'<path d="{d1}" fill="{col}"/><path d="{d2}" fill="{col}"/>', w1


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-labelledby="t"><title id="t">{title}</title>\n{body}\n</svg>\n')


def write(name, body, title, w=256, h=256):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(svg(w, h, body, title))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    # logo
    write("merit-mark.svg", centred(mark_brutal(DS), 0.96), "Merit mark — brand style")
    write("merit-mark-dark.svg", centred(mark_brutal(DS_DARK), 0.96), "Merit mark — for dark backgrounds")
    write("merit-mark-small.svg", centred(mark_brutal(DS, sw=6, sh=8, flat=True), 0.96), "Merit mark — flat, small sizes")
    write("merit-mark-small-dark.svg", centred(mark_brutal(DS_DARK, sw=6, sh=8, flat=True), 0.96), "Merit mark — small, dark backgrounds")
    write("merit-cube.svg", mark_cube(DS), "Merit cube")
    write("merit-mark-black.svg", centred(mark_one_colour(BLACK)), "Merit mark — black")
    write("merit-mark-white.svg", centred(mark_one_colour(WHITE)), "Merit mark — white")
    write("merit-mark-achiever.svg", centred(mark_brutal(ACHIEVER), 0.96), "Merit mark — Achiever (Pro)")
    # app icons
    write("merit-app-icon.svg", f'<rect width="256" height="256" fill="{CREAM}"/>' + centred(mark_brutal(DS, sw=5, sh=8), 0.84, -1), "Merit app icon")
    # Android adaptive: 108dp canvas, 66dp safe circle (r=0.305) → triangle circumradius 108·s ≤ 78 → s=0.70
    write("merit-android-foreground.svg", centred(mark_brutal(DS, sw=6, sh=9), 0.70, -1), "Merit adaptive foreground")
    write("merit-android-monochrome.svg", centred(mark_one_colour(BLACK, None, 7), 0.70, -1), "Merit themed icon")
    # Merit Points coin
    write("merit-coin.svg", coin(), "Merit Points coin")
    write("merit-coin-small.svg", coin(small=True), "Merit Points coin — small sizes (≤24px)")
    write("merit-coin-dark.svg", coin(CREAM_W), "Merit Points coin — for dark backgrounds")
    write("merit-coin-glyph-bold.svg", coin_glyph_bold(), "merit-coin icon (Bold)")
    write("merit-coin-glyph-fill.svg", coin_glyph_fill(), "merit-coin icon (Fill)")
    # lockups (need fonttools)
    wm, ww = wordmark(250, 146, 96, INK)
    W = int(250 + ww + 20)
    write("merit-lockup-horizontal.svg", centred(mark_brutal(DS), 0.96) + wm, "Merit Project — horizontal", W)
    wmd, _ = wordmark(250, 146, 96, CREAM_W)
    write("merit-lockup-horizontal-dark.svg", f'<rect width="{W}" height="256" fill="{DARK_BG}"/>' + centred(mark_brutal(DS_DARK), 0.96) + wmd,
          "Merit Project — horizontal dark", W)
    _, w1 = wordmark(0, 0, 80, INK)
    SW = int(max(w1 + 40, 300))
    wms, _ = wordmark(SW / 2 - w1 / 2, 286, 80, INK)
    write("merit-lockup-stacked.svg", f'<g transform="translate({SW/2-128} 0)">{centred(mark_brutal(DS), 0.96)}</g>' + wms,
          "Merit Project — stacked", SW, 340)
    print("\n".join(sorted(f for f in os.listdir(OUT) if f.endswith(".svg"))))
