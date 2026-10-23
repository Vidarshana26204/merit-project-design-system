"""Merit Points coin concepts (round 16, owner asked for a new design built from the v3 tokens).

Usage (from the design-system repo root):
    python3 scripts/brand/coin_concepts.py            # concepts only
    python3 scripts/brand/coin_concepts.py --final    # also write the shipped v3 coin family (FINAL = picked concept)

Writes assets/v3/brand/coin-concepts/{a,b,c}-{full,small,dark,dark-small}.svg. Every colour is read from
tokens/primitives.tokens.json (no hex typed here), so a palette change regenerates the coins.
  A  Stitched coin  : round coin, patchwork stitch ring, the Merit pyramid struck in the centre
  B  Patch coin     : round coin cut like a subject patchwork (X + corners), white plate, pyramid
  C  Hex medal      : hexagon plate (achievement medal shape), bevelled face, pyramid knock-out, sparkle
  D  Flat gold      : flat gold disc, deeper rim, top-down pyramid as four white facets in a broken ring (owner reference)
Cuts: full (>24px), small (<=24px: no stitches/patterns, heavier outline), dark (cream outline for dark surfaces).
"""
import json
import math
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "assets", "v3", "brand", "coin-concepts")
P = json.load(open(os.path.join(ROOT, "tokens", "primitives.tokens.json")))["color"]
C = lambda fam, step=None: P[fam][step]["$value"] if step else P[fam]["$value"]

INK, CREAM, WHITE = C("ink", "900"), C("mist", "50"), C("white")
FACE, DEEP, PALE = C("butter", "300"), C("butter", "500"), C("butter", "100")
ORANGE, ORANGE_T, SAND = C("orange", "500"), C("orange", "300"), C("sand", "300")
SPARK = C("violet", "600")


def mix(a, b, t):
    """a mixed t toward b (hex)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


PATTERN_INK = mix(ORANGE_T, INK, 0.42)   # the patchwork rule: pattern ink = tint mixed 42% toward ink


def pts(p):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in p)


def svg(title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img" '
            f'aria-labelledby="t"><title id="t">{title}</title>{body}</svg>\n')


TONES = [C("orange", "300"), C("orange", "400"), C("orange", "500"), C("orange", "700")]


def pyramid(cx, cy, w, line, sw, tones=None, small=False):
    """The Merit mark struck on the coin: a low pyramid seen from the left (ridge off-centre) with a tier line,
    four tonal facets, light from the top left. Deliberately not an outlined equilateral triangle, which on a disc
    reads as a warning sign. The small cut keeps two facets."""
    t = tones or TONES
    h = w * 0.78
    a = (cx + w * 0.10, cy - h * 0.60)                     # apex leans right: we see more of the left face
    bl, br, bm = (cx - w / 2, cy + h * 0.40), (cx + w / 2, cy + h * 0.40), (cx + w * 0.16, cy + h * 0.40)
    j = f'stroke="{line}" stroke-width="{sw}" stroke-linejoin="round"'
    if small:
        return (f'<polygon points="{pts([a, bm, bl])}" fill="{t[0]}" {j}/>'
                f'<polygon points="{pts([a, br, bm])}" fill="{t[2]}" {j}/>')
    k = 0.52                                                # tier line, as in the mark's bands
    lerp = lambda p, q: (p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k)
    ml, mm, mr = lerp(a, bl), lerp(a, bm), lerp(a, br)
    faces = [([a, mm, ml], t[0]), ([ml, mm, bm, bl], t[1]), ([a, mr, mm], t[2]), ([mm, mr, br, bm], t[3])]
    return "".join(f'<polygon points="{pts(f)}" fill="{c}" {j}/>' for f, c in faces)


# ---------------------------------------------------------------- A · Stitched coin
def coin_a(line, small):
    sw = 12 if small else 8
    out = [f'<circle cx="128" cy="128" r="108" fill="{FACE}" stroke="{line}" stroke-width="{sw}"/>',
           # lower-right rim shade: the face's deeper tone, a crescent inside the outline
           f'<path d="M 214 92 A 100 100 0 0 1 92 214 A 108 108 0 0 0 214 92 Z" fill="{DEEP}"/>']
    if not small:
        out.append(f'<circle cx="128" cy="128" r="84" fill="none" stroke="{line}" stroke-width="4" '
                   f'stroke-dasharray="10 9" stroke-linecap="round" opacity=".55"/>')
    out.append(pyramid(128, 134, 124 if small else 112, line, sw * 0.6, small=small))
    return "".join(out)


# ---------------------------------------------------------------- B · Patch coin
def coin_b(line, small):
    sw = 12 if small else 7
    c, r = 128, 108
    clip = '<clipPath id="cb"><circle cx="128" cy="128" r="108"/></clipPath>'
    if small:
        wedges = [([(c, c), (c - r, c - r), (c + r, c - r)], FACE), ([(c, c), (c + r, c - r), (c + r, c + r)], ORANGE_T),
                  ([(c, c), (c + r, c + r), (c - r, c + r)], FACE), ([(c, c), (c - r, c + r), (c - r, c - r)], ORANGE_T)]
    else:   # hourglass X + corner triangles, the subject patchwork cut (D16 rev 4)
        wedges = [([(c, c), (c - r, c - r), (c + r, c - r)], FACE), ([(c, c), (c + r, c - r), (c + r, c + r)], ORANGE_T),
                  ([(c, c), (c + r, c + r), (c - r, c + r)], SAND), ([(c, c), (c - r, c + r), (c - r, c - r)], PALE)]
    dots = ""
    if not small:
        dots = ('<pattern id="dt" width="14" height="14" patternUnits="userSpaceOnUse">'
                f'<circle cx="7" cy="7" r="2.6" fill="{PATTERN_INK}"/></pattern>')
    body = [f'<defs>{clip}{dots}</defs><g clip-path="url(#cb)">']
    for k, (p, fill) in enumerate(wedges):
        body.append(f'<polygon points="{pts(p)}" fill="{fill}"/>')
        if k == 1 and not small:
            body.append(f'<polygon points="{pts(p)}" fill="url(#dt)" opacity=".55"/>')
    if not small:
        body.append(f'<path d="M20 20 L236 236 M236 20 L20 236" stroke="{line}" stroke-width="3" opacity=".35"/>')
    body.append("</g>")
    body.append(f'<circle cx="128" cy="128" r="108" fill="none" stroke="{line}" stroke-width="{sw}"/>')
    plate = 96 if small else 84
    body.append(f'<rect x="{c - plate / 2}" y="{c - plate / 2}" width="{plate}" height="{plate}" rx="{plate * 0.22:.1f}" '
                f'fill="{WHITE}" stroke="{line}" stroke-width="{sw * 0.8:.1f}"/>')
    body.append(pyramid(128, 132, plate * 0.74, INK, sw * 0.45, small=small))
    return "".join(body)


# ---------------------------------------------------------------- C · Hex medal
def hexagon(cx, cy, r):
    return [(cx + r * math.cos(math.radians(90 + 60 * k)), cy - r * math.sin(math.radians(90 + 60 * k))) for k in range(6)]


def coin_c(line, small):
    sw = 12 if small else 8
    outer, inner = hexagon(128, 132, 112), hexagon(128, 132, 84)
    out = [f'<polygon points="{pts(outer)}" fill="{FACE}" stroke="{line}" stroke-width="{sw}" stroke-linejoin="round"/>']
    if not small:   # bevel: the three lower facets in the deeper tone
        for k in (2, 3, 4):
            a, b = outer[k], outer[(k + 1) % 6]
            ia, ib = inner[k], inner[(k + 1) % 6]
            out.append(f'<polygon points="{pts([a, b, ib, ia])}" fill="{DEEP}"/>')
        out.append(f'<polygon points="{pts(inner)}" fill="none" stroke="{line}" stroke-width="4" stroke-linejoin="round" opacity=".5"/>')
    out.append(pyramid(128, 138, 128 if small else 116, line, sw * 0.6, small=small))
    if not small:
        s = f'M206 30 Q210 50 230 54 Q210 58 206 78 Q202 58 182 54 Q202 50 206 30 Z'
        out.append(f'<path d="{s}" fill="{SPARK}" stroke="{line}" stroke-width="3" stroke-linejoin="round"/>')
    return "".join(out)


# ---------------------------------------------------------------- D · Flat gold (owner reference: flat disc + white knock-out)
RIM = mix(DEEP, C("orange", "700"), 0.48)
# The Merit mark's facet colours (assets/v3/brand/merit-mark.svg): orange top, violet right, sage left.
BRAND = [C("orange", "500"), C("violet", "500"), C("violet", "700"), C("sage", "500")]
BRAND_DARK = [C("orange", "400"), C("violet", "300"), C("violet", "500"), C("sage", "300")]   # dark cut: the 300/400 steps


def _shrink(poly, cx, cy, k):
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in poly]   # deeper gold: ~3:1 against white so the coin's edge reads on light surfaces


def coin_d(line, small, style="white"):
    """Flat gold disc, no ink outline, a deeper-gold rim, and the mark knocked out in white as separate facets with
    gold gaps between them (the segmented, flat style of the owner's reference, with our own geometry):
    the Merit pyramid seen from above, a diamond cut into four facets on the X (the subject-patchwork cut), lit from
    the top left (two facets white, two butter-100), inside a ring broken into four arcs.
    The small cut drops the ring and widens the gaps so the facets survive at 16px.
    style "fill"   (D1): facets in the Merit mark's brand colours (top-left orange, top-right violet, bottom-right deep
                         violet, bottom-left sage), white gaps, as the mark itself is coloured.
    style "border" (D2): white facets, each outlined in its brand colour (gold gaps kept between outlines)."""
    gap = 14 if small else 9
    out = [f'<circle cx="128" cy="128" r="120" fill="{RIM}"/>',
           f'<circle cx="128" cy="128" r="{112 if small else 113}" fill="{DEEP}"/>']
    if not small:   # ring of four arcs, broken on the diagonals
        r = 97
        for k in range(4):
            a0, a1 = math.radians(-90 + 90 * k + 14), math.radians(-90 + 90 * k + 76)
            x0, y0, x1, y1 = 128 + r * math.cos(a0), 128 + r * math.sin(a0), 128 + r * math.cos(a1), 128 + r * math.sin(a1)
            out.append(f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" stroke="{WHITE}" stroke-width="14"/>')
    R = 90 if small else 74               # diamond half-diagonal
    c = (128, 128)
    top, right, bottom, left = (128, 128 - R), (128 + R, 128), (128, 128 + R), (128 - R, 128)
    quads = [[top, c, left], [top, right, c], [c, right, bottom], [left, c, bottom]]
    if style == "white":
        faces = list(zip(quads, [WHITE, PALE, PALE, WHITE]))
        if small:
            faces = [([top, bottom, left], WHITE), ([top, right, bottom], PALE)]
        for f, fill in faces:
            out.append(f'<polygon points="{pts(f)}" fill="{fill}" stroke="{DEEP}" stroke-width="{gap}" stroke-linejoin="round"/>')
        return "".join(out)
    brand = BRAND_DARK if line == CREAM else BRAND
    if style == "fill":
        for f, col in zip(quads, brand):
            out.append(f'<polygon points="{pts(f)}" fill="{col}" stroke="{WHITE}" stroke-width="{gap}" stroke-linejoin="round"/>')
    else:   # border: white facets with gold gaps, and each facet's outer edge drawn as a brand-coloured bar
        for f in quads:
            out.append(f'<polygon points="{pts(f)}" fill="{WHITE}" stroke="{DEEP}" stroke-width="{gap}" stroke-linejoin="round"/>')
        bw, off = (18, 12) if small else (13, 13)
        edges = [(top, left), (top, right), (right, bottom), (left, bottom)]
        for (p0, p1), col in zip(edges, brand):
            mx, my = (p0[0] + p1[0]) / 2 - 128, (p0[1] + p1[1]) / 2 - 128
            n = math.hypot(mx, my)
            ox, oy = mx / n * off, my / n * off                     # push the bar outward, off the facet
            t0 = lambda p, q, t: (p[0] + (q[0] - p[0]) * t + ox, p[1] + (q[1] - p[1]) * t + oy)
            (x0, y0), (x1, y1) = t0(p0, p1, 0.08), t0(p0, p1, 0.92)
            out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{col}" stroke-width="{bw}" stroke-linecap="round"/>')
    return "".join(out)

CONCEPTS = {"a": ("Stitched coin", coin_a), "b": ("Patch coin", coin_b), "c": ("Hex medal", coin_c), "d": ("Flat gold", coin_d),
            "d1": ("Flat gold, brand facets", lambda l, sm: coin_d(l, sm, "fill")),
            "d2": ("Flat gold, brand borders", lambda l, sm: coin_d(l, sm, "border"))}


FINAL = "d1"   # owner pick 2026-10-24: D1, flat gold with brand-colour facets
V3_BRAND = os.path.join(ROOT, "assets", "v3", "brand")


def glyph_bold():
    """Single-colour icon (tint with currentColor): ring + the X-cut diamond, as outlines."""
    c = "currentColor"
    d = "M128 54 L202 128 L128 202 L54 128 Z"
    return (f'<circle cx="128" cy="128" r="108" fill="none" stroke="{c}" stroke-width="20"/>'
            f'<path d="{d} M128 54 L128 202 M54 128 L202 128" fill="none" stroke="{c}" stroke-width="16" stroke-linejoin="round"/>')


def glyph_fill():
    """Single-colour icon, filled: a disc with the four facets knocked out, joined by solid gaps (the X and rim)."""
    c, gap = "currentColor", 12
    r, cc = 74, (128, 128)
    top, right, bottom, left = (128, 128 - r), (128 + r, 128), (128, 128 + r), (128 - r, 128)
    quads = [[top, cc, left], [top, right, cc], [cc, right, bottom], [left, cc, bottom]]
    mask = "".join(f'<polygon points="{pts(q)}" fill="black" stroke="white" stroke-width="{gap}" stroke-linejoin="round"/>' for q in quads)
    return (f'<defs><mask id="m"><rect width="256" height="256" fill="white"/>{mask}</mask></defs>'
            f'<circle cx="128" cy="128" r="118" fill="{c}" mask="url(#m)"/>')


def final():
    """Write the shipped v3 coin family from the picked concept."""
    name, fn = CONCEPTS[FINAL]
    files = {
        "merit-coin.svg": ("Merit Points coin", fn(INK, False)),
        "merit-coin-small.svg": ("Merit Points coin — small sizes (≤24px)", fn(INK, True)),
        "merit-coin-dark.svg": ("Merit Points coin — for dark backgrounds", fn(CREAM, False)),
        "merit-coin-small-dark.svg": ("Merit Points coin — small sizes, dark backgrounds", fn(CREAM, True)),
        "merit-coin-glyph-bold.svg": ("merit-coin icon (Bold)", glyph_bold()),
        "merit-coin-glyph-fill.svg": ("merit-coin icon (Fill)", glyph_fill()),
    }
    for f, (title, body) in files.items():
        open(os.path.join(V3_BRAND, f), "w").write(svg(f"v3 · {title}", body))
    print("wrote", ", ".join(files))


def main():
    os.makedirs(OUT, exist_ok=True)
    for k, (name, fn) in CONCEPTS.items():
        for cut, line, small in (("full", INK, False), ("small", INK, True), ("dark", CREAM, False), ("dark-small", CREAM, True)):
            path = os.path.join(OUT, f"{k}-{cut}.svg")
            open(path, "w").write(svg(f"Merit Points coin concept {k.upper()} · {name} · {cut}", fn(line, small)))
    print("wrote", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    import sys
    main()
    if "--final" in sys.argv:
        final()
