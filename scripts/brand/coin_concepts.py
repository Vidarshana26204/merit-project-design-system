"""Merit Points coin concepts (round 16, owner asked for a new design built from the v3 tokens).

Usage (from the design-system repo root):
    python3 scripts/brand/coin_concepts.py

Writes assets/v3/brand/coin-concepts/{a,b,c}-{full,small,dark,dark-small}.svg. Every colour is read from
tokens/primitives.tokens.json (no hex typed here), so a palette change regenerates the coins.
  A  Stitched coin  : round coin, patchwork stitch ring, the Merit pyramid struck in the centre
  B  Patch coin     : round coin cut like a subject patchwork (X + corners), white plate, pyramid
  C  Hex medal      : hexagon plate (achievement medal shape), bevelled face, pyramid knock-out, sparkle
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


CONCEPTS = {"a": ("Stitched coin", coin_a), "b": ("Patch coin", coin_b), "c": ("Hex medal", coin_c)}


def main():
    os.makedirs(OUT, exist_ok=True)
    for k, (name, fn) in CONCEPTS.items():
        for cut, line, small in (("full", INK, False), ("small", INK, True), ("dark", CREAM, False), ("dark-small", CREAM, True)):
            path = os.path.join(OUT, f"{k}-{cut}.svg")
            open(path, "w").write(svg(f"Merit Points coin concept {k.upper()} · {name} · {cut}", fn(line, small)))
    print("wrote", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
