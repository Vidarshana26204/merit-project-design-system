"""Subject palettes: one subject colour (`subjects.color_hex`) → every colour its patchworks use.

Engine v5 (D16 rev 5). The subject's hex fixes the **hue**; lightness and chroma come from
fixed recipes in OKLCH, so any hex (a saturated Tailwind red, a muted teal) yields pastel
patch tints that sit with the DS tokens, solid patches that are the subject colour itself,
and icon accents that hold up on the white plate. Every topic and subtopic of the subject
draws from the same palette, so the whole branch reads as the subject's colour.

    palette("#EF4444") -> Palette(tints=[…7 hex], solids=[…2 hex], accents=[(accent, shade)…3])

Pure Python, deterministic; colours outside sRGB lose chroma until they fit.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    base: str                          # the subject colour, normalised "#RRGGBB"
    tints: list[str]                   # light patch fills
    solids: list[str]                  # strong patches (at most one per tile)
    accents: list[tuple[str, str]]     # icon accent + its darker twin


# (hue shift °, L, chroma cap, chroma × base) — patch tints, light enough for 42%-ink patterns
TINTS = [(0, 0.86, 0.10, 0.45), (0, 0.93, 0.05, 0.25), (28, 0.89, 0.08, 0.40), (-28, 0.88, 0.08, 0.40),
         (60, 0.91, 0.06, 0.30), (180, 0.92, 0.045, 0.25), (0, 0.955, 0.022, 0.12)]
ACCENTS = [(0, 0.76, 0.15, 0.75), (22, 0.78, 0.14, 0.70), (-22, 0.77, 0.14, 0.70)]


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def norm(hexv: str) -> str:
    m = re.fullmatch(r"#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})", hexv.strip())
    if not m:
        raise ValueError(f"not a hex colour: {hexv!r}")
    h = m.group(1)
    return "#" + ("".join(c * 2 for c in h) if len(h) == 3 else h).upper()


def to_oklch(hexv: str) -> tuple[float, float, float]:
    h = norm(hexv)
    r, g, b = (_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    A = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    B = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def _rgb(L: float, C: float, H: float) -> tuple[float, float, float]:
    A, B = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l_ = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m_ = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s_ = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    return (4.0767416621 * l_ - 3.3077118913 * m_ + 0.2309699292 * s_,
            -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
            -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)


def from_oklch(L: float, C: float, H: float) -> str:
    """OKLCH → hex, reducing chroma until the colour is inside sRGB."""
    for _ in range(40):
        rgb = _rgb(L, C, H)
        if all(-1e-4 <= c <= 1 + 1e-4 for c in rgb):
            break
        C *= 0.9
    return "#" + "".join(f"{round(min(1, max(0, _gam(min(1, max(0, c))))) * 255):02X}" for c in _rgb(L, C, H))


def palette(hexv: str) -> Palette:
    base = norm(hexv)
    L0, C0, H0 = to_oklch(base)

    def make(spec: list[tuple[float, float, float, float]]) -> list[str]:
        return [from_oklch(L, min(cap, C0 * k), H0 + dh) for dh, L, cap, k in spec]

    tints = list(dict.fromkeys(make(TINTS)))
    solid = from_oklch(min(max(L0, 0.52), 0.80), C0, H0)        # the subject colour (L clamped 0.52–0.80)
    deep = from_oklch(max(min(L0, 0.80) - 0.12, 0.40), C0, H0)
    accents = [(a, from_oklch(L - 0.10, min(cap, C0 * k), H0 + dh))
               for a, (dh, L, cap, k) in zip(make(ACCENTS), ACCENTS)]
    return Palette(base, tints, list(dict.fromkeys([solid, deep])), accents)
